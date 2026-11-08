"""
Run a checker on every pipeline copy.

Runs that already have results are skipped, so you can stop and restart safely.
If the free daily limit runs out, it stops; run the same command the next day.

Usage (from the project folder):
    python -m evaluation.run_all --checker rule_based
    python -m evaluation.run_all --checker agent
    python -m evaluation.run_all --checker agent --pipelines pipeline_01 pipeline_02
"""

import argparse

import pandas as pd

from common.checker_io import run_dir, run_exists
from common.llm_client import DailyLimitReached


def main():
    parser = argparse.ArgumentParser(description="Run a checker on all pipeline copies.")
    parser.add_argument("--checker", choices=["rule_based", "agent"], required=True)
    parser.add_argument("--runs", type=int, default=1, help="Runs per pipeline for the agent (rule_based always uses 1)")
    parser.add_argument("--pipelines", nargs="*", help="Only these pipeline IDs (default: all)")
    args = parser.parse_args()

    manifest = pd.read_csv("ground_truth/manifest.csv")
    pipeline_ids = list(manifest["pipeline_id"])
    if args.pipelines:
        pipeline_ids = args.pipelines

    # Import only the checker we need, so rule_based works without an API key
    if args.checker == "rule_based":
        from baselines.rule_based_checker import CHECKER_NAME, run_check
        n_runs = 1
    else:
        from agent.agent import CHECKER_NAME, run_agent
        n_runs = args.runs

    for run_number in range(1, n_runs + 1):
        for pipeline_id in pipeline_ids:
            if run_exists(CHECKER_NAME, pipeline_id, run_number):
                print(f"{CHECKER_NAME} {pipeline_id} run {run_number}: already done, skipping")
                continue

            folder = run_dir(CHECKER_NAME, pipeline_id, run_number)
            print(f"{CHECKER_NAME} {pipeline_id} run {run_number}: running...")

            try:
                if args.checker == "rule_based":
                    result = run_check(pipeline_id, folder)
                else:
                    result = run_agent(pipeline_id, folder)
            except DailyLimitReached as error:
                # No point continuing today; finished runs are kept and skipped next time
                print(f"  STOPPING: {error}")
                return
            except Exception as error:
                # Don't save anything, so this run is retried next time
                print(f"  ERROR: {error}")
                continue

            print(f"  -> {result['verdict']} ({len(result['findings'])} findings)")


if __name__ == "__main__":
    main()
