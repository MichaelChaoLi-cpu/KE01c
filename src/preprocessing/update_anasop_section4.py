#!/usr/bin/env python3
"""Update AnaSOP Section 4 from confirmed preprocessing decisions."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "data/exp/data-preprocessing/decisions.json"
ANASOP = ROOT / "docs/AnaSOP.md"
SECTION = "## 4. Variable Construction  /  Key Variables"


def role_for(name: str) -> str:
    lower = name.casefold()
    if "population" in lower or "household" in lower:
        return "exposure / vulnerability"
    if "building" in lower:
        return "spread explanatory"
    if "road" in lower or "route" in lower or "vertical level" in lower or "width category" in lower:
        return "accessibility explanatory"
    if "fire base" in lower or "dispatch base" in lower:
        return "response supply"
    if any(token in lower for token in ["hospital", "medical", "welfare", "school", "shelter", "evacuation", "public facility"]):
        return "critical-facility exposure"
    if any(token in lower for token in ["hazard", "warning zone", "disruption", "water outage", "power outage"]):
        return "scenario input"
    if "geometry" in lower:
        return "spatial key"
    if "municipality" in lower or lower.endswith(" id") or lower.endswith(" code"):
        return "identifier / reporting key"
    return "supporting explanatory"


def input_definition(name: str) -> str:
    definitions = {
        "Population Age 65+ Share": r"\(PopulationAge65Plus / TotalPopulation\).",
        "Population Age 75+ Share": r"\(PopulationAge75Plus / TotalPopulation\).",
        "Population Age 85+ Share": r"\(PopulationAge85Plus / TotalPopulation\).",
        "Older Single-Person Household Share": r"\(OlderSinglePersonHouseholds / TotalHouseholds\).",
        "Older Couple Household Share": r"\(OlderCoupleHouseholds / TotalHouseholds\).",
        "Candidate Dispatch Base": "Boolean source classification used to retain eligible Shapley players.",
        "Building Area (m2)": "Source building-footprint area in square metres.",
        "Geometry": "Spatial geometry with active GeoParquet metadata and a declared CRS.",
    }
    return definitions.get(name, "Source-defined value retained without numerical transformation or missing-value imputation.")


def construction_for(name: str) -> str:
    if name == "Geometry":
        return "Active geometry retained; source CRS preserved, with MLIT logical layers harmonized to EPSG:6668."
    if name == "Candidate Dispatch Base":
        return "Retain source Boolean; 81 of 94 facility records are eligible candidate dispatch bases."
    return "Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields."


def markdown_safe(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_section(decisions: dict[str, object]) -> str:
    unique_inputs: OrderedDict[str, dict[str, str]] = OrderedDict()
    configs = [*decisions.get("datasets", {}).values(), *decisions.get("logical_layers", {}).values()]
    for config in configs:
        for variable in config.get("variables", []):
            if variable.get("is_final_variable") != "yes":
                continue
            name = str(variable["readable_name"])
            unique_inputs.setdefault(
                name,
                {
                    "variable_name": name,
                    "full_name": str(variable.get("full_name") or name),
                    "role": role_for(name),
                    "formal_definition": input_definition(name),
                    "construction_or_coding": construction_for(name),
                    "is_final_variable": "yes",
                },
            )

    derived_rows = [
        {
            "variable_name": str(row["readable_name"]),
            "full_name": str(row["full_name"]),
            "role": str(row["role"]),
            "formal_definition": str(row["formal_definition"]),
            "construction_or_coding": str(row["construction_or_coding"]),
            "is_final_variable": str(row["is_final_variable"]),
        }
        for row in decisions.get("derived_variables", [])
    ]
    rows = list(unique_inputs.values()) + derived_rows
    lines = [
        SECTION,
        "",
        "The table separates standardized source inputs from planned derived analysis variables. "
        "Repeated readable names used consistently across spatial layers are documented once.",
        "",
        "| variable_name | full_name | role | formal_definition | construction_or_coding | is_final_variable |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| " + " | ".join(
                markdown_safe(row[key])
                for key in [
                    "variable_name",
                    "full_name",
                    "role",
                    "formal_definition",
                    "construction_or_coding",
                    "is_final_variable",
                ]
            ) + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    text = ANASOP.read_text(encoding="utf-8")
    section = build_section(decisions)
    if SECTION in text:
        start = text.index(SECTION)
        next_section = text.find("\n## ", start + len(SECTION))
        end = len(text) if next_section == -1 else next_section + 1
        text = text[:start] + section + ("" if end == len(text) else text[end:])
    else:
        text = text.rstrip() + "\n\n" + section
    ANASOP.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"Updated {ANASOP.relative_to(ROOT)} with {section.count(chr(10)) - 6} variable rows")


if __name__ == "__main__":
    main()
