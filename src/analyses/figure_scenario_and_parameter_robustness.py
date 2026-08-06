#!/usr/bin/env python3
"""Scenario and Parameter Robustness

Plan: show response reliability across road-failure mechanisms and severities,
then summarize fire-base priority stability and fixed-plan road-restoration benefit
across multiple 3% road states.
Framework: AnaSOP Sections 6.4, 6.6, 6.8, and workflow step 8.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import seaborn as sns

from fire_base_criticality_robustness_common import load_criticality_robustness
from robustness_analysis_common import MODELS, load_robustness


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data/results/figures/Figure_scenario_and_parameter_robustness.png"
FIGURE_DPI = 400

MODEL_LABELS = {
    "Length-dependent independent": "Length-dependent",
    "Spatially clustered": "Spatially clustered",
    "Hazard-weighted": "Hazard-weighted",
}
MODEL_COLORS = {
    "Length-dependent independent": "#2d7892",
    "Spatially clustered": "#d06b42",
    "Hazard-weighted": "#6f559a",
}
RULE_COLORS = {
    "Section count": "#2d7892",
    "Length-aware": "#d06b42",
}
RULE_MARKERS = {
    "Section count": "o",
    "Length-aware": "s",
}


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


def make_figure(
    road_summary: pd.DataFrame,
    station_stability: pd.DataFrame,
    intervention_stability: pd.DataFrame,
) -> None:
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
    fig = plt.figure(figsize=(13.4, 9.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 0.78), wspace=0.14, hspace=0.20)
    road_ax = fig.add_subplot(grid[0, 0])
    station_ax = fig.add_subplot(grid[0, 1])
    intervention_ax = fig.add_subplot(grid[1, :])
    axes = (road_ax, station_ax, intervention_ax)

    for model in MODELS:
        subset = road_summary.loc[
            road_summary["Road Failure Model"].eq(model)
        ].sort_values("Expected Failed Road Length Share")
        x = 100 * subset["Expected Failed Road Length Share"].to_numpy(float)
        mean = 100 * subset["Mean Timely Response Probability"].to_numpy(float)
        lower = 100 * subset["P10 Timely Response Probability"].to_numpy(float)
        upper = 100 * subset["P90 Timely Response Probability"].to_numpy(float)
        road_ax.fill_between(x, lower, upper, color=MODEL_COLORS[model], alpha=0.13)
        road_ax.plot(
            x,
            mean,
            marker="o",
            markersize=4.5,
            linewidth=1.7,
            color=MODEL_COLORS[model],
            label=MODEL_LABELS[model],
        )
    road_ax.set_xticks([1, 3, 5, 10])
    road_ax.set_xlabel("Nominal failed-road input (%)", fontsize=9)
    road_ax.set_ylabel("Population within 10-minute response (%)", fontsize=9)
    road_ax.tick_params(labelsize=8)
    road_ax.grid(color="#d6dadd", linewidth=0.55)
    road_ax.legend(frameon=False, fontsize=7.3, loc="lower left")
    sns.despine(ax=road_ax)

    population_stability = station_stability.loc[
        station_stability["Exposure Objective"].eq("Population")
    ].copy()
    retained = (
        population_stability.groupby("Road Failure Model")["Top Ten Fire Base Overlap"]
        .agg(["median", "min", "max"])
        .reindex(MODELS)
        * 10
    )
    station_x = np.arange(len(MODELS))
    station_bars = station_ax.bar(
        station_x,
        retained["median"].to_numpy(float),
        color=[MODEL_COLORS[model] for model in MODELS],
        width=0.62,
        zorder=3,
    )
    station_ax.errorbar(
        station_x,
        retained["median"].to_numpy(float),
        yerr=np.vstack(
            [
                retained["median"].to_numpy(float) - retained["min"].to_numpy(float),
                retained["max"].to_numpy(float) - retained["median"].to_numpy(float),
            ]
        ),
        fmt="none",
        ecolor="#263746",
        elinewidth=1.1,
        capsize=4,
        zorder=4,
    )
    for x_value, upper, median in zip(
        station_x,
        retained["max"].to_numpy(float),
        retained["median"].to_numpy(float),
        strict=True,
    ):
        station_ax.text(
            x_value,
            upper + 0.16,
            f"median {median:g} of 10",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#425461",
        )
    station_ax.set_xticks(station_x)
    station_ax.set_xticklabels([MODEL_LABELS[model] for model in MODELS], fontsize=8)
    station_ax.set_ylabel("Event-road top 10 fire bases retained", fontsize=9)
    station_ax.set_xlabel(
        "Road failure pattern under the nominal 3% input\n"
        "(range across 10 stratified states)",
        fontsize=9,
    )
    station_ax.set_ylim(0, 11.0)
    station_ax.set_yticks(range(0, 11, 2))
    station_ax.tick_params(axis="y", labelsize=8)
    station_ax.grid(axis="y", color="#d6dadd", linewidth=0.55)
    station_ax.grid(axis="x", visible=False)
    sns.despine(ax=station_ax)

    intervention_summary = (
        intervention_stability.groupby(
            ["Road Failure Model", "Road Priority Rule"],
            as_index=False,
        )["Retained Protection Gain Share"]
        .agg(
            Median="median",
            **{
                "Lower Quartile": lambda values: values.quantile(0.25),
                "Worst State": "min",
            },
        )
    )
    intervention_x = np.arange(len(MODELS), dtype=float)
    offsets = {"Section count": -0.13, "Length-aware": 0.13}
    plotted_values: list[float] = []
    for rule in ("Section count", "Length-aware"):
        subset = (
            intervention_summary.loc[
                intervention_summary["Road Priority Rule"].eq(rule)
            ]
            .set_index("Road Failure Model")
            .reindex(MODELS)
        )
        x = intervention_x + offsets[rule]
        median = 100 * subset["Median"].to_numpy(float)
        lower_quartile = 100 * subset["Lower Quartile"].to_numpy(float)
        worst = 100 * subset["Worst State"].to_numpy(float)
        plotted_values.extend(median.tolist() + lower_quartile.tolist() + worst.tolist())
        intervention_ax.vlines(
            x,
            worst,
            median,
            color=RULE_COLORS[rule],
            linewidth=1.5,
            zorder=2,
        )
        intervention_ax.hlines(
            worst,
            x - 0.045,
            x + 0.045,
            color=RULE_COLORS[rule],
            linewidth=1.5,
            zorder=3,
        )
        intervention_ax.scatter(
            x,
            lower_quartile,
            marker="D",
            s=31,
            facecolor="white",
            edgecolor=RULE_COLORS[rule],
            linewidth=1.25,
            zorder=4,
        )
        intervention_ax.scatter(
            x,
            median,
            marker=RULE_MARKERS[rule],
            s=48,
            color=RULE_COLORS[rule],
            edgecolor="white",
            linewidth=0.7,
            zorder=5,
        )
        for x_value, value in zip(x, median, strict=True):
            intervention_ax.annotate(
                f"{value:.1f}",
                (x_value, value),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.4,
                color="#425461",
            )
        for x_value, value in zip(x, worst, strict=True):
            intervention_ax.annotate(
                f"{value:.1f}",
                (x_value, value),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.2,
                color=RULE_COLORS[rule],
            )
    intervention_ax.axhline(
        100,
        color="#8a969e",
        linestyle="--",
        linewidth=0.9,
        zorder=1,
    )
    intervention_ax.set_xticks(intervention_x)
    intervention_ax.set_xticklabels(
        [MODEL_LABELS[model] for model in MODELS],
        fontsize=8,
    )
    intervention_ax.set_ylabel(
        "Retained road-restoration protection gain\nrelative to the event-specific case (%)",
        fontsize=9,
    )
    intervention_ax.set_xlabel(
        "Same preselected plan tested in 100 road states per pattern under the nominal 3% input",
        fontsize=9,
    )
    finite_values = np.asarray(plotted_values, dtype=float)
    finite_values = finite_values[np.isfinite(finite_values)]
    lower_limit = max(0.0, 5 * np.floor(finite_values.min() / 5) - 5)
    upper_limit = 5 * np.ceil(max(100.0, finite_values.max()) / 5) + 5
    intervention_ax.set_ylim(lower_limit, upper_limit)
    intervention_ax.tick_params(axis="y", labelsize=8)
    intervention_ax.grid(axis="y", color="#d6dadd", linewidth=0.55)
    intervention_ax.grid(axis="x", visible=False)
    legend_handles = [
        Line2D(
            [0],
            [0],
            color=RULE_COLORS[rule],
            marker=RULE_MARKERS[rule],
            linewidth=1.5,
            markersize=5.5,
            label=rule,
        )
        for rule in ("Section count", "Length-aware")
    ] + [
        Line2D([0], [0], marker="o", color="#425461", linestyle="none", markersize=5, label="Median"),
        Line2D([0], [0], marker="D", markerfacecolor="white", markeredgecolor="#425461", color="none", linestyle="none", markersize=5, label="Lower quartile"),
        Line2D([0], [0], marker="_", color="#425461", linestyle="none", markersize=8, label="Lowest state"),
    ]
    intervention_ax.legend(
        handles=legend_handles,
        frameon=False,
        fontsize=7.2,
        ncol=5,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.025),
    )
    sns.despine(ax=intervention_ax)

    for label, ax in zip("abc", axes, strict=True):
        draw_panel_label(ax, label)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    _, road_summary, _, intervention_stability = load_robustness()
    _, station_stability, _ = load_criticality_robustness()
    make_figure(road_summary, station_stability, intervention_stability)
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"road scenarios={len(road_summary)}; "
        f"fire-base states={len(station_stability.loc[station_stability['Exposure Objective'].eq('Population')])}; "
        f"minimum top-10 base overlap={100 * station_stability.loc[station_stability['Exposure Objective'].eq('Population'), 'Top Ten Fire Base Overlap'].min():.0f}%; "
        f"intervention state evaluations={len(intervention_stability)}; "
        f"minimum retained intervention gain={100 * intervention_stability['Retained Protection Gain Share'].min():.1f}%"
    )


if __name__ == "__main__":
    main()
