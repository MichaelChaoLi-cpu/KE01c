"""Shared sampled-Shapley estimation for accessibility-based fire-base value."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from fire_service_access_common import (
    BACKUP_THRESHOLD_MIN,
    DISPATCH_PATH,
    UNMET_SERVICE_CAP_MIN,
    build_station_od,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data/results"
CONSEQUENCE_PATH = RESULTS / "derived/fire_consequence_125m.parquet"
VALUE_PATH = RESULTS / "derived/fire_base_values.parquet"
CONVERGENCE_PATH = RESULTS / "derived/fire_base_value_convergence.parquet"

OBJECTIVES = {
    "Population": "Population Exposure",
    "Older population": "Older Population Vulnerability Exposure",
    "Critical facilities": "Critical Facility Exposure",
}
ROAD_SCENARIOS = ("normal", "central")

SHAPLEY_SEED = 20260805
SHAPLEY_BATCH_SIZE = 64
SHAPLEY_MIN_PERMUTATIONS = 256
SHAPLEY_MAX_PERMUTATIONS = 512
RANK_CORRELATION_TARGET = 0.995
TOP_TEN_OVERLAP_TARGET = 0.90
RELATIVE_CI_TARGET = 0.10
ROBUSTNESS_PENALTY = 0.5


def cache_is_current() -> bool:
    """Use the station-value cache only when all analytical inputs are older."""
    sources = [
        CONSEQUENCE_PATH,
        RESULTS / "derived/network/fire_station_od_normal.npz",
        RESULTS / "derived/network/fire_station_od_central.npz",
        RESULTS / "derived/network/fire_dispatch_base_access.parquet",
        Path(__file__),
    ]
    return (
        VALUE_PATH.exists()
        and CONVERGENCE_PATH.exists()
        and VALUE_PATH.stat().st_mtime >= max(path.stat().st_mtime for path in sources)
    )


def accessibility_penalty(
    response_time: np.ndarray,
    qualifying_base_count: np.ndarray,
) -> np.ndarray:
    """Evaluate the Section 6.3 equal-weight accessibility penalty."""
    return 0.5 * np.minimum(response_time / UNMET_SERVICE_CAP_MIN, 1) + 0.5 / np.maximum(
        qualifying_base_count,
        1,
    )


def leave_one_out_values(od: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Return objective-by-station full-coalition removal losses."""
    fastest_station = np.argmin(od, axis=0)
    two_fastest = np.partition(od, kth=1, axis=0)[:2]
    full_time = two_fastest[0]
    second_time = two_fastest[1]
    full_count = (od <= BACKUP_THRESHOLD_MIN).sum(axis=0).astype(np.int16)
    full_penalty = accessibility_penalty(full_time, full_count)

    values = np.zeros((weights.shape[0], od.shape[0]), dtype=np.float64)
    for station_index in range(od.shape[0]):
        removed_time = np.where(fastest_station == station_index, second_time, full_time)
        removed_count = full_count - (od[station_index] <= BACKUP_THRESHOLD_MIN)
        removed_penalty = accessibility_penalty(removed_time, removed_count)
        values[:, station_index] = weights @ (removed_penalty - full_penalty)
    return values


def rank_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Return Spearman rank correlation without an additional dependency."""
    left_rank = pd.Series(left).rank(method="average")
    right_rank = pd.Series(right).rank(method="average")
    return float(left_rank.corr(right_rank))


def convergence_metrics(
    previous: np.ndarray,
    current: np.ndarray,
    standard_error: np.ndarray,
) -> tuple[list[dict[str, float]], bool]:
    """Evaluate declared rank, top-ten, and relative-interval criteria."""
    rows: list[dict[str, float]] = []
    passes: list[bool] = []
    for objective_index, objective in enumerate(OBJECTIVES):
        previous_values = previous[objective_index]
        current_values = current[objective_index]
        correlation = rank_correlation(previous_values, current_values)
        previous_top = set(np.argsort(previous_values)[-10:])
        current_top = set(np.argsort(current_values)[-10:])
        overlap = len(previous_top & current_top) / 10
        top_indices = np.argsort(current_values)[-10:]
        relative_ci = np.divide(
            1.96 * standard_error[objective_index, top_indices],
            current_values[top_indices],
            out=np.full(10, np.inf),
            where=current_values[top_indices] > 0,
        )
        median_relative_ci = float(np.median(relative_ci))
        passed = (
            correlation >= RANK_CORRELATION_TARGET
            and overlap >= TOP_TEN_OVERLAP_TARGET
            and median_relative_ci <= RELATIVE_CI_TARGET
        )
        rows.append(
            {
                "Exposure Objective": objective,
                "Rank Correlation with Previous Batch": correlation,
                "Top Ten Overlap": overlap,
                "Median Relative 95% CI Half-Width": median_relative_ci,
                "Converged": passed,
            }
        )
        passes.append(passed)
    return rows, all(passes)


def sampled_shapley_values(
    od: np.ndarray,
    weights: np.ndarray,
    *,
    seed: int,
    scenario: str,
) -> tuple[np.ndarray, np.ndarray, int, bool, pd.DataFrame]:
    """Estimate station Shapley values in antithetic permutation batches."""
    rng = np.random.default_rng(seed)
    station_count, cell_count = od.shape
    value_sum = np.zeros((weights.shape[0], station_count), dtype=np.float64)
    square_sum = np.zeros_like(value_sum)
    permutations = 0
    previous_mean: np.ndarray | None = None
    convergence_rows: list[dict[str, object]] = []
    converged = False

    while permutations < SHAPLEY_MAX_PERMUTATIONS:
        samples_this_batch = min(
            SHAPLEY_BATCH_SIZE,
            SHAPLEY_MAX_PERMUTATIONS - permutations,
        )
        if samples_this_batch % 2:
            raise ValueError("Shapley batch size must be even for antithetic sampling")
        for _ in range(samples_this_batch // 2):
            forward = rng.permutation(station_count)
            for order in (forward, forward[::-1]):
                response_time = np.full(
                    cell_count,
                    UNMET_SERVICE_CAP_MIN,
                    dtype=np.float32,
                )
                qualifying_count = np.zeros(cell_count, dtype=np.int16)
                penalty = np.ones(cell_count, dtype=np.float32)
                permutation_value = np.zeros_like(value_sum)
                for station_index in order:
                    station_time = od[station_index]
                    next_time = np.minimum(response_time, station_time)
                    next_count = qualifying_count + (
                        station_time <= BACKUP_THRESHOLD_MIN
                    )
                    next_penalty = accessibility_penalty(next_time, next_count)
                    permutation_value[:, station_index] = weights @ (
                        penalty - next_penalty
                    )
                    response_time = next_time
                    qualifying_count = next_count
                    penalty = next_penalty
                value_sum += permutation_value
                square_sum += permutation_value**2
                permutations += 1

        mean = value_sum / permutations
        if permutations > 1:
            variance = np.maximum(
                (square_sum - permutations * mean**2) / (permutations - 1),
                0,
            )
            standard_error = np.sqrt(variance / permutations)
        else:
            standard_error = np.full_like(mean, np.nan)

        if previous_mean is not None:
            metric_rows, batch_converged = convergence_metrics(
                previous_mean,
                mean,
                standard_error,
            )
            for row in metric_rows:
                convergence_rows.append(
                    {
                        "Road Scenario": scenario,
                        "Permutation Count": permutations,
                        **row,
                    }
                )
            print(
                f"{scenario} sampled Shapley: {permutations} permutations; "
                f"minimum rank correlation="
                f"{min(row['Rank Correlation with Previous Batch'] for row in metric_rows):.4f}; "
                f"minimum top-ten overlap="
                f"{min(row['Top Ten Overlap'] for row in metric_rows):.2f}; "
                f"maximum median relative CI="
                f"{max(row['Median Relative 95% CI Half-Width'] for row in metric_rows):.3f}",
                flush=True,
            )
            if permutations >= SHAPLEY_MIN_PERMUTATIONS and batch_converged:
                converged = True
                break
        previous_mean = mean.copy()

    convergence = pd.DataFrame(convergence_rows)
    return mean, standard_error, permutations, converged, convergence


def construct_fire_base_values() -> gpd.GeoDataFrame:
    """Estimate and cache station values for two road and three exposure cases."""
    consequence = gpd.read_parquet(CONSEQUENCE_PATH)
    consequence["Mesh Code"] = consequence["Mesh Code"].astype("string")
    consequence = consequence.set_index("Mesh Code", drop=False)

    records: list[dict[str, object]] = []
    convergence_frames: list[pd.DataFrame] = []
    station_crs = None
    for scenario_index, scenario in enumerate(ROAD_SCENARIOS):
        od, demand, dispatch_order = build_station_od(scenario)
        dispatch = gpd.read_parquet(DISPATCH_PATH).reset_index(drop=True)
        expected_order = dispatch_order["Dispatch Base Node ID"].astype("string").reset_index(drop=True)
        geometry_order = dispatch["Dispatch Base Node ID"].astype("string").reset_index(drop=True)
        if not geometry_order.equals(expected_order):
            raise ValueError("GeoParquet station order does not match the station OD matrix")
        station_crs = dispatch.crs
        ordered = consequence.reindex(demand["Mesh Code"].astype("string"))
        if ordered["Conditional Spread Susceptibility"].isna().any():
            raise ValueError("Station OD demand cells do not align with consequence cells")
        weights = np.vstack(
            [
                (
                    ordered["Conditional Spread Susceptibility"]
                    * ordered[exposure_column]
                ).to_numpy(dtype=np.float32)
                for exposure_column in OBJECTIVES.values()
            ]
        )

        leave_one_out = leave_one_out_values(od, weights)
        shapley, standard_error, permutations, converged, convergence = (
            sampled_shapley_values(
                od,
                weights,
                seed=SHAPLEY_SEED + scenario_index,
                scenario=scenario,
            )
        )
        convergence_frames.append(convergence)
        shapley_total = shapley.sum(axis=1)
        leave_one_out_total = leave_one_out.sum(axis=1)

        for objective_index, objective in enumerate(OBJECTIVES):
            for station_index, station in dispatch.reset_index(drop=True).iterrows():
                records.append(
                    {
                        "Fire Base Name": station["Fire Facility Name"],
                        "Fire Base Type": station["Fire Facility Type"],
                        "Municipality Code": station["Municipality Code"],
                        "Candidate Dispatch Base": station["Candidate Dispatch Base"],
                        "Road Scenario": scenario,
                        "Exposure Objective": objective,
                        "Leave-One-Out Fire Base Value": leave_one_out[
                            objective_index, station_index
                        ],
                        "Leave-One-Out Value Share": (
                            leave_one_out[objective_index, station_index]
                            / leave_one_out_total[objective_index]
                            if leave_one_out_total[objective_index] > 0
                            else np.nan
                        ),
                        "Scenario Shapley Value": shapley[
                            objective_index, station_index
                        ],
                        "Scenario Shapley Standard Error": standard_error[
                            objective_index, station_index
                        ],
                        "Scenario Shapley Value Share": (
                            shapley[objective_index, station_index]
                            / shapley_total[objective_index]
                            if shapley_total[objective_index] > 0
                            else np.nan
                        ),
                        "Permutation Count": permutations,
                        "Shapley Converged": converged,
                        "Geometry": station["Geometry"],
                    }
                )

    values = gpd.GeoDataFrame(records, geometry="Geometry", crs=station_crs)
    grouping = ["Fire Base Name", "Exposure Objective"]
    robust = (
        values.groupby(grouping, sort=False)["Scenario Shapley Value Share"]
        .agg(
            Shapley_Share_Median="median",
            Shapley_Share_Q25=lambda series: series.quantile(0.25),
            Shapley_Share_Q75=lambda series: series.quantile(0.75),
        )
        .reset_index()
    )
    robust["Scenario Shapley Share IQR"] = (
        robust["Shapley_Share_Q75"] - robust["Shapley_Share_Q25"]
    )
    robust["Robust Fire Base Value"] = (
        robust["Shapley_Share_Median"]
        - ROBUSTNESS_PENALTY * robust["Scenario Shapley Share IQR"]
    )
    robust["Robust Fire Base Rank"] = robust.groupby("Exposure Objective")[
        "Robust Fire Base Value"
    ].rank(method="min", ascending=False)
    values = values.merge(
        robust[
            grouping
            + [
                "Shapley_Share_Median",
                "Scenario Shapley Share IQR",
                "Robust Fire Base Value",
                "Robust Fire Base Rank",
            ]
        ],
        on=grouping,
        how="left",
        validate="many_to_one",
    )
    values = gpd.GeoDataFrame(values, geometry="Geometry", crs=station_crs)

    VALUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    values.to_parquet(VALUE_PATH, index=False)
    pd.concat(convergence_frames, ignore_index=True).to_parquet(
        CONVERGENCE_PATH,
        index=False,
    )
    print(f"Saved: {VALUE_PATH.relative_to(ROOT)}", flush=True)
    print(f"Saved: {CONVERGENCE_PATH.relative_to(ROOT)}", flush=True)
    return values


def load_fire_base_values() -> gpd.GeoDataFrame:
    """Load a current cache or estimate station values from declared scenarios."""
    if cache_is_current():
        print(f"Using current station-value cache: {VALUE_PATH.relative_to(ROOT)}", flush=True)
        return gpd.read_parquet(VALUE_PATH)
    return construct_fire_base_values()
