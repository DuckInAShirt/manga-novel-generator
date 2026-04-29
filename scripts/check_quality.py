#!/usr/bin/env python3
"""Quality checker for manga-novel-generator output.

Checks a scene or full chapter against the structured Markdown format spec
and quality criteria. Prints a pass/fail report to stdout.

Usage:
    python3 check_quality.py <file_path>
    python3 check_quality.py --stdin  (reads from stdin)
"""

import re
import sys


def check_scene_headers(text: str) -> list[str]:
    """Every scene must have '## Scene N' header."""
    errors = []
    scenes = re.findall(r"^## Scene \d+$", text, re.MULTILINE)
    if not scenes:
        errors.append("MISSING: No '## Scene N' headers found")
    else:
        scene_numbers = [int(re.search(r"\d+", s).group()) for s in scenes]
        if min(scene_numbers) != 1:
            errors.append(f"FIRST_SCENE_MUST_BE_1: got {min(scene_numbers)}")
        expected = set(range(1, len(scenes) + 1))
        actual = set(scene_numbers)
        if expected != actual:
            errors.append(f"SCENE_GAP: expected scenes 1-{len(scenes)}, got {sorted(actual)}")
    return errors


def check_atmosphere_tags(text: str) -> list[str]:
    """Every scene must have [氛围: ... | 场景: ... | 时间: ...]."""
    errors = []
    scenes = re.split(r"^## Scene \d+$", text, flags=re.MULTILINE)[1:]
    for i, scene in enumerate(scenes, 1):
        if not re.search(r"\[氛围:\s*.+?\s*\|", scene):
            errors.append(f"SCENE_{i}_MISSING_ATMOSPHERE: no [氛围: ... | ...] tag")
        if not re.search(r"\[镜头:", scene):
            errors.append(f"SCENE_{i}_MISSING_CAMERA: no [镜头: ...] tag")
    return errors


def check_scene_separators(text: str) -> list[str]:
    """Every scene must end with --- separator."""
    errors = []
    scenes = re.split(r"^## Scene \d+$", text, flags=re.MULTILINE)[1:]
    for i, scene in enumerate(scenes, 1):
        if "---" not in scene:
            errors.append(f"SCENE_{i}_MISSING_SEPARATOR: no --- closing scene")
    return errors


def check_payoff_markers(text: str) -> list[str]:
    """Every scene must have at least one [爽点: ... ✓]."""
    errors = []
    scenes = re.split(r"^## Scene \d+$", text, flags=re.MULTILINE)[1:]
    total_payoffs = 0
    for i, scene in enumerate(scenes, 1):
        payoffs = re.findall(r"✓", scene)
        if not payoffs:
            errors.append(f"SCENE_{i}_NO_PAYOFF: no [爽点: ... ✓] marker found")
        total_payoffs += len(payoffs)

    if total_payoffs < len(scenes):
        errors.append(f"PAYOFF_DENSITY_LOW: {total_payoffs} payoffs across {len(scenes)} scenes")
    return errors


def check_dialogue_format(text: str) -> list[str]:
    """Dialogue must be: Name (emotion): \"text.\"."""
    errors = []
    # Skip headers, section markers, and action bracket lines
    bare_quotes = re.findall(r'^[^#\[\s-].*?:.*?"[^"]*"', text, re.MULTILINE)
    for match in bare_quotes[:5]:  # limit to avoid spam
        line = match.strip()
        if not re.match(r"^\w+ \(.+?\): ", line):
            errors.append(f"BAD_DIALOGUE_FORMAT: {line[:60]}...")
            break
    return errors


def check_character_count(text: str) -> list[str]:
    """Max 5 named characters."""
    errors = []
    # Match character names in dialogue: "Name (emotion):"
    names = set()
    dialogue_pattern = re.findall(r"(\w{1,4}) \(.+?\):", text)
    for name in dialogue_pattern:
        if len(name) >= 2:  # filter single-char false matches
            names.add(name)

    if len(names) > 5:
        errors.append(
            f"TOO_MANY_CHARACTERS: {len(names)} detected ({', '.join(sorted(names))}). Max 5 allowed."
        )
    return errors


def check_char_count(text: str) -> list[str]:
    """Total Chinese character count between 3000-8000."""
    errors = []
    # Count Chinese characters
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if chinese_chars < 3000:
        errors.append(f"BELOW_MIN_CHAR_COUNT: {chinese_chars} Chinese chars (min 3000)")
    if chinese_chars > 8000:
        errors.append(f"EXCEEDS_MAX_CHAR_COUNT: {chinese_chars} Chinese chars (max 8000)")
    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: check_quality.py <file> | --stdin", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--stdin":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], "r") as f:
            text = f.read()

    checks = [
        ("Scene Headers", check_scene_headers),
        ("Atmosphere Tags", check_atmosphere_tags),
        ("Scene Separators", check_scene_separators),
        ("Payoff Markers", check_payoff_markers),
        ("Dialogue Format", check_dialogue_format),
        ("Character Count", check_character_count),
        ("Chinese Char Count", check_char_count),
    ]

    all_errors = []
    for name, fn in checks:
        errors = fn(text)
        if errors:
            all_errors.extend(errors)
            print(f"[FAIL] {name}:")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"[PASS] {name}")

    if all_errors:
        print(f"\n{len(all_errors)} error(s) found.")
        sys.exit(1)
    else:
        print("\nAll checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
