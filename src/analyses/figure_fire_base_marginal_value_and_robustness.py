#!/usr/bin/env python3
"""Fire Base Marginal Value and Robustness

Plan: map accessibility-based station value, compare leave-one-out and sampled
Shapley values, and show ranking stability across normal and disrupted roads.
Framework: AnaSOP Sections 5, 6.5, and workflow step 6.
"""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
from pyproj import Transformer
import seaborn as sns
from shapely.geometry import LineString

from fire_base_value_common import load_fire_base_values


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
OUTPUT = RESULTS / "figures/Figure_fire_base_marginal_value_and_robustness.png"

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
FIGURE_DPI = 400
MAIN_OBJECTIVE = "Population"
TOP_STATIONS = 18

ENGLISH_STATION_LABELS = {
    "熊本市消防局東消防署託麻出張所": "Kumamoto East FS — Takuma branch",
    "熊本市消防局中央消防署出水出張所": "Kumamoto Central FS — Izumi branch",
    "熊本市消防局東消防署小山出張所": "Kumamoto East FS — Oyama branch",
    "八代広域行政事務組合八代消防署": "Yatsushiro Fire Station",
    "熊本市消防局中央消防署楠出張所": "Kumamoto Central FS — Kusu branch",
    "熊本市消防局東消防署": "Kumamoto East Fire Station",
    "熊本市消防局中央消防署": "Kumamoto Central Fire Station",
    "熊本市消防局中央消防署清水出張所": "Kumamoto Central FS — Shimizu branch",
    "熊本市消防局中央消防署南熊本庁舎": "Kumamoto Central FS — South Kumamoto office",
    "八代広域行政事務組合八代消防署新開分署": "Yatsushiro FS — Shinkai branch",
    "菊池広域連合泉ヶ丘消防署": "Izumigaoka Fire Station",
    "熊本市消防局西消防署": "Kumamoto West Fire Station",
    "熊本市消防局西消防署池田庁舎": "Kumamoto West FS — Ikeda office",
    "八代広域行政事務組合鏡消防署": "Kagami Fire Station",
    "有明広域行政事務組合玉名消防署西分署": "Tamana FS — West branch",
    "熊本市消防局西消防署平田出張所": "Kumamoto West FS — Hirata branch",
    "熊本市消防局西消防署田崎出張所": "Kumamoto West FS — Tasaki branch",
    "熊本市消防局西消防署川尻出張所": "Kumamoto West FS — Kawashiri branch",
}


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


def population_station_frame(values: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return one station geometry and robust value per population objective."""
    subset = values.loc[values["Exposure Objective"].eq(MAIN_OBJECTIVE)].copy()
    stable = subset.sort_values("Road Scenario").drop_duplicates("Fire Base Name")
    return gpd.GeoDataFrame(stable, geometry="Geometry", crs=values.crs)


def make_figure(values: gpd.GeoDataFrame) -> None:
    """Render the planned map, benchmark scatter, and ranked dot plot."""
    administrative = gpd.read_parquet(ADMIN_PATH).to_crs(PROJECTED_CRS)
    boundary = administrative.dissolve()
    bounds = tuple(boundary.total_bounds)
    geographic_bounds = tuple(boundary.to_crs(GEOGRAPHIC_CRS).total_bounds)
    stations = population_station_frame(values).to_crs(PROJECTED_CRS)
    central = values.loc[
        values["Exposure Objective"].eq(MAIN_OBJECTIVE)
        & values["Road Scenario"].eq("central")
    ].copy()

    sns.set_theme(context="paper", style="whitegrid", font="Hiragino Sans")
    mpl.rcParams.update(
        {
            "font.family": ["Hiragino Sans", "DejaVu Sans"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig = plt.figure(figsize=(13.4, 11.7), constrained_layout=True)
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=(1, 0.82),
        width_ratios=(1, 1),
        wspace=0.09,
        hspace=0.16,
    )
    map_ax = fig.add_subplot(grid[0, 0])
    scatter_ax = fig.add_subplot(grid[0, 1])
    rank_ax = fig.add_subplot(grid[1, :])
    axes = (map_ax, scatter_ax, rank_ax)

    boundary.plot(ax=map_ax, color="#f0f2f3", edgecolor="none", zorder=0)
    administrative.boundary.plot(
        ax=map_ax,
        color="#8f9aa2",
        linewidth=0.32,
        alpha=0.88,
        zorder=2,
    )
    boundary.boundary.plot(ax=map_ax, color="#46545e", linewidth=0.48, zorder=3)
    robust_percent = 100 * stations["Robust Fire Base Value"].to_numpy(dtype=float)
    maximum = max(float(np.nanmax(robust_percent)), 1e-9)
    marker_size = 18 + 170 * np.sqrt(np.clip(robust_percent / maximum, 0, 1))
    map_points = map_ax.scatter(
        stations.geometry.x,
        stations.geometry.y,
        c=robust_percent,
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
    colorbar_ax = map_ax.inset_axes([0.10, -0.115, 0.80, 0.025])
    map_colorbar = fig.colorbar(
        map_points,
        cax=colorbar_ax,
        orientation="horizontal",
    )
    map_colorbar.outline.set_visible(False)
    map_colorbar.ax.tick_params(labelsize=7.2, length=2.5, colors="#4f606d")
    map_colorbar.set_label(
        "Robust share of accessibility value (%)",
        fontsize=8,
        color="#425461",
    )

    type_colors = {
        "Fire Station": "#276d93",
        "Branch or Outpost": "#d27a35",
    }
    for base_type, group in central.groupby("Fire Base Type", sort=False):
        scatter_ax.scatter(
            100 * group["Leave-One-Out Value Share"],
            100 * group["Scenario Shapley Value Share"],
            s=34,
            color=type_colors.get(base_type, "#68757d"),
            edgecolor="white",
            linewidth=0.45,
            alpha=0.88,
            label=base_type,
            zorder=3,
        )
    limit = 1.08 * max(
        float((100 * central["Leave-One-Out Value Share"]).max()),
        float((100 * central["Scenario Shapley Value Share"]).max()),
    )
    scatter_ax.plot([0, limit], [0, limit], color="#9aa3a8", linewidth=0.8, zorder=1)
    correlation = central["Leave-One-Out Value Share"].rank().corr(
        central["Scenario Shapley Value Share"].rank()
    )
    scatter_ax.text(
        0.97,
        0.05,
        f"Rank correlation = {correlation:.2f}",
        transform=scatter_ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#46545e",
    )
    scatter_ax.set_xlim(0, limit)
    scatter_ax.set_ylim(0, limit)
    scatter_ax.set_aspect("equal", adjustable="box")
    scatter_ax.set_xlabel("Share of total leave-one-out value (%)", fontsize=9)
    scatter_ax.set_ylabel("Share of coalition value (%)", fontsize=9)
    scatter_ax.tick_params(labelsize=8)
    scatter_ax.legend(
        loc="upper left",
        frameon=False,
        fontsize=7.5,
        handletextpad=0.35,
    )
    sns.despine(ax=scatter_ax)

    population = values.loc[values["Exposure Objective"].eq(MAIN_OBJECTIVE)].copy()
    shares = population.pivot(
        index="Fire Base Name",
        columns="Road Scenario",
        values="Scenario Shapley Value Share",
    )
    robust = population.drop_duplicates("Fire Base Name").set_index("Fire Base Name")[
        "Robust Fire Base Value"
    ]
    ranking = robust.nlargest(TOP_STATIONS).index.tolist()
    y_positions = np.arange(len(ranking))[::-1]
    normal_share = 100 * shares.loc[ranking, "normal"].to_numpy(dtype=float)
    central_share = 100 * shares.loc[ranking, "central"].to_numpy(dtype=float)
    robust_share = 100 * robust.loc[ranking].to_numpy(dtype=float)
    for y_value, normal_value, central_value in zip(
        y_positions,
        normal_share,
        central_share,
        strict=True,
    ):
        rank_ax.plot(
            [normal_value, central_value],
            [y_value, y_value],
            color="#b7bec3",
            linewidth=1.0,
            zorder=1,
        )
    rank_ax.scatter(
        normal_share,
        y_positions,
        s=27,
        color="#2f80a8",
        marker="o",
        label="Normal roads",
        zorder=3,
    )
    rank_ax.scatter(
        central_share,
        y_positions,
        s=29,
        color="#d95f43",
        marker="s",
        label="Disrupted roads",
        zorder=3,
    )
    rank_ax.scatter(
        robust_share,
        y_positions,
        s=31,
        color="#27343b",
        marker="D",
        label="Robust value",
        zorder=4,
    )
    rank_ax.set_yticks(y_positions)
    english_labels = [
        ENGLISH_STATION_LABELS.get(name, f"Fire base {index + 1}")
        for index, name in enumerate(ranking)
    ]
    rank_ax.set_yticklabels(english_labels, fontsize=7.6)
    rank_ax.set_xlabel("Share of coalition accessibility value (%)", fontsize=9)
    rank_ax.tick_params(axis="x", labelsize=8)
    rank_ax.grid(axis="x", color="#d6dadd", linewidth=0.55)
    rank_ax.grid(axis="y", visible=False)
    rank_ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=7.2,
        handletextpad=0.35,
    )
    sns.despine(ax=rank_ax, left=True)

    for label, ax in zip("abc", axes, strict=True):
        draw_panel_label(ax, label)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    values = load_fire_base_values()
    make_figure(values)
    population = values.loc[values["Exposure Objective"].eq(MAIN_OBJECTIVE)]
    top = (
        population.drop_duplicates("Fire Base Name")
        .nlargest(1, "Robust Fire Base Value")
        .iloc[0]
    )
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"stations={population['Fire Base Name'].nunique()}; "
        f"permutations={int(population['Permutation Count'].max())}; "
        f"all scenarios converged={bool(population['Shapley Converged'].all())}; "
        f"top robust base={top['Fire Base Name']}; "
        f"top robust share={100 * top['Robust Fire Base Value']:.2f}%"
    )


if __name__ == "__main__":
    main()
