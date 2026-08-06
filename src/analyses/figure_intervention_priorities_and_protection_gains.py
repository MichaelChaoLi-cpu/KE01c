#!/usr/bin/env python3
"""Intervention Priorities and Protection Gains

Plan: show selected response-base, bounded-water, and road-restoration actions,
compare them with simple within-class baselines, and trace gains by unit budget.
Framework: AnaSOP Sections 5, 6.6, and workflow step 7.
"""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np
from pyproj import Transformer
import seaborn as sns
from shapely.geometry import LineString

from intervention_analysis_common import WATER_SUPPORT_RADIUS_M, load_interventions


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
OUTPUT = RESULTS / "figures/Figure_intervention_priorities_and_protection_gains.png"

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
FIGURE_DPI = 400
MAP_BUDGET = 3
BAR_BUDGET = 3

ACTION_COLORS = {
    "Candidate staging site": "#246b9a",
    "Bounded water support": "#1f927a",
    "Priority road restoration": "#c84d3a",
}
ACTION_MARKERS = {
    "Candidate staging site": "o",
    "Bounded water support": "s",
}
SHORT_LABELS = {
    "Candidate staging site": "Staging site",
    "Bounded water support": "Water support",
    "Priority road restoration": "Road sections",
}
BAR_ITEMS = (
    ("Candidate staging site", "Action count", "Staging site"),
    ("Bounded water support", "Action count", "Water support"),
    ("Priority road restoration", "Road section count", "Road: 3 sections"),
    (
        "Priority road restoration",
        "Normalized event-exposed length",
        "Road: length budget 3",
    ),
)


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
    """Apply the approved geographic frame and extent."""
    min_x, min_y, max_x, max_y = bounds
    margin_x = (max_x - min_x) * 0.018
    margin_y = (max_y - min_y) * 0.018
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(min_y - margin_y, max_y + margin_y)
    ax.set_aspect("equal")
    add_graticule(ax, geographic_bounds)


def draw_panel_label(ax: plt.Axes, label: str) -> None:
    """Place a panel marker without a panel title."""
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


def make_figure(
    actions: gpd.GeoDataFrame,
    performance,
    context: gpd.GeoDataFrame,
) -> None:
    """Render the map, comparator bars, and unit-budget curves."""
    administrative = gpd.read_parquet(ADMIN_PATH).to_crs(PROJECTED_CRS)
    boundary = administrative.dissolve()
    bounds = tuple(boundary.total_bounds)
    geographic_bounds = tuple(boundary.to_crs(GEOGRAPHIC_CRS).total_bounds)
    actions = actions.to_crs(PROJECTED_CRS)
    context = context.to_crs(PROJECTED_CRS)

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

    fig = plt.figure(figsize=(13.4, 11.5), constrained_layout=True)
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=(1, 0.78),
        width_ratios=(1, 1),
        wspace=0.10,
        hspace=0.16,
    )
    map_ax = fig.add_subplot(grid[0, 0])
    bar_ax = fig.add_subplot(grid[0, 1])
    curve_ax = fig.add_subplot(grid[1, :])
    axes = (map_ax, bar_ax, curve_ax)

    boundary.plot(ax=map_ax, color="#f0f2f3", edgecolor="none", zorder=0)
    priority_context = context.loc[
        context["Combined Stress Consequence Rank"] >= 0.90
    ]
    priority_context.plot(
        ax=map_ax,
        column="Combined Stress Consequence Rank",
        cmap="YlOrRd",
        norm=Normalize(0.90, 1),
        linewidth=0,
        rasterized=True,
        zorder=1,
    )
    administrative.boundary.plot(
        ax=map_ax,
        color="#8f9aa2",
        linewidth=0.32,
        alpha=0.88,
        zorder=3.5,
    )
    boundary.boundary.plot(ax=map_ax, color="#46545e", linewidth=0.48, zorder=4)

    mapped = actions.loc[actions["Selection Rank"] <= MAP_BUDGET]
    water = mapped.loc[mapped["Action Type"].eq("Bounded water support")]
    if not water.empty:
        water.geometry.buffer(WATER_SUPPORT_RADIUS_M).boundary.plot(
            ax=map_ax,
            color=ACTION_COLORS["Bounded water support"],
            linewidth=0.8,
            alpha=0.65,
            zorder=5,
        )
    for action_type in ("Candidate staging site", "Bounded water support"):
        subset = mapped.loc[mapped["Action Type"].eq(action_type)]
        if not subset.empty:
            subset.plot(
                ax=map_ax,
                color=ACTION_COLORS[action_type],
                marker=ACTION_MARKERS[action_type],
                markersize=36,
                edgecolor="white",
                linewidth=0.65,
                zorder=6,
            )
    roads = mapped.loc[
        mapped["Action Type"].eq("Priority road restoration")
        & mapped["Road Selection Basis"].eq("Road section count")
    ]
    if not roads.empty:
        roads.plot(
            ax=map_ax,
            color=ACTION_COLORS["Priority road restoration"],
            linewidth=2.3,
            zorder=7,
        )
        road_centres = roads.geometry.centroid
        map_ax.scatter(
            road_centres.x,
            road_centres.y,
            color=ACTION_COLORS["Priority road restoration"],
            marker="D",
            s=34,
            edgecolor="white",
            linewidth=0.65,
            zorder=8,
        )
    style_map(map_ax, bounds, geographic_bounds)
    map_ax.set_box_aspect(1)
    colorbar_ax = map_ax.inset_axes([0.10, -0.115, 0.80, 0.025])
    colorbar = mpl.colorbar.ColorbarBase(
        colorbar_ax,
        cmap=mpl.colormaps["YlOrRd"],
        norm=Normalize(0.90, 1),
        orientation="horizontal",
    )
    colorbar.outline.set_visible(False)
    colorbar.set_ticks([0.90, 0.95, 1.00])
    colorbar.set_ticklabels(["Top 10%", "Top 5%", "Highest"])
    colorbar.ax.tick_params(labelsize=7.2, length=2.5, colors="#4f606d")
    colorbar.set_label(
        "Highest combined-stress conditional consequence cells",
        fontsize=8,
        color="#425461",
    )
    map_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=ACTION_COLORS["Candidate staging site"],
            markeredgecolor="white",
            markersize=6,
            label="Candidate staging site",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            linestyle="none",
            markerfacecolor=ACTION_COLORS["Bounded water support"],
            markeredgecolor="white",
            markersize=6,
            label="1 km water-support area",
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            linestyle="none",
            markerfacecolor=ACTION_COLORS["Priority road restoration"],
            markeredgecolor="white",
            markersize=6,
            label="Restored road section",
        ),
    ]
    map_ax.legend(
        handles=map_handles,
        loc="lower left",
        frameon=True,
        framealpha=0.9,
        facecolor="white",
        edgecolor="#a9b1b7",
        fontsize=6.8,
    )

    bar_data = performance.loc[performance["Budget"].eq(BAR_BUDGET)].copy()
    strategy_order = ["Greedy consequence reduction", "Simple baseline"]
    x_positions = np.arange(len(BAR_ITEMS), dtype=float)
    bar_width = 0.34
    strategy_styles = {
        "Greedy consequence reduction": ("#2d758e", "Prioritized"),
        "Simple baseline": ("#b8c2c8", "Simple baseline"),
    }
    for strategy_index, strategy in enumerate(strategy_order):
        values = []
        for action_type, budget_definition, _ in BAR_ITEMS:
            row = bar_data.loc[
                bar_data["Action Type"].eq(action_type)
                & bar_data["Budget Definition"].eq(budget_definition)
                & bar_data["Strategy"].eq(strategy)
            ]
            values.append(100 * float(row["Consequence Reduction Share"].iloc[0]))
        positions = x_positions + (strategy_index - 0.5) * bar_width
        color, label = strategy_styles[strategy]
        bars = bar_ax.bar(
            positions,
            values,
            width=bar_width,
            color=color,
            label=label,
            zorder=3,
        )
        bar_ax.bar_label(bars, fmt="%.2f", fontsize=7, padding=2, color="#425461")
    bar_ax.set_xticks(x_positions)
    bar_ax.set_xticklabels([item[2] for item in BAR_ITEMS], fontsize=7.6)
    bar_ax.set_ylabel("Combined-stress consequence reduced (%)", fontsize=9)
    bar_ax.set_xlabel("Budget level 3 within each action class", fontsize=9)
    bar_ax.tick_params(axis="y", labelsize=8)
    bar_ax.set_ylim(
        0,
        1.18 * float((100 * bar_data["Consequence Reduction Share"]).max()),
    )
    bar_ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    bar_ax.grid(axis="y", color="#d6dadd", linewidth=0.55)
    bar_ax.grid(axis="x", visible=False)
    sns.despine(ax=bar_ax)

    prioritized = performance.loc[
        performance["Strategy"].eq("Greedy consequence reduction")
    ].copy()
    curve_items = (
        ("Candidate staging site", "Action count", "Staging site", "o", "#246b9a", "-"),
        ("Bounded water support", "Action count", "Water support", "s", "#1f927a", "-"),
        (
            "Priority road restoration",
            "Road section count",
            "Road: section count",
            "D",
            "#c84d3a",
            "-",
        ),
        (
            "Priority road restoration",
            "Normalized event-exposed length",
            "Road: length-aware budget",
            "^",
            "#7b4f9d",
            "--",
        ),
    )
    for action_type, budget_definition, label, marker, color, linestyle in curve_items:
        subset = prioritized.loc[
            prioritized["Action Type"].eq(action_type)
            & prioritized["Budget Definition"].eq(budget_definition)
        ].sort_values("Budget")
        curve_ax.plot(
            subset["Budget"],
            100 * subset["Consequence Reduction Share"],
            marker=marker,
            markersize=5,
            linewidth=1.7,
            linestyle=linestyle,
            color=color,
            label=label,
        )
    curve_ax.set_xticks(range(1, 6))
    curve_ax.set_xlabel("Class-specific budget level", fontsize=9)
    curve_ax.set_ylabel("Combined-stress consequence reduced (%)", fontsize=9)
    curve_ax.tick_params(labelsize=8)
    curve_ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=4)
    curve_ax.grid(color="#d6dadd", linewidth=0.55)
    sns.despine(ax=curve_ax)

    for label, ax in zip("abc", axes, strict=True):
        draw_panel_label(ax, label)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    actions, performance, context = load_interventions()
    make_figure(actions, performance, context)
    budget_three = performance.loc[
        performance["Budget"].eq(3)
        & performance["Strategy"].eq("Greedy consequence reduction")
    ]
    summary = "; ".join(
        f"{SHORT_LABELS[row['Action Type']]} ({row['Budget Definition']})="
        f"{100 * row['Consequence Reduction Share']:.2f}%"
        for _, row in budget_three.iterrows()
    )
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(f"Diagnostics: actions={len(actions)}; budget-3 reductions: {summary}")


if __name__ == "__main__":
    main()
