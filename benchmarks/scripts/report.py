#!/usr/bin/env python3
"""Generate comparison report from benchmark results.

Reads all results/<model>/<prompt>/*.json files, merges auto + judge scores.
Outputs a comparison Markdown table.
"""

import json
import sys
from pathlib import Path


BENCH_DIR = Path(__file__).resolve().parent.parent


def load_scores(results_dir):
    """Collect all scores from results directory."""
    rows = []

    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name

        for prompt_dir in sorted(model_dir.iterdir()):
            if not prompt_dir.is_dir():
                continue
            prompt_name = prompt_dir.name

            auto_path = prompt_dir / "auto.json"
            judge_path = prompt_dir / "judge.json"
            usage_path = prompt_dir / "usage.json"

            auto = {}
            judge = {}
            usage = {}

            if auto_path.exists():
                with open(auto_path) as f:
                    auto = json.load(f)
            if judge_path.exists():
                with open(judge_path) as f:
                    judge = json.load(f)
            if usage_path.exists():
                with open(usage_path) as f:
                    usage = json.load(f)

            rows.append(
                {
                    "model": model_name,
                    "prompt": prompt_name,
                    "auto": auto.get("scores", {}),
                    "auto_overall": auto.get("overall", 0),
                    "judge": judge.get("scores", {}),
                    "judge_overall": judge.get("overall", 0),
                    "comment": (
                        judge.get("scores", {}).get("一句话评价", "")
                        if judge.get("scores")
                        else ""
                    ),
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                }
            )

    return rows


def model_averages(rows):
    """Compute per-model averages across prompts."""
    models = {}
    for row in rows:
        m = row["model"]
        if m not in models:
            models[m] = {"auto_scores": {}, "judge_scores": {}, "count": 0, "total_in": 0, "total_out": 0}
        d = models[m]
        for k, v in row["auto"].items():
            d["auto_scores"][k] = d["auto_scores"].get(k, 0) + v
        for k, v in row["judge"].items():
            if isinstance(v, (int, float)):
                d["judge_scores"][k] = d["judge_scores"].get(k, 0) + v
        d["count"] += 1
        d["total_in"] += row["input_tokens"]
        d["total_out"] += row["output_tokens"]

    for m, d in models.items():
        n = d["count"]
        for k in d["auto_scores"]:
            d["auto_scores"][k] = round(d["auto_scores"][k] / n, 1)
        for k in d["judge_scores"]:
            d["judge_scores"][k] = round(d["judge_scores"][k] / n, 1)

    return models


def render_markdown(rows, averages):
    """Generate comparison Markdown table."""
    lines = ["# Model Benchmark Report\n"]

    # Per-model averages
    lines.append("## 各模型平均得分\n")
    judge_keys = ["爽度", "情节连贯性", "角色辨识度", "视觉适配性", "综合质量"]
    auto_keys = ["format_compliance", "payoff_density", "char_range", "character_limit", "annotation_coverage"]

    # Judge scores table
    lines.append("### LLM 裁判评分（1-5，minimax-m2.7 评定）\n")
    header = "| 模型 | " + " | ".join(judge_keys) + " |"
    lines.append(header)
    lines.append("|" + "|".join(["------"] * (len(judge_keys) + 1)) + "|")

    for model, d in sorted(averages.items()):
        vals = [str(d["judge_scores"].get(k, "-")) for k in judge_keys]
        lines.append(f"| {model} | " + " | ".join(vals) + " |")

    # Auto scores table
    lines.append("\n### 自动指标评分（0-5）\n")
    header = "| 模型 | " + " | ".join(auto_keys) + " |"
    lines.append(header)
    lines.append("|" + "|".join(["------"] * (len(auto_keys) + 1)) + "|")

    for model, d in sorted(averages.items()):
        vals = [str(d["auto_scores"].get(k, "-")) for k in auto_keys]
        lines.append(f"| {model} | " + " | ".join(vals) + " |")

    # Token usage
    lines.append("\n### API 消耗（3 个 prompt 合计）\n")
    lines.append("| 模型 | 输入 Tokens | 输出 Tokens |")
    lines.append("|------|-----------|-----------|")
    for model, d in sorted(averages.items()):
        lines.append(f"| {model} | {d['total_in']} | {d['total_out']} |")

    # Detail: per-model × per-prompt
    lines.append("\n## 逐 prompt 详情\n")
    for model in sorted(set(r["model"] for r in rows)):
        lines.append(f"### {model}\n")
        lines.append(
            "| Prompt | 自动分 | 裁判分 | 评价 |"
        )
        lines.append("|--------|--------|--------|------|")
        for row in rows:
            if row["model"] != model:
                continue
            lines.append(
                f"| {row['prompt']} | {row['auto_overall']} | {row['judge_overall']} "
                f"| {row['comment'][:30]} |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    results_dir = BENCH_DIR / "results"
    if not results_dir.exists():
        print("No results directory found. Run run.py first.", file=sys.stderr)
        sys.exit(1)

    rows = load_scores(results_dir)
    if not rows:
        print("No results found.", file=sys.stderr)
        sys.exit(1)

    averages = model_averages(rows)
    report = render_markdown(rows, averages)

    report_path = BENCH_DIR / "report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(report)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
