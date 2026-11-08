"""
Run every pipeline copy on the raw data and save each one's output.

  pipelines/pipeline_01.py  ->  outputs/pipeline_01/scores.csv
  ...

Each copy runs as a separate program, exactly like a black box would.

Usage:
    python harness/run_pipelines.py
"""

import os
import subprocess
import sys

RAW_DATA = "data/raw_responses.csv"


def main():
    pipeline_files = sorted(f for f in os.listdir("pipelines") if f.endswith(".py"))

    for file_name in pipeline_files:
        pipeline_id = file_name.replace(".py", "")
        output_dir = f"outputs/{pipeline_id}"
        os.makedirs(output_dir, exist_ok=True)

        command = [sys.executable, f"pipelines/{file_name}", RAW_DATA, f"{output_dir}/scores.csv"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"{pipeline_id}: FAILED")
            print(result.stderr)
        else:
            print(f"{pipeline_id}: {result.stdout.strip()}")

    # The reference output, for comparison
    os.makedirs("outputs/reference", exist_ok=True)
    command = [sys.executable, "harness/reference_pipeline.py", RAW_DATA, "outputs/reference/scores.csv"]
    subprocess.run(command, check=True)
    print("reference: done")


if __name__ == "__main__":
    main()
