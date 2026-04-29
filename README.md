# Manga Novel Generator

A reusable skill / agent pipeline for generating high-quality short-form power fantasy novels (爽文) optimized for motion comic (漫剧 / 动态漫) production.

## Core Idea

This is a skill following the [Agent Skills](https://agentskills.io) progressive disclosure pattern. Instead of cramming every instruction into the system prompt, it loads knowledge in three layers:

- **L1**: Skill name + description (always loaded, ~100 tokens)
- **L2**: `SKILL.md` body — generation pipeline and core principles (loaded when relevant)
- **L3**: `references/` and `scripts/` — trope library, format spec, quality checker (loaded on demand)

## Output Format

Structured Markdown with scene annotations, camera hints, and emotional cues:

```
## Scene 1
[氛围: 压抑 | 场景: 天海集团大厦一楼大厅 | 时间: 上午]
[镜头: 大厦外景 → 旋转门 → 男主人脸]

苏晨 (淡然): "我找你们李总。"
前台 (不耐烦): "有预约吗？"
[苏晨掏出一张黑色名片，烫金字折射出金光]

---
[爽点: 身份暗示 ✓ | 狗眼看人低反转 ✓]
```

## File Structure

```
manga-novel-generator/
├── SKILL.md                    # L1 + L2: frontmatter + principle-oriented instructions
├── references/
│   ├── trope_library.md        # 10 classic power fantasy tropes with scene templates
│   ├── quality_checklist.md    # Per-scene and full-chapter quality criteria
│   └── output_format.md        # Structured Markdown format specification
├── examples/
│   └── sample_output.md        # Complete example: "我的七个姐姐国色天香" excerpt
├── scripts/
│   └── check_quality.py        # Automated quality checker
└── README.md
```

## Usage

1. Install the skill to `~/.claude/skills/manga-novel-generator/`
2. In a Claude / opencode session, request novel generation:
   ```
   帮我写一篇都市扮猪吃虎的短篇爽文
   ```
3. The agent will follow the pipeline: gather input → outline → scene-by-scene generation with quality checks

## Quality Checker

```bash
python3 scripts/check_quality.py examples/sample_output.md
```
