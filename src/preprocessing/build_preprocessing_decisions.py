#!/usr/bin/env python3
"""Build the human-confirmed first-pass preprocessing decisions."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
VARIABLE_LIST = ROOT / "data/exp/data-preprocessing/variable_list.csv"
DECISIONS_PATH = ROOT / "data/exp/data-preprocessing/decisions.json"


def field(
    original: str,
    readable: str | None = None,
    *,
    final: bool = True,
    full: str | None = None,
) -> dict[str, object]:
    readable_name = readable or original
    full_name = full or readable_name.replace(" ID", " Identifier")
    return {
        "original_name": original,
        "readable_name": readable_name,
        "full_name": full_name,
        "is_final_variable": "yes" if final else "no",
    }


SOURCES: dict[str, dict[str, object]] = {
    "data/raw/prior_projects/KE01/kumamoto_damage_evidence_registry_preprocessed.parquet": {
        "slug": "earthquake_damage_evidence_reference",
        "fields": [
            field("Evidence ID", final=False),
            field("Event ID", final=False),
            field("Observation Time", final=False),
            field("Municipality", final=False),
            field("Latitude", final=False),
            field("Longitude", final=False),
            field("Coordinate Precision", final=False),
            field("Coordinate Uncertainty m", "Coordinate Uncertainty (m)", final=False),
            field("Evidence Tier", final=False),
            field("Verification Status", final=False),
            field("Asset Type", final=False),
            field("Observed Damage Type", final=False),
            field("Structural Damage Class", final=False),
            field("Reported Affected Asset Count", final=False),
            field("Place Description", final=False),
            field("Source Organization", final=False),
            field("Source Type", final=False),
            field("Source Report Number", final=False),
            field("Source Page", final=False),
            field("Source URL", final=False),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_designated_shelters_geospatial_preprocessed.parquet": {
        "slug": "designated_shelters",
        "fields": [
            field("Common ID", "Shelter ID", full="Shelter Identifier"),
            field("Facility Name", "Shelter Name", final=False),
            field("Same Address as Emergency Evacuation Site"),
            field("Accepted Persons", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_emergency_evacuation_sites_geospatial_preprocessed.parquet": {
        "slug": "emergency_evacuation_sites",
        "fields": [
            field("Common ID", "Evacuation Site ID", full="Evacuation Site Identifier"),
            field("Facility Name", "Evacuation Site Name", final=False),
            field("Earthquake", "Earthquake Designation"),
            field("Large-Scale Fire", "Large-Scale Fire Designation"),
            field("Same Address as Designated Shelter"),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_gsi_buildings_z15_preprocessed.parquet": {
        "slug": "buildings",
        "fields": [
            field("Building ID", full="Building Identifier"),
            field("Feature Code", "Building Feature Code"),
            field("Building Area m2", "Building Area (m2)"),
            field("Crosses Nominal Tile Boundary", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_housing_damage_snapshots_preprocessed.parquet": {
        "slug": "housing_damage_reference",
        "fields": [
            field("Snapshot ID", final=False),
            field("Observation Time", final=False),
            field("Geographic Level", final=False),
            field("Municipality", final=False),
            field("Full Collapse Buildings", final=False),
            field("Half Collapse Buildings", final=False),
            field("Partial Damage Buildings", final=False),
            field("Reported Affected Buildings", final=False),
            field("Data Status", final=False),
            field("Source Organization", final=False),
            field("Source Report Number", final=False),
            field("Source URL", final=False),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_mlit_medical_institutions_preprocessed.parquet": {
        "slug": "medical_facilities",
        "fields": [
            field("Support Facility ID", "Medical Facility ID", full="Medical Facility Identifier"),
            field("Facility Name", "Medical Facility Name", final=False),
            field("Medical Institution Class"),
            field("Bed Count"),
            field("Emergency Hospital Designation"),
            field("Disaster Base Hospital Class"),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_mlit_public_offices_halls_preprocessed.parquet": {
        "slug": "public_facilities",
        "fields": [
            field("Support Facility ID", "Public Facility ID", full="Public Facility Identifier"),
            field("Facility Class", "Public Facility Class"),
            field("Facility Name", "Public Facility Name", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_mlit_schools_preprocessed.parquet": {
        "slug": "schools",
        "fields": [
            field("Support Facility ID", "School Facility ID", full="School Facility Identifier"),
            field("School Code"),
            field("School Class"),
            field("Facility Name", "School Name", final=False),
            field("Suspension Status"),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_mlit_welfare_facilities_preprocessed.parquet": {
        "slug": "welfare_facilities",
        "fields": [
            field("Support Facility ID", "Welfare Facility ID", full="Welfare Facility Identifier"),
            field("Welfare Facility Major Class"),
            field("Welfare Facility Medium Class"),
            field("Welfare Facility Minor Class"),
            field("Facility Name", "Welfare Facility Name", final=False),
            field("Position Accuracy", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_population_disclosure_groups_preprocessed.parquet": {
        "slug": "population_disclosure_groups",
        "fields": [
            field("Disclosure Group Code"),
            field("geometry", "Geometry"),
            field("Disclosure Group Size"),
            field("Suppressed Source Mesh Count", final=False),
            field("Total Population"),
            field("Total Households"),
            field("General Households"),
            field("Population Age 65+"),
            field("Population Age 75+"),
            field("Population Age 85+"),
            field("One-Person Households"),
            field("Households with Member Age 65+"),
            field("Older Single-Person Households"),
            field("Older Couple Households"),
            field("Population Age 65+ Share"),
            field("Population Age 75+ Share"),
            field("Population Age 85+ Share"),
            field("Older Single-Person Household Share"),
            field("Older Couple Household Share"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_population_mesh_125m_preprocessed.parquet": {
        "slug": "population_mesh_125m",
        "fields": [
            field("Mesh Code"),
            field("geometry", "Geometry"),
            field("Disclosure Group Code"),
            field("Disclosure Group Size"),
            field("Disclosure Status"),
            field("Aggregation Destination Mesh Code"),
            field("Aggregated Source Mesh Codes"),
            field("Total Population"),
            field("Total Households"),
            field("General Households"),
        ],
    },
    "data/raw/prior_projects/KE01/kumamoto_service_disruption_snapshots_preprocessed.parquet": {
        "slug": "service_disruptions",
        "fields": [
            field("Disruption Snapshot ID", final=False),
            field("Observation Time", final=False),
            field("Geographic Level"),
            field("Municipality"),
            field("Disruption Type"),
            field("Service Status"),
            field("Reported Municipality Count"),
            field("Reported Affected Households"),
            field("Reported Affected People"),
            field("Observed Power Outage Customers"),
            field("Observed Water Outage Households"),
            field("Evidence Tier"),
            field("Verification Status"),
            field("Source Organization", final=False),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet": {
        "slug": "administrative_areas",
        "fields": [
            field("Municipality Code"),
            field("Municipality Name"),
            field("Ward Name"),
            field("Municipality Label"),
            field("Geometry"),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_emergency_transport_roads_2024_preprocessed.parquet": {
        "slug": "emergency_transport_roads",
        "fields": [
            field("Emergency Road Class Code"),
            field("Road Type Code", "Emergency Road Type Code"),
            field("Route Name", final=False),
            field("Route ID", full="Route Identifier"),
            field("Branch ID", full="Branch Identifier"),
            field("Service Status", "Emergency Road Service Status"),
            field("Geometry"),
            field("Emergency Road Class"),
            field("Road Type", "Emergency Road Type"),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_fire_jurisdictions_2012_preprocessed.parquet": {
        "slug": "fire_jurisdictions_reference",
        "fields": [
            field("Fire Station Name", final=False),
            field("Jurisdiction Area 1", "Jurisdiction Area", final=False),
            field("Geometry", final=False),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_fire_organization_validation_2024_preprocessed.parquet": {
        "slug": "fire_organization_reference",
        "fields": [
            field("Prefecture Name", final=False),
            field("Fire Headquarters Total", final=False),
            field("Municipal Headquarters", final=False),
            field("Joint Headquarters", final=False),
            field("Fire Stations", final=False),
            field("Fire Outposts", final=False),
            field("Fire Service Personnel", final=False),
            field("Volunteer Fire Corps", final=False),
            field("Volunteer Fire Divisions", final=False),
            field("Volunteer Firefighters", final=False),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_fire_stations_2012_preprocessed.parquet": {
        "slug": "fire_dispatch_bases",
        "fields": [
            field("Fire Facility Name", "Fire Base Name"),
            field("Municipality Code"),
            field("Fire Facility Type Code", "Fire Base Type Code"),
            field("Address", "Fire Base Address", final=False),
            field("Geometry"),
            field("Fire Facility Type", "Fire Base Type"),
            field("Candidate Dispatch Base"),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_landslide_warning_zones_2025_preprocessed.parquet": {
        "slug": "landslide_zones",
        "fields": [
            field("Hazard Type Code"),
            field("Warning Zone Class Code"),
            field("Zone ID", full="Zone Identifier"),
            field("Special Warning Zone Pending Code"),
            field("Geometry"),
            field("Hazard Type"),
            field("Warning Zone Class"),
            field("Special Warning Zone Pending"),
        ],
    },
    "data/raw/prior_projects/KE01b/kumamoto_road_centerlines_2024_preprocessed.parquet": {
        "slug": "road_centerlines",
        "fields": [
            field("Road Centerline Type Code"),
            field("Road Category Code"),
            field("Road State Code"),
            field("Vertical Level"),
            field("Width Category Code"),
            field("Toll Category Code", final=False),
            field("Secondary Mesh Code", final=False),
            field("Geometry"),
            field("Road Centerline Type"),
            field("Road Category"),
            field("Road State"),
            field("Width Category"),
            field("Toll Category", final=False),
        ],
    },
}


LOGICAL_LAYERS: dict[str, dict[str, object]] = {
    "mlit_a55_fire_prevention_zones": {
        "source_glob": "data/raw/mlit_ksj/fire_screening/extracted/**/*_bouka.geojson",
        "output": "data/processed/mlit_fire_prevention_zones_preprocessed.parquet",
        "fields": [
            field("AreaType", "Fire Prevention Area Type"),
            field("AreaCode", "Fire Prevention Area Code"),
            field("Pref", "Prefecture Name", final=False),
            field("Citycode", "Municipality Code"),
            field("Cityname", "Municipality Name", final=False),
            field("INDate", "Initial Decision Date", final=False),
            field("FNDate", "Final Decision Date", final=False),
            field("ValidType", "Validity Type", final=False),
            field("Custodian", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "mlit_a55_land_use_zones": {
        "source_glob": "data/raw/mlit_ksj/fire_screening/extracted/**/*_youto.geojson",
        "output": "data/processed/mlit_land_use_zones_preprocessed.parquet",
        "fields": [
            field("YoutoName", "Land Use Zone Name"),
            field("YoutoCode", "Land Use Zone Code"),
            field("FAR", "Floor Area Ratio"),
            field("BCR", "Permitted Building Coverage Ratio"),
            field("Citycode", "Municipality Code"),
            field("Cityname", "Municipality Name", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "mlit_a55_urban_parks": {
        "source_glob": "data/raw/mlit_ksj/fire_screening/extracted/**/*_kouen.geojson",
        "output": "data/processed/mlit_urban_parks_preprocessed.parquet",
        "fields": [
            field("ParkName", "Park Name", final=False),
            field("ParkType", "Park Type"),
            field("ParkCode", "Park Code"),
            field("Citycode", "Municipality Code"),
            field("Cityname", "Municipality Name", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "mlit_a55_planned_roads": {
        "source_glob": "data/raw/mlit_ksj/fire_screening/extracted/**/*_douro.geojson",
        "output": "data/processed/mlit_planned_roads_preprocessed.parquet",
        "fields": [
            field("DouroType", "Planned Road Type"),
            field("DouroCode", "Planned Road Code"),
            field("Citycode", "Municipality Code"),
            field("Cityname", "Municipality Name", final=False),
            field("geometry", "Geometry"),
        ],
    },
    "mlit_l03_urban_land_use_100m": {
        "source_glob": "data/raw/mlit_ksj/fire_screening/extracted/**/*.shp",
        "output": "data/processed/mlit_urban_land_use_100m_preprocessed.parquet",
        "fields": [
            field("L03b_u_001", "Urban Land Use Mesh Code"),
            field("L03b_u_002", "Urban Land Use Code"),
            field("L03b_u_003", "Source Reference Date", final=False),
            field("geometry", "Geometry"),
        ],
    },
}


DERIVED_VARIABLES: list[dict[str, str]] = [
    {
        "readable_name": "Building Count",
        "full_name": "Building Count per Analysis Cell",
        "role": "spread explanatory",
        "formal_definition": r"\(N_j = \sum_b 1(c_b \in j)\), where \(c_b\) is the building centroid; robustness to area-weighted allocation is required.",
        "construction_or_coding": "Planned from building geometry on the 125 m analysis grid.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Observed Building Footprint Coverage Ratio",
        "full_name": "Observed Building Footprint Coverage Ratio",
        "role": "spread explanatory",
        "formal_definition": r"\(BCR_j = \sum_b Area(b \cap j) / Area(j)\).",
        "construction_or_coding": "Planned area-weighted overlay of building footprints and analysis cells.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Mean Building Separation (m)",
        "full_name": "Mean Nearest-Building Boundary Separation",
        "role": "spread explanatory",
        "formal_definition": r"Mean nearest-neighbor boundary distance among buildings assigned to or neighboring cell \(j\).",
        "construction_or_coding": "Planned in projected coordinates; neighborhood buffer is TBD.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Built Continuity Index",
        "full_name": "Local Built-Form Continuity Index",
        "role": "spread explanatory",
        "formal_definition": r"Relative connectivity of buildings under a separation threshold \(d\); the final graph statistic and \(d\) are TBD.",
        "construction_or_coding": "Planned building-adjacency sensitivity measure.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Firebreak Share",
        "full_name": "Road, Park, Water, and Open-Space Firebreak Share",
        "role": "spread protective",
        "formal_definition": r"\(F_j = Area(Firebreak \cap j) / Area(j)\); road-buffer definitions are TBD.",
        "construction_or_coding": "Planned overlay of roads, parks, water/open-space land use, and relevant planning polygons.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Conditional Spread Susceptibility",
        "full_name": "Conditional Fire-Spread Susceptibility",
        "role": "intermediate outcome",
        "formal_definition": r"\(S_j(\omega) = f(Density_j, Separation_j, Continuity_j, LandUse_j, Firebreak_j, \omega)\); function \(f\) is TBD.",
        "construction_or_coding": "Scenario score conditional on imposed ignition; not an ignition probability.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Normal Response Time (min)",
        "full_name": "Normal-Scenario Minimum Fire-Service Travel Time",
        "role": "accessibility outcome",
        "formal_definition": r"\(T_j^0 = \min_{i \in N} t_{ij}^0\).",
        "construction_or_coding": "Planned shortest-path time from candidate dispatch bases under the normal network scenario.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Disrupted Response Time (min)",
        "full_name": "Disruption-Scenario Minimum Fire-Service Travel Time",
        "role": "accessibility outcome",
        "formal_definition": r"\(T_j(\omega) = \min_{i \in N(\omega)} t_{ij}(\omega)\).",
        "construction_or_coding": "Planned shortest-path time after stated link or base disruptions.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Backup Fire Base Count",
        "full_name": "Number of Alternative Candidate Dispatch Bases",
        "role": "accessibility redundancy",
        "formal_definition": r"\(B_j(\omega) = \sum_i 1(t_{ij}(\omega) \leq \tau) - 1\); threshold \(\tau\) is TBD.",
        "construction_or_coding": "Planned count of bases beyond the nearest base that meet a stated response threshold.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Single Route Dependence",
        "full_name": "Single-Route Dependence Indicator",
        "role": "accessibility vulnerability",
        "formal_definition": "TBD: indicator or proportion based on loss of feasible alternatives after removal of a critical route segment.",
        "construction_or_coding": "Planned from the explicitly noded road graph.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Water Constraint Scenario",
        "full_name": "Bounded Firefighting Water-Availability Scenario",
        "role": "scenario input",
        "formal_definition": "Categorical boundary scenario; location-specific hydrant functionality is not observed.",
        "construction_or_coding": "At minimum: normal reliance and affected-area network-water-unavailable scenarios.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Conditional Fire Consequence",
        "full_name": "Weighted Conditional Fire Consequence",
        "role": "main outcome",
        "formal_definition": r"\(C_j(S, \omega) = g(Spread_j(\omega), Access_j(S, \omega), Water_j(\omega), Exposure_j)\); function \(g\) is TBD.",
        "construction_or_coding": "Scenario-based consequence conditional on ignition, not calibrated building fire probability.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Leave-One-Out Fire Base Value",
        "full_name": "Leave-One-Out Candidate Dispatch-Base Value",
        "role": "station value outcome",
        "formal_definition": r"\(V_i^{LOO}(\omega) = J(N \setminus \{i\}, \omega) - J(N, \omega)\).",
        "construction_or_coding": "Planned transparent criticality benchmark under each scenario and system objective.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Scenario Shapley Value",
        "full_name": "Scenario-Specific Candidate Dispatch-Base Shapley Value",
        "role": "station value outcome",
        "formal_definition": r"Average marginal system-value contribution of base \(i\) across feasible base coalitions under scenario \(\omega\).",
        "construction_or_coding": "Planned sampled-permutation estimate with convergence checks.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Robust Fire Base Value",
        "full_name": "Scenario-Robust Candidate Dispatch-Base Value",
        "role": "station value outcome",
        "formal_definition": r"Central tendency and variability of \(\phi_i(\omega)\) across the declared scenario set.",
        "construction_or_coding": "Planned multi-scenario summary; no universal single-objective value is assumed.",
        "is_final_variable": "yes",
    },
    {
        "readable_name": "Intervention Benefit",
        "full_name": "Weighted Conditional-Consequence Reduction from Intervention",
        "role": "decision outcome",
        "formal_definition": r"\(Benefit_a(\omega) = J_0(\omega) - J_a(\omega)\).",
        "construction_or_coding": "Planned comparison with population-only, nearest-base, and road-class baselines.",
        "is_final_variable": "yes",
    },
]


def main() -> None:
    variable_list = pd.read_csv(VARIABLE_LIST, keep_default_na=False)
    available = {
        source: set(group["original_name"])
        for source, group in variable_list.groupby("source_dataset", sort=False)
    }
    decisions: dict[str, object] = {"datasets": {}, "logical_layers": {}, "derived_variables": DERIVED_VARIABLES}

    for source, config in SOURCES.items():
        if source not in available:
            raise ValueError(f"Source missing from variable list: {source}")
        fields = config["fields"]
        missing = [item["original_name"] for item in fields if item["original_name"] not in available[source]]
        if missing:
            raise ValueError(f"Variables missing from {source}: {missing}")

        dtype_map = variable_list.loc[variable_list["source_dataset"] == source].set_index("original_name")["dtype"]
        variables: list[dict[str, object]] = []
        for item in fields:
            original = str(item["original_name"])
            dtype = str(dtype_map.loc[original])
            preprocessing: list[str] = []
            if original.casefold() != "geometry" and dtype in {"string", "object"}:
                preprocessing.append("strip_whitespace")
            variables.append({**item, "preprocessing": preprocessing})

            selected = (variable_list["source_dataset"] == source) & (variable_list["original_name"] == original)
            variable_list.loc[selected, "readable_name"] = item["readable_name"]
            variable_list.loc[selected, "full_name"] = item["full_name"]
            variable_list.loc[selected, "is_final_variable"] = item["is_final_variable"]

        slug = str(config["slug"])
        decisions["datasets"][source] = {
            "output": f"data/processed/{slug}_preprocessed.parquet",
            "script": f"src/preprocessing/preprocess_{slug}.py",
            "variables": variables,
        }

    for layer_key, config in LOGICAL_LAYERS.items():
        decisions["logical_layers"][layer_key] = {
            "source_glob": config["source_glob"],
            "output": config["output"],
            "script": "src/preprocessing/preprocess_mlit_logical_layers.py",
            "variables": [
                {**item, "preprocessing": ["strip_whitespace"] if item["original_name"] != "geometry" else []}
                for item in config["fields"]
            ],
        }

    DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DECISIONS_PATH.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    variable_list.to_csv(VARIABLE_LIST, index=False)

    all_configs = [*decisions["datasets"].values(), *decisions["logical_layers"].values()]
    selected_count = sum(len(config["variables"]) for config in all_configs)
    final_count = sum(
        variable["is_final_variable"] == "yes"
        for config in all_configs
        for variable in config["variables"]
    )
    print(f"Wrote {DECISIONS_PATH.relative_to(ROOT)}")
    print(f"Datasets: {len(decisions['datasets'])}")
    print(f"Logical layers: {len(decisions['logical_layers'])}")
    print(f"Derived variables: {len(decisions['derived_variables'])}")
    print(f"Selected variables: {selected_count}")
    print(f"Final variables: {final_count}")


if __name__ == "__main__":
    main()
