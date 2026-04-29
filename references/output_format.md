# Output Format — Structured Markdown for Manhua Adaptation

This format is designed to be both human-readable and machine-parseable. Every scene block is self-contained and includes all information a storyboard artist or downstream tool needs.

---

## Scene Block Structure

```
## Scene N

[氛围: mood | 场景: location | 时间: time_of_day]

[镜头: camera_angle_or_movement]

CharacterName (emotion): "Dialogue text."
[Action description in brackets]

---
[爽点: payoff_type ✓ | payoff_type2 ✓]
```

---

## Annotation Types

### Scene Header
```
## Scene 3
```
- `N` is the scene number, starting from 1
- Scene header must be on its own line

### Atmosphere Tag
```
[氛围: 紧张 | 场景: 天海集团大厅 | 时间: 上午]
```
- **氛围**: emotional atmosphere (紧张/压抑/轻松/肃杀/暧昧/热血/绝望)
- **场景**: physical location (use 5-15 characters)
- **时间**: time of day or temporal context (上午/深夜/黄昏/三年前)

### Camera Hint
```
[镜头: 大厅全景 → 前台特写 → 男主人脸]
```
- Describe the visual sequence a camera would capture
- Use `→` to indicate transitions
- Common patterns: 全景, 近景, 特写, 俯拍, 仰拍, 慢动作, 快速切换

### Dialogue
```
苏晨 (冷): "我找你们李总。"
前台 (打量、不耐烦): "有预约吗？"
```
- Format: `Name (emotion): "text."`
- Emotion must be a single word or brief phrase in parentheses
- Use Chinese punctuation for dialogue

### Action Bracket
```
[苏晨掏出一张黑色名片，上面烫金两个字]
[李少后退一步，额头渗出冷汗]
```
- Any non-dialogue action description goes in `[square brackets]`
- One action per bracket line
- Every action must be visual — something the audience can see on screen

### Payoff Markers
```
[爽点: 身份揭穿 ✓ | 狗眼看人低打脸 ✓]
```
- Placed at the end of every scene, after the `---` separator
- Lists ALL payoffs delivered in this scene
- Emoji `✓` confirms each payoff is completed
- Use payoff types from `references/trope_library.md` or define new ones

### Scene Separator
```
---
```
- Three dashes on their own line close each scene

---

## Complete Example

```
## Scene 1

[氛围: 压抑 | 场景: 天海集团大厦一楼大厅 | 时间: 上午九点]

[镜头: 大厦外景 → 旋转门 → 大厅前台 → 男主人脸]

苏晨 (淡然): "我找你们李总。"
前台 (瞥了一眼苏晨的旧衬衫，不耐烦): "李总很忙，有预约吗？"
[苏晨没有回答，从口袋里掏出一张黑色名片，放在大理石台面上]
[名片的烫金字在灯光下折射出一丝金光]
前台 (瞳孔一缩，声音颤抖): "这...这是...请您稍等，我马上去通报！"
[前台慌忙起身，高跟鞋踩得哒哒作响，险些摔倒]

---
[爽点: 身份暗示 ✓ | 狗眼看人低反转 ✓]
```

---

## Format Rules (Machine-Enforceable)

1. Every scene opens with `## Scene N` (exact regex: `^## Scene \d+$`)
2. Every scene has exactly one atmosphere tag after the header
3. Camera hint is required but can be omitted in extreme close-up-only scenes
4. Dialogue format: `Name (emotion): "text."` — no exceptions
5. Action lines use `[square brackets]` — never parentheses or bare text
6. Scene closes with `---` separator, followed by payoff markers
7. Payoff markers start with `[爽点: ` and end with `]`
8. Each payoff entry ends with `✓`
