"""
Charts from the evaluation tables in results/. Saved as PNGs in charts/.

  charts/detection_by_category.png   detection rate per bug category, per checker
  charts/overall_rates.png           detection, diagnosis and false-alarm rate per checker
  charts/time_per_audit.png          mean seconds per audit, per checker

Usage (from the project folder):
    python -m evaluation.plot_results
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from evaluation.evaluate import CHECKER_ORDER

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"

# One fixed color per checker, so a checker keeps its color in every chart
CHECKER_COLORS = {
    "rule_based": "#2a78d6",
    "agent": "#eb6834",
}

CATEGORY_ORDER = ["reverse_coding", "missing_data", "item_set", "cutoff_bands", "off_by_one"]


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)


def ordered_checkers(names):
    present = [c for c in CHECKER_ORDER if c in set(names)]
    return present + sorted(set(names) - set(present))


def grouped_bars(ax, groups, checkers, values_for):
    """Draw one bar per checker inside each group."""
    width = 0.8 / len(checkers)
    x = np.arange(len(groups))
    for i, checker in enumerate(checkers):
        values = [values_for(checker, group) for group in groups]
        positions = x - 0.4 + width * (i + 0.5)
        ax.bar(positions, values, width=width * 0.92, color=CHECKER_COLORS.get(checker, MUTED), label=checker)
        # Value labels, so no one has to judge bar heights by color alone
        for position, number in zip(positions, values):
            ax.text(position, number + 1, f"{number:.0f}", ha="center", va="bottom", fontsize=7, color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, color=TEXT)


def detection_by_category_chart(categories):
    checkers = ordered_checkers(categories["checker"].unique())
    groups = [c for c in CATEGORY_ORDER if c in set(categories["category"])]

    def value(checker, group):
        match = categories[(categories["checker"] == checker) & (categories["category"] == group)]
        return match["detection_rate"].iloc[0] * 100 if len(match) else 0

    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor=SURFACE)
    style_axis(ax)
    grouped_bars(ax, groups, checkers, value)
    ax.axhline(90, color=MUTED, linestyle="--", linewidth=1)
    ax.text(len(groups) - 0.5, 91, "90% target", color=MUTED, ha="right", fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Detection rate (%)", color=MUTED)
    ax.set_title("Detection rate by bug category", color=TEXT, loc="left")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig("charts/detection_by_category.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


def overall_rates_chart(summary):
    checkers = ordered_checkers(summary["checker"])
    groups = ["detection_rate", "diagnosis_rate", "false_alarm_rate"]
    labels = ["Detection", "Diagnosis", "False alarms"]

    def value(checker, group):
        number = summary.loc[summary["checker"] == checker, group].iloc[0]
        return 0 if pd.isna(number) else number * 100

    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=SURFACE)
    style_axis(ax)
    grouped_bars(ax, groups, checkers, value)
    ax.set_xticklabels(labels, color=TEXT)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Rate (%)", color=MUTED)
    ax.set_title("Overall detection, diagnosis and false-alarm rates", color=TEXT, loc="left")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig("charts/overall_rates.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


def time_per_audit_chart(summary):
    checkers = ordered_checkers(summary["checker"])
    colors = [CHECKER_COLORS.get(c, MUTED) for c in checkers]
    seconds = [summary.loc[summary["checker"] == c, "mean_seconds_per_audit"].iloc[0] for c in checkers]

    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor=SURFACE)
    style_axis(ax)
    ax.bar(range(len(checkers)), seconds, color=colors, width=0.6)
    for position, number in enumerate(seconds):
        ax.text(position, number, f"{number:.1f}s", ha="center", va="bottom", fontsize=9, color=TEXT)
    ax.set_xticks(range(len(checkers)))
    ax.set_xticklabels(checkers, color=TEXT)
    ax.set_ylabel("Seconds", color=MUTED)
    ax.set_title("Mean time per audit", color=TEXT, loc="left")
    fig.tight_layout()
    fig.savefig("charts/time_per_audit.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main():
    summary = pd.read_csv("results/summary.csv")
    categories = pd.read_csv("results/by_category.csv")

    detection_by_category_chart(categories)
    overall_rates_chart(summary)
    time_per_audit_chart(summary)
    print("Saved charts/detection_by_category.png, charts/overall_rates.png, charts/time_per_audit.png")


if __name__ == "__main__":
    main()
