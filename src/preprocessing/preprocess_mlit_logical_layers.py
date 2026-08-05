#!/usr/bin/env python3
"""Combine selected MLIT municipal/tile files into five logical GeoParquet layers."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "data/exp/data-preprocessing/decisions.json"
TARGET_CRS = "EPSG:6668"


def preprocess_layer(layer_key: str, config: dict[str, object]) -> tuple[int, int, str]:
    paths = sorted(ROOT.glob(str(config["source_glob"])))
    if not paths:
        raise FileNotFoundError(f"No source files matched {config['source_glob']}")

    variables = list(config["variables"])
    rename_map = {str(item["original_name"]): str(item["readable_name"]) for item in variables}
    source_columns = [name for name in rename_map if name != "geometry"]
    frames: list[gpd.GeoDataFrame] = []

    for path in paths:
        frame = gpd.read_file(path)
        missing = sorted(set(source_columns) - set(frame.columns))
        if missing:
            raise ValueError(f"{path.relative_to(ROOT)} missing columns: {missing}")
        frame = frame.to_crs(TARGET_CRS)
        frame = frame[[*source_columns, frame.geometry.name]].rename(
            columns={**{name: rename_map[name] for name in source_columns}, frame.geometry.name: "Geometry"}
        )
        frame = frame.set_geometry("Geometry")
        for item in variables:
            readable = str(item["readable_name"])
            if "strip_whitespace" in item.get("preprocessing", []) and readable in frame.columns:
                if pd.api.types.is_string_dtype(frame[readable]) or frame[readable].dtype == object:
                    frame[readable] = frame[readable].astype("string").str.strip()
        frames.append(frame)

    combined = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="Geometry", crs=TARGET_CRS)
    if combined.geometry.isna().any() or combined.geometry.is_empty.any():
        raise ValueError(f"{layer_key} contains missing or empty geometry after combination")
    destination = ROOT / str(config["output"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(destination, index=False)
    return len(combined), len(combined.columns), str(destination.relative_to(ROOT))


def main() -> None:
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    logical_layers = decisions.get("logical_layers", {})
    if not logical_layers:
        raise ValueError("No logical_layers found in decisions.json")
    for layer_key, config in logical_layers.items():
        rows, columns, destination = preprocess_layer(layer_key, config)
        print(f"Saved {rows:,} rows x {columns} cols -> {destination}")


if __name__ == "__main__":
    main()
