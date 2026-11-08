"""
Score every checker's reports against the ground-truth manifest.

Definitions (per run):
  detected     a bug run with at least one finding on a questionnaire the bug affects
  diagnosed    a bug run with a finding on an affected questionnaire AND an accepted category
  false alarm  a clean run with at least one finding
  extra        findings on a bug run that point at a questionnaire the bug does not affect

Also:
  rule accuracy       how often the agent wrote down each scoring rule correctly
  independence audit  runs whose transcript mentions pipeline code or the answer key

Saves CSV tables in results/.

Usage (from the project folder):
    python -m evaluation.evaluate
"""

import json
import os

import pandas as pd
import yaml

from common.checker_io import INSTRUMENTS, REPORTS_DIR

RESULTS_DIR = "results"
FORBIDDEN_WORDS = ["pipelines/", "ground_truth", "manifest.csv", "reference_pipeline", "bug_definitions"]

CHECKER_ORDER = ["rule_based", "agent"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def split_list(text):
    if pd.isna(text) or text == "":
        return []
    return str(text).split(";")


def collect_runs():
    """Read every findings.json under reports/."""
    runs = []
    if not os.path.isdir(REPORTS_DIR):
        return runs
    for checker in sorted(os.listdir(REPORTS_DIR)):
        checker_dir = os.path.join(REPORTS_DIR, checker)
        if not os.path.isdir(checker_dir):
            continue
        for pipeline_id in sorted(os.listdir(checker_dir)):
            pipeline_dir = os.path.join(checker_dir, pipeline_id)
            for run_name in sorted(os.listdir(pipeline_dir)):
                folder = os.path.join(pipeline_dir, run_name)
                findings_path = os.path.join(folder, "findings.json")
                if not os.path.exists(findings_path):
                    continue
                runs.append({
                    "checker": checker,
                    "pipeline_id": pipeline_id,
                    "run": run_name,
                    "folder": folder,
                    "result": load_json(findings_path),
                    "usage": load_json(os.path.join(folder, "usage.json")),
                })
    return runs


def score_run(run, bug):
    findings = run["result"].get("findings", [])
    bug_instruments = split_list(bug["instruments"])
    accepted = split_list(bug["accepted_categories"])

    on_target = []
    extra = []
    for finding in findings:
        if finding["instrument"] in bug_instruments:
            on_target.append(finding)
        else:
            extra.append(finding)

    if bug["has_bug"]:
        detected = len(on_target) > 0
        diagnosed = False
        for finding in on_target:
            if finding["category"] in accepted:
                diagnosed = True
        false_alarm = None
    else:
        detected = None
        diagnosed = None
        false_alarm = len(findings) > 0

    return {
        "checker": run["checker"],
        "pipeline_id": run["pipeline_id"],
        "run": run["run"],
        "bug_id": bug["bug_id"],
        "has_bug": bug["has_bug"],
        "category": bug["category"],
        "verdict": run["result"].get("verdict"),
        "n_findings": len(findings),
        "detected": detected,
        "diagnosed": diagnosed,
        "false_alarm": false_alarm,
        "extra_findings": len(extra) if bug["has_bug"] else None,
        "finding_categories": ";".join(f"{f['instrument']}:{f['category']}" for f in findings),
        "input_tokens": run["usage"].get("input_tokens", 0),
        "output_tokens": run["usage"].get("output_tokens", 0),
        "seconds": run["usage"].get("seconds", 0),
        "turns": run["usage"].get("turns", 0),
    }


def rule_accuracy(runs):
    """Compare the agent's rules_understood with the YAML specs."""
    truth = {}
    for name in INSTRUMENTS:
        with open(f"specs/{name}.yaml") as f:
            spec = yaml.safe_load(f)
        levels = spec.get("bands", {}).get("levels", [])
        truth[name] = {
            "n_items": len(spec["items"]["columns"]),
            "reverse_items": sorted(spec["reverse_items"]["items"]),
            "max_missing_items": spec["missing_data"]["max_missing_items"],
            "half_rounding": "up",
            "band_starts": [level["min"] for level in levels],
        }

    rows = []
    for run in runs:
        understood = run["result"].get("rules_understood")
        if not understood:
            continue
        for name in INSTRUMENTS:
            given = understood.get(name, {}) or {}
            for rule, correct_value in truth[name].items():
                value = given.get(rule)
                if isinstance(value, list):
                    value = sorted(value)
                rows.append({
                    "checker": run["checker"],
                    "instrument": name,
                    "rule": rule,
                    "correct": value == correct_value,
                })
    return pd.DataFrame(rows)


def independence_audit(runs):
    flagged = []
    for run in runs:
        transcript_path = os.path.join(run["folder"], "transcript.json")
        if not os.path.exists(transcript_path):
            continue
        with open(transcript_path) as f:
            text = f.read()
        for word in FORBIDDEN_WORDS:
            if word in text:
                flagged.append({"checker": run["checker"], "pipeline_id": run["pipeline_id"], "run": run["run"], "word": word})
    return pd.DataFrame(flagged, columns=["checker", "pipeline_id", "run", "word"])


def summarise(per_run):
    rows = []
    checkers = [c for c in CHECKER_ORDER if c in set(per_run["checker"])]
    checkers += sorted(set(per_run["checker"]) - set(checkers))

    for checker in checkers:
        part = per_run[per_run["checker"] == checker]
        bug_runs = part[part["has_bug"]]
        clean_runs = part[~part["has_bug"]]

        rows.append({
            "checker": checker,
            "bug_runs": len(bug_runs),
            "clean_runs": len(clean_runs),
            "detection_rate": bug_runs["detected"].astype(bool).mean() if len(bug_runs) else None,
            "diagnosis_rate": bug_runs["diagnosed"].astype(bool).mean() if len(bug_runs) else None,
            "false_alarm_rate": clean_runs["false_alarm"].astype(bool).mean() if len(clean_runs) else None,
            "false_alarms": int(clean_runs["false_alarm"].astype(bool).sum()) if len(clean_runs) else 0,
            "mean_extra_findings": bug_runs["extra_findings"].mean() if len(bug_runs) else None,
            "mean_seconds_per_audit": part["seconds"].mean(),
            "mean_tokens_per_audit": (part["input_tokens"] + part["output_tokens"]).mean(),
            "mean_turns_per_audit": part["turns"].mean(),
        })
    return pd.DataFrame(rows)


def by_category(per_run):
    bug_runs = per_run[per_run["has_bug"]].copy()
    bug_runs["detected"] = bug_runs["detected"].astype(bool)
    bug_runs["diagnosed"] = bug_runs["diagnosed"].astype(bool)
    table = bug_runs.groupby(["checker", "category"]).agg(
        runs=("detected", "size"),
        detection_rate=("detected", "mean"),
        diagnosis_rate=("diagnosed", "mean"),
    )
    return table.reset_index()


def failures(per_run, manifest):
    descriptions = dict(zip(manifest["bug_id"], manifest["description"]))
    missed = per_run[
        (per_run["has_bug"] & ((per_run["detected"] == False) | (per_run["diagnosed"] == False)))
        | ((~per_run["has_bug"]) & (per_run["false_alarm"] == True))
    ].copy()

    kinds = []
    for _, row in missed.iterrows():
        if not row["has_bug"]:
            kinds.append("false_alarm")
        elif not row["detected"]:
            kinds.append("missed")
        else:
            kinds.append("detected_wrong_category")
    missed["failure_type"] = kinds
    missed["bug_description"] = missed["bug_id"].map(descriptions)

    columns = ["checker", "pipeline_id", "run", "bug_id", "category", "failure_type", "finding_categories", "bug_description"]
    return missed[columns]


def main():
    manifest = pd.read_csv("ground_truth/manifest.csv")
    bugs = {}
    for _, row in manifest.iterrows():
        bugs[row["pipeline_id"]] = row

    runs = collect_runs()
    if not runs:
        print("No reports found. Run evaluation/run_all.py first.")
        return

    per_run = pd.DataFrame([score_run(run, bugs[run["pipeline_id"]]) for run in runs])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    per_run.to_csv(f"{RESULTS_DIR}/per_run.csv", index=False)

    summary = summarise(per_run)
    summary.to_csv(f"{RESULTS_DIR}/summary.csv", index=False)

    categories = by_category(per_run)
    categories.to_csv(f"{RESULTS_DIR}/by_category.csv", index=False)

    failure_table = failures(per_run, manifest)
    failure_table.to_csv(f"{RESULTS_DIR}/failures.csv", index=False)

    rules = rule_accuracy(runs)
    if len(rules):
        rule_table = rules.groupby(["checker", "instrument", "rule"])["correct"].mean().reset_index()
        rule_table.to_csv(f"{RESULTS_DIR}/rule_accuracy.csv", index=False)

    audit = independence_audit(runs)
    audit.to_csv(f"{RESULTS_DIR}/independence_audit.csv", index=False)

    pd.set_option("display.width", 200)
    print("=== Summary ===")
    print(summary.round(3).to_string(index=False))
    print()
    print("=== Detection rate by bug category ===")
    print(categories.pivot(index="category", columns="checker", values="detection_rate").round(2).to_string())
    print()
    print("=== Hypothesis check: detection >= 90% and false alarms < 5% ===")
    for _, row in summary.iterrows():
        if row["detection_rate"] is None or row["false_alarm_rate"] is None:
            continue
        meets = row["detection_rate"] >= 0.90 and row["false_alarm_rate"] < 0.05
        print(f"  {row['checker']:22s} detection {row['detection_rate']:.0%}  false alarms {row['false_alarms']}/{row['clean_runs']}  -> {'meets' if meets else 'does not meet'}")
    print()
    print(f"Failures listed: {len(failure_table)}  (results/failures.csv)")
    print(f"Independence audit flags: {len(audit)}  (results/independence_audit.csv)")
    if len(rules):
        print("Rule accuracy saved: results/rule_accuracy.csv")


if __name__ == "__main__":
    main()
