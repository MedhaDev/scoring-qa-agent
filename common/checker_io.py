"""
Shared helpers for all checkers (rule-based, single-prompt, agent).

  - build_workspace(): makes a fresh folder holding ONLY what a checker may see:
    the scoring guides, the raw data, and one pipeline's output.
    It is created outside the project folder, so pipeline code and the answer key
    are not anywhere nearby.
  - save_run(): saves every checker's results in the same format, so the
    evaluation can treat all checkers the same way.
"""

import json
import os
import shutil
import tempfile

INSTRUMENTS = ["phq9", "gad7", "rses"]
CATEGORIES = ["reverse_coding", "missing_data", "item_set", "cutoff_bands", "off_by_one", "other"]

INSTRUCTIONS_DIR = "specs/instructions"
RAW_DATA = "data/raw_responses.csv"
REPORTS_DIR = "reports"


def build_workspace(pipeline_id):
    """Create a temporary folder with the guides, raw data and one pipeline output."""
    workspace = tempfile.mkdtemp(prefix="scoring_qa_")

    for file_name in sorted(os.listdir(INSTRUCTIONS_DIR)):
        if file_name.endswith(".md"):
            shutil.copy(os.path.join(INSTRUCTIONS_DIR, file_name), workspace)

    shutil.copy(RAW_DATA, os.path.join(workspace, "raw_responses.csv"))
    shutil.copy(f"outputs/{pipeline_id}/scores.csv", os.path.join(workspace, "pipeline_output.csv"))

    return workspace


def remove_workspace(workspace):
    shutil.rmtree(workspace, ignore_errors=True)


def run_dir(checker_name, pipeline_id, run_number):
    return os.path.join(REPORTS_DIR, checker_name, pipeline_id, f"run_{run_number}")


def run_exists(checker_name, pipeline_id, run_number):
    return os.path.exists(os.path.join(run_dir(checker_name, pipeline_id, run_number), "findings.json"))


def save_run(folder, findings, report_markdown, usage, transcript=None):
    """
    findings:  dict with "verdict", "findings" (list) and optionally "rules_understood"
    usage:     dict with model, input_tokens, output_tokens, seconds, turns
    """
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "findings.json"), "w") as f:
        json.dump(findings, f, indent=2)

    with open(os.path.join(folder, "report.md"), "w") as f:
        f.write(report_markdown)

    with open(os.path.join(folder, "usage.json"), "w") as f:
        json.dump(usage, f, indent=2)

    if transcript is not None:
        with open(os.path.join(folder, "transcript.json"), "w") as f:
            json.dump(transcript, f, indent=2)


def clean_findings(raw_findings):
    """Keep only well-formed findings, with known instrument and category names."""
    cleaned = []
    for finding in raw_findings:
        if not isinstance(finding, dict):
            continue
        instrument = str(finding.get("instrument", "")).lower()
        category = str(finding.get("category", "")).lower()
        if instrument not in INSTRUMENTS:
            instrument = "unknown"
        if category not in CATEGORIES:
            category = "other"
        finding["instrument"] = instrument
        finding["category"] = category
        cleaned.append(finding)
    return cleaned
