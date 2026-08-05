#!/usr/bin/env python3
"""Map conditional fire consequence for three exposure objectives.

The figure combines conditional spread susceptibility, the central disrupted-
road accessibility penalty, and population, older-resident, or critical-
facility exposure. It is a relative screen conditional on an imposed ignition,
not a probability of fire, a monetary loss estimate, or a real-time dispatch
assessment.
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
import pandas as pd
from pyproj import Transformer
import seaborn as sns
from shapely.geometry import LineString

from fire_service_access_common import fire_service_access_layer


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
RESULTS = ROOT / "data/results"

SUSCEPTIBILITY_PATH = RESULTS / "derived/fire_susceptibility_125m.parquet"
POPULATION_GROUP_PATH = PROCESSED / "population_disclosure_groups_preprocessed.parquet"
ADMIN_PATH = PROCESSED / "administrative_areas_preprocessed.parquet"
OUTPUT = RESULTS / "figures/Figure_conditional_fire_consequence_and_vulnerable_exposure.png"
CACHE = RESULTS / "derived/fire_consequence_125m.parquet"

FACILITY_SPECS = (
    (
        "Medical facility",
        PROCESSED / "medical_facilities_preprocessed.parquet",
        "Medical Facility ID",
        "#286f9b",
        "^",
    ),
    (
        "Welfare facility",
        PROCESSED / "welfare_facilities_preprocessed.parquet",
        "Welfare Facility ID",
        "#7f4f8f",
        "o",
    ),
    (
        "Designated shelter",
        PROCESSED / "designated_shelters_preprocessed.parquet",
        "Shelter ID",
        "#24856a",
        "s",
    ),
)

PROJECTED_CRS = 6670
GEOGRAPHIC_CRS = 6668
FIGURE_DPI = 400


def percentile_rank(values: pd.Series) -> pd.Series:
    """Apply the average-rank percentile transform in AnaSOP Section 6.1."""
    numeric = pd.to_numeric(values, errors="coerce")
    valid_n = int(numeric.notna().sum())
    if valid_n <= 1:
        return pd.Series(np.nan, index=values.index, dtype="float64")
    return (numeric.rank(method="average", na_option="keep") - 1) / (valid_n - 1)


def load_facilities(crs) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Load the three facility classes named in the Figure 3 plan."""
    frames: list[gpd.GeoDataFrame] = []
    source_counts: dict[str, int] = {}
    for label, path, identifier, color, marker in FACILITY_SPECS:
        frame = gpd.read_parquet(path, columns=[identifier, "Geometry"]).to_crs(crs)
        frame = frame.loc[frame[identifier].notna() & frame.geometry.notna()].copy()
        frame["Facility Class"] = label
        frame["Facility ID"] = frame[identifier].astype("string")
        frame["Plot Color"] = color
        frame["Plot Marker"] = marker
        source_counts[label] = len(frame)
        frames.append(frame[["Facility Class", "Facility ID", "Plot Color", "Plot Marker", "Geometry"]])
    facilities = gpd.GeoDataFrame(
        pd.concat(frames, ignore_index=True),
        geometry="Geometry",
        crs=crs,
    )
    return facilities, source_counts


def construct_consequence() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict[str, int]]:
    """Construct exposure objectives and central-scenario consequence scores."""
    mesh = gpd.read_parquet(SUSCEPTIBILITY_PATH).to_crs(PROJECTED_CRS)
    if not mesh["Mesh Code"].is_unique:
        raise ValueError("Mesh Code must be unique in the susceptibility layer")

    access = fire_service_access_layer()
    access["Mesh Code"] = access["Mesh Code"].astype("string")
    mesh["Mesh Code"] = mesh["Mesh Code"].astype("string")
    mesh = mesh.merge(access, on="Mesh Code", how="left", validate="one_to_one")

    groups = pd.read_parquet(
        POPULATION_GROUP_PATH,
        columns=["Disclosure Group Code", "Population Age 65+ Share"],
    )
    groups["Disclosure Group Code"] = groups["Disclosure Group Code"].astype("string")
    mesh["Disclosure Group Code"] = mesh["Disclosure Group Code"].astype("string")
    mesh = mesh.merge(groups, on="Disclosure Group Code", how="left", validate="many_to_one")

    facilities, source_counts = load_facilities(mesh.crs)
    assignment = gpd.sjoin(
        facilities,
        mesh[["Mesh Code", "Geometry"]],
        how="left",
        predicate="within",
    ).drop(columns="index_right")
    assigned = assignment.loc[assignment["Mesh Code"].notna()].copy()
    facility_counts = assigned.groupby("Mesh Code", sort=False).size().rename("Critical Facility Count")
    mesh = mesh.join(facility_counts, on="Mesh Code")
    mesh["Critical Facility Count"] = mesh["Critical Facility Count"].fillna(0).astype("int32")

    mesh["Population Exposure"] = percentile_rank(np.log1p(mesh["Total Population"]))
    mesh["Older Population Share Rank"] = percentile_rank(mesh["Population Age 65+ Share"])
    mesh["Older Population Vulnerability Exposure"] = (
        0.5 * mesh["Population Exposure"] + 0.5 * mesh["Older Population Share Rank"]
    )
    mesh["Critical Facility Exposure"] = percentile_rank(mesh["Critical Facility Count"])

    multiplier = 1 + mesh["Accessibility Penalty"]
    objectives = (
        ("Population", "Population Exposure"),
        ("Older Population", "Older Population Vulnerability Exposure"),
        ("Critical Facility", "Critical Facility Exposure"),
    )
    for label, exposure_column in objectives:
        consequence_column = f"{label} Conditional Fire Consequence"
        rank_column = f"{label} Conditional Fire Consequence Rank"
        mesh[consequence_column] = (
            mesh["Conditional Spread Susceptibility"]
            * mesh[exposure_column]
            * multiplier
        )
        mesh[rank_column] = percentile_rank(mesh[consequence_column])

    assigned = assigned.merge(
        mesh[
            [
                "Mesh Code",
                "Critical Facility Conditional Fire Consequence",
                "Critical Facility Conditional Fire Consequence Rank",
                "Disrupted Response Time (min)",
            ]
        ],
        on="Mesh Code",
        how="left",
        validate="many_to_one",
    )
    assigned = gpd.GeoDataFrame(assigned, geometry="Geometry", crs=mesh.crs)

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    mesh.to_parquet(CACHE, index=False)
    return mesh, assigned, source_counts


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


def make_figure(mesh: gpd.GeoDataFrame, facilities: gpd.GeoDataFrame) -> None:
    """Render the three planned consequence maps at 400 dpi."""
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
    grid = fig.add_gridspec(2, 3, height_ratios=(1, 0.035), wspace=0.07, hspace=0.035)
    axes = [fig.add_subplot(grid[0, index]) for index in range(3)]
    color_axes = [fig.add_subplot(grid[1, index]) for index in range(3)]
    norm = Normalize(0, 1)
    panel_specs = (
        (
            "Population Conditional Fire Consequence Rank",
            "Population-weighted conditional consequence (relative rank)",
            "a",
        ),
        (
            "Older Population Conditional Fire Consequence Rank",
            "Older-population conditional consequence (relative rank)",
            "b",
        ),
        (
            "Critical Facility Conditional Fire Consequence Rank",
            "Critical-facility conditional consequence (relative rank)",
            "c",
        ),
    )

    for ax, color_ax, (column, colorbar_label, panel_label) in zip(
        axes, color_axes, panel_specs, strict=True
    ):
        boundary.plot(ax=ax, color="#f0f2f3", edgecolor="none", zorder=0)
        mesh.plot(
            ax=ax,
            column=column,
            cmap="YlOrRd",
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
        draw_panel_label(ax, panel_label)

        colorbar = ColorbarBase(
            color_ax,
            cmap=mpl.colormaps["YlOrRd"],
            norm=norm,
            orientation="horizontal",
        )
        colorbar.outline.set_visible(False)
        colorbar.set_ticks([0.08, 0.5, 0.92])
        colorbar.set_ticklabels(["Lower", "Middle", "Higher"])
        colorbar.set_label(colorbar_label, fontsize=8, color="#425461")
        color_ax.tick_params(axis="x", labelsize=7.5, length=2.5, colors="#4f606d")
        color_ax.set_yticks([])
        for spine in color_ax.spines.values():
            spine.set_visible(False)

    for label, _, _, color, marker in FACILITY_SPECS:
        subset = facilities.loc[facilities["Facility Class"].eq(label)]
        subset.plot(
            ax=axes[2],
            color=color,
            marker=marker,
            markersize=2.1,
            alpha=0.52,
            linewidth=0,
            rasterized=True,
            zorder=5,
        )
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            linestyle="none",
            markerfacecolor=color,
            markeredgecolor="none",
            markersize=4.2,
            label=label,
        )
        for label, _, _, color, marker in FACILITY_SPECS
    ]
    axes[2].legend(
        handles=legend_handles,
        loc="lower left",
        frameon=True,
        framealpha=0.9,
        facecolor="white",
        edgecolor="#a9b1b7",
        fontsize=6.8,
        handletextpad=0.35,
        borderpad=0.45,
        labelspacing=0.3,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    mesh, facilities, source_counts = construct_consequence()
    make_figure(mesh, facilities)
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(f"Derived layer: {CACHE.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"cells={len(mesh):,}; "
        f"facilities assigned={len(facilities):,}/{sum(source_counts.values()):,}; "
        f"median disrupted response={mesh['Disrupted Response Time (min)'].median():.2f} min; "
        f"cells at 30-minute cap={(mesh['Disrupted Response Time (min)'] >= 30).sum():,}; "
        f"top-decile population consequence="
        f"{(mesh['Population Conditional Fire Consequence Rank'] >= 0.9).sum():,}"
    )


if __name__ == "__main__":
    main()
