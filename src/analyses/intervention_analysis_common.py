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
    EDGE_PATH,
    UNMET_SERVICE_CAP_MIN,
    accepted_connectors,
    build_augmented_graph,
    build_station_od,
    scenario_availability,
)


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"

CONSEQUENCE_PATH = RESULTS / "derived/fire_consequence_125m.parquet"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
ACTION_PATH = RESULTS / "derived/intervention_actions.parquet"
PERFORMANCE_PATH = RESULTS / "derived/intervention_performance.parquet"
CONTEXT_PATH = RESULTS / "derived/intervention_context_125m.parquet"

PROJECTED_CRS = 6670
MAX_BUDGET = 5
PREPOSITION_CANDIDATES = 35
PREPOSITION_SPACING_M = 2_000.0
WATER_CANDIDATES = 25
WATER_SPACING_M = 1_200.0
WATER_SUPPORT_RADIUS_M = 1_000.0
ROAD_SCREEN_CANDIDATES = 10
MINAMI_WARD_CODE = "43104"


def cache_is_current() -> bool:
    """Use intervention caches only when source layers and this code are older."""
    sources = [
        CONSEQUENCE_PATH,
        ADMIN_PATH,
        EDGE_PATH,
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


def road_bridge_candidates(
    graph: nx.Graph,
    removed_edges: gpd.GeoDataFrame,
    demand_nodes: list[str],
    station_sources: list[str],
    objective_weight: np.ndarray,
) -> gpd.GeoDataFrame:
    """Screen removed edges that reconnect distinct central-network components."""
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
    candidates: list[dict[str, object]] = []
    candidate_columns = [
        "Road Edge ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Emergency Route Membership",
        "Road Category",
        "Geometry",
    ]
    for (
        edge_id,
        from_node_value,
        to_node_value,
        edge_minutes,
        membership_value,
        road_category,
        geometry,
    ) in removed_edges[candidate_columns].itertuples(index=False, name=None):
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
        candidates.append(
            {
                "Road Edge ID": str(edge_id),
                "Component Pair": tuple(sorted((from_component, to_component))),
                "Bridge Screening Score": potential,
                "Emergency Priority": membership_priority.get(membership, 1),
                "Baseline Edge Travel Time (min)": float(edge_minutes),
                "Road Category": road_category,
                "Emergency Route Membership": membership,
                "Geometry": geometry,
            }
        )
    if not candidates:
        raise ValueError("No disrupted component-bridging road candidates were found")
    candidate_frame = gpd.GeoDataFrame(candidates, geometry="Geometry", crs=removed_edges.crs)
    candidate_frame = candidate_frame.sort_values(
        [
            "Component Pair",
            "Emergency Priority",
            "Baseline Edge Travel Time (min)",
        ],
        ascending=[True, False, True],
        kind="stable",
    ).drop_duplicates("Component Pair")
    candidate_frame["Screen Rank Score"] = (
        candidate_frame["Bridge Screening Score"]
        * (1 + 0.15 * (candidate_frame["Emergency Priority"] - 1))
    )
    return candidate_frame.nlargest(ROAD_SCREEN_CANDIDATES, "Screen Rank Score").copy()


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
    all_edges = gpd.read_parquet(EDGE_PATH, columns=edge_columns).to_crs(PROJECTED_CRS)
    all_edges["Road Edge ID"] = all_edges["Road Edge ID"].astype("string")
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

    bridge_candidates = road_bridge_candidates(
        central_graph,
        removed_edges,
        demand_nodes,
        station_sources,
        objective_weight,
    )
    edge_lookup = all_edges.set_index("Road Edge ID", drop=False)
    road_penalty_cache: dict[frozenset[str], np.ndarray] = {}

    def road_bundle_benefit(edge_ids: list[str]) -> float:
        key = frozenset(edge_ids)
        if key not in road_penalty_cache:
            restored = edge_lookup.loc[list(key)]
            scenario_edges = gpd.GeoDataFrame(
                pd.concat([central_edges, restored], ignore_index=True),
                geometry="Geometry",
                crs=central_edges.crs,
            ).drop_duplicates("Road Edge ID")
            graph = build_augmented_graph(scenario_edges, connectors)
            response_time, qualifying = network_metrics(
                graph,
                station_sources,
                demand_lookup,
                len(context),
            )
            road_penalty_cache[key] = accessibility_penalty(response_time, qualifying)
        return float(objective_weight @ (baseline_penalty - road_penalty_cache[key]))

    bridge_ids = bridge_candidates["Road Edge ID"].astype("string").tolist()
    road_selected: list[str] = []
    road_benefits: list[float] = []
    for budget in range(1, MAX_BUDGET + 1):
        best_edge = None
        best_benefit = -np.inf
        for edge_id in bridge_ids:
            if edge_id in road_selected:
                continue
            benefit = road_bundle_benefit(road_selected + [edge_id])
            if benefit > best_benefit:
                best_benefit = benefit
                best_edge = edge_id
        if best_edge is None:
            break
        road_selected.append(best_edge)
        road_benefits.append(best_benefit)
        print(f"road-restoration greedy budget: {budget}/{MAX_BUDGET}", flush=True)

    category_priority = {
        "National Expressway or Equivalent": 4,
        "National Highway": 3,
        "Prefectural Road": 2,
        "Municipal Road or Equivalent": 1,
        "Other": 0,
    }
    baseline_order = bridge_candidates.assign(
        Category_Priority=bridge_candidates["Road Category"].map(category_priority).fillna(0)
    ).sort_values(
        ["Category_Priority", "Emergency Priority", "Bridge Screening Score"],
        ascending=False,
        kind="stable",
    )["Road Edge ID"].astype("string").tolist()
    road_baseline_selected: list[str] = []
    road_baseline_benefits: list[float] = []
    for edge_id in baseline_order[:MAX_BUDGET]:
        road_baseline_selected.append(edge_id)
        road_baseline_benefits.append(road_bundle_benefit(road_baseline_selected))

    performance_records: list[dict[str, object]] = []
    performance_specs = (
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
            road_benefits,
        ),
        (
            "Priority road restoration",
            "Simple baseline",
            road_baseline_selected,
            road_baseline_benefits,
        ),
    )
    for action_type, strategy, selected, benefits in performance_specs:
        for budget, benefit in enumerate(benefits, start=1):
            performance_records.append(
                {
                    "Action Type": action_type,
                    "Strategy": strategy,
                    "Budget": budget,
                    "Selected Action IDs": " | ".join(map(str, selected[:budget])),
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
                "Action Description": "Temporary water support within a 1 km screening radius",
                "Geometry": cell_points.iloc[index],
            }
        )
    for rank, edge_id in enumerate(road_selected, start=1):
        row = edge_lookup.loc[edge_id]
        action_records.append(
            {
                "Action ID": f"ROAD::{edge_id}",
                "Action Type": "Priority road restoration",
                "Selection Rank": rank,
                "Action Description": "Restore one disrupted component-bridging road edge",
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
