#!/usr/bin/env python3
"""Map conditional fire-spread susceptibility across populated Kumamoto cells.

The script constructs the Section 6.2 morphology components from processed
geometries, caches the analysis result under ``data/results/derived``, and
renders the three-panel figure specified in AnaSOP Section 8.  The result is a
relative screen conditional on an imposed ignition, not an ignition model.
"""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
from pyproj import Transformer
import seaborn as sns
from shapely import STRtree, area, intersection, length, point_on_surface
from shapely.geometry import LineString


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
OUTPUT = RESULTS / "figures/Figure_conditional_fire_susceptibility_across_kumamoto.png"
CACHE = RESULTS / "derived/fire_susceptibility_125m.parquet"

MESH_PATH = PROCESSED / "population_mesh_125m_preprocessed.parquet"
BUILDING_PATH = PROCESSED / "buildings_preprocessed.parquet"
ROAD_PATH = PROCESSED / "road_centerlines_preprocessed.parquet"
LAND_USE_PATH = PROCESSED / "mlit_urban_land_use_100m_preprocessed.parquet"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
CONTINUITY_DISTANCE_M = 6.0
FIGURE_DPI = 400
BATCH_SIZE = 50_000

# Approximate full corridor widths represented by each source width class.
ROAD_WIDTH_M = {
    "Under 3 m": 2.0,
    "3 to Under 5.5 m": 4.25,
    "5.5 to Under 13 m": 9.25,
    "13 to Under 19.5 m": 16.25,
    "19.5 m or More": 22.0,
    "Unknown": 4.0,
}

# MLIT L03-b-u classes used as mapped non-building firebreak context.  Road
# corridors are handled from the more detailed road-centreline layer.
OPEN_LAND_CODES = {"0902", "1002", "1003", "1100", "1400", "1500"}


def percentile_rank(values: np.ndarray) -> np.ndarray:
    """Return the empirical percentile transform used in AnaSOP Section 6.1."""
    series = pd.Series(values, dtype="float64")
    valid_n = int(series.notna().sum())
    if valid_n <= 1:
        return np.full(len(series), np.nan, dtype=float)
    ranked = (series.rank(method="average", na_option="keep") - 1) / (valid_n - 1)
    return ranked.to_numpy(dtype=float)


def cache_is_current() -> bool:
    """Use the derived layer only when inputs and generating code are unchanged."""
    if not CACHE.exists():
        return False
    source_paths = (
        MESH_PATH,
        BUILDING_PATH,
        ROAD_PATH,
        LAND_USE_PATH,
        Path(__file__).resolve(),
    )
    return CACHE.stat().st_mtime >= max(path.stat().st_mtime for path in source_paths)


def add_intersection_area(
    target: np.ndarray,
    source_geometries,
    target_geometries,
    target_tree: STRtree,
    *,
    label: str,
) -> None:
    """Accumulate exact source-target overlap area in bounded batches."""
    for start in range(0, len(source_geometries), BATCH_SIZE):
        stop = min(start + BATCH_SIZE, len(source_geometries))
        batch = source_geometries[start:stop]
        pairs = target_tree.query(batch, predicate="intersects")
        if pairs.size:
            source_index, target_index = pairs
            overlap = intersection(batch[source_index], target_geometries[target_index])
            np.add.at(target, target_index, area(overlap))
        print(f"{label}: {stop:,}/{len(source_geometries):,}", flush=True)


def add_road_corridor_area(
    target: np.ndarray,
    roads: gpd.GeoDataFrame,
    target_geometries,
    target_tree: STRtree,
) -> None:
    """Accumulate centreline length times declared corridor width by cell."""
    road_geometries = roads.geometry.array
    road_width = roads["Width Category"].map(ROAD_WIDTH_M).fillna(4.0).to_numpy(dtype=float)
    for start in range(0, len(roads), BATCH_SIZE):
        stop = min(start + BATCH_SIZE, len(roads))
        batch = road_geometries[start:stop]
        pairs = target_tree.query(batch, predicate="intersects")
        if pairs.size:
            road_index, target_index = pairs
            clipped = intersection(batch[road_index], target_geometries[target_index])
            corridor_area = length(clipped) * road_width[start:stop][road_index]
            np.add.at(target, target_index, corridor_area)
        print(f"road corridors: {stop:,}/{len(roads):,}", flush=True)


def construct_susceptibility() -> gpd.GeoDataFrame:
    """Construct morphology, firebreak, and equal-weight susceptibility fields."""
    mesh = gpd.read_parquet(MESH_PATH).to_crs(PROJECTED_CRS)
    if not mesh["Mesh Code"].is_unique:
        raise ValueError("Mesh Code must be unique")
    mesh_geometry = mesh.geometry.array
    mesh_tree = STRtree(mesh_geometry)
    cell_area = mesh.geometry.area.to_numpy(dtype=float)

    print("Reading and projecting building footprints...", flush=True)
    buildings = gpd.read_parquet(BUILDING_PATH, columns=["Geometry"]).to_crs(PROJECTED_CRS)
    building_geometry = buildings.geometry.array

    # Exact footprint overlap allows buildings crossing a cell edge to
    # contribute only their area inside that cell.
    footprint_area = np.zeros(len(mesh), dtype=float)
    add_intersection_area(
        footprint_area,
        building_geometry,
        mesh_geometry,
        mesh_tree,
        label="building overlap",
    )

    # Assign each building to one populated cell for count, separation, and
    # continuity summaries; nearest separation can cross the cell boundary.
    building_points = point_on_surface(building_geometry)
    point_pairs = mesh_tree.query(building_points, predicate="within")
    point_index, point_mesh_index = point_pairs
    building_count = np.bincount(point_mesh_index, minlength=len(mesh)).astype(np.int32)

    print("Constructing nearest-building separation and continuity...", flush=True)
    building_tree = STRtree(building_geometry)
    separation_sum = np.zeros(len(mesh), dtype=float)
    separation_count = np.zeros(len(mesh), dtype=np.int32)
    connected_count = np.zeros(len(mesh), dtype=np.int32)
    building_to_mesh = np.full(len(buildings), -1, dtype=np.int32)
    building_to_mesh[point_index] = point_mesh_index

    for start in range(0, len(buildings), BATCH_SIZE):
        stop = min(start + BATCH_SIZE, len(buildings))
        batch = building_geometry[start:stop]
        indices, distances = building_tree.query_nearest(
            batch,
            all_matches=False,
            exclusive=True,
            return_distance=True,
        )
        local_index = indices[0]
        global_index = start + local_index
        assigned_mesh = building_to_mesh[global_index]
        keep = (assigned_mesh >= 0) & np.isfinite(distances)
        if keep.any():
            retained_mesh = assigned_mesh[keep]
            retained_distance = distances[keep]
            np.add.at(separation_sum, retained_mesh, retained_distance)
            np.add.at(separation_count, retained_mesh, 1)
            np.add.at(
                connected_count,
                retained_mesh,
                (retained_distance <= CONTINUITY_DISTANCE_M).astype(np.int32),
            )
        print(f"nearest-building distance: {stop:,}/{len(buildings):,}", flush=True)

    mean_separation = np.divide(
        separation_sum,
        separation_count,
        out=np.full(len(mesh), np.nan, dtype=float),
        where=separation_count > 0,
    )
    built_continuity = np.divide(
        connected_count,
        separation_count,
        out=np.zeros(len(mesh), dtype=float),
        where=separation_count > 0,
    )

    print("Constructing mapped firebreak share...", flush=True)
    roads = gpd.read_parquet(ROAD_PATH, columns=["Width Category", "Geometry"]).to_crs(
        PROJECTED_CRS
    )
    road_area = np.zeros(len(mesh), dtype=float)
    add_road_corridor_area(road_area, roads, mesh_geometry, mesh_tree)

    land_use = gpd.read_parquet(
        LAND_USE_PATH, columns=["Urban Land Use Code", "Geometry"]
    )
    open_land = land_use.loc[land_use["Urban Land Use Code"].isin(OPEN_LAND_CODES)].to_crs(
        PROJECTED_CRS
    )
    open_area = np.zeros(len(mesh), dtype=float)
    add_intersection_area(
        open_area,
        open_land.geometry.array,
        mesh_geometry,
        mesh_tree,
        label="open-land overlap",
    )

    coverage = np.clip(footprint_area / cell_area, 0, 1)
    firebreak_share = np.clip((road_area + open_area) / cell_area, 0, 1)

    coverage_rank = percentile_rank(coverage)
    continuity_rank = percentile_rank(built_continuity)
    separation_rank = percentile_rank(mean_separation)
    firebreak_rank = percentile_rank(firebreak_share)

    inverse_separation = 1 - separation_rank
    inverse_separation[~np.isfinite(inverse_separation)] = 0
    continuity_rank[building_count < 2] = 0
    limited_firebreak = 1 - firebreak_rank

    susceptibility = np.nanmean(
        np.column_stack(
            [coverage_rank, continuity_rank, inverse_separation, limited_firebreak]
        ),
        axis=1,
    )
    supporting_conditions = np.nanmean(
        np.column_stack([continuity_rank, inverse_separation, limited_firebreak]),
        axis=1,
    )

    mesh["Building Count"] = building_count
    mesh["Observed Building Footprint Coverage Ratio"] = coverage
    mesh["Mean Building Separation (m)"] = mean_separation
    mesh["Built Continuity Index"] = built_continuity
    mesh["Firebreak Share"] = firebreak_share
    mesh["Other Spread-Supporting Conditions"] = supporting_conditions
    mesh["Conditional Spread Susceptibility"] = susceptibility

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    mesh.to_parquet(CACHE, index=False)
    return mesh


def load_analysis() -> gpd.GeoDataFrame:
    """Load a current derived layer or reconstruct it from processed sources."""
    if cache_is_current():
        print(f"Using current derived layer: {CACHE.relative_to(ROOT)}", flush=True)
        return gpd.read_parquet(CACHE)
    return construct_susceptibility()


def graticule_values(lower: float, upper: float, step: float) -> list[float]:
    """Return stable graticule values within a geographic extent."""
    start = math.ceil((lower - 1e-9) / step) * step
    stop = math.floor((upper + 1e-9) / step) * step
    count = int(round((stop - start) / step)) + 1
    return [round(start + index * step, 8) for index in range(max(0, count))]


def add_graticule(
    ax: plt.Axes,
    geographic_bounds: tuple[float, float, float, float],
    step: float = 0.25,
) -> None:
    """Draw and label longitude/latitude graticules on projected axes."""
    lon_min, lat_min, lon_max, lat_max = geographic_bounds
    longitudes = graticule_values(lon_min, lon_max, step)
    latitudes = graticule_values(lat_min, lat_max, step)
    samples = 160
    lines: list[LineString] = []
    for longitude in longitudes:
        lines.append(
            LineString(
                zip(
                    np.full(samples, longitude),
                    np.linspace(lat_min - step, lat_max + step, samples),
                    strict=True,
                )
            )
        )
    for latitude in latitudes:
        lines.append(
            LineString(
                zip(
                    np.linspace(lon_min - step, lon_max + step, samples),
                    np.full(samples, latitude),
                    strict=True,
                )
            )
        )
    gpd.GeoSeries(lines, crs=GEOGRAPHIC_CRS).to_crs(PROJECTED_CRS).plot(
        ax=ax,
        color="#7d8992",
        linewidth=0.42,
        linestyle=(0, (2.5, 3.5)),
        alpha=0.48,
        zorder=3,
    )

    transformer = Transformer.from_crs(
        GEOGRAPHIC_CRS,
        PROJECTED_CRS,
        always_xy=True,
    )
    centre_latitude = (lat_min + lat_max) / 2
    centre_longitude = (lon_min + lon_max) / 2
    label_style = {"fontsize": 7.2, "color": "#3f4a52", "clip_on": False}
    for longitude in longitudes:
        x_position, _ = transformer.transform(longitude, centre_latitude)
        ax.text(
            x_position,
            -0.014,
            f"{longitude:.2f}°E",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            **label_style,
        )
    for latitude in latitudes:
        _, y_position = transformer.transform(centre_longitude, latitude)
        ax.text(
            -0.020,
            y_position,
            f"{latitude:.2f}°N",
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="center",
            **label_style,
        )
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#303a40")
        spine.set_linewidth(0.85)
        spine.set_zorder(10)


def style_map(
    ax: plt.Axes,
    bounds: tuple[float, float, float, float],
    geographic_bounds: tuple[float, float, float, float],
) -> None:
    """Apply the sibling-project geographic frame and map extent."""
    min_x, min_y, max_x, max_y = bounds
    margin_x = (max_x - min_x) * 0.018
    margin_y = (max_y - min_y) * 0.018
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(min_y - margin_y, max_y + margin_y)
    ax.set_aspect("equal")
    add_graticule(ax, geographic_bounds)


def draw_panel_label(ax: plt.Axes, label: str) -> None:
    """Place the KE01b-style panel marker without a panel title."""
    ax.text(
        -0.04,
        1.02,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        color="#263746",
    )
def make_figure(mesh: gpd.GeoDataFrame) -> None:
    """Render the three planned gridded maps at 400 dpi."""
    administrative = gpd.read_parquet(ADMIN_PATH).to_crs(mesh.crs)
    boundary = administrative.dissolve()
    bounds = tuple(boundary.total_bounds)
    geographic_bounds = tuple(boundary.to_crs(GEOGRAPHIC_CRS).total_bounds)

    sns.set_theme(context="paper", style="white", font="DejaVu Sans")
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig = plt.figure(figsize=(17.2, 6.6), constrained_layout=True)
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=(1, 0.035),
        wspace=0.07,
        hspace=0.035,
    )
    axes = [fig.add_subplot(grid[0, index]) for index in range(3)]
    color_axes = [fig.add_subplot(grid[1, index]) for index in range(3)]

    coverage_vmax = max(
        0.20,
        float(mesh["Observed Building Footprint Coverage Ratio"].quantile(0.99)),
    )
    panel_specs = [
        (
            "Observed Building Footprint Coverage Ratio",
            "Blues",
            Normalize(0, coverage_vmax),
            "a",
        ),
        (
            "Other Spread-Supporting Conditions",
            "PuBuGn",
            Normalize(0, 1),
            "b",
        ),
        (
            "Conditional Spread Susceptibility",
            "YlOrRd",
            Normalize(0, 1),
            "c",
        ),
    ]

    for ax, color_ax, spec in zip(axes, color_axes, panel_specs, strict=True):
        column, cmap_name, norm, label = spec
        boundary.plot(ax=ax, color="#f0f2f3", edgecolor="none", zorder=0)
        mesh.plot(
            ax=ax,
            column=column,
            cmap=cmap_name,
            norm=norm,
            linewidth=0,
            rasterized=True,
            missing_kwds={"color": "#d9dde0"},
            zorder=1,
        )
        administrative.boundary.plot(
            ax=ax,
            color="#8f9aa2",
            linewidth=0.32,
            alpha=0.88,
            zorder=3.5,
        )
        boundary.boundary.plot(ax=ax, color="#46545e", linewidth=0.48, zorder=4)
        style_map(ax, bounds, geographic_bounds)
        draw_panel_label(ax, label)

        colorbar = ColorbarBase(
            color_ax,
            cmap=mpl.colormaps[cmap_name],
            norm=norm,
            orientation="horizontal",
        )
        colorbar.outline.set_visible(False)
        color_ax.tick_params(axis="x", labelsize=7.5, length=2.5, colors="#4f606d")
        color_ax.set_yticks([])
        for spine in color_ax.spines.values():
            spine.set_visible(False)
        if column == "Observed Building Footprint Coverage Ratio":
            colorbar.ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            colorbar.set_label(
                "Building footprint coverage (share of populated 125 m cell)",
                fontsize=8,
                color="#425461",
            )
        else:
            colorbar.set_ticks([0.08, 0.5, 0.92])
            colorbar.set_ticklabels(["Lower", "Middle", "Higher"])
            colorbar_label = (
                "Conditions for continuous spread (relative score)"
                if column == "Other Spread-Supporting Conditions"
                else "Conditional spread susceptibility (relative score)"
            )
            colorbar.set_label(colorbar_label, fontsize=8, color="#425461")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    mesh = load_analysis()
    make_figure(mesh)
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(f"Derived layer: {CACHE.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"cells={len(mesh):,}; "
        f"median coverage={mesh['Observed Building Footprint Coverage Ratio'].median():.3f}; "
        f"median separation={mesh['Mean Building Separation (m)'].median():.2f} m; "
        f"median firebreak share={mesh['Firebreak Share'].median():.3f}; "
        f"p95 susceptibility={mesh['Conditional Spread Susceptibility'].quantile(0.95):.3f}"
    )


if __name__ == "__main__":
    main()
