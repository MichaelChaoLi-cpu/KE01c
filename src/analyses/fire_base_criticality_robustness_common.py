"""Multi-state robustness for leave-one-fire-base-out criticality."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.special import ndtr

from fire_base_criticality_common import (
    OBJECTIVES,
    leave_one_out_values,
    load_fire_base_criticality,
)
from fire_service_reliability_common import DISPATCH_PATH, build_compact_fire_network
from robustness_analysis_common import (
    BASE_SEED,
    CLUSTER_CORRELATION,
    CLUSTER_SIZE_M,
    HAZARD_WEIGHT,
    MODELS,
    PROJECTED_CRS,
    calibrate_intensity,
)


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
ROBUSTNESS = RESULTS / "derived/robustness"

PROBABILITY_PATH = PROCESSED / "road_section_failure_probabilities_preprocessed.parquet"
SECTION_PATH = PROCESSED / "road_section_intervention_preprocessed.parquet"
CONSEQUENCE_PATH = RESULTS / "derived/fire_consequence_125m.parquet"
ROAD_REPLICATE_PATH = ROBUSTNESS / "road_mechanism_replicate_metrics.parquet"
STATE_OUTPUT = ROBUSTNESS / "fire_base_leave_one_out_state_values.parquet"
METRIC_OUTPUT = ROBUSTNESS / "fire_base_leave_one_out_state_stability.parquet"
SUMMARY_OUTPUT = ROBUSTNESS / "fire_base_leave_one_out_stability_summary.parquet"

MAIN_SEVERITY = 0.03
RESPONSE_CAP_MIN = 30.0
STATE_QUANTILES = np.arange(0.05, 1.0, 0.10)
TOP_BASE_COUNT = 10


def cache_is_current() -> bool:
    outputs = (STATE_OUTPUT, METRIC_OUTPUT, SUMMARY_OUTPUT)
    sources = (
        PROBABILITY_PATH,
        SECTION_PATH,
        CONSEQUENCE_PATH,
        ROAD_REPLICATE_PATH,
        RESULTS / "derived/fire_base_leave_one_out_criticality.parquet",
        Path(__file__),
        Path(__file__).with_name("fire_base_criticality_common.py"),
        Path(__file__).with_name("robustness_analysis_common.py"),
        Path(__file__).with_name("fire_service_reliability_common.py"),
    )
    return all(path.exists() for path in outputs) and min(
        path.stat().st_mtime for path in outputs
    ) >= max(path.stat().st_mtime for path in sources)


def select_stratified_states(metrics: pd.DataFrame, model: str) -> pd.DataFrame:
    """Select ten unique states spanning the timely-response distribution."""
    subset = metrics.loc[
        metrics["Road Failure Model"].eq(model)
        & metrics["Expected Failed Road Length Share"].eq(MAIN_SEVERITY)
    ].copy()
    if len(subset) < len(STATE_QUANTILES):
        raise ValueError(f"Too few road states for {model}")
    value_column = "Population-Weighted Timely Response Probability"
    selected_rows: list[pd.Series] = []
    used: set[int] = set()
    for quantile in STATE_QUANTILES:
        target = float(subset[value_column].quantile(quantile))
        candidates = subset.loc[~subset["Simulation Replicate"].isin(used)].copy()
        candidates["_distance"] = (candidates[value_column] - target).abs()
        chosen = candidates.sort_values(
            ["_distance", "Simulation Replicate"], kind="stable"
        ).iloc[0]
        used.add(int(chosen["Simulation Replicate"]))
        chosen = chosen.copy()
        chosen["State Distribution Quantile"] = float(quantile)
        selected_rows.append(chosen)
    selected = pd.DataFrame(selected_rows).drop(columns="_distance")
    if selected["Simulation Replicate"].duplicated().any():
        raise RuntimeError("Stratified state selection is not unique")
    return selected.sort_values("State Distribution Quantile").reset_index(drop=True)


def rank_metrics(reference: np.ndarray, alternative: np.ndarray) -> tuple[float, float]:
    reference_rank = pd.Series(reference).rank(method="average")
    alternative_rank = pd.Series(alternative).rank(method="average")
    correlation = float(reference_rank.corr(alternative_rank))
    reference_top = set(np.argsort(reference)[-TOP_BASE_COUNT:])
    alternative_top = set(np.argsort(alternative)[-TOP_BASE_COUNT:])
    overlap = len(reference_top & alternative_top) / TOP_BASE_COUNT
    return correlation, overlap


def construct_criticality_robustness() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Estimate leave-one-out criticality in ten states per failure model."""
    network = build_compact_fire_network(include_event_removed=True)
    section_ids = network.road_section_ids.astype(str)
    lengths = network.road_section_lengths.astype(np.float64)

    probability = pd.read_parquet(PROBABILITY_PATH)
    probability["Road Section ID"] = probability["Road Section ID"].astype(str)
    independent_probability = (
        probability.loc[
            probability["Expected Failed Road Length Share"].eq(MAIN_SEVERITY)
        ]
        .set_index("Road Section ID")["Section Failure Probability"]
        .reindex(section_ids)
        .to_numpy(np.float64)
    )
    if np.isnan(independent_probability).any():
        raise ValueError("Independent failure probabilities do not align with sections")

    sections = gpd.read_parquet(SECTION_PATH).to_crs(PROJECTED_CRS)
    sections["Road Section ID"] = sections["Road Section ID"].astype(str)
    sections = sections.set_index("Road Section ID").reindex(section_ids)
    if sections["Geometry"].isna().any():
        raise ValueError("Road-section geometry does not align with the sparse network")
    hazard_multiplier = np.where(
        sections["Event-Exposed Road Length (m)"].to_numpy(float) > 0,
        HAZARD_WEIGHT,
        1.0,
    )
    hazard_intensity = calibrate_intensity(MAIN_SEVERITY, lengths, hazard_multiplier)
    hazard_probability = -np.expm1(
        -hazard_intensity * lengths * hazard_multiplier
    )
    centroids = sections.geometry.centroid
    cell_x = np.floor(centroids.x.to_numpy() / CLUSTER_SIZE_M).astype(np.int32)
    cell_y = np.floor(centroids.y.to_numpy() / CLUSTER_SIZE_M).astype(np.int32)
    _, cluster_index = np.unique(
        np.column_stack((cell_x, cell_y)), axis=0, return_inverse=True
    )
    cluster_count = int(cluster_index.max()) + 1

    consequence = pd.read_parquet(CONSEQUENCE_PATH)
    consequence["Mesh Code"] = consequence["Mesh Code"].astype(str)
    consequence = consequence.set_index("Mesh Code").reindex(
        network.mesh_codes.astype(str)
    )
    if consequence["Conditional Spread Susceptibility"].isna().any():
        raise ValueError("Consequence cells do not align with the sparse network")
    weights = np.vstack(
        [
            (
                consequence["Conditional Spread Susceptibility"]
                * consequence[column]
            ).to_numpy(np.float64)
            for column in OBJECTIVES.values()
        ]
    )

    reference = load_fire_base_criticality()
    reference = reference.loc[reference["Road Scenario"].eq("central")].copy()
    reference_lookup = {
        objective: subset.set_index("Fire Base Name")[
            "Leave-One-Out Fire Base Value Share"
        ]
        for objective, subset in reference.groupby("Exposure Objective", sort=False)
    }
    # The sparse OD rows retain eligible dispatch bases in the original
    # connector-table order.  Keep that order here; alphabetical sorting would
    # attach a leave-one-out result to the wrong base.
    dispatch = pd.read_parquet(DISPATCH_PATH)
    eligible_dispatch = (
        dispatch["Network Snap Accepted"].fillna(False)
        & dispatch["Candidate Dispatch Base"].fillna(False)
        & dispatch["Dispatch Base Node ID"].notna()
    )
    base_identity = (
        dispatch.loc[
            eligible_dispatch,
            ["Fire Facility Name", "Fire Facility Type", "Municipality Code"],
        ]
        .rename(
            columns={
                "Fire Facility Name": "Fire Base Name",
                "Fire Facility Type": "Fire Base Type",
            }
        )
        .reset_index(drop=True)
    )
    if len(base_identity) != len(network.dispatch_source_indices):
        raise ValueError("Fire-base identity count does not match sparse-network sources")

    road_metrics = pd.read_parquet(ROAD_REPLICATE_PATH)
    state_records: list[dict[str, object]] = []
    metric_records: list[dict[str, object]] = []
    for model_index, model in enumerate(MODELS):
        selected = select_stratified_states(road_metrics, model)
        for state_number, state in selected.iterrows():
            replicate = int(state["Simulation Replicate"])
            rng = np.random.default_rng(BASE_SEED + model_index * 100_000 + replicate)
            independent_uniform = rng.random(len(section_ids))
            if model == "Spatially clustered":
                section_normal = rng.standard_normal(len(section_ids))
                cluster_normal = rng.standard_normal(cluster_count)
                latent = (
                    np.sqrt(CLUSTER_CORRELATION) * cluster_normal[cluster_index]
                    + np.sqrt(1 - CLUSTER_CORRELATION) * section_normal
                )
                mechanism_uniform = ndtr(latent)
                failure_probability = independent_probability
            elif model == "Hazard-weighted":
                mechanism_uniform = independent_uniform
                failure_probability = hazard_probability
            else:
                mechanism_uniform = independent_uniform
                failure_probability = independent_probability
            failed = mechanism_uniform < failure_probability
            od, routing_seconds = network.station_od(
                failed=failed,
                response_cap_min=RESPONSE_CAP_MIN,
            )
            values = leave_one_out_values(od, weights)
            totals = values.sum(axis=1)
            for objective_index, objective in enumerate(OBJECTIVES):
                if totals[objective_index] <= 0:
                    raise RuntimeError(
                        f"Unidentified leave-one-out loss for {model}, {replicate}, {objective}"
                    )
                shares = values[objective_index] / totals[objective_index]
                reference_shares = (
                    reference_lookup[objective]
                    .reindex(base_identity["Fire Base Name"])
                    .to_numpy(float)
                )
                correlation, overlap = rank_metrics(reference_shares, shares)
                metric_records.append(
                    {
                        "Road Failure Model": model,
                        "Expected Failed Road Length Share": MAIN_SEVERITY,
                        "Simulation Replicate": replicate,
                        "State Distribution Quantile": float(
                            state["State Distribution Quantile"]
                        ),
                        "Exposure Objective": objective,
                        "Population-Weighted Timely Response Probability": float(
                            state["Population-Weighted Timely Response Probability"]
                        ),
                        "Fire Base Rank Correlation": correlation,
                        "Top Ten Fire Base Overlap": overlap,
                        "Routing Seconds": routing_seconds,
                    }
                )
                ranks = pd.Series(shares).rank(method="min", ascending=False).to_numpy(int)
                for base_index, base in base_identity.iterrows():
                    state_records.append(
                        {
                            "Road Failure Model": model,
                            "Expected Failed Road Length Share": MAIN_SEVERITY,
                            "Simulation Replicate": replicate,
                            "State Distribution Quantile": float(
                                state["State Distribution Quantile"]
                            ),
                            "Exposure Objective": objective,
                            "Fire Base Name": base["Fire Base Name"],
                            "Fire Base Type": base["Fire Base Type"],
                            "Municipality Code": base["Municipality Code"],
                            "Leave-One-Out Fire Base Value": values[
                                objective_index, base_index
                            ],
                            "Leave-One-Out Fire Base Value Share": shares[base_index],
                            "State Criticality Rank": int(ranks[base_index]),
                            "High-Criticality Membership": bool(
                                ranks[base_index] <= TOP_BASE_COUNT
                            ),
                        }
                    )
            print(
                f"fire-base robustness: {model}, state {state_number + 1}/{len(selected)}",
                flush=True,
            )

    state_values = pd.DataFrame(state_records)
    state_metrics = pd.DataFrame(metric_records)
    summary = (
        state_values.groupby(
            ["Road Failure Model", "Exposure Objective", "Fire Base Name"],
            as_index=False,
        )
        .agg(
            **{
                "State Count": ("Simulation Replicate", "nunique"),
                "Median Leave-One-Out Share": (
                    "Leave-One-Out Fire Base Value Share",
                    "median",
                ),
                "Q25 Leave-One-Out Share": (
                    "Leave-One-Out Fire Base Value Share",
                    lambda values: values.quantile(0.25),
                ),
                "Q75 Leave-One-Out Share": (
                    "Leave-One-Out Fire Base Value Share",
                    lambda values: values.quantile(0.75),
                ),
                "High-Criticality Membership Frequency": (
                    "High-Criticality Membership",
                    "mean",
                ),
            }
        )
    )
    summary["Road-Scenario Leave-One-Out IQR"] = (
        summary["Q75 Leave-One-Out Share"] - summary["Q25 Leave-One-Out Share"]
    )

    ROBUSTNESS.mkdir(parents=True, exist_ok=True)
    state_values.to_parquet(STATE_OUTPUT, index=False)
    state_metrics.to_parquet(METRIC_OUTPUT, index=False)
    summary.to_parquet(SUMMARY_OUTPUT, index=False)
    print(f"Saved: {STATE_OUTPUT.relative_to(ROOT)}", flush=True)
    print(f"Saved: {METRIC_OUTPUT.relative_to(ROOT)}", flush=True)
    print(f"Saved: {SUMMARY_OUTPUT.relative_to(ROOT)}", flush=True)
    return state_values, state_metrics, summary


def load_criticality_robustness() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if cache_is_current():
        print("Using current multi-state fire-base robustness caches", flush=True)
        return (
            pd.read_parquet(STATE_OUTPUT),
            pd.read_parquet(METRIC_OUTPUT),
            pd.read_parquet(SUMMARY_OUTPUT),
        )
    return construct_criticality_robustness()
