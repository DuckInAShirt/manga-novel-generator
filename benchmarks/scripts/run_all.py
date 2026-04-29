#!/usr/bin/env python3
"""Orchestrate full benchmark pipeline: generate → auto-score → judge → report.

Usage: python3 scripts/run_all.py
"""

import subprocess
import sys
from pathlib import Path


BENCH_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BENCH_DIR / "scripts"


def run_step(name, args):
    print(f"\n{'='*50}")
    print(f"STEP: {name}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / args[0])] + list(args[1:]),
        cwd=str(BENCH_DIR),
    )
    if result.returncode != 0:
        print(f"\n[FAIL] {name} exited with code {result.returncode}")
        return False
    print(f"[DONE] {name}")
    return True


def main():
    cfg_path = BENCH_DIR / "config.json"
    if not cfg_path.exists():
        print("No config.json found", file=sys.stderr)
        sys.exit(1)

    import json
    with open(cfg_path) as f:
        cfg = json.load(f)

    results_dir = BENCH_DIR / "results"

    # Step 1: Generate
    if not run_step("Generate", ["run.py"]):
        sys.exit(1)

    # Step 2: Auto-score all outputs
    for model in cfg["test_models"]:
        model_name = model["name"]
        for prompt_id in cfg["prompts"]:
            output_file = results_dir / model_name / prompt_id / "output.md"
            if not output_file.exists():
                print(f"[SKIP] No output for {model_name}/{prompt_id}")
                continue
            auto_file = results_dir / model_name / prompt_id / "auto.json"
            print(f"Auto-scoring {model_name}/{prompt_id} ...")
            with open(output_file) as fin, open(auto_file, "w") as fout:
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS_DIR / "auto_score.py"), str(output_file)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    print(f"  WARN: {result.stderr[:100]}")
                fout.write(result.stdout)

    # Step 3: Judge all outputs
    judge_model = cfg["judge_model"]["name"]
    for model in cfg["test_models"]:
        model_name = model["name"]
        for prompt_id in cfg["prompts"]:
            output_file = results_dir / model_name / prompt_id / "output.md"
            if not output_file.exists():
                continue
            judge_file = results_dir / model_name / prompt_id / "judge.json"
            print(f"Judging {model_name}/{prompt_id} (by {judge_model}) ...")
            with open(judge_file, "w") as fout:
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS_DIR / "judge.py"), str(output_file)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    print(f"  WARN: {result.stderr[:100]}")
                fout.write(result.stdout)

    # Step 4: Report
    run_step("Report", ["report.py"])


if __name__ == "__main__":
    main()
