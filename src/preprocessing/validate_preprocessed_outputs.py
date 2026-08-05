#!/usr/bin/env python3
"""Validate all standard and logical-layer preprocessing outputs."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "data/exp/data-preprocessing/decisions.json"
OUTPUT_DIR = ROOT / "data/exp/data-preprocessing"


def read_parquet(path: Path) -> pd.DataFrame:
    try:
        return gpd.read_parquet(path)
    except ValueError:
        return pd.read_parquet(path)


def expected_source_rows(source: str, logical: bool) -> int:
    if logical:
        return sum(len(gpd.read_file(path)) for path in sorted(ROOT.glob(source)))
    return len(read_parquet(ROOT / source))


def validate_record(key: str, config: dict[str, object], *, logical: bool) -> dict[str, object]:
    source = str(config["source_glob"] if logical else key)
    destination = ROOT / str(config["output"])
    variables = list(config["variables"])
    expected_columns = [str(item["readable_name"]) for item in variables]
    errors: list[str] = []

    if not destination.exists():
        return {
            "dataset": key,
            "kind": "logical_layer" if logical else "source_dataset",
            "output": str(destination.relative_to(ROOT)),
            "status": "failed",
            "errors": "output missing",
        }

    frame = read_parquet(destination)
    source_rows = expected_source_rows(source, logical)
    if len(frame) != source_rows:
        errors.append(f"row count {len(frame)} != source {source_rows}")
    if list(frame.columns) != expected_columns:
        errors.append("output columns do not exactly match confirmed readable names")
    if len(set(name.casefold() for name in frame.columns)) != len(frame.columns):
        errors.append("duplicate case-insensitive output columns")
    if any(not str(name).isascii() for name in frame.columns):
        errors.append("non-ASCII output column")

    expects_geometry = "Geometry" in expected_columns
    if expects_geometry:
        if not isinstance(frame, gpd.GeoDataFrame):
            errors.append("GeoParquet metadata missing")
            crs = ""
            geometry_name = ""
            missing_geometry = ""
            empty_geometry = ""
        else:
            crs = str(frame.crs)
            geometry_name = frame.geometry.name
            missing_geometry = int(frame.geometry.isna().sum())
            empty_geometry = int(frame.geometry.is_empty.sum())
            if frame.crs is None:
                errors.append("CRS missing")
            if geometry_name != "Geometry":
                errors.append(f"active geometry is {geometry_name}, expected Geometry")
            if missing_geometry or empty_geometry:
                errors.append("missing or empty geometry")
    else:
        crs = ""
        geometry_name = ""
        missing_geometry = ""
        empty_geometry = ""

    return {
        "dataset": key,
        "kind": "logical_layer" if logical else "source_dataset",
        "source": source,
        "output": str(destination.relative_to(ROOT)),
        "status": "passed" if not errors else "failed",
        "rows": len(frame),
        "columns": len(frame.columns),
        "size_bytes": destination.stat().st_size,
        "crs": crs,
        "geometry_name": geometry_name,
        "missing_geometry": missing_geometry,
        "empty_geometry": empty_geometry,
        "errors": " | ".join(errors),
    }


def main() -> None:
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for source, config in decisions.get("datasets", {}).items():
        rows.append(validate_record(source, config, logical=False))
    for layer_key, config in decisions.get("logical_layers", {}).items():
        rows.append(validate_record(layer_key, config, logical=True))

    validation = pd.DataFrame(rows)
    validation.to_csv(OUTPUT_DIR / "output_validation.csv", index=False)
    failed = validation.loc[validation["status"] != "passed"]
    if not failed.empty:
        raise ValueError("Validation failures:\n" + failed[["dataset", "errors"]].to_string(index=False))

    dispatch = gpd.read_parquet(ROOT / "data/processed/fire_dispatch_bases_preprocessed.parquet")
    candidate_dispatch = int(dispatch["Candidate Dispatch Base"].fillna(False).astype(bool).sum())
    geospatial_count = int((validation["geometry_name"] == "Geometry").sum())
    total_size = int(validation["size_bytes"].sum())
    total_rows = int(validation["rows"].sum())
    summary = f"""# Data Preprocessing Output Summary

- Outputs validated: {len(validation)}
- GeoParquet outputs with active `Geometry`: {geospatial_count}
- Non-spatial Parquet outputs: {len(validation) - geospatial_count}
- Total output rows across datasets: {total_rows:,}
- Total output size: {total_size:,} bytes
- Candidate dispatch bases retained: {candidate_dispatch}
- Validation failures: 0

All output columns exactly match the confirmed English readable names. No missing-value
imputation, outlier clipping, or numeric transformation was applied. Selected string fields
were stripped of surrounding whitespace. Time fields remain provenance metadata only.

MLIT municipal and tile files were combined into five logical layers and harmonized to
JGD2011 geographic coordinates (`EPSG:6668`). Other GeoParquet outputs preserve their source CRS.
"""
    (OUTPUT_DIR / "OUTPUT_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(f"Validated {len(validation)} outputs; {geospatial_count} GeoParquet; 0 failures")


if __name__ == "__main__":
    main()
