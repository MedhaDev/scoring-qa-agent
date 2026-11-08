"""
Baseline 1: a rule-based QA script (no AI).

This is the kind of automated check a team typically writes: it reads the
structured YAML specs and runs consistency checks on the pipeline output.
It does NOT re-score the data from scratch. It checks:

  1. Totals are inside the allowed range.
  2. Each severity label matches its total, using the spec's bands.
  3. The total is blank exactly when too many items are missing.
  4. The prorated flag is True exactly when one item is missing.

Usage (from the project folder):
    python -m baselines.rule_based_checker pipeline_01
"""

import sys
import time

import pandas as pd
import yaml

from common.checker_io import INSTRUMENTS, build_workspace, remove_workspace, run_dir, save_run

CHECKER_NAME = "rule_based"
MAX_EXAMPLE_IDS = 5


def load_spec(name):
    with open(f"specs/{name}.yaml") as f:
        return yaml.safe_load(f)


def is_blank(value):
    return pd.isna(value) or value == ""


def count_missing(row, item_cols, valid_values):
    n_missing = 0
    for col in item_cols:
        value = row[col]
        if pd.isna(value) or value not in valid_values:
            n_missing += 1
    return n_missing


def expected_band(total, levels):
    for level in levels:
        if level["min"] <= total <= level["max"]:
            return level["label"]
    return None


def add_problem(problems, key, respondent_id):
    """Group problems by (instrument, category, column, description)."""
    if key not in problems:
        problems[key] = []
    problems[key].append(respondent_id)


def check_instrument(name, raw, output, problems):
    spec = load_spec(name)
    item_cols = spec["items"]["columns"]
    valid_values = spec["items"]["valid_values"]
    max_missing = spec["missing_data"]["max_missing_items"]
    low, high = spec["total"]["range"]
    levels = spec.get("bands", {}).get("levels", [])

    total_col = f"{name}_total"
    band_col = f"{name}_band"
    prorated_col = f"{name}_prorated"

    for i in range(len(raw)):
        raw_row = raw.iloc[i]
        out_row = output.iloc[i]
        rid = raw_row["respondent_id"]

        n_missing = count_missing(raw_row, item_cols, valid_values)
        total = out_row[total_col]

        # Check 3: blank total exactly when too many items are missing
        if n_missing > max_missing and not is_blank(total):
            add_problem(problems, (name, "missing_data", total_col, "total given although too many items are missing"), rid)
        if n_missing <= max_missing and is_blank(total):
            add_problem(problems, (name, "missing_data", total_col, "total blank although enough items were answered"), rid)

        if is_blank(total):
            continue

        total = float(total)

        # Check 1: range
        if total < low or total > high:
            add_problem(problems, (name, "other", total_col, f"total outside the allowed range {low}-{high}"), rid)

        # Check 2: band matches total
        if levels:
            band = out_row[band_col]
            if band != expected_band(total, levels):
                add_problem(problems, (name, "cutoff_bands", band_col, "severity label does not match the total"), rid)

        # Check 4: prorated flag
        prorated = str(out_row[prorated_col])
        if n_missing == 1 and prorated != "True":
            add_problem(problems, (name, "missing_data", prorated_col, "one item missing but not marked as prorated"), rid)
        if n_missing == 0 and prorated != "False":
            add_problem(problems, (name, "missing_data", prorated_col, "no items missing but marked as prorated"), rid)


def run_check(pipeline_id, folder):
    start = time.time()
    workspace = build_workspace(pipeline_id)
    raw = pd.read_csv(f"{workspace}/raw_responses.csv")
    output = pd.read_csv(f"{workspace}/pipeline_output.csv", dtype=str, keep_default_na=False)
    remove_workspace(workspace)

    problems = {}
    for name in INSTRUMENTS:
        check_instrument(name, raw, output, problems)

    findings = []
    report_lines = [f"# Rule-based QA report: {pipeline_id}", ""]
    for (instrument, category, column, description), ids in problems.items():
        findings.append({
            "instrument": instrument,
            "category": category,
            "columns": column,
            "description": description,
            "evidence": "Example respondents: " + ", ".join(ids[:MAX_EXAMPLE_IDS]),
            "rows_affected": len(ids),
            "confirmed": True,
        })
        report_lines.append(f"- **{instrument} / {column}**: {description} ({len(ids)} rows)")

    if not findings:
        report_lines.append("All checks passed.")

    result = {
        "verdict": "issues_found" if findings else "pass",
        "findings": findings,
    }
    usage = {
        "checker": CHECKER_NAME,
        "model": "none",
        "input_tokens": 0,
        "output_tokens": 0,
        "seconds": round(time.time() - start, 2),
        "turns": 0,
    }
    save_run(folder, result, "\n".join(report_lines) + "\n", usage)
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m baselines.rule_based_checker <pipeline_id>")
        sys.exit(1)
    pipeline_id = sys.argv[1]
    folder = run_dir(CHECKER_NAME, pipeline_id, 1)
    result = run_check(pipeline_id, folder)
    print(f"{pipeline_id}: {result['verdict']} ({len(result['findings'])} findings) -> {folder}")


if __name__ == "__main__":
    main()
