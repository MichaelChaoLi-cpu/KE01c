#!/usr/bin/env python3
"""Supplement the generic feasibility check for GeoParquet/GeoJSON inputs."""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "data" / "exp" / "feasibility-check"
MAX_VALIDITY_SAMPLE = 100_000
PROJECTED_CRS = "EPSG:6670"  # JGD2011 / Japan Plane Rectangular CS II


CORE_DATASETS = {
    "buildings": (
        "data/raw/prior_projects/KE01/kumamoto_gsi_buildings_z15_preprocessed.parquet",
        "conditional spread morphology",
    ),
    "population_125m": (
        "data/raw/prior_projects/KE01/kumamoto_population_mesh_125m_preprocessed.parquet",
        "population-weighted demand",
    ),
    "roads": (
        "data/raw/prior_projects/KE01b/kumamoto_road_centerlines_2024_preprocessed.parquet",
        "response routing and disruption",
    ),
    "emergency_roads": (
        "data/raw/prior_projects/KE01b/kumamoto_emergency_transport_roads_2024_preprocessed.parquet",
        "restoration candidates and route priority",
    ),
    "fire_stations": (
        "data/raw/prior_projects/KE01b/kumamoto_fire_stations_2012_preprocessed.parquet",
        "candidate response bases",
    ),
    "administrative_areas": (
        "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet",
        "reporting and clipping",
    ),
    "landslide_zones": (
        "data/raw/prior_projects/KE01b/kumamoto_landslide_warning_zones_2025_preprocessed.parquet",
        "bounded road-disruption scenarios",
    ),
    "shelters": (
        "data/raw/prior_projects/KE01/kumamoto_designated_shelters_geospatial_preprocessed.parquet",
        "critical-facility exposure",
    ),
    "medical_facilities": (
        "data/raw/prior_projects/KE01/kumamoto_mlit_medical_institutions_preprocessed.parquet",
        "critical-facility exposure",
    ),
    "welfare_facilities": (
        "data/raw/prior_projects/KE01/kumamoto_mlit_welfare_facilities_preprocessed.parquet",
        "vulnerable-facility exposure",
    ),
    "schools": (
        "data/raw/prior_projects/KE01/kumamoto_mlit_schools_preprocessed.parquet",
        "critical-facility exposure",
    ),
}


def read_vector(path: Path) -> gpd.GeoDataFrame:
    if path.suffix.lower() == ".parquet":
        return gpd.read_parquet(path)
    return gpd.read_file(path)


def sampled_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    geometry = gdf.geometry.dropna()
    if len(geometry) <= MAX_VALIDITY_SAMPLE:
        return geometry
    step = len(geometry) / MAX_VALIDITY_SAMPLE
    positions = [min(int(i * step), len(geometry) - 1) for i in range(MAX_VALIDITY_SAMPLE)]
    return geometry.iloc[positions]


def summarize_vector(key: str, path: Path, role: str) -> dict[str, object]:
    try:
        gdf = read_vector(path)
        geometry = gdf.geometry
        sample = sampled_geometry(gdf)
        bounds = gdf.total_bounds if len(gdf) else [math.nan] * 4
        non_geometry = [str(column) for column in gdf.columns if column != gdf.geometry.name]
        return {
            "dataset": key,
            "source_file": str(path.relative_to(ROOT)),
            "role": role,
            "status": "readable",
            "rows": len(gdf),
            "columns": len(gdf.columns),
            "crs": str(gdf.crs),
            "geometry_types": "|".join(sorted(set(geometry.geom_type.dropna().astype(str)))),
            "missing_geometry": int(geometry.isna().sum()),
            "empty_geometry": int(geometry.is_empty.sum()),
            "validity_sample_n": len(sample),
            "invalid_in_sample": int((~sample.is_valid).sum()),
            "min_x": bounds[0],
            "min_y": bounds[1],
            "max_x": bounds[2],
            "max_y": bounds[3],
            "available_fields": "|".join(non_geometry),
            "error": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "dataset": key,
            "source_file": str(path.relative_to(ROOT)),
            "role": role,
            "status": "unreadable",
            "rows": 0,
            "columns": 0,
            "crs": "",
            "geometry_types": "",
            "missing_geometry": "",
            "empty_geometry": "",
            "validity_sample_n": 0,
            "invalid_in_sample": "",
            "min_x": "",
            "min_y": "",
            "max_x": "",
            "max_y": "",
            "available_fields": "",
            "error": str(exc),
        }


class UnionFind:
    def __init__(self) -> None:
        self.parent: list[int] = []
        self.size: list[int] = []

    def add(self) -> int:
        node = len(self.parent)
        self.parent.append(node)
        self.size.append(1)
        return node

    def find(self, node: int) -> int:
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.size[left_root] < self.size[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        self.size[left_root] += self.size[right_root]


def line_parts(geometry: object):
    if geometry is None or geometry.is_empty:
        return
    if geometry.geom_type == "LineString":
        yield geometry
    elif geometry.geom_type == "MultiLineString":
        yield from geometry.geoms


def endpoint_topology(roads: gpd.GeoDataFrame) -> dict[str, object]:
    geographic = bool(roads.crs and roads.crs.is_geographic)
    decimals = 5 if geographic else 1
    node_ids: dict[tuple[float, float], int] = {}
    union_find = UnionFind()
    edge_count = 0
    skipped_parts = 0

    def node_id(coordinate: tuple[float, ...]) -> int:
        key = (round(float(coordinate[0]), decimals), round(float(coordinate[1]), decimals))
        if key not in node_ids:
            node_ids[key] = union_find.add()
        return node_ids[key]

    for geometry in roads.geometry:
        found_part = False
        for part in line_parts(geometry):
            found_part = True
            coordinates = list(part.coords)
            if len(coordinates) < 2:
                skipped_parts += 1
                continue
            union_find.union(node_id(coordinates[0]), node_id(coordinates[-1]))
            edge_count += 1
        if not found_part:
            skipped_parts += 1

    roots = [union_find.find(node) for node in range(len(union_find.parent))]
    component_sizes: dict[int, int] = {}
    for root in roots:
        component_sizes[root] = component_sizes.get(root, 0) + 1
    largest = max(component_sizes.values(), default=0)
    return {
        "road_features": len(roads),
        "line_parts": edge_count,
        "endpoint_nodes": len(node_ids),
        "endpoint_components": len(component_sizes),
        "largest_component_nodes": largest,
        "largest_component_node_share": largest / len(node_ids) if node_ids else 0,
        "endpoint_rounding_decimals": decimals,
        "skipped_parts": skipped_parts,
        "interpretation": "Endpoint connectivity is a screening diagnostic; intersections still require explicit noding.",
    }


def station_snap_metrics(roads: gpd.GeoDataFrame, stations: gpd.GeoDataFrame) -> dict[str, object]:
    road_geometry = gpd.GeoSeries(roads.geometry.dropna(), crs=roads.crs).to_crs(PROJECTED_CRS)
    station_geometry = gpd.GeoSeries(stations.geometry.dropna(), crs=stations.crs).to_crs(PROJECTED_CRS)
    tree = STRtree(road_geometry.array)
    distances: list[float] = []
    for station in station_geometry.array:
        nearest_index = int(tree.nearest(station))
        distances.append(float(shapely.distance(station, road_geometry.array[nearest_index])))
    series = pd.Series(distances, dtype="float64")
    return {
        "stations_with_geometry": len(series),
        "nearest_road_distance_min_m": series.min(),
        "nearest_road_distance_median_m": series.median(),
        "nearest_road_distance_p90_m": series.quantile(0.9),
        "nearest_road_distance_max_m": series.max(),
        "stations_within_50m": int((series <= 50).sum()),
        "stations_within_100m": int((series <= 100).sum()),
        "stations_within_500m": int((series <= 500).sum()),
    }


def question_assessment(candidate_station_count: int, station_record_count: int) -> pd.DataFrame:
    rows = [
        {
            "id": "RQ1",
            "status": "partly-testable",
            "supported_components": "buildings|population|roads|stations|land use|firebreaks|critical facilities|event context",
            "unresolved_components": "observed road passability|hydrant and water-network function|station-level vehicles and staffing",
            "interpretation": "Supports conditional consequence and nominal accessibility, not actual operational capacity.",
            "next_check": "Integrate the core layers on a common grid and define alternative system value functions.",
        },
        {
            "id": "RQ2",
            "status": "partly-testable",
            "supported_components": "building geometry|125 m population|urban land use|roads|parks|water and open-space firebreaks",
            "unresolved_components": "building material and age|verified building damage|calibrated ignition probabilities|event-window wind",
            "interpretation": "Supports relative conditional spread susceptibility and consequence, not calibrated building fire probability.",
            "next_check": "Construct morphology and firebreak variables and test alternative grid and ignition definitions.",
        },
        {
            "id": "RQ3",
            "status": "partly-testable",
            "supported_components": "road centerlines|road class and width|emergency routes|stations|secondary-hazard zones",
            "unresolved_components": "observed travel speed|verified 2026 closures|bridge-level damage|dispatch records",
            "interpretation": "Supports bounded network-disruption scenarios and nominal travel-time change.",
            "next_check": "Create explicit intersections, validate connected components, snap stations, and document speed assumptions.",
        },
        {
            "id": "RQ4",
            "status": "partly-testable",
            "supported_components": f"{candidate_station_count} candidate dispatch bases among {station_record_count} facility records|road network|population demand|critical facilities|conditional consequence weights",
            "unresolved_components": "current station roster|station-level capacity|mutual-aid rules|actual dispatch availability",
            "interpretation": "Supports accessibility-based Shapley value only; does not support total operational station value.",
            "next_check": "Benchmark leave-one-out and sampled-permutation values under multiple transparent objectives.",
        },
        {
            "id": "RQ5",
            "status": "weakly-testable",
            "supported_components": "candidate station locations|road restoration candidates|population and facility demand|scenario risk outputs",
            "unresolved_components": "realistic intervention budgets|candidate temporary water sites|costs|vehicle and crew constraints",
            "interpretation": "Road restoration and abstract unit pre-positioning can be compared; water recommendations remain illustrative.",
            "next_check": "Confirm intervention budgets and defer location-specific water optimization unless source feasibility is verified.",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, object]] = []
    for key, (relative_path, role) in CORE_DATASETS.items():
        summaries.append(summarize_vector(key, ROOT / relative_path, role))

    for path in sorted((ROOT / "data/raw/mlit_ksj/fire_screening/extracted").glob("**/*_bouka.geojson")):
        summaries.append(summarize_vector(f"fire_prevention_{path.stem}", path, "fire-prevention zoning"))
    for path in sorted((ROOT / "data/raw/mlit_ksj/fire_screening/extracted").glob("**/*.shp")):
        summaries.append(summarize_vector(f"urban_land_use_{path.stem}", path, "100 m urban land-use screening"))

    availability = pd.DataFrame(summaries)
    availability.to_csv(OUTPUT_DIR / "geospatial_dataset_availability.csv", index=False)

    roads = gpd.read_parquet(ROOT / CORE_DATASETS["roads"][0])
    stations = gpd.read_parquet(ROOT / CORE_DATASETS["fire_stations"][0])
    candidate_mask = stations["Candidate Dispatch Base"].fillna(False).astype(bool)
    candidate_stations = stations.loc[candidate_mask].copy()
    topology = endpoint_topology(roads)
    snap = station_snap_metrics(roads, candidate_stations)
    snap["station_records_total"] = len(stations)
    snap["candidate_dispatch_bases"] = len(candidate_stations)
    snap["unique_station_coordinates_total"] = int(stations.geometry.to_wkb().nunique())
    network = pd.DataFrame([{**topology, **snap}])
    network.to_csv(OUTPUT_DIR / "network_feasibility.csv", index=False)

    population_rows = int(availability.loc[availability["dataset"] == "population_125m", "rows"].iloc[0])
    building_rows = int(availability.loc[availability["dataset"] == "buildings", "rows"].iloc[0])
    station_record_rows = int(availability.loc[availability["dataset"] == "fire_stations", "rows"].iloc[0])
    station_rows = len(candidate_stations)
    od_pairs = population_rows * station_rows
    scale = pd.DataFrame(
        [
            {
                "building_features": building_rows,
                "population_demand_cells": population_rows,
                "candidate_fire_facilities": station_rows,
                "station_demand_pairs_per_scenario": od_pairs,
                "float32_od_matrix_mib": od_pairs * 4 / (1024**2),
                "assessment": "Prefecture-wide grid screening is tractable; building-level spread simulation should be restricted to priority clusters.",
            }
        ]
    )
    scale.to_csv(OUTPUT_DIR / "computational_scale.csv", index=False)

    questions = question_assessment(station_rows, station_record_rows)
    questions.to_csv(OUTPUT_DIR / "question_feasibility_geospatial.csv", index=False)

    readable = int((availability["status"] == "readable").sum())
    invalid = int(pd.to_numeric(availability["invalid_in_sample"], errors="coerce").fillna(0).sum())
    status_counts = questions["status"].value_counts().to_dict()
    readme = f"""# Geospatial Feasibility Supplement

The generic feasibility checker supports CSV, TSV, and text files only. Its zero-dataset
result is a format-coverage limitation and must not be interpreted as absence of project data.

## Evidence inspected

- Geospatial sources readable: {readable} of {len(availability)}
- Geometry validity observations checked: up to {MAX_VALIDITY_SAMPLE:,} per source
- Invalid geometries in all validity samples: {invalid:,}
- Road features: {topology['road_features']:,}
- Candidate fire facilities: {station_rows:,}
- Populated 125 m demand cells: {population_rows:,}
- Building features: {building_rows:,}
- Station-demand pairs per scenario: {od_pairs:,}

## Network screening

- Endpoint components before explicit intersection noding: {topology['endpoint_components']:,}
- Largest endpoint component share: {topology['largest_component_node_share']:.3f}
- Median station-to-road snap distance: {snap['nearest_road_distance_median_m']:.1f} m
- 90th percentile station-to-road snap distance: {snap['nearest_road_distance_p90_m']:.1f} m
- Stations within 100 m of a road feature: {snap['stations_within_100m']} of {snap['stations_with_geometry']}

Endpoint connectivity is a diagnostic, not a finished routing graph. Intersections must be
explicitly noded and normal-condition routes must be validated before disruption results are used.

## Question assessment

- Partly testable: {status_counts.get('partly-testable', 0)}
- Weakly testable: {status_counts.get('weakly-testable', 0)}
- Not yet testable after geospatial review: {status_counts.get('not-yet-testable', 0)}

The current data support conditional fire-consequence screening, nominal network accessibility,
and accessibility-based station valuation. They do not support calibrated building ignition
probabilities, observed 2026 road performance, actual station capacity, or location-specific
water-supply optimization.

## Recommendation

Proceed to data preprocessing, but treat network construction and station verification as gating
checks. Keep the resource-allocation question partially deferred: road restoration and abstract
unit pre-positioning are feasible, while specific temporary-water recommendations require new
source evidence or explicitly illustrative scenarios.
"""
    (OUTPUT_DIR / "README_geospatial.md").write_text(readme, encoding="utf-8")

    print(
        pd.Series(
            {
                "geospatial_sources": len(availability),
                "readable_sources": readable,
                "questions_partly_testable": status_counts.get("partly-testable", 0),
                "questions_weakly_testable": status_counts.get("weakly-testable", 0),
                "recommended_next_skill": "data-preprocessing",
            }
        ).to_json()
    )


if __name__ == "__main__":
    main()
