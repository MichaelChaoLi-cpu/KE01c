"""Road-section Monte Carlo reliability for fire-service accessibility.

The event-specific disrupted network is the baseline. Additional failures use
the finalized length-dependent section probabilities and full sparse-graph
rerouting. Outputs are sensitivity results, not observed 2026 road failures.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
NETWORK = ROOT / "data" / "results" / "derived" / "network"
OUTPUT_DIR = ROOT / "data" / "results" / "derived" / "road_reliability"

EDGE_PATH = PROCESSED / "routable_road_edges_sectioned_preprocessed.parquet"
PROBABILITY_PATH = PROCESSED / "road_section_failure_probabilities_preprocessed.parquet"
DEMAND_PATH = NETWORK / "population_mesh_access.parquet"
DISPATCH_PATH = NETWORK / "fire_dispatch_base_access.parquet"
ACCESS_PATH = NETWORK / "fire_service_access_125m.parquet"

GRID_OUTPUT = OUTPUT_DIR / "fire_service_reliability_125m.parquet"
REPLICATE_OUTPUT = OUTPUT_DIR / "road_failure_replicate_metrics.parquet"
CONVERGENCE_OUTPUT = OUTPUT_DIR / "road_reliability_convergence.parquet"
REALIZATION_OUTPUT = OUTPUT_DIR / "road_failure_realization_replicate_001.parquet"
METADATA_OUTPUT = OUTPUT_DIR / "road_reliability_metadata.json"

FAILURE_MODEL = "Length-Dependent Independent"
MAIN_SEVERITY = 0.03
REPLICATES = 1_000
BASE_SEED = 20260806
THRESHOLDS = np.array([5.0, 10.0, 15.0], dtype=np.float64)
CHECKPOINTS = (100, 250, 500, 750, 1_000)
EVENT_HAZARD_CLASSES = {"Warning Zone", "Special Warning Zone"}


@dataclass
class CompactFireNetwork:
    """Fixed sparse topology with road-section labels on candidate arcs."""

    road_section_ids: np.ndarray
    road_section_lengths: np.ndarray
    section_failure_probability: np.ndarray
    mesh_codes: np.ndarray
    total_population: np.ndarray
    demand_node_index: np.ndarray
    dispatch_source_indices: np.ndarray
    graph: csr_matrix
    arc_base_weight: np.ndarray
    arc_road_section: np.ndarray
    arc_event_available: np.ndarray
    arc_group_starts: np.ndarray
    build_seconds: float

    def _set_state(
        self,
        failed: np.ndarray | None = None,
        restored: np.ndarray | None = None,
    ) -> None:
        """Update sparse arc weights for one failed/restored road-section state."""
        section_count = len(self.road_section_ids)
        if failed is None:
            failed = np.zeros(section_count, dtype=bool)
        if restored is None:
            restored = np.zeros(section_count, dtype=bool)
        failed = np.asarray(failed, dtype=bool)
        restored = np.asarray(restored, dtype=bool)
        if failed.shape != (section_count,) or restored.shape != (section_count,):
            raise ValueError("Road-section state mask has an unexpected shape")

        available = self.arc_event_available.copy()
        road_arc = self.arc_road_section >= 0
        section = self.arc_road_section[road_arc]
        available[road_arc] &= ~failed[section]
        available[road_arc] |= restored[section]
        candidate_weight = np.where(available, self.arc_base_weight, np.inf)
        self.graph.data[:] = np.minimum.reduceat(
            candidate_weight,
            self.arc_group_starts,
        )

    def route(
        self,
        failed: np.ndarray | None = None,
        restored: np.ndarray | None = None,
    ) -> tuple[np.ndarray, float]:
        """Return nearest-fire-base time for every populated mesh."""
        started = perf_counter()
        self._set_state(failed=failed, restored=restored)
        distance = dijkstra(
            self.graph,
            directed=True,
            indices=self.dispatch_source_indices,
            return_predecessors=False,
            min_only=True,
        )
        valid = self.demand_node_index >= 0
        response = np.full(len(self.demand_node_index), np.inf, dtype=np.float64)
        response[valid] = distance[self.demand_node_index[valid]]
        return response, perf_counter() - started

    def route_metrics(
        self,
        *,
        failed: np.ndarray | None = None,
        restored: np.ndarray | None = None,
        backup_threshold_min: float = 10.0,
        response_cap_min: float = 20.0,
        source_batch_size: int = 16,
    ) -> tuple[np.ndarray, np.ndarray, float]:
        """Return nearest time and backup-base count with bounded memory."""
        started = perf_counter()
        self._set_state(failed=failed, restored=restored)
        valid = self.demand_node_index >= 0
        response = np.full(len(self.demand_node_index), response_cap_min, dtype=np.float64)
        nearest = dijkstra(
            self.graph,
            directed=True,
            indices=self.dispatch_source_indices,
            return_predecessors=False,
            min_only=True,
            limit=response_cap_min,
        )
        response[valid] = np.minimum(
            nearest[self.demand_node_index[valid]],
            response_cap_min,
        )
        qualifying = np.zeros(len(self.demand_node_index), dtype=np.int16)
        for start in range(0, len(self.dispatch_source_indices), source_batch_size):
            source_batch = self.dispatch_source_indices[
                start : start + source_batch_size
            ]
            distance = dijkstra(
                self.graph,
                directed=True,
                indices=source_batch,
                return_predecessors=False,
                limit=backup_threshold_min,
            )
            if distance.ndim == 1:
                distance = distance[None, :]
            qualifying[valid] += (
                distance[:, self.demand_node_index[valid]] <= backup_threshold_min
            ).sum(axis=0).astype(np.int16)
        return response, qualifying, perf_counter() - started

    def station_od(
        self,
        *,
        failed: np.ndarray | None = None,
        restored: np.ndarray | None = None,
        response_cap_min: float = 20.0,
    ) -> tuple[np.ndarray, float]:
        """Return station-by-demand travel times for one road-section state."""
        started = perf_counter()
        self._set_state(failed=failed, restored=restored)
        distance = dijkstra(
            self.graph,
            directed=True,
            indices=self.dispatch_source_indices,
            return_predecessors=False,
            limit=response_cap_min,
        )
        valid = self.demand_node_index >= 0
        od = np.full(
            (len(self.dispatch_source_indices), len(self.demand_node_index)),
            response_cap_min,
            dtype=np.float32,
        )
        od[:, valid] = np.minimum(
            distance[:, self.demand_node_index[valid]],
            response_cap_min,
        ).astype(np.float32)
        return od, perf_counter() - started


def _accepted_connectors(
    frame: pd.DataFrame,
    identifier: str,
    eligibility: str | None,
    connector_type: str,
) -> pd.DataFrame:
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


def _append_undirected(
    arc_from: list[int],
    arc_to: list[int],
    arc_weight: list[float],
    arc_failure: list[int],
    arc_event_available: list[bool],
    start: int,
    end: int,
    weight: float,
    road_section: int,
    event_available: bool,
) -> None:
    if weight < 0 or not np.isfinite(weight):
        raise ValueError(f"Invalid graph weight: {weight}")
    arc_from.extend((start, end))
    arc_to.extend((end, start))
    arc_weight.extend((weight, weight))
    arc_failure.extend((road_section, road_section))
    arc_event_available.extend((event_available, event_available))


def build_compact_fire_network(
    *,
    include_event_removed: bool = False,
) -> CompactFireNetwork:
    """Build a sparse road graph for reliability or restoration rerouting."""
    started = perf_counter()
    probability = pd.read_parquet(PROBABILITY_PATH)
    probability = probability.loc[
        probability["Road Failure Model"].eq(FAILURE_MODEL)
        & probability["Expected Failed Road Length Share"].eq(MAIN_SEVERITY)
    ].copy()
    probability["Road Section ID"] = probability["Road Section ID"].astype(str)
    if not probability["Road Section ID"].is_unique:
        raise ValueError("Road-section probability rows must be unique at one severity")
    probability = probability.sort_values("Road Section ID", kind="stable").reset_index(drop=True)
    road_section_ids = probability["Road Section ID"].to_numpy(str)
    road_section_lengths = probability["Road Section Length (m)"].to_numpy(np.float64)
    section_failure_probability = probability["Section Failure Probability"].to_numpy(
        np.float64
    )
    section_index = pd.Series(
        np.arange(len(probability), dtype=np.int32),
        index=road_section_ids,
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
    ]
    edges = pd.read_parquet(EDGE_PATH, columns=edge_columns)
    eligible = edges["Road Available"].fillna(False) & edges[
        "Network Analysis Eligible"
    ].fillna(False)
    event_available = eligible & ~edges["Hazard Exposure Class"].astype("string").isin(
        EVENT_HAZARD_CLASSES
    )
    edges = edges.loc[eligible if include_event_removed else event_available].copy()
    edges["Event Available"] = event_available.loc[edges.index].to_numpy(bool)
    edges = edges.reset_index(drop=True)
    if not edges["Road Edge ID"].is_unique:
        raise ValueError("Road Edge ID must be unique")
    edges["Road Edge ID"] = edges["Road Edge ID"].astype(str)
    edges["Road Section ID"] = edges["Road Section ID"].astype(str)
    edge_section_index = edges["Road Section ID"].map(section_index)
    if edge_section_index.isna().any():
        raise ValueError("Every retained edge must map to a probability row")
    edge_section_index = edge_section_index.to_numpy(np.int32)
    edge_index_by_id = pd.Series(
        np.arange(len(edges), dtype=np.int32),
        index=edges["Road Edge ID"],
    )
    speed_by_edge = pd.Series(
        edges["Assumed Speed (km/h)"].to_numpy(np.float64),
        index=edges["Road Edge ID"],
    )

    demand = pd.read_parquet(DEMAND_PATH)
    dispatch = pd.read_parquet(DISPATCH_PATH)
    connectors = pd.concat(
        [
            _accepted_connectors(demand, "Demand Node ID", None, "demand"),
            _accepted_connectors(
                dispatch,
                "Dispatch Base Node ID",
                "Candidate Dispatch Base",
                "dispatch",
            ),
        ],
        ignore_index=True,
    )
    connectors["Connector ID"] = connectors["Connector ID"].astype(str)
    connectors["Access Road Edge ID"] = connectors["Access Road Edge ID"].astype(str)
    connectors = connectors.loc[
        connectors["Access Road Edge ID"].isin(edge_index_by_id.index)
    ].copy()
    if not connectors["Connector ID"].is_unique:
        raise ValueError("Accepted connector identifiers must be globally unique")
    connectors["Edge Index"] = connectors["Access Road Edge ID"].map(
        edge_index_by_id
    ).astype(np.int32)
    connectors["Road Section Index"] = edge_section_index[
        connectors["Edge Index"].to_numpy(np.int32)
    ]
    connectors["Assumed Speed (km/h)"] = connectors["Access Road Edge ID"].map(
        speed_by_edge
    )
    connectors["Access Edge Fraction"] = connectors["Access Edge Fraction"].astype(
        float
    ).clip(0.0, 1.0)
    connectors["Connector Time (min)"] = (
        60.0
        * connectors["Network Snap Distance (m)"].astype(float)
        / (1_000.0 * connectors["Assumed Speed (km/h)"].astype(float))
    )

    road_node_ids = pd.Index(
        pd.concat([edges["From Node ID"], edges["To Node ID"]], ignore_index=True)
        .astype(str)
        .unique()
    )
    road_node_index = pd.Series(
        np.arange(len(road_node_ids), dtype=np.int32),
        index=road_node_ids,
    )
    from_index = edges["From Node ID"].astype(str).map(road_node_index).to_numpy(np.int32)
    to_index = edges["To Node ID"].astype(str).map(road_node_index).to_numpy(np.int32)
    edge_minutes = edges["Baseline Edge Travel Time (min)"].to_numpy(np.float64)
    edge_event_available = edges["Event Available"].to_numpy(bool)

    connector_start = len(road_node_ids)
    connectors["Connector Node Index"] = np.arange(
        connector_start,
        connector_start + len(connectors),
        dtype=np.int32,
    )
    connector_node_by_id = pd.Series(
        connectors["Connector Node Index"].to_numpy(np.int32),
        index=connectors["Connector ID"],
    )

    arc_from: list[int] = []
    arc_to: list[int] = []
    arc_weight: list[float] = []
    arc_failure: list[int] = []
    arc_event_available: list[bool] = []
    next_node = connector_start + len(connectors)
    connectors_by_edge = {
        int(position): group.sort_values(
            ["Access Edge Fraction", "Connector ID"], kind="stable"
        )
        for position, group in connectors.groupby("Edge Index", sort=False)
    }
    no_connector = np.ones(len(edges), dtype=bool)
    if connectors_by_edge:
        no_connector[np.fromiter(connectors_by_edge, dtype=np.int32)] = False
    for edge_position in np.flatnonzero(no_connector):
        _append_undirected(
            arc_from,
            arc_to,
            arc_weight,
            arc_failure,
            arc_event_available,
            int(from_index[edge_position]),
            int(to_index[edge_position]),
            float(edge_minutes[edge_position]),
            int(edge_section_index[edge_position]),
            bool(edge_event_available[edge_position]),
        )

    for edge_position, group in connectors_by_edge.items():
        section = int(edge_section_index[edge_position])
        fractions = np.sort(group["Access Edge Fraction"].unique().astype(float))
        position_node = {
            0.0: int(from_index[edge_position]),
            1.0: int(to_index[edge_position]),
        }
        for fraction in fractions:
            if 0.0 < fraction < 1.0:
                position_node[float(fraction)] = next_node
                next_node += 1
        chain = np.concatenate(
            ([0.0], fractions[(fractions > 0) & (fractions < 1)], [1.0])
        )
        for start_fraction, end_fraction in zip(chain[:-1], chain[1:], strict=True):
            _append_undirected(
                arc_from,
                arc_to,
                arc_weight,
                arc_failure,
                arc_event_available,
                position_node[float(start_fraction)],
                position_node[float(end_fraction)],
                float(edge_minutes[edge_position] * (end_fraction - start_fraction)),
                section,
                bool(edge_event_available[edge_position]),
            )
        for connector_node, fraction, connector_minutes in group[
            ["Connector Node Index", "Access Edge Fraction", "Connector Time (min)"]
        ].itertuples(index=False, name=None):
            _append_undirected(
                arc_from,
                arc_to,
                arc_weight,
                arc_failure,
                arc_event_available,
                int(connector_node),
                position_node[float(fraction)],
                float(connector_minutes),
                section,
                bool(edge_event_available[edge_position]),
            )

    arc_from_array = np.asarray(arc_from, dtype=np.int32)
    arc_to_array = np.asarray(arc_to, dtype=np.int32)
    arc_weight_array = np.asarray(arc_weight, dtype=np.float64)
    arc_failure_array = np.asarray(arc_failure, dtype=np.int32)
    arc_event_available_array = np.asarray(arc_event_available, dtype=bool)
    node_count = next_node
    pair_key = arc_from_array.astype(np.int64) * np.int64(node_count) + arc_to_array
    order = np.argsort(pair_key, kind="stable")
    pair_key = pair_key[order]
    arc_from_array = arc_from_array[order]
    arc_to_array = arc_to_array[order]
    arc_weight_array = arc_weight_array[order]
    arc_failure_array = arc_failure_array[order]
    arc_event_available_array = arc_event_available_array[order]
    group_starts = np.flatnonzero(np.r_[True, pair_key[1:] != pair_key[:-1]]).astype(
        np.int64
    )
    unique_from = arc_from_array[group_starts]
    unique_to = arc_to_array[group_starts]
    base_pair_weight = np.minimum.reduceat(arc_weight_array, group_starts)
    row_counts = np.bincount(unique_from, minlength=node_count)
    indptr = np.empty(node_count + 1, dtype=np.int64)
    indptr[0] = 0
    np.cumsum(row_counts, out=indptr[1:])
    graph = csr_matrix(
        (base_pair_weight.copy(), unique_to, indptr),
        shape=(node_count, node_count),
    )

    demand_ids = demand["Demand Node ID"].astype("string")
    demand_node_index = np.full(len(demand), -1, dtype=np.int32)
    demand_valid = demand_ids.notna() & demand["Network Snap Accepted"].fillna(False)
    mapped_demand = demand.loc[demand_valid, "Demand Node ID"].astype(str).map(
        connector_node_by_id
    )
    retained_demand = mapped_demand.notna()
    demand_positions = np.flatnonzero(demand_valid.to_numpy())[retained_demand.to_numpy()]
    demand_node_index[demand_positions] = mapped_demand.loc[retained_demand].to_numpy(
        np.int32
    )
    dispatch_sources = connectors.loc[
        connectors["Connector Type"].eq("dispatch"), "Connector Node Index"
    ].to_numpy(np.int32)
    if not len(dispatch_sources):
        raise ValueError("No candidate dispatch base remains connected")

    return CompactFireNetwork(
        road_section_ids=road_section_ids,
        road_section_lengths=road_section_lengths,
        section_failure_probability=section_failure_probability,
        mesh_codes=demand["Mesh Code"].astype("string").to_numpy(),
        total_population=demand["Total Population"].fillna(0).to_numpy(np.float64),
        demand_node_index=demand_node_index,
        dispatch_source_indices=dispatch_sources,
        graph=graph,
        arc_base_weight=arc_weight_array,
        arc_road_section=arc_failure_array,
        arc_event_available=arc_event_available_array,
        arc_group_starts=group_starts,
        build_seconds=perf_counter() - started,
    )


def cache_is_current() -> bool:
    outputs = (
        GRID_OUTPUT,
        REPLICATE_OUTPUT,
        CONVERGENCE_OUTPUT,
        REALIZATION_OUTPUT,
        METADATA_OUTPUT,
    )
    if not all(path.exists() for path in outputs):
        return False
    sources = (
        EDGE_PATH,
        PROBABILITY_PATH,
        DEMAND_PATH,
        DISPATCH_PATH,
        ACCESS_PATH,
        Path(__file__),
    )
    return min(path.stat().st_mtime for path in outputs) >= max(
        path.stat().st_mtime for path in sources
    )


def _top_decile_overlap(left: np.ndarray, right: np.ndarray) -> float:
    cutoff_left = np.nanquantile(left, 0.90)
    cutoff_right = np.nanquantile(right, 0.90)
    left_top = left >= cutoff_left
    right_top = right >= cutoff_right
    union = left_top | right_top
    return float((left_top & right_top).sum() / union.sum()) if union.any() else np.nan


def run_main_reliability() -> pd.DataFrame:
    """Run or load the formal 3% length-dependent accessibility experiment."""
    if cache_is_current():
        print(f"Using current road-reliability layer: {GRID_OUTPUT.relative_to(ROOT)}")
        return pd.read_parquet(GRID_OUTPUT)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    overall_started = perf_counter()
    network = build_compact_fire_network()
    baseline, baseline_seconds = network.route()
    access = pd.read_parquet(ACCESS_PATH)
    access["Mesh Code"] = access["Mesh Code"].astype("string")
    baseline_frame = pd.DataFrame(
        {"Mesh Code": network.mesh_codes, "Sparse Baseline Response Time": baseline}
    ).merge(
        access[["Mesh Code", "Disrupted Response Time (min)"]],
        on="Mesh Code",
        how="left",
        validate="one_to_one",
    )
    comparable = np.isfinite(baseline_frame["Sparse Baseline Response Time"]) & (
        baseline_frame["Disrupted Response Time (min)"] < 30.0
    )
    maximum_baseline_difference = float(
        np.max(
            np.abs(
                baseline_frame.loc[comparable, "Sparse Baseline Response Time"]
                - baseline_frame.loc[comparable, "Disrupted Response Time (min)"]
            )
        )
    )
    if maximum_baseline_difference > 1e-4:
        raise RuntimeError(
            "Sparse event-baseline routing does not match the accepted accessibility layer"
        )

    time_path = OUTPUT_DIR / ".response_times_working.float32"
    all_times = np.memmap(
        time_path,
        mode="w+",
        shape=(REPLICATES, len(network.mesh_codes)),
        dtype=np.float32,
    )
    timely_counts = np.zeros((len(THRESHOLDS), len(network.mesh_codes)), dtype=np.uint16)
    replicate_records: list[dict[str, float | int | str]] = []
    checkpoint_probabilities: dict[int, np.ndarray] = {}
    first_failed: np.ndarray | None = None
    simulation_started = perf_counter()
    total_length = float(network.road_section_lengths.sum())

    for offset in range(REPLICATES):
        replicate = offset + 1
        rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, replicate]))
        failed = rng.random(len(network.road_section_ids)) < network.section_failure_probability
        if first_failed is None:
            first_failed = failed.copy()
        response, routing_seconds = network.route(failed)
        all_times[offset] = response.astype(np.float32)
        for threshold_index, threshold in enumerate(THRESHOLDS):
            timely_counts[threshold_index] += response <= threshold
        replicate_records.append(
            {
                "Road Failure Model": FAILURE_MODEL,
                "Expected Failed Road Length Share": MAIN_SEVERITY,
                "Simulation Replicate": replicate,
                "Realized Failed Road Length Share": float(
                    network.road_section_lengths[failed].sum() / total_length
                ),
                "Failed Road Section Count": int(failed.sum()),
                "Routing Seconds": float(routing_seconds),
            }
        )
        if replicate in CHECKPOINTS:
            checkpoint_probabilities[replicate] = (
                timely_counts[1].astype(np.float32) / replicate
            )
            print(f"Recorded convergence checkpoint {replicate}", flush=True)
        if replicate == 1 or replicate % 50 == 0 or replicate == REPLICATES:
            elapsed = perf_counter() - simulation_started
            print(
                f"Completed {replicate}/{REPLICATES} road states in {elapsed:.1f}s",
                flush=True,
            )

    all_times.flush()
    finite = np.isfinite(all_times)
    finite_count = finite.sum(axis=0)
    disconnection_probability = 1.0 - finite_count / REPLICATES
    p90 = np.full(len(network.mesh_codes), np.nan, dtype=np.float32)
    p90_supported = disconnection_probability < 0.10
    if p90_supported.any():
        p90[p90_supported] = np.quantile(
            np.asarray(all_times[:, p90_supported]),
            0.90,
            axis=0,
        ).astype(np.float32)

    grid = pd.DataFrame(
        {
            "Mesh Code": pd.Series(network.mesh_codes, dtype="string"),
            "Road Failure Model": FAILURE_MODEL,
            "Expected Failed Road Length Share": MAIN_SEVERITY,
            "Simulation Replicates": REPLICATES,
            "Timely Response Probability 5 min": timely_counts[0] / REPLICATES,
            "Timely Response Probability": timely_counts[1] / REPLICATES,
            "Timely Response Probability 15 min": timely_counts[2] / REPLICATES,
            "P90 Response Time (min)": p90,
            "Disconnection Probability": disconnection_probability,
        }
    )
    grid.to_parquet(GRID_OUTPUT, index=False)
    replicate_frame = pd.DataFrame(replicate_records)
    replicate_frame.to_parquet(REPLICATE_OUTPUT, index=False)

    convergence_records: list[dict[str, float | int | str]] = []
    previous: np.ndarray | None = None
    previous_checkpoint: int | None = None
    population = network.total_population
    population_total = float(population.sum())
    for checkpoint in CHECKPOINTS:
        values = checkpoint_probabilities[checkpoint]
        record: dict[str, float | int | str] = {
            "Road Failure Model": FAILURE_MODEL,
            "Expected Failed Road Length Share": MAIN_SEVERITY,
            "Simulation Replicates": checkpoint,
            "Population-Weighted Timely Response Probability": float(
                np.dot(population, values) / population_total
            ),
            "Mean Grid Timely Response Probability": float(values.mean()),
            "Previous Checkpoint": previous_checkpoint or 0,
            "Mean Absolute Grid Probability Change": np.nan,
            "Maximum Absolute Grid Probability Change": np.nan,
            "Top-Decile Priority Jaccard": np.nan,
        }
        if previous is not None:
            change = np.abs(values - previous)
            record["Mean Absolute Grid Probability Change"] = float(change.mean())
            record["Maximum Absolute Grid Probability Change"] = float(change.max())
            record["Top-Decile Priority Jaccard"] = _top_decile_overlap(
                1.0 - previous,
                1.0 - values,
            )
        convergence_records.append(record)
        previous = values
        previous_checkpoint = checkpoint
    pd.DataFrame(convergence_records).to_parquet(CONVERGENCE_OUTPUT, index=False)

    if first_failed is None:
        raise RuntimeError("No failure realization was generated")
    pd.DataFrame(
        {
            "Road Section ID": network.road_section_ids,
            "Road Failure Model": FAILURE_MODEL,
            "Expected Failed Road Length Share": MAIN_SEVERITY,
            "Simulation Replicate": 1,
            "Section Failure Probability": network.section_failure_probability,
            "Road Section Failure Indicator": first_failed,
        }
    ).to_parquet(REALIZATION_OUTPUT, index=False)

    metadata = {
        "status": "pass",
        "interpretation": "Additional length-dependent road-section sensitivity imposed on the event-specific disrupted network; not observed 2026 failure probability.",
        "failure_model": FAILURE_MODEL,
        "expected_failed_road_length_share": MAIN_SEVERITY,
        "replicates": REPLICATES,
        "base_seed": BASE_SEED,
        "thresholds_minutes": THRESHOLDS.tolist(),
        "network": {
            "road_sections": int(len(network.road_section_ids)),
            "sparse_nodes": int(network.graph.shape[0]),
            "directed_pairs": int(network.graph.nnz),
            "connected_dispatch_bases": int(len(network.dispatch_source_indices)),
            "population_meshes": int(len(network.mesh_codes)),
            "event_baseline_routing_seconds": baseline_seconds,
            "maximum_baseline_time_difference_minutes": maximum_baseline_difference,
        },
        "runtime": {
            "network_build_seconds": network.build_seconds,
            "simulation_seconds": perf_counter() - simulation_started,
            "total_seconds": perf_counter() - overall_started,
            "mean_state_routing_seconds": float(
                replicate_frame["Routing Seconds"].mean()
            ),
        },
        "outputs": {
            "grid_reliability": GRID_OUTPUT.name,
            "replicate_metrics": REPLICATE_OUTPUT.name,
            "convergence": CONVERGENCE_OUTPUT.name,
            "replicate_001_realization": REALIZATION_OUTPUT.name,
        },
    }
    METADATA_OUTPUT.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    del all_times
    time_path.unlink(missing_ok=True)
    print(f"Saved: {GRID_OUTPUT.relative_to(ROOT)}", flush=True)
    return grid
