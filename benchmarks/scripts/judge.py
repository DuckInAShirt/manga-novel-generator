#!/usr/bin/env python3
"""LLM-as-judge scoring using minimax-m2.7.

Reads an output.md, calls the judge model with a scoring rubric.
Outputs structured JSON to stdout.
"""

import json
import os
import sys
from pathlib import Path

import requests


BENCH_DIR = Path(__file__).resolve().parent.parent
JUDGE_PROMPT = """你是一个爽文质量裁判。请阅读以下由 AI 生成的小说，从五个维度评分（1=极差，5=优秀）。

评分维度：
1. 爽度（阅读快感）：打脸是否到位，爽点是否密集，读者是否会觉得痛快
2. 情节连贯性：场景衔接是否自然，故事是否有完整起承转合
3. 角色辨识度：不同角色的对话和行为是否有区分性
4. 视觉适配性：文本是否能直接用于漫剧改编，是否每句话都暗示画面
5. 综合质量：整体阅读体验和完成度

请仅输出以下 JSON 格式，不要加任何其他文字：
{
  "爽度": <1-5的整数>,
  "情节连贯性": <1-5的整数>,
  "角色辨识度": <1-5的整数>,
  "视觉适配性": <1-5的整数>,
  "综合质量": <1-5的整数>,
  "一句话评价": "<简短中文评价，不超过50字>"
}

---以下是待评分小说---"""


def load_config():
    with open(BENCH_DIR / "config.json") as f:
        return json.load(f)


def get_api_key(cfg):
    key = os.environ.get("OPENCODE_GO_KEY", "")
    if key and key != "OPENCODE_GO_KEY":
        return key
    gocommit_cfg = Path.home() / ".gocommit.json"
    if gocommit_cfg.exists():
        with open(gocommit_cfg) as f:
            gc = json.load(f)
            key = gc.get("api_key", "")
    if not key:
        print("No API key found.", file=sys.stderr)
        sys.exit(1)
    return key


def main():
    if len(sys.argv) < 2:
        print("Usage: judge.py <output.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        novel_text = f.read()

    cfg = load_config()
    api_key = get_api_key(cfg)
    base_url = cfg["api"]["base_url"]
    judge_model = cfg["judge_model"]["name"]

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": judge_model,
            "messages": [
                {"role": "system", "content": JUDGE_PROMPT},
                {"role": "user", "content": novel_text},
            ],
            "temperature": 0.3,
        },
        timeout=300,
    )

    if resp.status_code != 200:
        print(f"Judge API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    # Extract JSON from response
    try:
        # Try direct parse
        scores = json.loads(content)
    except json.JSONDecodeError:
        # Try to find JSON block
        import re
        match = re.search(r"\{[^}]+\}", content, re.DOTALL)
        if match:
            scores = json.loads(match.group())
        else:
            print(f"Could not parse judge response: {content[:200]}", file=sys.stderr)
            sys.exit(1)

    input_tk = data.get("usage", {}).get("prompt_tokens", 0)
    output_tk = data.get("usage", {}).get("completion_tokens", 0)

    result = {
        "scores": scores,
        "overall": round(
            sum(
                v
                for k, v in scores.items()
                if isinstance(v, (int, float)) and k != "一句话评价"
            )
            / 5,
            1,
        ),
        "usage": {"input_tokens": input_tk, "output_tokens": output_tk},
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
