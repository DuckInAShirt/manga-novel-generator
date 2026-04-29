#!/usr/bin/env python3
"""Automated scoring: format compliance, character count, char range, payoff density, emotion tags.

Usage: python3 auto_score.py results/<model>/<prompt>/output.md
Outputs structured JSON scores to stdout.
"""

import json
import re
import sys


def check_scene_headers(text):
    scenes = re.findall(r"^## Scene \d+$", text, re.MULTILINE)
    if not scenes:
        return 0, 0
    numbers = [int(re.search(r"\d+", s).group()) for s in scenes]
    expected = list(range(1, len(scenes) + 1))
    has_gaps = numbers != expected
    return len(scenes), 0 if has_gaps else len(scenes)


def check_annotation_tags(text):
    total = len(re.findall(r"^## Scene \d+$", text, re.MULTILINE))
    if total == 0:
        return 0, 0, 0
    atmos = len(re.findall(r"\[氛围:\s*.+?\s*\|", text))
    camera = len(re.findall(r"\[镜头:", text))
    return atmos, camera, total


def check_payoffs(text):
    payoffs = len(re.findall(r"✓", text))
    scenes = len(re.findall(r"^## Scene \d+$", text, re.MULTILINE))
    return payoffs, scenes, round(payoffs / scenes, 1) if scenes else 0


def check_emotion_tags(text):
    dialogues_with_emo = len(re.findall(r"^\w+ \(.+?\):", text, re.MULTILINE))
    dialogues_all = len(re.findall(r"\):\s*\"", text))
    return dialogues_with_emo, dialogues_all


def check_character_count(text):
    names = set()
    for m in re.finditer(r"(\w+) \(.+?\):", text):
        name = m.group(1)
        if name not in ("电话那头", "手机那头", "那头"):
            names.add(name)
    return len(names)


def check_char_count(text):
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    return chinese


def score(value, best, worst, weight=1.0, invert=False):
    if best == worst:
        return 5.0 * weight
    ratio = (value - worst) / (best - worst)
    if invert:
        ratio = 1 - ratio
    return round(ratio * 5 * weight, 1)


def main():
    if len(sys.argv) < 2:
        print("Usage: auto_score.py <output.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        text = f.read()

    scene_count, valid_scenes = check_scene_headers(text)
    atmos, camera, total = check_annotation_tags(text)
    payoffs, scenes, density = check_payoffs(text)
    dialogues_emo, dialogues_all = check_emotion_tags(text)
    char_num = check_character_count(text)
    chinese_chars = check_char_count(text)

    # Score each metric 0-5
    scores = {
        "format_compliance": round((valid_scenes / scene_count) * 5, 1) if scene_count else 0,
        "annotation_coverage": round(
            ((atmos / total if total else 0) * 2.5 + (camera / total if total else 0) * 2.5), 1
        ),
        "payoff_density": min(5.0, density * 1.5) if density else 0,
        "emotion_tag_rate": round(
            (dialogues_emo / dialogues_all) * 5 if dialogues_all else 0, 1
        ),
        "character_limit": 5.0 if char_num <= 5 else max(0, 5 - (char_num - 5)),
        "char_range": (
            5.0 if 3000 <= chinese_chars <= 8000
            else max(0, 5 - abs(chinese_chars - 4000) / 800)
        ),
    }

    auto = {
        "raw": {
            "scene_count": scene_count,
            "valid_scenes": valid_scenes,
            "atmosphere_tags": atmos,
            "camera_tags": camera,
            "total_scenes": total,
            "payoff_checkmarks": payoffs,
            "payoff_density_per_scene": density,
            "dialogues_with_emotion": dialogues_emo,
            "dialogues_total": dialogues_all,
            "characters_detected": char_num,
            "chinese_chars": chinese_chars,
        },
        "scores": scores,
        "overall": round(sum(scores.values()) / len(scores), 1),
    }

    print(json.dumps(auto, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
