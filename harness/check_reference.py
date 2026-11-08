"""
Check the reference pipeline:
  1. It gets every worked example in the specs right.
  2. Show how scores are spread in the synthetic data, and how many people
     land exactly on each cutoff (cutoff bugs only show up if someone does).
  3. Save a score-distribution chart to charts/.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from reference_pipeline import (
    GAD7_ITEMS,
    PHQ9_ITEMS,
    RSES_ITEMS,
    score_all,
    score_gad7,
    score_phq9,
    score_rses,
)

# Chart colors
BAR_COLOR = "#2a78d6"
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"


def load_spec(name):
    with open(f"specs/{name}.yaml") as f:
        return yaml.safe_load(f)


def check_worked_examples():
    checks = [
        ("phq9", PHQ9_ITEMS, score_phq9),
        ("gad7", GAD7_ITEMS, score_gad7),
        ("rses", RSES_ITEMS, score_rses),
    ]

    n_failed = 0
    for name, item_cols, score_function in checks:
        spec = load_spec(name)
        for example in spec["worked_examples"]:
            row = dict(zip(item_cols, example["items"]))
            result = score_function(row)

            expected = example["expected"]
            mismatches = []
            for key, expected_value in expected.items():
                actual_value = result[f"{name}_{key}"]
                if actual_value != expected_value:
                    mismatches.append(f"{key}: expected {expected_value}, got {actual_value}")

            if mismatches:
                n_failed += 1
                print(f"  FAIL {name}: {example['name']} -> {'; '.join(mismatches)}")
            else:
                print(f"  PASS {name}: {example['name']}")

    return n_failed


def show_cutoff_counts(scores):
    cutoffs = {
        "phq9_total": [5, 10, 15, 20],
        "gad7_total": [5, 10, 15],
    }
    for col, values in cutoffs.items():
        parts = []
        for cutoff in values:
            n_exact = (scores[col] == cutoff).sum()
            parts.append(f"{cutoff}: {n_exact}")
        print(f"  {col}: " + ", ".join(parts))


def save_chart(scores):
    panels = [
        ("PHQ-9 total", "phq9_total", 27, [5, 10, 15, 20]),
        ("GAD-7 total", "gad7_total", 21, [5, 10, 15]),
        ("Rosenberg total", "rses_total", 30, []),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), facecolor=SURFACE)

    for ax, (title, col, max_score, cutoffs) in zip(axes, panels):
        values = scores[col].dropna().astype(int)
        counts = values.value_counts().reindex(range(max_score + 1), fill_value=0)

        ax.set_facecolor(SURFACE)
        ax.bar(counts.index, counts.values, width=0.85, color=BAR_COLOR, edgecolor=SURFACE, linewidth=1)

        for cutoff in cutoffs:
            ax.axvline(cutoff - 0.5, color=MUTED, linestyle="--", linewidth=1)

        n_blank = scores[col].isna().sum()
        ax.set_title(f"{title}  (n = {len(values)}, blank = {n_blank})", color=TEXT, fontsize=11, loc="left")
        ax.set_xlabel("Score", color=MUTED)
        ax.set_xlim(-1, max_score + 1)
        ax.tick_params(colors=MUTED)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ["top", "right", "left"]:
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)

    axes[0].set_ylabel("Respondents", color=MUTED)
    fig.suptitle("Reference scores on synthetic data (dashed lines = band cutoffs)", color=TEXT, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig("charts/reference_score_distributions.png", dpi=150, facecolor=SURFACE)
    print("  Saved charts/reference_score_distributions.png")


def main():
    print("1. Worked examples from the specs:")
    n_failed = check_worked_examples()
    print(f"  -> {n_failed} failed")
    print()

    data = pd.read_csv("data/raw_responses.csv")
    scores = score_all(data)

    print("2. Band counts:")
    print("  PHQ-9:", scores["phq9_band"].value_counts(dropna=False).to_dict())
    print("  GAD-7:", scores["gad7_band"].value_counts(dropna=False).to_dict())
    print()

    print("3. Respondents landing exactly on each cutoff:")
    show_cutoff_counts(scores)
    print()

    print("4. Prorated respondents:")
    for col in ["phq9_prorated", "gad7_prorated", "rses_prorated"]:
        n_true = (scores[col] == True).sum()
        print(f"  {col}: {n_true}")
    print()

    print("5. Chart:")
    save_chart(scores)


if __name__ == "__main__":
    main()
