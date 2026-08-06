#!/usr/bin/env python3
"""Fire Base Accessibility Dependence under Road Disruption.

Plan: map event-road leave-one-out criticality and compare the same deterministic
full-system removal estimand under normal and event-specific roads.
Framework: AnaSOP Sections 5.3, 6.6, and workflow step 6.
"""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from pyproj import Transformer
import seaborn as sns
from shapely.geometry import LineString

from fire_base_criticality_common import load_fire_base_criticality
from fire_base_labels import fire_base_label_table


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
OUTPUT = RESULTS / "figures/Figure_fire_base_accessibility_dependence_under_road_disruption.png"

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
FIGURE_DPI = 400
MAIN_OBJECTIVE = "Population"
TOP_BASES = 18


def graticule_values(lower: float, upper: float, step: float) -> list[float]:
    start = math.ceil((lower - 1e-9) / step) * step
    stop = math.floor((upper + 1e-9) / step) * step
    count = int(round((stop - start) / step)) + 1
    return [round(start + index * step, 8) for index in range(max(0, count))]


def add_graticule(
    ax: plt.Axes,
    geographic_bounds: tuple[float, float, float, float],
    step: float = 0.25,
) -> None:
    lon_min, lat_min, lon_max, lat_max = geographic_bounds
    longitudes = graticule_values(lon_min, lon_max, step)
    latitudes = graticule_values(lat_min, lat_max, step)
    samples = 160
    lines = [
        LineString(
            zip(
                np.full(samples, longitude),
                np.linspace(lat_min - step, lat_max + step, samples),
                strict=True,
            )
        )
        for longitude in longitudes
    ]
    lines.extend(
        LineString(
            zip(
                np.linspace(lon_min - step, lon_max + step, samples),
                np.full(samples, latitude),
                strict=True,
            )
        )
        for latitude in latitudes
    )
    gpd.GeoSeries(lines, crs=GEOGRAPHIC_CRS).to_crs(PROJECTED_CRS).plot(
        ax=ax,
        color="#7d8992",
        linewidth=0.42,
        linestyle=(0, (2.5, 3.5)),
        alpha=0.48,
        zorder=3,
    )

    transformer = Transformer.from_crs(GEOGRAPHIC_CRS, PROJECTED_CRS, always_xy=True)
    centre_latitude = (lat_min + lat_max) / 2
    centre_longitude = (lon_min + lon_max) / 2
    label_style = {"fontsize": 7.0, "color": "#3f4a52", "clip_on": False}
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
            -0.022,
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
    min_x, min_y, max_x, max_y = bounds
    margin_x = (max_x - min_x) * 0.018
    margin_y = (max_y - min_y) * 0.018
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(min_y - margin_y, max_y + margin_y)
    ax.set_aspect("equal")
    add_graticule(ax, geographic_bounds)


def draw_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.075,
        1.02,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        color="#263746",
    )


def make_figure(values: gpd.GeoDataFrame) -> None:
    population = values.loc[values["Exposure Objective"].eq(MAIN_OBJECTIVE)].copy()
    labels = fire_base_label_table(population)
    population = population.merge(
        labels[["Fire Base Name", "Fire Base"]],
        on="Fire Base Name",
        how="left",
        validate="many_to_one",
    )
    event = population.loc[population["Road Scenario"].eq("central")].copy()
    event = gpd.GeoDataFrame(event, geometry="Geometry", crs=values.crs).to_crs(
        PROJECTED_CRS
    )

    administrative = gpd.read_parquet(ADMIN_PATH).to_crs(PROJECTED_CRS)
    boundary = administrative.dissolve()
    bounds = tuple(boundary.total_bounds)
    geographic_bounds = tuple(boundary.to_crs(GEOGRAPHIC_CRS).total_bounds)

    sns.set_theme(context="paper", style="whitegrid", font="DejaVu Sans")
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig = plt.figure(figsize=(16.0, 6.6), constrained_layout=True)
    grid = fig.add_gridspec(1, 2, width_ratios=(1.15, 1.30), wspace=0.10)
    map_ax = fig.add_subplot(grid[0, 0])
    rank_ax = fig.add_subplot(grid[0, 1])

    boundary.plot(ax=map_ax, color="#f0f2f3", edgecolor="none", zorder=0)
    administrative.boundary.plot(
        ax=map_ax,
        color="#8f9aa2",
        linewidth=0.32,
        alpha=0.88,
        zorder=2,
    )
    boundary.boundary.plot(ax=map_ax, color="#46545e", linewidth=0.48, zorder=3)
    event_share = 100 * event["Leave-One-Out Fire Base Value Share"].to_numpy(float)
    maximum = max(float(np.nanmax(event_share)), 1e-9)
    marker_size = 18 + 170 * np.sqrt(np.clip(event_share / maximum, 0, 1))
    points = map_ax.scatter(
        event.geometry.x,
        event.geometry.y,
        c=event_share,
        s=marker_size,
        cmap="viridis",
        norm=Normalize(0, maximum),
        edgecolor="white",
        linewidth=0.45,
        alpha=0.92,
        zorder=5,
    )
    style_map(map_ax, bounds, geographic_bounds)
    map_ax.set_box_aspect(1)
    map_ax.set_anchor("N")
    colorbar_ax = map_ax.inset_axes([0.10, -0.115, 0.80, 0.025])
    colorbar = fig.colorbar(points, cax=colorbar_ax, orientation="horizontal")
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(labelsize=7.2, length=2.5, colors="#4f606d")
    colorbar.set_label(
        "Event-road share of leave-one-out system loss (%)",
        fontsize=8,
        color="#425461",
    )

    shares = population.pivot(
        index="Fire Base Name",
        columns="Road Scenario",
        values="Leave-One-Out Fire Base Value Share",
    )
    event_order = event.set_index("Fire Base Name")[
        "Leave-One-Out Fire Base Value Share"
    ].nlargest(TOP_BASES)
    ranking = event_order.index.tolist()
    label_lookup = labels.set_index("Fire Base Name")["Fire Base"]
    y_positions = np.arange(len(ranking))[::-1]
    normal_share = 100 * shares.loc[ranking, "normal"].to_numpy(float)
    event_rank_share = 100 * shares.loc[ranking, "central"].to_numpy(float)
    for y_value, normal_value, disrupted_value in zip(
        y_positions, normal_share, event_rank_share, strict=True
    ):
        rank_ax.plot(
            [normal_value, disrupted_value],
            [y_value, y_value],
            color="#b7bec3",
            linewidth=1.0,
            zorder=1,
        )
    rank_ax.scatter(
        normal_share,
        y_positions,
        s=28,
        color="#2f80a8",
        marker="o",
        label="Normal roads",
        zorder=3,
    )
    rank_ax.scatter(
        event_rank_share,
        y_positions,
        s=30,
        color="#d95f43",
        marker="s",
        label="Event-disrupted roads",
        zorder=3,
    )
    rank_ax.set_yticks(y_positions)
    rank_ax.set_yticklabels(label_lookup.loc[ranking].tolist(), fontsize=7.6)
    rank_ax.set_xlabel("Share of leave-one-out system loss (%)", fontsize=9)
    rank_ax.tick_params(axis="x", labelsize=8)
    rank_ax.grid(axis="x", color="#d6dadd", linewidth=0.55)
    rank_ax.grid(axis="y", visible=False)
    rank_ax.legend(loc="lower right", frameon=False, fontsize=7.2)
    sns.despine(ax=rank_ax, left=True)

    fig.canvas.draw()
    map_position = map_ax.get_position()
    rank_position = rank_ax.get_position()
    target_map_width = rank_position.height * fig.get_figheight() / fig.get_figwidth()
    available_map_width = rank_position.x0 - map_position.x0
    if target_map_width >= available_map_width:
        raise ValueError("Figure layout does not leave enough width to align panel axes")
    fig.set_layout_engine("none")
    map_ax.set_position(
        [map_position.x0, rank_position.y0, target_map_width, rank_position.height]
    )
    draw_panel_label(map_ax, "a")
    draw_panel_label(rank_ax, "b")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    values = load_fire_base_criticality()
    make_figure(values)
    population_event = values.loc[
        values["Exposure Objective"].eq(MAIN_OBJECTIVE)
        & values["Road Scenario"].eq("central")
    ]
    top = population_event.nlargest(1, "Leave-One-Out Fire Base Value Share").iloc[0]
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"eligible bases={population_event['Fire Base Name'].nunique()}; "
        f"minimum loss={population_event['Leave-One-Out Fire Base Value'].min():.6f}; "
        f"top event-road share={100 * top['Leave-One-Out Fire Base Value Share']:.2f}%"
    )


if __name__ == "__main__":
    main()
