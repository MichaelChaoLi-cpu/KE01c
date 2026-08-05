#!/usr/bin/env python3
"""Map normal and disrupted fire-service accessibility across Kumamoto.

The four panels report nominal network travel time, redundancy, and shortest-
route concentration under declared scenarios. They are planning screens rather
than observed emergency response times or confirmed road closures.
"""

from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np
from pyproj import Transformer
import seaborn as sns
from shapely.geometry import LineString

from fire_service_access_common import add_single_route_dependence


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"

MESH_PATH = PROCESSED / "population_mesh_125m_preprocessed.parquet"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
OUTPUT = RESULTS / "figures/Figure_post_earthquake_fire_service_accessibility.png"

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
FIGURE_DPI = 400


def load_analysis() -> gpd.GeoDataFrame:
    """Join the cached accessibility metrics to populated 125 m cells."""
    mesh = gpd.read_parquet(MESH_PATH, columns=["Mesh Code", "Geometry"]).to_crs(
        PROJECTED_CRS
    )
    mesh["Mesh Code"] = mesh["Mesh Code"].astype("string")
    access = add_single_route_dependence()
    access["Mesh Code"] = access["Mesh Code"].astype("string")
    return mesh.merge(access, on="Mesh Code", how="left", validate="one_to_one")


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
    """Apply the approved KE01b-style frame and geographic extent."""
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
        -0.045,
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
    """Render the four planned accessibility maps at 400 dpi."""
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

    fig = plt.figure(figsize=(12.8, 11.8), constrained_layout=True)
    grid = fig.add_gridspec(
        4,
        2,
        height_ratios=(1, 0.035, 1, 0.035),
        wspace=0.08,
        hspace=0.055,
    )
    axes = [
        fig.add_subplot(grid[0, 0]),
        fig.add_subplot(grid[0, 1]),
        fig.add_subplot(grid[2, 0]),
        fig.add_subplot(grid[2, 1]),
    ]
    color_axes = [
        fig.add_subplot(grid[1, 0]),
        fig.add_subplot(grid[1, 1]),
        fig.add_subplot(grid[3, 0]),
        fig.add_subplot(grid[3, 1]),
    ]

    panel_specs = (
        (
            "Normal Response Time (min)",
            "YlOrRd",
            Normalize(0, 30),
            [0, 5, 10, 20, 30],
            ["0", "5", "10", "20", "30+"],
            "Normal response time (minutes)",
            "a",
        ),
        (
            "Disrupted Response Time (min)",
            "YlOrRd",
            Normalize(0, 30),
            [0, 5, 10, 20, 30],
            ["0", "5", "10", "20", "30+"],
            "Response time under road disruption (minutes)",
            "b",
        ),
        (
            "Backup Fire Base Count",
            "YlGnBu",
            Normalize(0, 5),
            [0, 1, 3, 5],
            ["0", "1", "3", "5+"],
            "Additional bases able to arrive within 10 minutes",
            "c",
        ),
        (
            "Single Route Dependence",
            "YlOrRd",
            Normalize(0.5, 1),
            [0.5, 0.75, 1],
            ["Half", "Three quarters", "All"],
            "Largest share of base routes using the same road segment",
            "d",
        ),
    )

    for ax, color_ax, spec in zip(axes, color_axes, panel_specs, strict=True):
        column, cmap_name, norm, ticks, ticklabels, colorbar_label, panel_label = spec
        boundary.plot(ax=ax, color="#eef1f2", edgecolor="none", zorder=0)
        mesh.plot(
            ax=ax,
            column=column,
            cmap=cmap_name,
            norm=norm,
            linewidth=0,
            rasterized=True,
            missing_kwds={"color": "#c9ced2"},
            zorder=1,
        )
        administrative.boundary.plot(
            ax=ax,
            color="#8f9aa2",
            linewidth=0.30,
            alpha=0.88,
            zorder=3.5,
        )
        boundary.boundary.plot(ax=ax, color="#46545e", linewidth=0.46, zorder=4)
        style_map(ax, bounds, geographic_bounds)
        draw_panel_label(ax, panel_label)

        colorbar = ColorbarBase(
            color_ax,
            cmap=mpl.colormaps[cmap_name],
            norm=norm,
            orientation="horizontal",
        )
        colorbar.outline.set_visible(False)
        colorbar.set_ticks(ticks)
        colorbar.set_ticklabels(ticklabels)
        colorbar.set_label(colorbar_label, fontsize=7.7, color="#425461")
        color_ax.tick_params(axis="x", labelsize=7.1, length=2.5, colors="#4f606d")
        color_ax.set_yticks([])
        for spine in color_ax.spines.values():
            spine.set_visible(False)

    axes[3].legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="s",
                linestyle="none",
                markerfacecolor="#c9ced2",
                markeredgecolor="none",
                markersize=5,
                label="No base within 10 minutes",
            )
        ],
        loc="lower left",
        frameon=True,
        framealpha=0.9,
        facecolor="white",
        edgecolor="#a9b1b7",
        fontsize=6.6,
        handletextpad=0.35,
        borderpad=0.45,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    mesh = load_analysis()
    make_figure(mesh)
    served = mesh["Single Route Dependence"].notna()
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"cells={len(mesh):,}; "
        f"normal median={mesh['Normal Response Time (min)'].median():.2f} min; "
        f"disrupted median={mesh['Disrupted Response Time (min)'].median():.2f} min; "
        f"served within 10 min={served.sum():,}; "
        f"fully shared route={(mesh.loc[served, 'Single Route Dependence'] >= 0.999).sum():,}"
    )


if __name__ == "__main__":
    main()
