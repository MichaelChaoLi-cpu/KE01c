#!/usr/bin/env python3
"""Generate a compact English-only robustness and sensitivity summary."""

from __future__ import annotations

from pathlib import Path
import re

from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ROBUSTNESS = ROOT / "data/results/derived/robustness"
CONVERGENCE_PATH = (
    ROOT / "data/results/derived/road_reliability/road_reliability_convergence.parquet"
)
OUTPUT = ROOT / "data/results/tables/Table_robustness_and_sensitivity_summary.xlsx"
HAN_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")

LD = "Length-dependent independent"
SC = "Spatially clustered"
HW = "Hazard-weighted"


def reliability_assessment(loss_pp: float, reference: bool = False) -> str:
    if reference:
        return "Reference"
    if loss_pp <= 1.0:
        return "Stable"
    if loss_pp <= 3.0:
        return "Moderately sensitive"
    return "Sensitive"


def base_assessment(rank_correlation: float, overlap: float) -> str:
    if rank_correlation >= 0.98 and overlap >= 0.80:
        return "Stable"
    if rank_correlation >= 0.95 and overlap >= 0.70:
        return "Moderately sensitive"
    return "Sensitive"


def intervention_assessment(retained_gain: float, overlap: float) -> str:
    if retained_gain >= 0.98 and overlap >= 0.80:
        return "Stable"
    if retained_gain >= 0.95 and overlap >= 0.67:
        return "Moderately sensitive"
    return "Sensitive"


def build_table() -> pd.DataFrame:
    """Combine exact nonredundant robustness results into 16 compact rows."""
    road = pd.read_parquet(ROBUSTNESS / "road_mechanism_summary.parquet")
    base = pd.read_parquet(ROBUSTNESS / "fire_base_priority_stability.parquet")
    intervention = pd.read_parquet(
        ROBUSTNESS / "road_intervention_priority_stability.parquet"
    )
    convergence = pd.read_parquet(CONVERGENCE_PATH)

    rows: list[dict[str, str]] = []
    reliability_specs = [
        (LD, 0.01, "Primary severity path"),
        (LD, 0.03, "Primary severity path"),
        (LD, 0.05, "Primary severity path"),
        (LD, 0.10, "Primary stress boundary"),
        (SC, 0.03, "Alternative failure mechanism"),
        (HW, 0.03, "Alternative failure mechanism"),
    ]
    one_percent = road.loc[
        road["Expected Failed Road Length Share"].eq(0.01)
    ].set_index("Road Failure Model")["Mean Timely Response Probability"]
    for model, share, specification in reliability_specs:
        match = road.loc[
            road["Road Failure Model"].eq(model)
            & road["Expected Failed Road Length Share"].eq(share)
        ]
        if len(match) != 1:
            raise ValueError(f"Missing road robustness row for {model}, {share}")
        item = match.iloc[0]
        loss_pp = 100 * (
            float(one_percent.loc[model])
            - float(item["Mean Timely Response Probability"])
        )
        rows.append(
            {
                "Domain": "Road-response reliability",
                "Specification": specification,
                "Failure Model": model,
                "Failed Road Length": f"{100 * share:.0f}%",
                "Primary Result": (
                    f"Mean timely response {100 * item['Mean Timely Response Probability']:.2f}%"
                ),
                "Secondary Result": (
                    f"Mean P90 response {item['Mean P90 Response Time (min)']:.2f} min"
                ),
                "Assessment": reliability_assessment(loss_pp, reference=share == 0.01),
                "Interpretation": (
                    f"Timely-response loss versus the same-mechanism 1% case: {loss_pp:.2f} percentage points; "
                    f"mean disconnected demand share: {100 * item['Mean Disconnected Demand Share']:.2f}%."
                ),
            }
        )

    for model in [LD, SC, HW]:
        subset = base.loc[base["Road Failure Model"].eq(model)]
        if subset["Exposure Objective"].nunique() != 3:
            raise ValueError(f"Expected three exposure objectives for {model}")
        minimum_correlation = float(subset["Station Rank Correlation"].min())
        minimum_overlap = float(subset["Top Ten Fire Base Overlap"].min())
        rows.append(
            {
                "Domain": "Fire-base priority",
                "Specification": "Worst case across three exposure objectives",
                "Failure Model": model,
                "Failed Road Length": "3%",
                "Primary Result": f"Minimum rank correlation {minimum_correlation:.3f}",
                "Secondary Result": f"Minimum top-10 retained {100 * minimum_overlap:.0f}%",
                "Assessment": base_assessment(minimum_correlation, minimum_overlap),
                "Interpretation": (
                    "Worst case across population, older-population, and critical-facility objectives; "
                    + (
                        "top-base membership changes despite high overall rank agreement."
                        if minimum_overlap < 0.80
                        else "both ordering and top-base membership remain stable."
                    )
                ),
            }
        )

    for model in [LD, SC, HW]:
        for rule in ["Section count", "Length-aware"]:
            match = intervention.loc[
                intervention["Road Failure Model"].eq(model)
                & intervention["Road Priority Rule"].eq(rule)
            ]
            if len(match) != 1:
                raise ValueError(f"Missing intervention robustness row for {model}, {rule}")
            item = match.iloc[0]
            retained = float(item["Retained Protection Gain Share"])
            overlap = float(item["Top Three Road Priority Overlap"])
            correlation = float(item["Intervention Rank Correlation"])
            rows.append(
                {
                    "Domain": "Road-intervention priority",
                    "Specification": rule,
                    "Failure Model": model,
                    "Failed Road Length": "3%",
                    "Primary Result": f"Retained protection gain {100 * retained:.2f}%",
                    "Secondary Result": f"Top-three overlap {100 * overlap:.0f}%",
                    "Assessment": intervention_assessment(retained, overlap),
                    "Interpretation": (
                        f"Priority rank correlation {correlation:.3f}; protection-gain loss relative to the event-specific bundle: "
                        f"{100 * (1 - retained):.2f}%."
                    ),
                }
            )

    final = convergence.loc[convergence["Simulation Replicates"].eq(1000)]
    if len(final) != 1:
        raise ValueError("Expected one 1,000-replicate convergence checkpoint")
    checkpoint = final.iloc[0]
    mean_change = float(checkpoint["Mean Absolute Grid Probability Change"])
    jaccard = float(checkpoint["Top-Decile Priority Jaccard"])
    assessment = "Stable" if mean_change <= 0.001 and jaccard >= 0.90 else "Sensitive"
    rows.append(
        {
            "Domain": "Road-reliability convergence",
            "Specification": "1,000-replicate checkpoint",
            "Failure Model": LD,
            "Failed Road Length": "3%",
            "Primary Result": f"Mean probability change {mean_change:.4f}",
            "Secondary Result": f"Top-decile Jaccard {jaccard:.3f}",
            "Assessment": assessment,
            "Interpretation": (
                f"Change relative to the {int(checkpoint['Previous Checkpoint'])}-replicate checkpoint; "
                f"maximum cell probability change: {checkpoint['Maximum Absolute Grid Probability Change']:.4f}."
            ),
        }
    )

    table = pd.DataFrame(rows)
    if table.isna().any().any():
        raise ValueError("Robustness summary contains missing cells")
    return table


def build_definitions() -> pd.DataFrame:
    rows = [
        (
            "Scope",
            "The table reports exact values that support, but do not duplicate, the accepted Scenario and Parameter Robustness figure.",
        ),
        (
            "Road-response rows",
            "The primary length-dependent mechanism is shown at 1%, 3%, 5%, and 10%; alternative mechanisms are shown at the main 3% severity. Each summary uses 100 pilot replicates.",
        ),
        (
            "Fire-base rows",
            "Representative seeded road states are evaluated across population, older-population, and critical-facility objectives. The table reports the worst objective-specific result for each mechanism.",
        ),
        (
            "Intervention rows",
            "Representative seeded road states test section-count and length-aware road priorities. These are stability checks, not complete re-optimization under every replicate.",
        ),
        (
            "Road reliability assessment",
            "Stable means timely-response loss of at most 1 percentage point relative to the same-mechanism 1% case; moderately sensitive means more than 1 and at most 3 points; sensitive means more than 3 points.",
        ),
        (
            "Fire-base assessment",
            "Stable requires rank correlation at least 0.98 and top-10 overlap at least 80%; moderately sensitive requires correlation at least 0.95 and overlap at least 70%; otherwise sensitive.",
        ),
        (
            "Intervention assessment",
            "Stable requires at least 98% retained protection gain and 80% top-priority overlap; moderately sensitive requires at least 95% retained gain and 67% overlap; otherwise sensitive.",
        ),
        (
            "Convergence assessment",
            "Stable at the final checkpoint requires mean absolute grid-probability change at most 0.001 and top-decile Jaccard at least 0.90.",
        ),
        (
            "Interpretation boundary",
            "Failure shares and mechanisms are declared scenario inputs, not observed damage rates or engineering-calibrated failure probabilities.",
        ),
    ]
    return pd.DataFrame(rows, columns=["Item", "Definition or Boundary"])


def format_workbook(path: Path) -> None:
    from openpyxl import load_workbook

    workbook = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="263746")
    band_fill = PatternFill("solid", fgColor="F1F4F6")
    assessment_fill = {
        "Reference": PatternFill("solid", fgColor="E8EEF2"),
        "Stable": PatternFill("solid", fgColor="E5F2EA"),
        "Moderately sensitive": PatternFill("solid", fgColor="FFF1D6"),
        "Sensitive": PatternFill("solid", fgColor="F8DEDE"),
    }
    sheet = workbook["Robustness Summary"]
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True, size=9)
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    widths = [27, 36, 31, 18, 31, 31, 23, 62]
    for column, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(column)].width = width
    for row_number in range(2, sheet.max_row + 1):
        if row_number % 2 == 0:
            for cell in sheet[row_number]:
                cell.fill = band_fill
        for column, cell in enumerate(sheet[row_number], start=1):
            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top",
                horizontal="center" if column in {4, 7} else "left",
            )
        assessment = sheet.cell(row_number, 7)
        assessment.fill = assessment_fill.get(assessment.value, band_fill)
        assessment.font = Font(bold=True, color="263746")
        sheet.row_dimensions[row_number].height = 52
    sheet.row_dimensions[1].height = 48
    sheet.freeze_panes = "E2"
    sheet.auto_filter.ref = sheet.dimensions

    definitions = workbook["Definitions"]
    for cell in definitions[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
    definitions.column_dimensions["A"].width = 32
    definitions.column_dimensions["B"].width = 112
    for row_number in range(2, definitions.max_row + 1):
        definitions.cell(row_number, 1).font = Font(bold=True, color="263746")
        definitions.cell(row_number, 1).alignment = Alignment(vertical="top")
        definitions.cell(row_number, 2).alignment = Alignment(wrap_text=True, vertical="top")
        definitions.row_dimensions[row_number].height = 46
    definitions.freeze_panes = "A2"
    workbook.save(path)


def validate_english_only(path: Path) -> None:
    from openpyxl import load_workbook

    workbook = load_workbook(path, data_only=True)
    hits = [
        (sheet.title, cell.coordinate, cell.value)
        for sheet in workbook.worksheets
        for row in sheet.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and HAN_PATTERN.search(cell.value)
    ]
    if hits:
        raise ValueError(f"Han characters remain in workbook: {hits[:5]}")


def main() -> None:
    table = build_table()
    if table.shape != (16, 8):
        raise ValueError(f"Expected a 16 x 8 table, received {table.shape}")
    definitions = build_definitions()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        table.to_excel(writer, sheet_name="Robustness Summary", index=False)
        definitions.to_excel(writer, sheet_name="Definitions", index=False)
    format_workbook(OUTPUT)
    validate_english_only(OUTPUT)
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"rows={len(table)}; columns={len(table.columns)}; "
        f"assessments={table['Assessment'].value_counts().to_dict()}; "
        "han_character_cells=0"
    )


if __name__ == "__main__":
    main()
