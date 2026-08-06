#!/usr/bin/env python3
"""Scenario and Parameter Robustness

Plan: show response reliability across road-failure mechanisms and severities,
then summarize fire-base and road-restoration priority overlap at 3% severity.
Framework: AnaSOP Sections 6.4, 6.6, 6.8, and workflow step 8.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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
    road_ax.set_xlabel("Expected failed road length (%)", fontsize=9)
    road_ax.set_ylabel("Population within 10-minute response (%)", fontsize=9)
    road_ax.tick_params(labelsize=8)
    road_ax.grid(color="#d6dadd", linewidth=0.55)
    road_ax.legend(frameon=False, fontsize=7.3, loc="lower left")
    sns.despine(ax=road_ax)

    retained = (
        station_stability.groupby("Road Failure Model")["Top Ten Fire Base Overlap"]
        .min()
        .reindex(MODELS)
        * 10
    )
    station_x = np.arange(len(MODELS))
    station_bars = station_ax.bar(
        station_x,
        retained.to_numpy(float),
        color=[MODEL_COLORS[model] for model in MODELS],
        width=0.62,
        zorder=3,
    )
    station_ax.bar_label(
        station_bars,
        labels=[f"{value:.0f} of 10" for value in retained],
        fontsize=8,
        padding=3,
        color="#425461",
    )
    station_ax.set_xticks(station_x)
    station_ax.set_xticklabels([MODEL_LABELS[model] for model in MODELS], fontsize=8)
    station_ax.set_ylabel("Original priority fire bases retained", fontsize=9)
    station_ax.set_xlabel("Road failure pattern at 3% severity", fontsize=9)
    station_ax.set_ylim(0, 10.8)
    station_ax.set_yticks(range(0, 11, 2))
    station_ax.tick_params(axis="y", labelsize=8)
    station_ax.grid(axis="y", color="#d6dadd", linewidth=0.55)
    station_ax.grid(axis="x", visible=False)
    sns.despine(ax=station_ax)

    conservative_retained = (
        intervention_stability.groupby("Road Failure Model")[
            "Retained Protection Gain Share"
        ]
        .min()
        .reindex(MODELS)
    )
    protection_loss = 100 * (1 - conservative_retained.to_numpy(float))
    intervention_x = np.arange(len(MODELS), dtype=float)
    loss_bars = intervention_ax.bar(
        intervention_x,
        protection_loss,
        width=0.62,
        color=[MODEL_COLORS[model] for model in MODELS],
        zorder=3,
    )
    intervention_ax.bar_label(
        loss_bars,
        labels=[f"{value:.1f}%" for value in protection_loss],
        fontsize=8,
        padding=3,
        color="#425461",
    )
    intervention_ax.set_xticks(intervention_x)
    intervention_ax.set_xticklabels(
        [MODEL_LABELS[model] for model in MODELS],
        fontsize=8,
    )
    intervention_ax.set_ylabel(
        "Road-restoration protection gain lost\nrelative to the event-specific case (%)",
        fontsize=9,
    )
    intervention_ax.set_xlabel("Road failure pattern at 3% severity", fontsize=9)
    intervention_ax.set_ylim(0, float(np.nanmax(protection_loss)) * 1.22)
    intervention_ax.tick_params(axis="y", labelsize=8)
    intervention_ax.grid(axis="y", color="#d6dadd", linewidth=0.55)
    intervention_ax.grid(axis="x", visible=False)
    sns.despine(ax=intervention_ax)

    for label, ax in zip("abc", axes, strict=True):
        draw_panel_label(ax, label)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    _, road_summary, station_stability, intervention_stability = load_robustness()
    make_figure(road_summary, station_stability, intervention_stability)
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")
    print(
        "Diagnostics: "
        f"road scenarios={len(road_summary)}; "
        f"minimum top-10 base overlap={100 * station_stability['Top Ten Fire Base Overlap'].min():.0f}%; "
        f"minimum top-3 road overlap={100 * intervention_stability['Top Three Road Priority Overlap'].min():.0f}%"
    )


if __name__ == "__main__":
    main()
