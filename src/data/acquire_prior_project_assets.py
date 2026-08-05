#!/usr/bin/env python3
"""Copy reusable KE01/KE01b assets into KE01c without modifying source repos.

Sibling-project GeoParquet files are treated as immutable external inputs in
this project. The script copies regular files (never symlinks), verifies their
SHA-256 checksums, and writes a provenance manifest under data/raw.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "prior_projects"


@dataclass(frozen=True)
class Asset:
    source_project: str
    source_relative_path: str
    role: str
    reference_period: str
    limitation: str


ASSETS = (
    Asset(
        "KE01",
        "data/processed/kumamoto_population_mesh_125m_preprocessed.parquet",
        "Population exposure on populated 125 m census meshes.",
        "2020 Census",
        "Predates the 2026 earthquake and includes official disclosure handling.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_population_disclosure_groups_preprocessed.parquet",
        "Disclosure-safe total and older-population exposure groups.",
        "2020 Census",
        "Grouped geography must not be interpreted as exact household locations.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_gsi_buildings_z15_preprocessed.parquet",
        "Pre-event building footprints for density, spacing, and continuity measures.",
        "GSI vector map current 2026-04-01",
        "Mapped polygons are not dwellings, structural types, or damaged buildings.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_designated_shelters_geospatial_preprocessed.parquet",
        "Critical-facility and evacuation-context points.",
        "Snapshot acquired 2026-08-02",
        "Designation does not verify post-event opening or functionality.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_emergency_evacuation_sites_geospatial_preprocessed.parquet",
        "Emergency evacuation-site context.",
        "Snapshot acquired 2026-08-02",
        "Designation does not verify post-event opening or occupancy.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_service_disruption_snapshots_preprocessed.parquet",
        "Time-stamped 2026 service-disruption context.",
        "2026 event updates through 2026-08-02",
        "Observations are incomplete and reported at mixed spatial and temporal scales.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_damage_evidence_registry_preprocessed.parquet",
        "Geographically bounded 2026 damage evidence.",
        "2026 event updates through 2026-08-02",
        "Evidence coverage is selective rather than an exhaustive damage census.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_housing_damage_snapshots_preprocessed.parquet",
        "Official evolving housing-damage totals for event context and constraints.",
        "2026 event updates through 2026-08-01",
        "Preliminary totals lack complete small-area locations.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_mlit_medical_institutions_preprocessed.parquet",
        "Medical-facility exposure points.",
        "2020",
        "Does not verify post-event operation or emergency capacity.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_mlit_public_offices_halls_preprocessed.parquet",
        "Public-office and assembly-facility exposure points.",
        "2022",
        "Does not verify post-event operation or occupancy.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_mlit_schools_preprocessed.parquet",
        "School exposure points.",
        "2023",
        "Does not verify post-event operation or occupancy.",
    ),
    Asset(
        "KE01",
        "data/processed/kumamoto_mlit_welfare_facilities_preprocessed.parquet",
        "Welfare-facility exposure points.",
        "2023",
        "Does not verify post-event operation, occupancy, or resident vulnerability.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_administrative_areas_preprocessed.parquet",
        "Administrative boundaries for clipping and reporting.",
        "2025",
        "Boundary vintage differs from some other source layers.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_emergency_transport_roads_2024_preprocessed.parquet",
        "Emergency-road hierarchy and route context.",
        "2024",
        "Designation is not evidence that a segment remained passable after the event.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_fire_jurisdictions_2012_preprocessed.parquet",
        "Fire-service jurisdiction context.",
        "2012",
        "The roster is old and requires current validation.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_fire_organization_validation_2024_preprocessed.parquet",
        "Current aggregate validation of fire-service organization counts.",
        "2024",
        "Aggregate totals do not identify station-level vehicles or staffing.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_fire_stations_2012_preprocessed.parquet",
        "Candidate nominal fire-response bases.",
        "2012",
        "Locations and inclusion require current station-by-station verification.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_landslide_warning_zones_2025_preprocessed.parquet",
        "Road-disruption susceptibility and secondary-hazard context.",
        "2025",
        "Warning zones do not prove that individual roads failed in 2026.",
    ),
    Asset(
        "KE01b",
        "data/processed/kumamoto_road_centerlines_2024_preprocessed.parquet",
        "Road geometry and classes for constructing a routable response network.",
        "2024",
        "No ready-made node-link topology or observed travel-time field.",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_asset(asset: Asset, source_root: Path) -> dict[str, object]:
    source = source_root / asset.source_relative_path
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError(f"Expected regular source file: {source}")

    destination = RAW_ROOT / asset.source_project / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256(source)

    if destination.exists():
        if not destination.is_file() or destination.is_symlink():
            raise RuntimeError(f"Destination is not a regular file: {destination}")
        status = "existing"
    else:
        shutil.copy2(source, destination, follow_symlinks=False)
        status = "copied"

    destination_hash = sha256(destination)
    if destination_hash != source_hash:
        raise RuntimeError(f"Checksum mismatch after copy: {destination}")

    return {
        **asdict(asset),
        "source_path": str(source.resolve()),
        "destination_path": str(destination.relative_to(PROJECT_ROOT)),
        "bytes": destination.stat().st_size,
        "sha256": destination_hash,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ke01-root", type=Path, default=PROJECT_ROOT.parent / "KE01")
    parser.add_argument("--ke01b-root", type=Path, default=PROJECT_ROOT.parent / "KE01b")
    args = parser.parse_args()

    roots = {
        "KE01": args.ke01_root.expanduser().resolve(),
        "KE01b": args.ke01b_root.expanduser().resolve(),
    }
    records = [copy_asset(asset, roots[asset.source_project]) for asset in ASSETS]

    manifest = {
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "copy_policy": "Sources are read-only; KE01c stores independent regular-file copies.",
        "assets": records,
    }
    manifest_path = RAW_ROOT / "source_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    copied = sum(record["status"] == "copied" for record in records)
    existing = sum(record["status"] == "existing" for record in records)
    total_bytes = sum(int(record["bytes"]) for record in records)
    print(
        json.dumps(
            {
                "manifest": str(manifest_path.relative_to(PROJECT_ROOT)),
                "assets": len(records),
                "copied": copied,
                "existing": existing,
                "bytes": total_bytes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
