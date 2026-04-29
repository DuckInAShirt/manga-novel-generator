# Quality Checklist

Run `scripts/check_quality.py` after each scene and after final assembly. Fix all issues before declaring completion.

---

## Per-Scene Checks

### Structural (MUST PASS)
- [ ] Scene has `## Scene N` header
- [ ] Scene has `[氛围: ... | 场景: ... | 时间: ...]` annotation
- [ ] Scene has `[镜头: ...]` camera hint
- [ ] At least one dialogue line attributed as `Name (emotion): "text"`
- [ ] At least one action bracket line: `[ action description ]`
- [ ] Scene ends with `---` separator

### Payoff (MUST PASS)
- [ ] Scene has at least one `[爽点: ... ✓]` marker at the end
- [ ] If this is a payoff scene (not pure exposition), the payoff is clearly delivered
- [ ] Villain reactions are described when applicable (no disappearing villains between scenes)

### Character Consistency (MUST PASS)
- [ ] No new character names appear beyond the 5 named in the outline
- [ ] Each character's behavior matches their established personality
- [ ] Protagonist gains visible momentum toward the arc goal

### Scene Quality (SHOULD PASS)
- [ ] Scene moves the arc forward — no filler scenes
- [ ] Scene has a distinct beginning (arrival/entrance), middle (conflict), end (resolution or cliffhanger)

---

## Full-Chapter Checks

### Meta (MUST PASS)
- [ ] Total character count between 3000-8000
- [ ] Clean separation between scenes: each `## Scene N` block is self-contained
- [ ] No duplicate scene numbers

### Arc Completion (MUST PASS)
- [ ] First scene establishes the status quo / conflict
- [ ] Last scene delivers a satisfying payoff or cliffhanger
- [ ] The protagonist's arc (underdog → power) is visible across scenes
- [ ] There are no dangling plot threads

### Payoff Density (SHOULD PASS)
- [ ] At least one minor payoff per scene
- [ ] At least one major payoff per 3 scenes
- [ ] Payoff types are varied (not all 身份揭穿, mix in 实力碾压, 财富打脸, etc.)

### Audience Impact (SHOULD PASS)
- [ ] The opening hook grabs within first 200 characters
- [ ] Villain build-up is proportionate to the beatdown
- [ ] Ending leaves reader satisfied (resolution) or hungry (cliffhanger)
- [ ] Visual cinematography is consistently implied throughout (camera angles, facial expressions, crowd reaction)

---

## Red Flags (Immediate Rewrite)

- [ ] Protagonist never struggles — every payoff is free (boring)
- [ ] Antagonist has no presence — defeated without build-up (no stakes)
- [ ] Scene is pure narration with no visual action (can't adapt to manhua)
- [ ] Character count exceeds 5 (short-form limit breached)
- [ ] Dialogue sounds identical across characters (no voice differentiation)
