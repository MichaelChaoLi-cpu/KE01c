#!/usr/bin/env python3
"""Construct road-section reliability inputs and restoration cost proxies.

This script uses only KE01c-local preprocessed road edges and sections. It does
not generate stochastic road states or accessibility outcomes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
EXP = ROOT / "data" / "exp" / "data-preprocessing"

EDGE_PATH = PROCESSED / "routable_road_edges_sectioned_preprocessed.parquet"
SECTION_PATH = PROCESSED / "road_sections_preprocessed.parquet"
FAILURE_PATH = PROCESSED / "road_section_failure_probabilities_preprocessed.parquet"
INTERVENTION_PATH = PROCESSED / "road_section_intervention_preprocessed.parquet"
REPORT_PATH = EXP / "road_section_validation.json"

FAILURE_MODEL = "Length-Dependent Independent"
TARGET_SHARES = np.array([0.005, 0.01, 0.03, 0.05, 0.10], dtype=np.float64)
EVENT_HAZARD_CLASSES = {"Warning Zone", "Special Warning Zone"}


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of one file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_failed_length_share(intensity: float, lengths: np.ndarray) -> float:
    """Return expected unavailable length share at one failure intensity."""
    probability = -np.expm1(-intensity * lengths)
    return float(np.dot(lengths, probability) / lengths.sum())


def calibrate_intensity(target: float, lengths: np.ndarray) -> float:
    """Solve for intensity so expected unavailable length equals target."""
    if not 0.0 < target < 1.0:
        raise ValueError(f"Target share must lie in (0, 1), got {target}")
    low = 0.0
    high = 1.0 / float(np.median(lengths))
    while expected_failed_length_share(high, lengths) < target:
        high *= 2.0
    for _ in range(80):
        midpoint = 0.5 * (low + high)
        if expected_failed_length_share(midpoint, lengths) < target:
            low = midpoint
        else:
            high = midpoint
    return 0.5 * (low + high)


def validate_topology(edges: gpd.GeoDataFrame, sections: gpd.GeoDataFrame) -> dict[str, object]:
    """Validate edge-to-section membership, lengths, counts, and CRS."""
    if not edges["Road Edge ID"].is_unique:
        raise ValueError("Road Edge ID must be unique")
    if not sections["Road Section ID"].is_unique:
        raise ValueError("Road Section ID must be unique")
    if not edges["Road Section ID"].isin(sections["Road Section ID"]).all():
        raise ValueError("Every road edge must map to one retained Road Section ID")
    if edges.crs != sections.crs:
        raise ValueError(f"Road edge and section CRS differ: {edges.crs} versus {sections.crs}")

    grouped = edges.groupby("Road Section ID", sort=False).agg(
        Aggregated_Length=("Road Length (m)", "sum"),
        Aggregated_Edge_Count=("Road Edge ID", "size"),
    )
    declared = sections.set_index("Road Section ID")
    length_difference = (
        grouped["Aggregated_Length"] - declared["Road Section Length (m)"]
    ).abs()
    count_match = grouped["Aggregated_Edge_Count"].eq(declared["Road Edge Count"])
    if float(length_difference.max()) > 1e-6:
        raise ValueError("Aggregated edge length does not match Road Section Length (m)")
    if not bool(count_match.all()):
        raise ValueError("Aggregated edge count does not match Road Edge Count")

    return {
        "road_edge_id_unique": True,
        "road_section_id_unique": True,
        "all_edges_map_to_sections": True,
        "maximum_length_difference_m": float(length_difference.max()),
        "all_edge_counts_match": True,
        "crs": str(edges.crs),
    }


def construct_intervention_layer(
    edges: gpd.GeoDataFrame,
    sections: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, dict[str, float | int]]:
    """Add event-exposed length and a relative restoration cost proxy."""
    hazard = edges["Hazard Exposure Class"].astype("string").isin(EVENT_HAZARD_CLASSES)
    exposed_edges = edges.loc[hazard].copy()
    exposed = exposed_edges.groupby("Road Section ID", sort=False).agg(
        **{
            "Event-Exposed Road Length (m)": ("Road Length (m)", "sum"),
            "Event-Exposed Road Edge Count": ("Road Edge ID", "size"),
        }
    )
    intervention = sections.merge(
        exposed,
        how="left",
        left_on="Road Section ID",
        right_index=True,
        validate="one_to_one",
    )
    intervention["Event-Exposed Road Length (m)"] = intervention[
        "Event-Exposed Road Length (m)"
    ].fillna(0.0)
    intervention["Event-Exposed Road Edge Count"] = intervention[
        "Event-Exposed Road Edge Count"
    ].fillna(0).astype(np.int32)
    intervention["Event-Exposed Road Length Share"] = np.divide(
        intervention["Event-Exposed Road Length (m)"],
        intervention["Road Section Length (m)"],
        out=np.zeros(len(intervention), dtype=np.float64),
        where=intervention["Road Section Length (m)"].to_numpy(float) > 0,
    )
    positive = intervention["Event-Exposed Road Length (m)"] > 0
    median_positive = float(
        intervention.loc[positive, "Event-Exposed Road Length (m)"].median()
    )
    intervention["Road Restoration Cost Proxy"] = np.nan
    intervention.loc[positive, "Road Restoration Cost Proxy"] = (
        intervention.loc[positive, "Event-Exposed Road Length (m)"] / median_positive
    )
    intervention = gpd.GeoDataFrame(
        intervention,
        geometry="Geometry",
        crs=sections.crs,
    )
    intervention.to_parquet(INTERVENTION_PATH, index=False)

    diagnostics: dict[str, float | int] = {
        "event_exposed_road_edges": int(hazard.sum()),
        "event_exposed_road_sections": int(positive.sum()),
        "median_positive_event_exposed_length_m": median_positive,
        "maximum_event_exposed_length_m": float(
            intervention["Event-Exposed Road Length (m)"].max()
        ),
        "maximum_restoration_cost_proxy": float(
            intervention["Road Restoration Cost Proxy"].max()
        ),
    }
    return intervention, diagnostics


def construct_failure_probabilities(
    sections: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, list[dict[str, float]]]:
    """Build one section-by-severity length-dependent probability table."""
    eligible = sections["Road Available"].fillna(False) & sections[
        "Network Analysis Eligible"
    ].fillna(False)
    dimension = sections.loc[
        eligible,
        ["Road Section ID", "Road Section Length (m)"],
    ].reset_index(drop=True)
    lengths = dimension["Road Section Length (m)"].to_numpy(np.float64)
    if not np.isfinite(lengths).all() or np.any(lengths <= 0):
        raise ValueError("Every eligible road section must have one positive finite length")

    frames: list[pd.DataFrame] = []
    calibration: list[dict[str, float]] = []
    for target in TARGET_SHARES:
        intensity = calibrate_intensity(float(target), lengths)
        probability = -np.expm1(-intensity * lengths)
        frame = dimension.copy()
        frame["Road Failure Model"] = FAILURE_MODEL
        frame["Expected Failed Road Length Share"] = float(target)
        frame["Failure Intensity per Metre"] = intensity
        frame["Section Failure Probability"] = probability
        frames.append(frame)
        calibration.append(
            {
                "expected_failed_road_length_share": float(target),
                "failure_intensity_per_metre": float(intensity),
                "calibrated_expected_failed_road_length_share": expected_failed_length_share(
                    intensity, lengths
                ),
                "expected_failed_road_section_share": float(probability.mean()),
                "section_failure_probability_p50": float(np.quantile(probability, 0.50)),
                "section_failure_probability_p95": float(np.quantile(probability, 0.95)),
                "section_failure_probability_maximum": float(probability.max()),
            }
        )
    result = pd.concat(frames, ignore_index=True)
    result.to_parquet(FAILURE_PATH, index=False)
    return result, calibration


def main() -> None:
    edges = gpd.read_parquet(EDGE_PATH)
    sections = gpd.read_parquet(SECTION_PATH)
    topology_checks = validate_topology(edges, sections)
    intervention, intervention_diagnostics = construct_intervention_layer(edges, sections)
    probabilities, calibration = construct_failure_probabilities(sections)

    lengths = sections["Road Section Length (m)"].to_numpy(np.float64)
    length_quantiles = {
        str(probability): float(np.quantile(lengths, probability))
        for probability in (0.0, 0.50, 0.90, 0.95, 0.99, 0.999, 1.0)
    }
    report = {
        "status": "pass",
        "scope": "Preprocessing and calibration inputs only; no Monte Carlo road states or accessibility outcomes generated.",
        "source_provenance": {
            "upstream_repository_state": "KE01b working-tree derived artifacts, user-confirmed read-only transfer",
            "local_edge_sha256": sha256(EDGE_PATH),
            "local_section_sha256": sha256(SECTION_PATH),
        },
        "row_counts": {
            "routable_road_edges": int(len(edges)),
            "road_sections": int(len(sections)),
            "road_section_intervention": int(len(intervention)),
            "road_section_failure_probabilities": int(len(probabilities)),
        },
        "topology_checks": topology_checks,
        "road_section_length_quantiles_m": length_quantiles,
        "route_name_missing_share": float(sections["Route Name"].isna().mean()),
        "intervention_diagnostics": intervention_diagnostics,
        "length_dependent_calibration": calibration,
        "interpretation_limits": [
            "Section Failure Probability is a declared stochastic sensitivity, not an engineering or observed 2026 failure probability.",
            "Road Restoration Cost Proxy is normalized event-exposed length, not repair duration or monetary cost.",
            "Full-section and connector-aware local-fragment closure must be compared during robustness analysis.",
        ],
    }
    EXP.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Saved {len(probabilities):,} rows x {len(probabilities.columns)} cols -> "
        f"{FAILURE_PATH.relative_to(ROOT)}"
    )
    print(
        f"Saved {len(intervention):,} rows x {len(intervention.columns)} cols -> "
        f"{INTERVENTION_PATH.relative_to(ROOT)}"
    )
    print(f"Saved validation report -> {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
