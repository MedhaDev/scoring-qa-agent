"""
Sanity-check the test harness before any checker is evaluated on it.

  - Clean copies must match the reference output exactly.
  - Every buggy copy must differ from the reference on at least one row,
    otherwise the bug is invisible in the data and can't fairly be counted as missed.

Also records, for each copy, how many rows and which columns the bug changes.
Saves ground_truth/harness_check.csv.

Usage:
    python harness/check_harness.py
"""

import pandas as pd


def load_scores(path):
    # Read everything as text so blanks and True/False compare exactly
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def main():
    manifest = pd.read_csv("ground_truth/manifest.csv")
    reference = load_scores("outputs/reference/scores.csv")

    rows = []
    n_problems = 0

    for _, entry in manifest.iterrows():
        pipeline_id = entry["pipeline_id"]
        output = load_scores(f"outputs/{pipeline_id}/scores.csv")

        same_shape = list(output.columns) == list(reference.columns) and len(output) == len(reference)
        if not same_shape:
            raise ValueError(f"{pipeline_id}: output has a different shape or columns than the reference")

        differs = output != reference
        changed_columns = [col for col in reference.columns if differs[col].any()]
        n_rows_changed = int(differs.any(axis=1).sum())

        if entry["has_bug"]:
            ok = n_rows_changed > 0
        else:
            ok = n_rows_changed == 0

        status = "OK" if ok else "PROBLEM"
        if not ok:
            n_problems += 1

        print(f"{status:7s} {pipeline_id}  {entry['bug_id']:32s} rows changed: {n_rows_changed:4d}  columns: {', '.join(changed_columns)}")

        rows.append({
            "pipeline_id": pipeline_id,
            "bug_id": entry["bug_id"],
            "rows_changed": n_rows_changed,
            "columns_changed": ";".join(changed_columns),
            "check": status,
        })

    pd.DataFrame(rows).to_csv("ground_truth/harness_check.csv", index=False)
    print()
    print(f"{n_problems} problems. Saved ground_truth/harness_check.csv")


if __name__ == "__main__":
    main()
