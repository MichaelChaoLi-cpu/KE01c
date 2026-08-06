"""Shared leave-one-fire-base-out accessibility criticality calculations."""

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
OUTPUT_PATH = RESULTS / "derived/fire_base_leave_one_out_criticality.parquet"

OBJECTIVES = {
    "Population": "Population Exposure",
    "Older population": "Older Population Vulnerability Exposure",
    "Critical facilities": "Critical Facility Exposure",
}
ROAD_SCENARIOS = ("normal", "central")


def cache_is_current() -> bool:
    """Use the deterministic criticality cache only when all inputs are older."""
    sources = (
        CONSEQUENCE_PATH,
        RESULTS / "derived/network/fire_station_od_normal.npz",
        RESULTS / "derived/network/fire_station_od_central.npz",
        RESULTS / "derived/network/fire_dispatch_base_access.parquet",
        Path(__file__),
    )
    return OUTPUT_PATH.exists() and OUTPUT_PATH.stat().st_mtime >= max(
        path.stat().st_mtime for path in sources
    )


def accessibility_penalty(
    response_time: np.ndarray,
    qualifying_base_count: np.ndarray,
) -> np.ndarray:
    """Evaluate the Section 6.3 response-time and redundancy penalty."""
    return 0.5 * np.minimum(response_time / UNMET_SERVICE_CAP_MIN, 1.0) + 0.5 / np.maximum(
        qualifying_base_count,
        1,
    )


def leave_one_out_values(od: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Return objective-by-base loss increases after one-base removal."""
    if od.ndim != 2 or weights.ndim != 2 or weights.shape[1] != od.shape[1]:
        raise ValueError("OD and objective-weight arrays do not align")
    if od.shape[0] < 2:
        raise ValueError("Leave-one-out criticality requires at least two bases")

    fastest_base = np.argmin(od, axis=0)
    two_fastest = np.partition(od, kth=1, axis=0)[:2]
    full_time = two_fastest[0]
    second_time = two_fastest[1]
    full_qualifying = (od <= BACKUP_THRESHOLD_MIN).sum(axis=0).astype(np.int16)
    full_penalty = accessibility_penalty(full_time, full_qualifying)

    values = np.zeros((weights.shape[0], od.shape[0]), dtype=np.float64)
    for base_index in range(od.shape[0]):
        removed_time = np.where(fastest_base == base_index, second_time, full_time)
        removed_qualifying = full_qualifying - (od[base_index] <= BACKUP_THRESHOLD_MIN)
        removed_penalty = accessibility_penalty(removed_time, removed_qualifying)
        values[:, base_index] = weights @ (removed_penalty - full_penalty)

    tolerance = 1e-8
    if float(values.min()) < -tolerance:
        raise RuntimeError("Removing a base produced an implausible negative loss increase")
    values[values < 0] = 0.0
    return values


def construct_fire_base_criticality() -> gpd.GeoDataFrame:
    """Evaluate all eligible bases under normal and event-specific roads."""
    consequence = gpd.read_parquet(CONSEQUENCE_PATH)
    consequence["Mesh Code"] = consequence["Mesh Code"].astype("string")
    consequence = consequence.set_index("Mesh Code", drop=False)

    records: list[dict[str, object]] = []
    station_crs = None
    for scenario in ROAD_SCENARIOS:
        od, demand, dispatch_order = build_station_od(scenario)
        dispatch = gpd.read_parquet(DISPATCH_PATH).reset_index(drop=True)
        expected_order = dispatch_order["Dispatch Base Node ID"].astype("string").reset_index(drop=True)
        geometry_order = dispatch["Dispatch Base Node ID"].astype("string").reset_index(drop=True)
        if not geometry_order.equals(expected_order):
            raise ValueError("Station geometry order does not match the OD matrix")
        if not dispatch["Candidate Dispatch Base"].fillna(False).all():
            raise ValueError("The station OD matrix contains an ineligible response origin")
        station_crs = dispatch.crs

        ordered = consequence.reindex(demand["Mesh Code"].astype("string"))
        if ordered["Conditional Spread Susceptibility"].isna().any():
            raise ValueError("Station OD demand cells do not align with consequence cells")
        weights = np.vstack(
            [
                (
                    ordered["Conditional Spread Susceptibility"]
                    * ordered[exposure_column]
                ).to_numpy(dtype=np.float64)
                for exposure_column in OBJECTIVES.values()
            ]
        )
        values = leave_one_out_values(od, weights)
        totals = values.sum(axis=1)

        for objective_index, objective in enumerate(OBJECTIVES):
            if totals[objective_index] <= 0:
                raise RuntimeError(
                    f"Leave-one-out loss is unidentified for {scenario}, {objective}"
                )
            shares = values[objective_index] / totals[objective_index]
            for base_index, base in dispatch.iterrows():
                records.append(
                    {
                        "Fire Base Name": base["Fire Facility Name"],
                        "Fire Base Type": base["Fire Facility Type"],
                        "Municipality Code": base["Municipality Code"],
                        "Candidate Dispatch Base": bool(base["Candidate Dispatch Base"]),
                        "Road Scenario": scenario,
                        "Exposure Objective": objective,
                        "Leave-One-Out Fire Base Value": values[
                            objective_index, base_index
                        ],
                        "Leave-One-Out Fire Base Value Share": shares[base_index],
                        "Scenario Criticality Rank": int(
                            pd.Series(shares).rank(method="min", ascending=False).iloc[
                                base_index
                            ]
                        ),
                        "Geometry": base["Geometry"],
                    }
                )

    result = gpd.GeoDataFrame(records, geometry="Geometry", crs=station_crs)
    grouping = ["Fire Base Name", "Exposure Objective"]
    scenario_summary = (
        result.groupby(grouping, sort=False)["Leave-One-Out Fire Base Value Share"]
        .agg(
            Road_Scenario_Share_Median="median",
            Road_Scenario_Share_Q25=lambda values: values.quantile(0.25),
            Road_Scenario_Share_Q75=lambda values: values.quantile(0.75),
        )
        .reset_index()
    )
    scenario_summary["Road-Scenario Leave-One-Out IQR"] = (
        scenario_summary["Road_Scenario_Share_Q75"]
        - scenario_summary["Road_Scenario_Share_Q25"]
    )
    shares = result.pivot(
        index=grouping,
        columns="Road Scenario",
        values="Leave-One-Out Fire Base Value Share",
    )
    shares["Event Minus Normal Leave-One-Out Share"] = shares["central"] - shares["normal"]
    scenario_summary = scenario_summary.merge(
        shares[["Event Minus Normal Leave-One-Out Share"]].reset_index(),
        on=grouping,
        how="left",
        validate="one_to_one",
    )
    result = result.merge(
        scenario_summary[
            grouping
            + [
                "Road-Scenario Leave-One-Out IQR",
                "Event Minus Normal Leave-One-Out Share",
            ]
        ],
        on=grouping,
        how="left",
        validate="many_to_one",
    )
    result = gpd.GeoDataFrame(result, geometry="Geometry", crs=station_crs)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT_PATH, index=False)
    print(f"Saved: {OUTPUT_PATH.relative_to(ROOT)}", flush=True)
    return result


def load_fire_base_criticality() -> gpd.GeoDataFrame:
    """Load a current cache or recompute deterministic criticality."""
    if cache_is_current():
        print(f"Using current criticality cache: {OUTPUT_PATH.relative_to(ROOT)}", flush=True)
        return gpd.read_parquet(OUTPUT_PATH)
    return construct_fire_base_criticality()
