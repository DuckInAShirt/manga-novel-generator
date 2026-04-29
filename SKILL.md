---
name: manga-novel-generator
description: Generate short-form power fantasy novels (爽文, 3000-8000 chars) optimized for motion comic / manhua adaptation. Use when user requests novel generation, story creation, or script writing for manhua-style content across urban, fantasy, xianxia, isekai, and web novel genres.
---

# Manga Novel Generator

Generate short-form power fantasy novels optimized for motion comic (漫剧) production. Output structured Markdown with scene annotations, camera hints, and emotional cues ready for downstream adaptation.

## Design Philosophy

You are writing a novel that must be visually adapted. Every sentence should suggest an image. Think like a storyboard artist who also writes.

## Core Principles

### Thrill Density (爽点密度)
- One minor payoff every ~200 characters
- One major payoff per scene
- The villain must be made sufficiently insufferable before the beatdown lands — no flat villains, no flat payoffs

### Character Constraints
- Maximum 5 named characters (short-form limit)
- Exactly one protagonist with a clear underdog-to-power arc
- At least one arrogant antagonist who underestimates the protagonist
- Optional: one ally, one love interest, one bystander for reaction shots

### Structured Output
Every scene must follow the format in `references/output_format.md`. Never deviate — this format is consumed by downstream tools.

### Quality Gates
After generating each scene, run `scripts/check_quality.py` on the output. Fix issues before proceeding. See `references/quality_checklist.md` for the full criteria.

## Generation Pipeline

### Step 1: Gather Input
Ask the user for:
- Genre (都市/玄幻/仙侠/穿越/重生/异能)
- Core trope or premise, or consult `references/trope_library.md`
- Protagonist name and a 1-line personality sketch

If user provides only genre, fill in the rest.

### Step 2: Outline
Generate a 5-8 scene outline. Each scene entry includes:
- Scene purpose (exposition / build-up / payoff / cliffhanger)
- Characters present
- Target payoff type (身份揭穿 / 实力碾压 / 财富打脸 / 众叛亲离反杀... — see trope library)

Present outline to user. Wait for confirmation before writing.

### Step 3: Per-Scene Generation
For each scene:
1. Write the scene in structured Markdown format (see `references/output_format.md`)
2. Run `scripts/check_quality.py` on the scene
3. Fix any flagged issues
4. Proceed to next scene

### Step 4: Final Assembly
Combine all scenes, add title and word count, run final quality check, output the result.

## Constraints

- Never exceed 5 characters. Merge roles if the plot demands more.
- Each scene is a `## Scene N` block.
- Dialogue attributed as `Name (emotion): "text"`.
- Every action description must suggest a visual — what the audience sees.
- Total output: 3000-8000 Chinese characters.

## Reference Files

- `references/trope_library.md` — 10 classic power fantasy tropes with scene templates
- `references/quality_checklist.md` — Per-scene and full-chapter quality criteria
- `references/output_format.md` — Structured Markdown specification with examples
- `examples/sample_output.md` — Complete example meeting the quality bar
