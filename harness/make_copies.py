"""
Make the test copies of the reference pipeline.

  - One copy per planted bug (see bug_definitions.py), plus a few clean copies.
  - Copies get shuffled IDs (pipeline_01 ... pipeline_22) so the file name
    says nothing about which bug is inside.
  - The answer key is saved to ground_truth/manifest.csv.

Usage:
    python harness/make_copies.py
"""

import os
import random

import pandas as pd

from bug_definitions import BUGS, N_CLEAN_COPIES

SHUFFLE_SEED = 42
REFERENCE_PATH = "harness/reference_pipeline.py"

ORIGINAL_HEADER = "This is the CORRECT version. The test copies in pipelines/ are made from this file."
COPY_HEADER = "Production scoring pipeline."


def plant_bug(code, bug):
    """Apply one find-and-replace. The find text must appear exactly once."""
    n_found = code.count(bug["find"])
    if n_found != 1:
        raise ValueError(f"{bug['bug_id']}: find text appears {n_found} times, expected 1")
    return code.replace(bug["find"], bug["replace"])


def main():
    with open(REFERENCE_PATH) as f:
        reference_code = f.read()

    # The copies should not say "this is the correct version"
    reference_code = reference_code.replace(ORIGINAL_HEADER, COPY_HEADER)

    # Build the list of copies: every bug, plus the clean ones
    copies = []
    for bug in BUGS:
        copies.append(bug)
    for k in range(N_CLEAN_COPIES):
        copies.append({
            "bug_id": f"clean_{k + 1}",
            "category": "none",
            "accepted_categories": [],
            "instruments": [],
            "description": "No bug. Identical to the reference pipeline.",
            "find": None,
            "replace": None,
        })

    random.Random(SHUFFLE_SEED).shuffle(copies)

    os.makedirs("pipelines", exist_ok=True)
    os.makedirs("ground_truth", exist_ok=True)

    manifest_rows = []
    for number, copy in enumerate(copies, start=1):
        pipeline_id = f"pipeline_{number:02d}"

        if copy["find"] is None:
            code = reference_code
        else:
            code = plant_bug(reference_code, copy)

        with open(f"pipelines/{pipeline_id}.py", "w") as f:
            f.write(code)

        manifest_rows.append({
            "pipeline_id": pipeline_id,
            "bug_id": copy["bug_id"],
            "has_bug": copy["find"] is not None,
            "category": copy["category"],
            "accepted_categories": ";".join(copy["accepted_categories"]),
            "instruments": ";".join(copy["instruments"]),
            "description": copy["description"],
        })

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv("ground_truth/manifest.csv", index=False)

    n_bugs = manifest["has_bug"].sum()
    print(f"Wrote {len(manifest)} pipeline copies to pipelines/ ({n_bugs} with a bug, {len(manifest) - n_bugs} clean)")
    print("Wrote ground_truth/manifest.csv")
    print()
    print(manifest["category"].value_counts().to_string())


if __name__ == "__main__":
    main()
