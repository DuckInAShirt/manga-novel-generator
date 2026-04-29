#!/usr/bin/env python3
"""Run generation for all models × prompts combinations.

Reads config.json, iterates over test_models and prompts,
calls the OpenCode Go API, saves outputs to results/<model>/<prompt>/output.md
"""

import json
import os
import sys
import time
from pathlib import Path

import requests


BENCH_DIR = Path(__file__).resolve().parent.parent


def load_config():
    with open(BENCH_DIR / "config.json") as f:
        return json.load(f)


def get_api_key(cfg):
    key = os.environ.get("OPENCODE_GO_KEY", "")
    if key and key != "OPENCODE_GO_KEY":
        return key
    # Try gocommit config
    gocommit_cfg = Path.home() / ".gocommit.json"
    if gocommit_cfg.exists():
        with open(gocommit_cfg) as f:
            gc = json.load(f)
            key = gc.get("api_key", "")
    if not key:
        print("No API key found. Set OPENCODE_GO_KEY env var or run 'gocommit config'")
        sys.exit(1)
    return key


def call_api(base_url, api_key, model, prompt, skill_md, refs):
    """Call OpenCode-compatible chat API."""
    system_prompt = skill_md
    for ref_name, ref_content in refs.items():
        system_prompt += f"\n\n{ref_content}"

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.8,
        },
        timeout=180,
    )

    if resp.status_code != 200:
        print(f"API error {resp.status_code}: {resp.text[:300]}")
        return None, 0, 0

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    input_tokens = data.get("usage", {}).get("prompt_tokens", 0)
    output_tokens = data.get("usage", {}).get("completion_tokens", 0)
    return content, input_tokens, output_tokens


def main():
    cfg = load_config()
    api_key = get_api_key(cfg)
    base_url = cfg["api"]["base_url"]

    # Load skill files
    skill_path = BENCH_DIR / cfg["skill_path"]
    refs_path = BENCH_DIR / cfg["references_path"]
    with open(skill_path) as f:
        skill_md = f.read()

    refs = {}
    for ref_file in refs_path.glob("*.md"):
        with open(ref_file) as f:
            refs[ref_file.name] = f.read()

    total = len(cfg["test_models"]) * len(cfg["prompts"])
    count = 0

    for model_info in cfg["test_models"]:
        model = model_info["name"]
        for prompt_id in cfg["prompts"]:
            count += 1
            print(f"[{count}/{total}] {model} × {prompt_id} ... ", end="", flush=True)

            prompt_path = BENCH_DIR / "prompts" / f"{prompt_id}.md"
            with open(prompt_path) as f:
                prompt = f.read()

            result_dir = BENCH_DIR / "results" / model / prompt_id
            result_dir.mkdir(parents=True, exist_ok=True)

            content, input_tk, output_tk = call_api(
                base_url, api_key, model, prompt, skill_md, refs
            )

            if content is None:
                print("FAILED")
                continue

            with open(result_dir / "output.md", "w") as f:
                f.write(content)

            usage = {"input_tokens": input_tk, "output_tokens": output_tk}
            with open(result_dir / "usage.json", "w") as f:
                json.dump(usage, f, indent=2)

            print(f"OK ({input_tk}+{output_tk} tokens)")
            time.sleep(0.5)  # rate limiting

    print("Done.")


if __name__ == "__main__":
    main()
