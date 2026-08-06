"""Analytical overlap diagnostics for nominal stochastic road-failure inputs.

The stored stochastic road states are calibrated over the full eligible
pre-mask road-section length.  This helper quantifies how much of that nominal
failure input overlaps the event-specific road mask and how much represents
additional unavailable length.  It performs no routing and does not alter any
stored road state.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
PROBABILITY_PATH = PROCESSED / "road_section_failure_probabilities_preprocessed.parquet"
SECTION_PATH = PROCESSED / "road_section_intervention_preprocessed.parquet"
HAZARD_WEIGHT = 2.5


def calibrate_intensity(
    target: float,
    lengths: np.ndarray,
    multiplier: np.ndarray,
) -> float:
    """Match the existing nominal failed-length calibration without rerouting."""
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


def build_overlap_diagnostics(
    severities: tuple[float, ...] = (0.03,),
) -> pd.DataFrame:
    """Return expected overlap and effective added-length shares by mechanism."""
    probability = pd.read_parquet(
        PROBABILITY_PATH,
        columns=[
            "Road Section ID",
            "Expected Failed Road Length Share",
            "Road Section Length (m)",
            "Section Failure Probability",
        ],
    )
    probability["Road Section ID"] = probability["Road Section ID"].astype(str)
    sections = pd.read_parquet(
        SECTION_PATH,
        columns=["Road Section ID", "Event-Exposed Road Length (m)"],
    )
    sections["Road Section ID"] = sections["Road Section ID"].astype(str)
    event_exposed = sections.set_index("Road Section ID")[
        "Event-Exposed Road Length (m)"
    ].astype(float)

    rows: list[dict[str, float | str]] = []
    for severity in severities:
        selected = probability.loc[
            probability["Expected Failed Road Length Share"].eq(severity)
        ].copy()
        if not selected["Road Section ID"].is_unique:
            raise ValueError("Nominal road-failure probabilities must be unique by section")
        selected["Event-Exposed Road Length (m)"] = (
            selected["Road Section ID"].map(event_exposed).fillna(0.0)
        )
        lengths = selected["Road Section Length (m)"].to_numpy(np.float64)
        exposed = selected["Event-Exposed Road Length (m)"].to_numpy(np.float64)
        if np.any(exposed < 0) or np.any(exposed > lengths + 1e-6):
            raise ValueError("Event-exposed length must lie within road-section length")
        available = np.maximum(lengths - exposed, 0.0)
        independent_probability = selected["Section Failure Probability"].to_numpy(
            np.float64
        )
        hazard_multiplier = np.where(exposed > 0, HAZARD_WEIGHT, 1.0)
        hazard_intensity = calibrate_intensity(
            severity,
            lengths,
            hazard_multiplier,
        )
        hazard_probability = -np.expm1(
            -hazard_intensity * lengths * hazard_multiplier
        )

        for model, failure_probability in (
            ("Length-dependent / spatially clustered", independent_probability),
            ("Hazard-weighted", hazard_probability),
        ):
            expected_failed_length = float(lengths @ failure_probability)
            expected_overlap_length = float(exposed @ failure_probability)
            expected_added_length = float(available @ failure_probability)
            rows.append(
                {
                    "Failure Model Group": model,
                    "Nominal Failed Road Length Input": severity,
                    "Pre-Existing Event-Unavailable Road Length Share": float(
                        exposed.sum() / lengths.sum()
                    ),
                    "Expected Failed-Length Overlap Share": (
                        expected_overlap_length / expected_failed_length
                    ),
                    "Expected Added Unavailable Share of Pre-Event Network": (
                        expected_added_length / lengths.sum()
                    ),
                    "Expected Added Unavailable Share of Event-Available Network": (
                        expected_added_length / available.sum()
                    ),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(build_overlap_diagnostics().to_string(index=False))
