"""Scenario and parameter robustness for road reliability and priorities."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.special import ndtr

from fire_base_criticality_common import OBJECTIVES, leave_one_out_values
from fire_service_access_common import UNMET_SERVICE_CAP_MIN, build_station_od
from fire_service_reliability_common import build_compact_fire_network


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
OUTPUT_DIR = RESULTS / "derived/robustness"
REPLICATE_PATH = OUTPUT_DIR / "road_mechanism_replicate_metrics.parquet"
ROAD_SUMMARY_PATH = OUTPUT_DIR / "road_mechanism_summary.parquet"
STATION_PATH = OUTPUT_DIR / "fire_base_priority_stability.parquet"
INTERVENTION_PATH = OUTPUT_DIR / "road_intervention_priority_stability.parquet"

PROBABILITY_PATH = PROCESSED / "road_section_failure_probabilities_preprocessed.parquet"
SECTION_PATH = PROCESSED / "road_section_intervention_preprocessed.parquet"
CONSEQUENCE_PATH = RESULTS / "derived/fire_consequence_125m.parquet"
INTERVENTION_PERFORMANCE_PATH = RESULTS / "derived/intervention_performance.parquet"
ACCESS_COMMON_PATH = Path(__file__).with_name("fire_service_access_common.py")
RELIABILITY_COMMON_PATH = Path(__file__).with_name("fire_service_reliability_common.py")
FIRE_BASE_COMMON_PATH = Path(__file__).with_name("fire_base_criticality_common.py")

MODELS = (
    "Length-dependent independent",
    "Spatially clustered",
    "Hazard-weighted",
)
SEVERITIES = (0.01, 0.03, 0.05, 0.10)
PILOT_REPLICATES = 100
BASE_SEED = 20260806
CLUSTER_SIZE_M = 5_000.0
CLUSTER_CORRELATION = 0.70
HAZARD_WEIGHT = 2.5
PROJECTED_CRS = 6670
TIMELY_THRESHOLD_MIN = 10.0
RESPONSE_CAP_MIN = UNMET_SERVICE_CAP_MIN


def cache_is_current() -> bool:
    outputs = (REPLICATE_PATH, ROAD_SUMMARY_PATH, STATION_PATH, INTERVENTION_PATH)
    sources = (
        PROBABILITY_PATH,
        SECTION_PATH,
        CONSEQUENCE_PATH,
        INTERVENTION_PERFORMANCE_PATH,
        ACCESS_COMMON_PATH,
        RELIABILITY_COMMON_PATH,
        FIRE_BASE_COMMON_PATH,
        Path(__file__),
    )
    return all(path.exists() for path in outputs) and min(
        path.stat().st_mtime for path in outputs
    ) >= max(path.stat().st_mtime for path in sources)


def calibrate_intensity(
    target: float,
    lengths: np.ndarray,
    multiplier: np.ndarray,
) -> float:
    """Calibrate a hazard multiplier to one expected failed-length share."""
    total_length = float(lengths.sum())

    def share(intensity: float) -> float:
        probability = -np.expm1(-intensity * lengths * multiplier)
        return float(lengths @ probability / total_length)

    low = 0.0
    high = 1.0 / float(np.median(lengths))
    while share(high) < target:
        high *= 2.0
    for _ in range(70):
        midpoint = 0.5 * (low + high)
        if share(midpoint) < target:
            low = midpoint
        else:
            high = midpoint
    return 0.5 * (low + high)


def rank_metrics(reference: np.ndarray, alternative: np.ndarray, top_n: int) -> tuple[float, float]:
    """Return Spearman correlation and fixed-size top-set overlap."""
    reference_rank = pd.Series(reference).rank(method="average")
    alternative_rank = pd.Series(alternative).rank(method="average")
    correlation = float(reference_rank.corr(alternative_rank))
    reference_top = set(np.argsort(reference)[-top_n:])
    alternative_top = set(np.argsort(alternative)[-top_n:])
    overlap = len(reference_top & alternative_top) / top_n
    return correlation, overlap


def construct_robustness() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run paired road mechanisms and fixed-plan intervention robustness checks."""
    network = build_compact_fire_network(include_event_removed=True)
    section_ids = network.road_section_ids.astype(str)
    lengths = network.road_section_lengths.astype(np.float64)
    total_length = float(lengths.sum())

    probability = pd.read_parquet(PROBABILITY_PATH)
    probability["Road Section ID"] = probability["Road Section ID"].astype(str)
    probability = probability.set_index(
        ["Road Section ID", "Expected Failed Road Length Share"]
    )
    independent_probability = {
        severity: probability.loc[
            pd.IndexSlice[:, severity], "Section Failure Probability"
        ].droplevel(1).reindex(section_ids).to_numpy(np.float64)
        for severity in SEVERITIES
    }

    sections = gpd.read_parquet(SECTION_PATH).to_crs(PROJECTED_CRS)
    sections["Road Section ID"] = sections["Road Section ID"].astype(str)
    sections = sections.set_index("Road Section ID").reindex(section_ids)
    if sections["Geometry"].isna().any():
        raise ValueError("Road-section geometry does not align with sparse network")
    hazard_multiplier = np.where(
        sections["Event-Exposed Road Length (m)"].to_numpy(float) > 0,
        HAZARD_WEIGHT,
        1.0,
    )
    hazard_probability = {
        severity: -np.expm1(
            -calibrate_intensity(severity, lengths, hazard_multiplier)
            * lengths
            * hazard_multiplier
        )
        for severity in SEVERITIES
    }
    centroids = sections.geometry.centroid
    cell_x = np.floor(centroids.x.to_numpy() / CLUSTER_SIZE_M).astype(np.int32)
    cell_y = np.floor(centroids.y.to_numpy() / CLUSTER_SIZE_M).astype(np.int32)
    _, cluster_index = np.unique(
        np.column_stack((cell_x, cell_y)),
        axis=0,
        return_inverse=True,
    )
    cluster_count = int(cluster_index.max()) + 1

    records: list[dict[str, object]] = []
    states_at_main: dict[str, list[np.ndarray]] = {model: [] for model in MODELS}
    timely_at_main: dict[str, list[float]] = {model: [] for model in MODELS}
    for model_index, model in enumerate(MODELS):
        for replicate in range(1, PILOT_REPLICATES + 1):
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
            else:
                mechanism_uniform = independent_uniform

            for severity in SEVERITIES:
                if model == "Hazard-weighted":
                    failure_probability = hazard_probability[severity]
                else:
                    failure_probability = independent_probability[severity]
                failed = mechanism_uniform < failure_probability
                response, routing_seconds = network.route(failed=failed)
                timely = response <= TIMELY_THRESHOLD_MIN
                population = network.total_population
                population_probability = float(population @ timely / population.sum())
                finite = np.isfinite(response)
                p90 = float(np.quantile(response[finite], 0.90)) if finite.any() else np.nan
                records.append(
                    {
                        "Road Failure Model": model,
                        "Expected Failed Road Length Share": severity,
                        "Simulation Replicate": replicate,
                        "Realized Failed Road Length Share": float(
                            lengths[failed].sum() / total_length
                        ),
                        "Population-Weighted Timely Response Probability": population_probability,
                        "P90 Response Time (min)": p90,
                        "Disconnected Demand Share": float((~finite).mean()),
                        "Routing Seconds": routing_seconds,
                    }
                )
                if severity == 0.03:
                    states_at_main[model].append(failed.copy())
                    timely_at_main[model].append(population_probability)
        print(f"robustness road mechanism complete: {model}", flush=True)

    replicate_frame = pd.DataFrame(records)
    summary = replicate_frame.groupby(
        ["Road Failure Model", "Expected Failed Road Length Share"],
        as_index=False,
    ).agg(
        **{
            "Mean Timely Response Probability": (
                "Population-Weighted Timely Response Probability",
                "mean",
            ),
            "P10 Timely Response Probability": (
                "Population-Weighted Timely Response Probability",
                lambda values: values.quantile(0.10),
            ),
            "P90 Timely Response Probability": (
                "Population-Weighted Timely Response Probability",
                lambda values: values.quantile(0.90),
            ),
            "Mean P90 Response Time (min)": ("P90 Response Time (min)", "mean"),
            "Mean Disconnected Demand Share": ("Disconnected Demand Share", "mean"),
            "Mean Realized Failed Road Length Share": (
                "Realized Failed Road Length Share",
                "mean",
            ),
        }
    )

    representative_state: dict[str, np.ndarray] = {}
    for model in MODELS:
        values = np.asarray(timely_at_main[model])
        representative_index = int(np.argmin(np.abs(values - np.median(values))))
        representative_state[model] = states_at_main[model][representative_index]

    consequence = pd.read_parquet(CONSEQUENCE_PATH)
    consequence["Mesh Code"] = consequence["Mesh Code"].astype(str)
    consequence = consequence.set_index("Mesh Code").reindex(network.mesh_codes.astype(str))
    weights = np.vstack(
        [
            (
                consequence["Conditional Spread Susceptibility"]
                * consequence[column]
            ).to_numpy(np.float32)
            for column in OBJECTIVES.values()
        ]
    )
    central_od, _, _ = build_station_od("central")
    reference_value = leave_one_out_values(central_od, weights)
    station_rows: list[dict[str, object]] = []
    for model in MODELS:
        od, routing_seconds = network.station_od(
            failed=representative_state[model],
            response_cap_min=RESPONSE_CAP_MIN,
        )
        alternative_value = leave_one_out_values(od, weights)
        for objective_index, objective in enumerate(OBJECTIVES):
            correlation, overlap = rank_metrics(
                reference_value[objective_index],
                alternative_value[objective_index],
                top_n=10,
            )
            station_rows.append(
                {
                    "Road Failure Model": model,
                    "Expected Failed Road Length Share": 0.03,
                    "Exposure Objective": objective,
                    "Station Rank Correlation": correlation,
                    "Top Ten Fire Base Overlap": overlap,
                    "Representative State Routing Seconds": routing_seconds,
                }
            )
    station_stability = pd.DataFrame(station_rows)

    intervention = pd.read_parquet(INTERVENTION_PERFORMANCE_PATH)
    road = intervention.loc[
        intervention["Action Type"].eq("Priority road restoration")
    ]
    bundle_rows = road.loc[
        road["Strategy"].eq("Greedy consequence reduction")
        & road["Budget"].eq(3)
    ].set_index("Budget Definition")
    bundle_by_rule = {
        "Section count": [
            value
            for value in str(
                bundle_rows.loc["Road section count", "Selected Action IDs"]
            ).split(" | ")
            if value
        ],
        "Length-aware": [
            value
            for value in str(
                bundle_rows.loc[
                    "Normalized event-exposed length",
                    "Selected Action IDs",
                ]
            ).split(" | ")
            if value
        ],
    }
    section_position = pd.Series(
        np.arange(len(section_ids), dtype=np.int32),
        index=section_ids,
    )
    objective_weight = weights[0].astype(np.float64)

    def accessibility_penalty(response: np.ndarray, qualifying: np.ndarray) -> np.ndarray:
        return 0.5 * np.minimum(response / RESPONSE_CAP_MIN, 1) + 0.5 / np.maximum(
            qualifying,
            1,
        )

    def bundle_benefit(
        failed: np.ndarray,
        selected: list[str],
        baseline_time: np.ndarray,
        baseline_count: np.ndarray,
    ) -> tuple[float, float]:
        restored = np.zeros(len(section_ids), dtype=bool)
        restored[section_position.loc[selected].to_numpy(np.int32)] = True
        response_time, qualifying, routing_seconds = network.route_metrics(
            failed=failed,
            restored=restored,
            backup_threshold_min=TIMELY_THRESHOLD_MIN,
            response_cap_min=RESPONSE_CAP_MIN,
        )
        benefit = float(
            objective_weight
            @ (
                accessibility_penalty(baseline_time, baseline_count)
                - accessibility_penalty(response_time, qualifying)
            )
        )
        return benefit, routing_seconds

    no_failures = np.zeros(len(section_ids), dtype=bool)
    reference_time, reference_count, _ = network.route_metrics(
        failed=no_failures,
        backup_threshold_min=TIMELY_THRESHOLD_MIN,
        response_cap_min=RESPONSE_CAP_MIN,
    )
    reference_bundle_benefit: dict[str, float] = {}
    for rule, selected in bundle_by_rule.items():
        reference_bundle_benefit[rule], _ = bundle_benefit(
            no_failures,
            selected,
            reference_time,
            reference_count,
        )
        if reference_bundle_benefit[rule] <= 0:
            raise ValueError(f"Reference intervention benefit is nonpositive for {rule}")

    intervention_rows: list[dict[str, object]] = []
    for model in MODELS:
        for replicate, failed in enumerate(states_at_main[model], start=1):
            baseline_time, baseline_count, baseline_seconds = network.route_metrics(
                failed=failed,
                backup_threshold_min=TIMELY_THRESHOLD_MIN,
                response_cap_min=RESPONSE_CAP_MIN,
            )
            for rule, selected in bundle_by_rule.items():
                state_benefit, restoration_seconds = bundle_benefit(
                    failed,
                    selected,
                    baseline_time,
                    baseline_count,
                )
                intervention_rows.append(
                    {
                        "Road Failure Model": model,
                        "Expected Failed Road Length Share": 0.03,
                        "Simulation Replicate": replicate,
                        "Road Priority Rule": rule,
                        "Evaluation Mode": "Fixed event-road bundle",
                        "Selected Road Section IDs": " | ".join(selected),
                        "Selected Road Section Count": len(selected),
                        "Event-Specific Bundle Benefit": reference_bundle_benefit[rule],
                        "Road-State Bundle Benefit": state_benefit,
                        "Retained Protection Gain Share": (
                            state_benefit / reference_bundle_benefit[rule]
                        ),
                        "Realized Failed Road Length Share": float(
                            lengths[failed].sum() / total_length
                        ),
                        "Baseline Routing Seconds": baseline_seconds,
                        "Restoration Routing Seconds": restoration_seconds,
                    }
                )
            if replicate == 1 or replicate % 20 == 0 or replicate == PILOT_REPLICATES:
                print(
                    f"fixed-plan intervention states: {model} {replicate}/{PILOT_REPLICATES}",
                    flush=True,
                )
    intervention_stability = pd.DataFrame(intervention_rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    replicate_frame.to_parquet(REPLICATE_PATH, index=False)
    summary.to_parquet(ROAD_SUMMARY_PATH, index=False)
    station_stability.to_parquet(STATION_PATH, index=False)
    intervention_stability.to_parquet(INTERVENTION_PATH, index=False)
    return replicate_frame, summary, station_stability, intervention_stability


def load_robustness() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if cache_is_current():
        print("Using current scenario-robustness caches", flush=True)
        return (
            pd.read_parquet(REPLICATE_PATH),
            pd.read_parquet(ROAD_SUMMARY_PATH),
            pd.read_parquet(STATION_PATH),
            pd.read_parquet(INTERVENTION_PATH),
        )
    return construct_robustness()
