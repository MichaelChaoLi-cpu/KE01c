"""Shared fire-service network accessibility calculations for KE01c figures."""

from __future__ import annotations

import heapq
import json
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
NETWORK_DIR = ROOT / "data/results/derived/network"
EDGE_PATH = NETWORK_DIR / "routable_road_edges.parquet"
DISPATCH_PATH = NETWORK_DIR / "fire_dispatch_base_access.parquet"
DEMAND_PATH = NETWORK_DIR / "population_mesh_access.parquet"
ACCESS_PATH = NETWORK_DIR / "fire_service_access_125m.parquet"
ACCESS_METADATA_PATH = NETWORK_DIR / "fire_service_access_125m.metadata.json"

UNMET_SERVICE_CAP_MIN = 30.0
BACKUP_THRESHOLD_MIN = 10.0
CACHE_VERSION = 2


def file_signature(path: Path) -> dict[str, int | str]:
    """Return a compact freshness signature for one cache dependency."""
    stat = path.stat()
    return {
        "path": str(path.relative_to(ROOT)),
        "size": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
    }


def ordered_identifier_vector(frame: pd.DataFrame, columns: list[str]) -> np.ndarray:
    """Encode ordered row identifiers without relying on dataframe dimensions."""
    identifiers = frame.loc[:, columns].astype("string").fillna("<NA>")
    return identifiers.agg("\x1f".join, axis=1).to_numpy(dtype=str)


def od_cache_metadata(
    scenario: str,
    demand: pd.DataFrame,
    dispatch: pd.DataFrame,
) -> dict[str, object]:
    """Describe the inputs and declared parameters that determine one OD cache."""
    return {
        "cache_version": CACHE_VERSION,
        "kind": "fire_station_od",
        "scenario": scenario.casefold(),
        "parameters": {
            "unmet_service_cap_min": UNMET_SERVICE_CAP_MIN,
            "backup_threshold_min": BACKUP_THRESHOLD_MIN,
        },
        "row_counts": {"demand": len(demand), "dispatch": len(dispatch)},
        "sources": [
            file_signature(path)
            for path in [EDGE_PATH, DEMAND_PATH, DISPATCH_PATH, Path(__file__).resolve()]
        ],
    }


def access_cache_metadata() -> dict[str, object]:
    """Describe the current combined fire-access layer dependencies."""
    return {
        "cache_version": CACHE_VERSION,
        "kind": "fire_service_access_125m",
        "parameters": {
            "normal_scenario": "normal",
            "disrupted_scenario": "central",
            "unmet_service_cap_min": UNMET_SERVICE_CAP_MIN,
            "backup_threshold_min": BACKUP_THRESHOLD_MIN,
        },
        "sources": [
            file_signature(path)
            for path in [
                EDGE_PATH,
                DEMAND_PATH,
                DISPATCH_PATH,
                NETWORK_DIR / "fire_station_od_normal.npz",
                NETWORK_DIR / "fire_station_od_central.npz",
                Path(__file__).resolve(),
            ]
        ],
    }


def json_metadata_matches(path: Path, expected: dict[str, object]) -> bool:
    """Return whether a JSON sidecar exactly matches the expected metadata."""
    if not path.exists():
        return False
    try:
        return json.loads(path.read_text(encoding="utf-8")) == expected
    except (OSError, json.JSONDecodeError):
        return False


def write_json_metadata(path: Path, metadata: dict[str, object]) -> None:
    """Write deterministic cache metadata after its associated output succeeds."""
    path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def scenario_availability(edges: pd.DataFrame, scenario: str) -> pd.Series:
    """Return a transparent baseline or bounded central-disruption mask."""
    available = edges["Road Available"].fillna(False) & edges[
        "Network Analysis Eligible"
    ].fillna(False)
    key = scenario.casefold()
    if key == "normal":
        return available
    if key == "central":
        hazard = edges["Hazard Exposure Class"].astype("string")
        return available & ~hazard.isin(["Warning Zone", "Special Warning Zone"])
    raise ValueError(f"Unknown fire-service scenario: {scenario}")


def accepted_connectors(
    frame: pd.DataFrame,
    identifier: str,
    eligibility: str | None,
    connector_type: str,
) -> pd.DataFrame:
    """Return accepted demand or dispatch connectors with a common schema."""
    selected = frame.loc[frame["Network Snap Accepted"].fillna(False)].copy()
    if eligibility is not None:
        selected = selected.loc[selected[eligibility].fillna(False)].copy()
    selected = selected.loc[selected[identifier].notna()].copy()
    return selected.rename(columns={identifier: "Connector ID"}).assign(
        **{"Connector Type": connector_type}
    )[
        [
            "Connector ID",
            "Connector Type",
            "Access Road Edge ID",
            "Access Edge Fraction",
            "Network Snap Distance (m)",
        ]
    ]


def add_minimum_edge(graph: nx.Graph, start: str, end: str, minutes: float) -> None:
    """Add an undirected edge while retaining the fastest parallel connection."""
    if graph.has_edge(start, end):
        if minutes < float(graph[start][end]["minutes"]):
            graph[start][end]["minutes"] = minutes
    else:
        graph.add_edge(start, end, minutes=minutes)


def build_augmented_graph(edges: pd.DataFrame, connectors: pd.DataFrame) -> nx.Graph:
    """Split retained road edges at accepted access positions and attach connectors."""
    edge_lookup = edges.set_index("Road Edge ID")
    connectors = connectors.loc[
        connectors["Access Road Edge ID"].isin(edge_lookup.index)
    ].copy()
    connectors = connectors.join(
        edge_lookup[["Assumed Speed (km/h)"]],
        on="Access Road Edge ID",
        validate="many_to_one",
    )
    connectors["Access Edge Fraction"] = connectors["Access Edge Fraction"].astype(float).clip(0, 1)
    connectors["Connector Time (min)"] = (
        60.0
        * connectors["Network Snap Distance (m)"].astype(float)
        / (1_000.0 * connectors["Assumed Speed (km/h)"].astype(float))
    )
    access_by_edge = {
        str(edge_id): group.sort_values(
            ["Access Edge Fraction", "Connector ID"], kind="stable"
        )
        for edge_id, group in connectors.groupby("Access Road Edge ID", sort=False)
    }

    graph = nx.Graph()
    edge_values = edges[
        [
            "Road Edge ID",
            "From Node ID",
            "To Node ID",
            "Baseline Edge Travel Time (min)",
        ]
    ].itertuples(index=False, name=None)
    for edge_id, from_node, to_node, edge_minutes in edge_values:
        edge_id = str(edge_id)
        from_node = str(from_node)
        to_node = str(to_node)
        edge_minutes = float(edge_minutes)
        access = access_by_edge.get(edge_id)
        if access is None:
            add_minimum_edge(graph, from_node, to_node, edge_minutes)
            continue

        positions = access["Access Edge Fraction"].drop_duplicates().sort_values().tolist()
        chain_nodes = [from_node]
        chain_fractions = [0.0]
        for number, fraction in enumerate(positions, start=1):
            chain_nodes.append(f"SNAP::{edge_id}::{number:05d}")
            chain_fractions.append(float(fraction))
        chain_nodes.append(to_node)
        chain_fractions.append(1.0)
        for start, end, start_fraction, end_fraction in zip(
            chain_nodes[:-1],
            chain_nodes[1:],
            chain_fractions[:-1],
            chain_fractions[1:],
            strict=True,
        ):
            add_minimum_edge(
                graph,
                start,
                end,
                edge_minutes * (end_fraction - start_fraction),
            )

        snap_for_fraction = dict(zip(positions, chain_nodes[1:-1], strict=True))
        for connector_id, _, _, fraction, _, _, connector_minutes in access[
            [
                "Connector ID",
                "Connector Type",
                "Access Road Edge ID",
                "Access Edge Fraction",
                "Network Snap Distance (m)",
                "Assumed Speed (km/h)",
                "Connector Time (min)",
            ]
        ].itertuples(index=False, name=None):
            add_minimum_edge(
                graph,
                str(connector_id),
                snap_for_fraction[float(fraction)],
                float(connector_minutes),
            )
    return graph


def labelled_multi_source_distances(
    graph: nx.Graph,
    sources: list[str],
) -> tuple[dict[str, float], dict[str, str]]:
    """Return nearest-base times and deterministic nearest-base labels."""
    distances: dict[str, float] = {}
    labels: dict[str, str] = {}
    queue: list[tuple[float, str, str]] = []
    for source in sorted(set(sources)):
        distances[source] = 0.0
        labels[source] = source
        heapq.heappush(queue, (0.0, source, source))
    tolerance = 1e-12
    while queue:
        distance, source, node = heapq.heappop(queue)
        known_distance = distances.get(node, np.inf)
        known_source = labels.get(node)
        if distance > known_distance + tolerance:
            continue
        if abs(distance - known_distance) <= tolerance and known_source != source:
            continue
        for neighbour, attributes in graph[node].items():
            candidate = distance + float(attributes["minutes"])
            known = distances.get(neighbour, np.inf)
            previous_source = labels.get(neighbour)
            if candidate < known - tolerance or (
                abs(candidate - known) <= tolerance
                and (previous_source is None or source < previous_source)
            ):
                distances[neighbour] = candidate
                labels[neighbour] = source
                heapq.heappush(queue, (candidate, source, neighbour))
    return distances, labels


def build_station_od(scenario: str) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    """Build or load a capped station-by-cell travel-time matrix for one scenario."""
    output_path = NETWORK_DIR / f"fire_station_od_{scenario.casefold()}.npz"
    demand = pd.read_parquet(DEMAND_PATH)
    dispatch = pd.read_parquet(DISPATCH_PATH)
    expected_metadata = od_cache_metadata(scenario, demand, dispatch)
    expected_demand_ids = ordered_identifier_vector(
        demand,
        ["Mesh Code", "Demand Node ID"],
    )
    expected_dispatch_ids = ordered_identifier_vector(
        dispatch,
        ["Dispatch Base Node ID", "Candidate Dispatch Base"],
    )
    if output_path.exists():
        try:
            with np.load(output_path, allow_pickle=False) as payload:
                required = {
                    "travel_time",
                    "metadata_json",
                    "demand_identifiers",
                    "dispatch_identifiers",
                }
                if required.issubset(payload.files):
                    matrix = payload["travel_time"].copy()
                    metadata = json.loads(str(payload["metadata_json"].item()))
                    demand_ids = payload["demand_identifiers"]
                    dispatch_ids = payload["dispatch_identifiers"]
                    current = (
                        matrix.shape == (len(dispatch), len(demand))
                        and metadata == expected_metadata
                        and np.array_equal(demand_ids, expected_demand_ids)
                        and np.array_equal(dispatch_ids, expected_dispatch_ids)
                    )
                    if current:
                        print(
                            f"Using current OD cache: {output_path.relative_to(ROOT)}",
                            flush=True,
                        )
                        return matrix, demand, dispatch
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            pass
        print(f"Rebuilding stale OD cache: {output_path.relative_to(ROOT)}", flush=True)

    edge_columns = [
        "Road Edge ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Assumed Speed (km/h)",
        "Road Available",
        "Network Analysis Eligible",
        "Hazard Exposure Class",
    ]
    all_edges = pd.read_parquet(EDGE_PATH, columns=edge_columns)
    edges = all_edges.loc[scenario_availability(all_edges, scenario)].copy()
    demand_connectors = accepted_connectors(demand, "Demand Node ID", None, "demand")
    dispatch_connectors = accepted_connectors(
        dispatch,
        "Dispatch Base Node ID",
        "Candidate Dispatch Base",
        "dispatch",
    )
    connectors = pd.concat([demand_connectors, dispatch_connectors], ignore_index=True)
    print(
        f"Building {scenario} graph from {len(edges):,} retained road edges...",
        flush=True,
    )
    graph = build_augmented_graph(edges, connectors)

    demand_node = demand["Demand Node ID"].astype("string")
    demand_lookup = {
        str(identifier): position
        for position, identifier in enumerate(demand_node)
        if pd.notna(identifier)
    }
    sources = dispatch["Dispatch Base Node ID"].astype("string").tolist()
    matrix = np.full(
        (len(sources), len(demand)),
        UNMET_SERVICE_CAP_MIN,
        dtype=np.float32,
    )
    for station_index, source in enumerate(sources):
        if pd.notna(source) and str(source) in graph:
            distances = nx.single_source_dijkstra_path_length(
                graph,
                str(source),
                cutoff=UNMET_SERVICE_CAP_MIN,
                weight="minutes",
            )
            for node, minutes in distances.items():
                demand_index = demand_lookup.get(str(node))
                if demand_index is not None:
                    matrix[station_index, demand_index] = min(
                        float(minutes), UNMET_SERVICE_CAP_MIN
                    )
        print(
            f"{scenario} station OD: {station_index + 1}/{len(sources)}",
            flush=True,
        )

    np.savez_compressed(
        output_path,
        travel_time=matrix,
        metadata_json=np.asarray(
            json.dumps(expected_metadata, sort_keys=True),
            dtype=str,
        ),
        demand_identifiers=expected_demand_ids,
        dispatch_identifiers=expected_dispatch_ids,
    )
    print(f"Saved: {output_path.relative_to(ROOT)}", flush=True)
    return matrix, demand, dispatch


def fire_service_access_layer() -> pd.DataFrame:
    """Return normal/disrupted response time, backup count, and access penalty."""
    normal, demand, _ = build_station_od("normal")
    central, _, _ = build_station_od("central")
    expected_metadata = access_cache_metadata()
    if ACCESS_PATH.exists() and json_metadata_matches(
        ACCESS_METADATA_PATH,
        expected_metadata,
    ):
        cached = pd.read_parquet(ACCESS_PATH)
        cached_ids = cached["Mesh Code"].astype("string").to_numpy(dtype=str)
        expected_ids = demand["Mesh Code"].astype("string").to_numpy(dtype=str)
        required_columns = {
            "Mesh Code",
            "Normal Response Time (min)",
            "Disrupted Response Time (min)",
            "Backup Fire Base Count",
            "Accessibility Penalty",
            "Network Snap Accepted",
        }
        if required_columns.issubset(cached.columns) and np.array_equal(
            cached_ids,
            expected_ids,
        ):
            print(
                f"Using current fire-access layer: {ACCESS_PATH.relative_to(ROOT)}",
                flush=True,
            )
            return cached
        print(
            f"Rebuilding fire-access layer with changed mesh order: {ACCESS_PATH.relative_to(ROOT)}",
            flush=True,
        )
    elif ACCESS_PATH.exists():
        print(f"Rebuilding stale fire-access layer: {ACCESS_PATH.relative_to(ROOT)}", flush=True)

    normal_time = normal.min(axis=0)
    disrupted_time = central.min(axis=0)
    qualifying = (central <= BACKUP_THRESHOLD_MIN).sum(axis=0)
    backup_count = np.maximum(qualifying - 1, 0).astype(np.int16)
    access_penalty = 0.5 * np.minimum(
        disrupted_time / UNMET_SERVICE_CAP_MIN,
        1,
    ) + 0.5 / (1 + backup_count)
    result = pd.DataFrame(
        {
            "Mesh Code": demand["Mesh Code"].astype("string"),
            "Normal Response Time (min)": normal_time,
            "Disrupted Response Time (min)": disrupted_time,
            "Backup Fire Base Count": backup_count,
            "Accessibility Penalty": access_penalty,
            "Network Snap Accepted": demand["Network Snap Accepted"].fillna(False),
        }
    )
    result.to_parquet(ACCESS_PATH, index=False)
    write_json_metadata(ACCESS_METADATA_PATH, expected_metadata)
    print(f"Saved: {ACCESS_PATH.relative_to(ROOT)}", flush=True)
    return result


def add_single_route_dependence() -> pd.DataFrame:
    """Add central-scenario shortest-route concentration to the access layer.

    Connector edges at the station and demand endpoints are excluded because
    they are modelling devices rather than mapped road segments. Cells without
    a base route within the declared threshold remain missing (unserved).
    """
    result = fire_service_access_layer()
    if "Single Route Dependence" in result.columns:
        print(f"Using current route-dependence layer: {ACCESS_PATH.relative_to(ROOT)}", flush=True)
        return result

    central, demand, dispatch = build_station_od("central")
    qualifying_count = (central <= BACKUP_THRESHOLD_MIN).sum(axis=0)

    edge_columns = [
        "Road Edge ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Assumed Speed (km/h)",
        "Road Available",
        "Network Analysis Eligible",
        "Hazard Exposure Class",
    ]
    all_edges = pd.read_parquet(EDGE_PATH, columns=edge_columns)
    edges = all_edges.loc[scenario_availability(all_edges, "central")].copy()
    demand_connectors = accepted_connectors(demand, "Demand Node ID", None, "demand")
    dispatch_connectors = accepted_connectors(
        dispatch,
        "Dispatch Base Node ID",
        "Candidate Dispatch Base",
        "dispatch",
    )
    connectors = pd.concat([demand_connectors, dispatch_connectors], ignore_index=True)
    print("Building central graph for route dependence...", flush=True)
    graph = build_augmented_graph(edges, connectors)

    demand_nodes = demand["Demand Node ID"].astype("string").tolist()
    multi_route_indices = set(np.flatnonzero(qualifying_count > 1).tolist())
    edge_counts: dict[int, Counter[tuple[str, str]]] = {
        index: Counter() for index in multi_route_indices
    }
    for station_index, source_value in enumerate(
        dispatch["Dispatch Base Node ID"].astype("string")
    ):
        source = str(source_value)
        if pd.isna(source_value) or source not in graph:
            continue
        _, paths = nx.single_source_dijkstra(
            graph,
            source,
            cutoff=BACKUP_THRESHOLD_MIN + 1e-9,
            weight="minutes",
        )
        station_targets = np.flatnonzero(
            (central[station_index] <= BACKUP_THRESHOLD_MIN)
            & (qualifying_count > 1)
        )
        for demand_index in station_targets:
            target = str(demand_nodes[demand_index])
            path = paths.get(target)
            if path is None:
                continue
            road_edges: set[tuple[str, str]] = set()
            for start, end in zip(path[:-1], path[1:], strict=True):
                start = str(start)
                end = str(end)
                if source in (start, end) or target in (start, end):
                    continue
                road_edges.add(tuple(sorted((start, end))))
            edge_counts[int(demand_index)].update(road_edges)
        print(
            f"central route dependence: {station_index + 1}/{len(dispatch)}",
            flush=True,
        )

    dependence = np.full(len(demand), np.nan, dtype=np.float32)
    dependence[qualifying_count == 1] = 1.0
    for demand_index, counts in edge_counts.items():
        if counts:
            dependence[demand_index] = max(counts.values()) / qualifying_count[demand_index]

    route_frame = pd.DataFrame(
        {
            "Mesh Code": demand["Mesh Code"].astype("string"),
            "Single Route Dependence": dependence,
        }
    )
    result = result.drop(columns=["Single Route Dependence"], errors="ignore").merge(
        route_frame,
        on="Mesh Code",
        how="left",
        validate="one_to_one",
    )
    result.to_parquet(ACCESS_PATH, index=False)
    print(f"Updated: {ACCESS_PATH.relative_to(ROOT)}", flush=True)
    return result
