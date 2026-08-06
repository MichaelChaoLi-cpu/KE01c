"""Shared intervention screening for the KE01c conditional-fire analysis."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd

from fire_service_access_common import (
    BACKUP_THRESHOLD_MIN,
    DEMAND_PATH,
    DISPATCH_PATH,
    UNMET_SERVICE_CAP_MIN,
    accepted_connectors,
    build_augmented_graph,
    build_station_od,
    scenario_availability,
)
from fire_service_reliability_common import build_compact_fire_network


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"

CONSEQUENCE_PATH = RESULTS / "derived/fire_consequence_125m.parquet"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
ACTION_PATH = RESULTS / "derived/intervention_actions.parquet"
PERFORMANCE_PATH = RESULTS / "derived/intervention_performance.parquet"
CONTEXT_PATH = RESULTS / "derived/intervention_context_125m.parquet"
SECTION_EDGE_PATH = PROCESSED / "routable_road_edges_sectioned_preprocessed.parquet"
SECTION_INTERVENTION_PATH = PROCESSED / "road_section_intervention_preprocessed.parquet"

PROJECTED_CRS = 6670
MAX_BUDGET = 5
PREPOSITION_CANDIDATES = 35
PREPOSITION_SPACING_M = 2_000.0
WATER_CANDIDATES = 25
WATER_SPACING_M = 1_200.0
WATER_SUPPORT_RADIUS_M = 1_000.0
ROAD_BRIDGE_CANDIDATES = 14
ROAD_PROXIMITY_CANDIDATES = 14
ROAD_SCREEN_CANDIDATES = 24
ROAD_PROXIMITY_DISTANCE_M = 5_000.0
ROAD_PRIORITY_CELL_COUNT = 250
MINAMI_WARD_CODE = "43104"


def cache_is_current() -> bool:
    """Use intervention caches only when source layers and this code are older."""
    sources = [
        CONSEQUENCE_PATH,
        ADMIN_PATH,
        SECTION_EDGE_PATH,
        SECTION_INTERVENTION_PATH,
        DEMAND_PATH,
        DISPATCH_PATH,
        RESULTS / "derived/network/fire_station_od_central.npz",
        Path(__file__),
    ]
    return (
        ACTION_PATH.exists()
        and PERFORMANCE_PATH.exists()
        and CONTEXT_PATH.exists()
        and min(
            ACTION_PATH.stat().st_mtime,
            PERFORMANCE_PATH.stat().st_mtime,
            CONTEXT_PATH.stat().st_mtime,
        )
        >= max(path.stat().st_mtime for path in sources)
    )


def accessibility_penalty(response_time: np.ndarray, qualifying: np.ndarray) -> np.ndarray:
    """Evaluate the Section 6.3 accessibility penalty."""
    return 0.5 * np.minimum(response_time / UNMET_SERVICE_CAP_MIN, 1) + 0.5 / np.maximum(
        qualifying,
        1,
    )


def spaced_candidates(
    points: gpd.GeoSeries,
    scores: np.ndarray,
    eligible: np.ndarray,
    *,
    count: int,
    spacing_m: float,
) -> list[int]:
    """Select high-scoring candidate cells with a declared minimum spacing."""
    order = np.argsort(np.where(eligible, scores, -np.inf))[::-1]
    selected: list[int] = []
    selected_xy: list[tuple[float, float]] = []
    for index in order:
        if not eligible[index] or not np.isfinite(scores[index]):
            continue
        point = points.iloc[index]
        xy = (float(point.x), float(point.y))
        if selected_xy and min(
            np.hypot(xy[0] - x, xy[1] - y) for x, y in selected_xy
        ) < spacing_m:
            continue
        selected.append(int(index))
        selected_xy.append(xy)
        if len(selected) >= count:
            break
    return selected


def travel_vector(
    graph: nx.Graph,
    source: str,
    demand_lookup: dict[str, int],
    cell_count: int,
) -> np.ndarray:
    """Return one temporary origin's capped travel time to every demand cell."""
    vector = np.full(cell_count, UNMET_SERVICE_CAP_MIN, dtype=np.float32)
    distances = nx.single_source_dijkstra_path_length(
        graph,
        source,
        cutoff=UNMET_SERVICE_CAP_MIN,
        weight="minutes",
    )
    for node, minutes in distances.items():
        index = demand_lookup.get(str(node))
        if index is not None:
            vector[index] = min(float(minutes), UNMET_SERVICE_CAP_MIN)
    return vector


def greedy_prepositioning(
    candidate_indices: list[int],
    candidate_times: dict[int, np.ndarray],
    baseline_time: np.ndarray,
    baseline_count: np.ndarray,
    objective_weight: np.ndarray,
    selection_weight: np.ndarray,
) -> tuple[list[int], list[float]]:
    """Forward-select temporary origins under one declared selection objective."""
    current_time = baseline_time.copy()
    current_count = baseline_count.copy()
    baseline_penalty = accessibility_penalty(baseline_time, baseline_count)
    selected: list[int] = []
    benefits: list[float] = []
    for _ in range(MAX_BUDGET):
        best_index = None
        best_selection_gain = -np.inf
        for index in candidate_indices:
            if index in selected:
                continue
            candidate_time = candidate_times[index]
            next_time = np.minimum(current_time, candidate_time)
            next_count = current_count + (candidate_time <= BACKUP_THRESHOLD_MIN)
            gain = float(
                selection_weight
                @ (
                    accessibility_penalty(current_time, current_count)
                    - accessibility_penalty(next_time, next_count)
                )
            )
            if gain > best_selection_gain:
                best_selection_gain = gain
                best_index = index
        if best_index is None:
            break
        selected.append(best_index)
        chosen_time = candidate_times[best_index]
        current_time = np.minimum(current_time, chosen_time)
        current_count = current_count + (chosen_time <= BACKUP_THRESHOLD_MIN)
        benefit = float(
            objective_weight
            @ (baseline_penalty - accessibility_penalty(current_time, current_count))
        )
        benefits.append(benefit)
    return selected, benefits


def greedy_water_support(
    masks: dict[int, np.ndarray],
    objective_weight: np.ndarray,
    selection_weight: np.ndarray,
) -> tuple[list[int], list[float]]:
    """Forward-select bounded one-kilometre water-support areas."""
    covered = np.zeros(len(objective_weight), dtype=bool)
    selected: list[int] = []
    benefits: list[float] = []
    for _ in range(MAX_BUDGET):
        best_index = None
        best_gain = -np.inf
        for index, mask in masks.items():
            if index in selected:
                continue
            gain = float(selection_weight[mask & ~covered].sum())
            if gain > best_gain:
                best_gain = gain
                best_index = index
        if best_index is None:
            break
        selected.append(best_index)
        covered |= masks[best_index]
        benefits.append(float(objective_weight[covered].sum()))
    return selected, benefits


def network_metrics(
    graph: nx.Graph,
    station_sources: list[str],
    demand_lookup: dict[str, int],
    cell_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute exact nearest response time and 10-minute station count."""
    sources = [source for source in station_sources if source in graph]
    minimum_time = np.full(cell_count, UNMET_SERVICE_CAP_MIN, dtype=np.float32)
    if sources:
        nearest = nx.multi_source_dijkstra_path_length(
            graph,
            sources,
            cutoff=UNMET_SERVICE_CAP_MIN,
            weight="minutes",
        )
        for node, minutes in nearest.items():
            index = demand_lookup.get(str(node))
            if index is not None:
                minimum_time[index] = min(float(minutes), UNMET_SERVICE_CAP_MIN)

    qualifying = np.zeros(cell_count, dtype=np.int16)
    for source in sources:
        distances = nx.single_source_dijkstra_path_length(
            graph,
            source,
            cutoff=BACKUP_THRESHOLD_MIN,
            weight="minutes",
        )
        for node in distances:
            index = demand_lookup.get(str(node))
            if index is not None:
                qualifying[index] += 1
    return minimum_time, qualifying


def road_section_candidates(
    graph: nx.Graph,
    sections: gpd.GeoDataFrame,
    demand_nodes: list[str],
    station_sources: list[str],
    objective_weight: np.ndarray,
    cell_points: gpd.GeoSeries,
) -> gpd.GeoDataFrame:
    """Screen event-exposed road sections by bridging and consequence proximity."""
    component_of: dict[str, int] = {}
    for component_id, nodes in enumerate(nx.connected_components(graph)):
        for node in nodes:
            component_of[str(node)] = component_id
    demand_weight: defaultdict[int, float] = defaultdict(float)
    for index, node in enumerate(demand_nodes):
        component = component_of.get(str(node))
        if component is not None:
            demand_weight[component] += float(objective_weight[index])
    station_count: defaultdict[int, int] = defaultdict(int)
    for source in station_sources:
        component = component_of.get(str(source))
        if component is not None:
            station_count[component] += 1

    membership_priority = {
        "Primary Emergency Road": 3,
        "Secondary Emergency Road": 2,
        "None": 1,
    }
    eligible = sections.loc[
        sections["Road Restoration Cost Proxy"].notna()
        & sections["Network Analysis Eligible"].fillna(False)
        & sections["Road Available"].fillna(False)
    ].copy()
    if eligible.empty:
        raise ValueError("No event-exposed road sections are eligible for restoration")

    bridging_rows: list[dict[str, object]] = []
    bridge_columns = [
        "Road Section ID",
        "Section From Node ID",
        "Section To Node ID",
        "Emergency Route Membership",
    ]
    for section_id, from_node_value, to_node_value, membership_value in eligible[
        bridge_columns
    ].itertuples(index=False, name=None):
        from_node = str(from_node_value)
        to_node = str(to_node_value)
        from_component = component_of.get(from_node)
        to_component = component_of.get(to_node)
        if (
            from_component is None
            or to_component is None
            or from_component == to_component
        ):
            continue
        potential = 0.0
        if station_count[from_component] > 0:
            potential += demand_weight[to_component]
        if station_count[to_component] > 0:
            potential += demand_weight[from_component]
        if potential <= 0:
            continue
        membership = str(membership_value)
        bridging_rows.append(
            {
                "Road Section ID": str(section_id),
                "Bridge Screening Score": potential,
                "Emergency Priority": membership_priority.get(membership, 1),
            }
        )
    bridge = pd.DataFrame(bridging_rows)
    if bridge.empty:
        bridge_ids: list[str] = []
    else:
        bridge["Screen Rank Score"] = bridge["Bridge Screening Score"] * (
            1 + 0.15 * (bridge["Emergency Priority"] - 1)
        )
        bridge_ids = bridge.nlargest(
            ROAD_BRIDGE_CANDIDATES,
            "Screen Rank Score",
        )["Road Section ID"].tolist()

    priority_indices = np.argsort(objective_weight)[-ROAD_PRIORITY_CELL_COUNT:]
    priority_cells = gpd.GeoDataFrame(
        {"Priority Weight": objective_weight[priority_indices]},
        geometry=cell_points.iloc[priority_indices].to_numpy(),
        crs=cell_points.crs,
    )
    nearest = gpd.sjoin_nearest(
        priority_cells,
        eligible[["Road Section ID", "Geometry"]],
        how="left",
        max_distance=ROAD_PROXIMITY_DISTANCE_M,
        distance_col="Distance to Road Section (m)",
    )
    nearest = nearest.dropna(subset=["Road Section ID"]).copy()
    nearest["Proximity Screening Score"] = nearest["Priority Weight"] / (
        1 + nearest["Distance to Road Section (m)"] / 1_000
    )
    proximity = nearest.groupby("Road Section ID", as_index=False).agg(
        **{"Proximity Screening Score": ("Proximity Screening Score", "sum")}
    )
    proximity_ids = proximity.nlargest(
        ROAD_PROXIMITY_CANDIDATES,
        "Proximity Screening Score",
    )["Road Section ID"].astype(str).tolist()

    candidate_ids = list(dict.fromkeys(bridge_ids + proximity_ids))
    if not candidate_ids:
        raise ValueError("No event-exposed road-section candidates were screened")
    candidate_frame = eligible.loc[
        eligible["Road Section ID"].astype(str).isin(candidate_ids)
    ].copy()
    candidate_frame["Road Section ID"] = candidate_frame["Road Section ID"].astype(str)
    candidate_frame = candidate_frame.merge(
        bridge[["Road Section ID", "Bridge Screening Score", "Screen Rank Score"]]
        if not bridge.empty
        else pd.DataFrame(
            columns=["Road Section ID", "Bridge Screening Score", "Screen Rank Score"]
        ),
        how="left",
        on="Road Section ID",
    ).merge(
        proximity,
        how="left",
        on="Road Section ID",
    )
    candidate_frame["Bridge Screening Score"] = candidate_frame[
        "Bridge Screening Score"
    ].fillna(0.0)
    candidate_frame["Screen Rank Score"] = candidate_frame["Screen Rank Score"].fillna(0.0)
    candidate_frame["Proximity Screening Score"] = candidate_frame[
        "Proximity Screening Score"
    ].fillna(0.0)
    candidate_frame["Screened as Bridge"] = candidate_frame["Road Section ID"].isin(
        bridge_ids
    )
    candidate_frame["Screened by Consequence Proximity"] = candidate_frame[
        "Road Section ID"
    ].isin(proximity_ids)
    candidate_frame = gpd.GeoDataFrame(
        candidate_frame,
        geometry="Geometry",
        crs=eligible.crs,
    )
    candidate_frame = candidate_frame.sort_values(
        ["Screened as Bridge", "Screen Rank Score", "Proximity Screening Score"],
        ascending=False,
        kind="stable",
    ).head(ROAD_SCREEN_CANDIDATES)
    return candidate_frame.reset_index(drop=True)


def construct_interventions() -> tuple[gpd.GeoDataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """Construct intervention actions and budget-performance results."""
    context = gpd.read_parquet(CONSEQUENCE_PATH).to_crs(PROJECTED_CRS)
    context["Mesh Code"] = context["Mesh Code"].astype("string")
    demand = gpd.read_parquet(DEMAND_PATH).to_crs(PROJECTED_CRS).reset_index(drop=True)
    dispatch = gpd.read_parquet(DISPATCH_PATH).reset_index(drop=True)
    central_od, demand_order, _ = build_station_od("central")
    if not demand["Mesh Code"].astype("string").equals(
        demand_order["Mesh Code"].astype("string").reset_index(drop=True)
    ):
        raise ValueError("Geographic demand order does not match the central OD matrix")
    context = context.set_index("Mesh Code").reindex(
        demand["Mesh Code"].astype("string")
    ).reset_index()
    context = gpd.GeoDataFrame(context, geometry="Geometry", crs=PROJECTED_CRS)

    administrative = gpd.read_parquet(ADMIN_PATH).to_crs(PROJECTED_CRS)
    minami = administrative.loc[
        administrative["Municipality Code"].astype("string").eq(MINAMI_WARD_CODE)
    ].dissolve()
    cell_points = context.geometry.centroid
    in_water_boundary = cell_points.within(minami.geometry.iloc[0]).to_numpy()

    objective_weight = (
        context["Conditional Spread Susceptibility"]
        * context["Population Exposure"]
    ).to_numpy(dtype=np.float64)
    population_weight = context["Total Population"].to_numpy(dtype=np.float64)
    baseline_time = central_od.min(axis=0)
    baseline_count = (central_od <= BACKUP_THRESHOLD_MIN).sum(axis=0).astype(np.int16)
    baseline_penalty = accessibility_penalty(baseline_time, baseline_count)
    water_penalty = in_water_boundary.astype(np.float64)
    cell_loss = objective_weight * (1 + baseline_penalty + water_penalty)
    baseline_loss = float(cell_loss.sum())
    context["Combined Stress Conditional Consequence"] = cell_loss
    context["Combined Stress Consequence Rank"] = pd.Series(cell_loss).rank(
        method="average",
        pct=True,
    ).to_numpy()
    context["Water Constraint Scenario"] = np.where(
        in_water_boundary,
        "Bounded water-unavailable stress",
        "Normal-reliance boundary",
    )

    edge_columns = [
        "Road Edge ID",
        "Road Section ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Assumed Speed (km/h)",
        "Road Available",
        "Network Analysis Eligible",
        "Hazard Exposure Class",
        "Emergency Route Membership",
        "Road Category",
        "Geometry",
    ]
    all_edges = gpd.read_parquet(SECTION_EDGE_PATH, columns=edge_columns).to_crs(
        PROJECTED_CRS
    )
    all_edges["Road Edge ID"] = all_edges["Road Edge ID"].astype("string")
    all_edges["Road Section ID"] = all_edges["Road Section ID"].astype("string")
    central_mask = scenario_availability(all_edges, "central")
    eligible_mask = all_edges["Road Available"].fillna(False) & all_edges[
        "Network Analysis Eligible"
    ].fillna(False)
    central_edges = all_edges.loc[central_mask].copy()
    removed_edges = all_edges.loc[eligible_mask & ~central_mask].copy()
    demand_connectors = accepted_connectors(demand, "Demand Node ID", None, "demand")
    dispatch_connectors = accepted_connectors(
        dispatch,
        "Dispatch Base Node ID",
        "Candidate Dispatch Base",
        "dispatch",
    )
    connectors = pd.concat([demand_connectors, dispatch_connectors], ignore_index=True)
    central_graph = build_augmented_graph(central_edges, connectors)
    demand_nodes = demand["Demand Node ID"].astype("string").tolist()
    demand_lookup = {str(node): index for index, node in enumerate(demand_nodes)}
    station_sources = dispatch["Dispatch Base Node ID"].astype("string").tolist()

    eligible_preposition = np.array(
        [str(node) in central_graph for node in demand_nodes],
        dtype=bool,
    )
    preposition_candidates = spaced_candidates(
        cell_points,
        cell_loss,
        eligible_preposition,
        count=PREPOSITION_CANDIDATES,
        spacing_m=PREPOSITION_SPACING_M,
    )
    candidate_times: dict[int, np.ndarray] = {}
    for number, index in enumerate(preposition_candidates, start=1):
        candidate_times[index] = travel_vector(
            central_graph,
            str(demand_nodes[index]),
            demand_lookup,
            len(context),
        )
        print(
            f"temporary-origin travel times: {number}/{len(preposition_candidates)}",
            flush=True,
        )
    preposition_selected, preposition_benefits = greedy_prepositioning(
        preposition_candidates,
        candidate_times,
        baseline_time,
        baseline_count,
        objective_weight,
        objective_weight,
    )
    preposition_baseline_selected, preposition_baseline_benefits = greedy_prepositioning(
        preposition_candidates,
        candidate_times,
        baseline_time,
        baseline_count,
        objective_weight,
        population_weight,
    )

    water_candidates = spaced_candidates(
        cell_points,
        cell_loss,
        in_water_boundary,
        count=WATER_CANDIDATES,
        spacing_m=WATER_SPACING_M,
    )
    point_x = cell_points.x.to_numpy()
    point_y = cell_points.y.to_numpy()
    water_masks: dict[int, np.ndarray] = {}
    for index in water_candidates:
        distance_squared = (
            (point_x - point_x[index]) ** 2 + (point_y - point_y[index]) ** 2
        )
        water_masks[index] = (
            distance_squared <= WATER_SUPPORT_RADIUS_M**2
        ) & in_water_boundary
    water_selected, water_benefits = greedy_water_support(
        water_masks,
        objective_weight,
        objective_weight,
    )
    water_baseline_selected, water_baseline_benefits = greedy_water_support(
        water_masks,
        objective_weight,
        population_weight,
    )

    sections = gpd.read_parquet(SECTION_INTERVENTION_PATH).to_crs(PROJECTED_CRS)
    sections["Road Section ID"] = sections["Road Section ID"].astype("string")
    road_candidates = road_section_candidates(
        central_graph,
        sections,
        demand_nodes,
        station_sources,
        objective_weight,
        cell_points,
    )
    section_lookup = sections.set_index("Road Section ID", drop=False)
    candidate_ids = road_candidates["Road Section ID"].astype(str).tolist()
    candidate_cost = road_candidates.set_index("Road Section ID")[
        "Road Restoration Cost Proxy"
    ].astype(float)
    sparse_network = build_compact_fire_network(include_event_removed=True)
    if not np.array_equal(
        sparse_network.mesh_codes.astype(str),
        demand["Mesh Code"].astype(str).to_numpy(),
    ):
        raise ValueError("Sparse road network demand order does not match interventions")
    section_position = pd.Series(
        np.arange(len(sparse_network.road_section_ids), dtype=np.int32),
        index=sparse_network.road_section_ids,
    )
    if not set(candidate_ids).issubset(section_position.index):
        raise ValueError("A screened restoration section is absent from the sparse network")
    sparse_baseline_time, _ = sparse_network.route()
    sparse_baseline_time = np.minimum(sparse_baseline_time, UNMET_SERVICE_CAP_MIN)
    baseline_difference = np.nanmax(np.abs(sparse_baseline_time - baseline_time))
    if baseline_difference > 1e-5:
        raise ValueError(
            "Sparse event baseline does not reproduce the accepted station OD matrix: "
            f"maximum difference={baseline_difference:.6g} minutes"
        )
    road_time_cache: dict[frozenset[str], np.ndarray] = {
        frozenset(): baseline_time
    }
    road_penalty_cache: dict[frozenset[str], np.ndarray] = {
        frozenset(): baseline_penalty
    }

    def restored_mask(section_ids: frozenset[str]) -> np.ndarray:
        mask = np.zeros(len(sparse_network.road_section_ids), dtype=bool)
        if section_ids:
            mask[section_position.loc[list(section_ids)].to_numpy(np.int32)] = True
        return mask

    def road_bundle_time_benefit(section_ids: list[str]) -> float:
        """Fast screening benefit using exact nearest-base rerouting."""
        key = frozenset(section_ids)
        if key not in road_time_cache:
            response_time, _ = sparse_network.route(
                restored=restored_mask(key),
            )
            road_time_cache[key] = np.minimum(response_time, UNMET_SERVICE_CAP_MIN)
        candidate_penalty = accessibility_penalty(
            road_time_cache[key],
            baseline_count,
        )
        return float(objective_weight @ (baseline_penalty - candidate_penalty))

    def road_bundle_benefit(section_ids: list[str]) -> float:
        """Final benefit using nearest time and exact 10-minute backup counts."""
        key = frozenset(section_ids)
        if key not in road_penalty_cache:
            response_time, qualifying, _ = sparse_network.route_metrics(
                restored=restored_mask(key),
                backup_threshold_min=BACKUP_THRESHOLD_MIN,
                response_cap_min=UNMET_SERVICE_CAP_MIN,
            )
            road_penalty_cache[key] = accessibility_penalty(response_time, qualifying)
        return float(objective_weight @ (baseline_penalty - road_penalty_cache[key]))

    singleton_benefit = {
        section_id: road_bundle_time_benefit([section_id])
        for section_id in candidate_ids
    }
    candidate_ids = [
        section_id for section_id in candidate_ids if singleton_benefit[section_id] > 0
    ]
    if not candidate_ids:
        raise ValueError("Screened road sections produced no positive accessibility gain")

    road_selected: list[str] = []
    for budget in range(1, MAX_BUDGET + 1):
        best_section = None
        best_benefit = -np.inf
        for section_id in candidate_ids:
            if section_id in road_selected:
                continue
            benefit = road_bundle_time_benefit(road_selected + [section_id])
            if benefit > best_benefit:
                best_benefit = benefit
                best_section = section_id
        if best_section is None:
            break
        road_selected.append(best_section)
        print(
            f"road-section count screening budget: {budget}/{MAX_BUDGET}",
            flush=True,
        )

    category_priority = {
        "National Expressway or Equivalent": 4,
        "National Highway": 3,
        "Prefectural Road": 2,
        "Municipal Road or Equivalent": 1,
        "Other": 0,
    }
    emergency_priority = {
        "Primary Emergency Road": 3,
        "Secondary Emergency Road": 2,
        "None": 1,
    }
    baseline_order = road_candidates.loc[
        road_candidates["Road Section ID"].astype(str).isin(candidate_ids)
    ].assign(
        Category_Priority=lambda frame: frame["Road Category"].map(
            category_priority
        ).fillna(0),
        Emergency_Priority=lambda frame: frame["Emergency Route Membership"].map(
            emergency_priority
        ).fillna(1),
    ).sort_values(
        ["Category_Priority", "Emergency_Priority", "Bridge Screening Score"],
        ascending=False,
        kind="stable",
    )["Road Section ID"].astype(str).tolist()
    road_baseline_selected = baseline_order[:MAX_BUDGET]
    cost_order = sorted(
        candidate_ids,
        key=lambda section_id: (
            singleton_benefit[section_id] / candidate_cost.loc[section_id]
        ),
        reverse=True,
    )

    def nested_bundles_within_cost(order: list[str]) -> list[list[str]]:
        selected: list[str] = []
        used = 0.0
        bundles: list[list[str]] = []
        for budget in range(1, MAX_BUDGET + 1):
            for section_id in order:
                if section_id in selected:
                    continue
                cost = float(candidate_cost.loc[section_id])
                if used + cost <= float(budget) + 1e-12:
                    selected.append(section_id)
                    used += cost
            bundles.append(selected.copy())
        return bundles

    road_count_bundles = [
        road_selected[: min(budget, len(road_selected))]
        for budget in range(1, MAX_BUDGET + 1)
    ]
    road_baseline_count_bundles = [
        road_baseline_selected[: min(budget, len(road_baseline_selected))]
        for budget in range(1, MAX_BUDGET + 1)
    ]
    road_cost_bundles = nested_bundles_within_cost(cost_order)
    road_baseline_cost_bundles = nested_bundles_within_cost(baseline_order)
    road_count_benefits = [road_bundle_benefit(bundle) for bundle in road_count_bundles]
    road_baseline_count_benefits = [
        road_bundle_benefit(bundle) for bundle in road_baseline_count_bundles
    ]
    road_cost_benefits = [road_bundle_benefit(bundle) for bundle in road_cost_bundles]
    road_baseline_cost_benefits = [
        road_bundle_benefit(bundle) for bundle in road_baseline_cost_bundles
    ]

    performance_records: list[dict[str, object]] = []
    count_performance_specs = (
        (
            "Temporary response base",
            "Greedy consequence reduction",
            preposition_selected,
            preposition_benefits,
        ),
        (
            "Temporary response base",
            "Simple baseline",
            preposition_baseline_selected,
            preposition_baseline_benefits,
        ),
        (
            "Bounded water support",
            "Greedy consequence reduction",
            water_selected,
            water_benefits,
        ),
        (
            "Bounded water support",
            "Simple baseline",
            water_baseline_selected,
            water_baseline_benefits,
        ),
        (
            "Priority road restoration",
            "Greedy consequence reduction",
            road_selected,
            road_count_benefits,
        ),
        (
            "Priority road restoration",
            "Simple baseline",
            road_baseline_selected,
            road_baseline_count_benefits,
        ),
    )
    for action_type, strategy, selected, benefits in count_performance_specs:
        for budget, benefit in enumerate(benefits, start=1):
            selected_ids = selected[:budget]
            is_road = action_type == "Priority road restoration"
            performance_records.append(
                {
                    "Action Type": action_type,
                    "Strategy": strategy,
                    "Budget Definition": (
                        "Road section count" if is_road else "Action count"
                    ),
                    "Budget": budget,
                    "Budget Used": float(budget),
                    "Selected Action IDs": " | ".join(map(str, selected_ids)),
                    "Selected Road Section Count": (
                        len(selected_ids) if is_road else np.nan
                    ),
                    "Selected Road Section Length (m)": (
                        float(
                            section_lookup.loc[
                                selected_ids,
                                "Road Section Length (m)",
                            ].sum()
                        )
                        if is_road and selected_ids
                        else np.nan
                    ),
                    "Road Restoration Cost Proxy": (
                        float(candidate_cost.loc[selected_ids].sum())
                        if is_road and selected_ids
                        else np.nan
                    ),
                    "Intervention Benefit": benefit,
                    "Consequence Reduction Share": benefit / baseline_loss,
                    "Baseline Combined-Stress Loss": baseline_loss,
                }
            )

    for strategy, bundles, benefits in (
        ("Greedy consequence reduction", road_cost_bundles, road_cost_benefits),
        ("Simple baseline", road_baseline_cost_bundles, road_baseline_cost_benefits),
    ):
        for budget, (selected_ids, benefit) in enumerate(
            zip(bundles, benefits, strict=True),
            start=1,
        ):
            used_cost = (
                float(candidate_cost.loc[selected_ids].sum()) if selected_ids else 0.0
            )
            performance_records.append(
                {
                    "Action Type": "Priority road restoration",
                    "Strategy": strategy,
                    "Budget Definition": "Normalized event-exposed length",
                    "Budget": budget,
                    "Budget Used": used_cost,
                    "Selected Action IDs": " | ".join(selected_ids),
                    "Selected Road Section Count": len(selected_ids),
                    "Selected Road Section Length (m)": (
                        float(
                            section_lookup.loc[
                                selected_ids,
                                "Road Section Length (m)",
                            ].sum()
                        )
                        if selected_ids
                        else 0.0
                    ),
                    "Road Restoration Cost Proxy": used_cost,
                    "Intervention Benefit": benefit,
                    "Consequence Reduction Share": benefit / baseline_loss,
                    "Baseline Combined-Stress Loss": baseline_loss,
                }
            )
    performance = pd.DataFrame(performance_records)

    action_records: list[dict[str, object]] = []
    for rank, index in enumerate(preposition_selected, start=1):
        action_records.append(
            {
                "Action ID": f"PREPOSITION::{context.iloc[index]['Mesh Code']}",
                "Action Type": "Temporary response base",
                "Selection Rank": rank,
                "Road Selection Basis": None,
                "Road Section ID": None,
                "Road Section Length (m)": np.nan,
                "Road Restoration Cost Proxy": np.nan,
                "Action Description": "Temporary dispatch origin at a screened 125 m cell",
                "Geometry": cell_points.iloc[index],
            }
        )
    for rank, index in enumerate(water_selected, start=1):
        action_records.append(
            {
                "Action ID": f"WATER::{context.iloc[index]['Mesh Code']}",
                "Action Type": "Bounded water support",
                "Selection Rank": rank,
                "Road Selection Basis": None,
                "Road Section ID": None,
                "Road Section Length (m)": np.nan,
                "Road Restoration Cost Proxy": np.nan,
                "Action Description": "Temporary water support within a 1 km screening radius",
                "Geometry": cell_points.iloc[index],
            }
        )
    for selection_basis, selected_sections in (
        ("Road section count", road_selected),
        ("Normalized event-exposed length", road_cost_bundles[-1]),
    ):
        for rank, section_id in enumerate(selected_sections, start=1):
            row = section_lookup.loc[section_id]
            action_records.append(
                {
                    "Action ID": f"ROAD::{selection_basis}::{section_id}",
                    "Action Type": "Priority road restoration",
                    "Selection Rank": rank,
                    "Road Selection Basis": selection_basis,
                    "Road Section ID": section_id,
                    "Road Section Length (m)": float(row["Road Section Length (m)"]),
                    "Road Restoration Cost Proxy": float(
                        row["Road Restoration Cost Proxy"]
                    ),
                    "Action Description": (
                        "Restore the event-exposed internal edges of one "
                        "junction-to-junction road section"
                    ),
                    "Geometry": row["Geometry"],
                }
            )
    actions = gpd.GeoDataFrame(action_records, geometry="Geometry", crs=PROJECTED_CRS)

    ACTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    actions.to_parquet(ACTION_PATH, index=False)
    performance.to_parquet(PERFORMANCE_PATH, index=False)
    context.to_parquet(CONTEXT_PATH, index=False)
    print(f"Saved: {ACTION_PATH.relative_to(ROOT)}", flush=True)
    print(f"Saved: {PERFORMANCE_PATH.relative_to(ROOT)}", flush=True)
    print(f"Saved: {CONTEXT_PATH.relative_to(ROOT)}", flush=True)
    return actions, performance, context


def load_interventions() -> tuple[gpd.GeoDataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """Load current intervention caches or construct them."""
    if cache_is_current():
        print("Using current intervention caches", flush=True)
        return (
            gpd.read_parquet(ACTION_PATH),
            pd.read_parquet(PERFORMANCE_PATH),
            gpd.read_parquet(CONTEXT_PATH),
        )
    return construct_interventions()
