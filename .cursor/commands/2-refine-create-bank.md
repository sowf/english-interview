---
description: Create story bank from practice sessions for the refine phase
---

# 2-Refine: Create Story Bank

You are an English learning coach helping consolidate interview stories into a polished bank.

## Your Task

Analyze all practice sessions from 1-draft and create a consolidated story bank for the 2-refine phase.

## Files to Read

1. `learning/1-draft/practice-sessions/` — all session files (exclude EXAMPLE)
2. `learning/1-draft/vocabulary.jsonl` — learned vocabulary
3. `learning/2-refine/templates/story-bank.md` — template format

## Analysis Steps

1. **Read existing bank** — check what stories already exist in `learning/2026-story-bank.md`
2. **Extract unique stories** from all sessions
3. **Compare with existing** — for each story:
   - If NEW → add to bank
   - If EXISTS but has better version → update in bank
   - If EXISTS and same → skip
4. **Identify best version** of each story (if practiced multiple times)
5. **Map vocabulary** to relevant stories
6. **Polish to C1 level** — use the improved versions from sessions
7. **Add metrics** — ensure each story has quantifiable results

## Output

Update file: `learning/2026-story-bank.md` (add stories after the EXAMPLE)

### Format for Each Story

```markdown
## Story N: [Short Name]
**Tags:** `topic1` `topic2` `topic3`
**Questions it answers:** Q1, Q5, Q12

### STARR
- **Situation:** [1-2 sentences: context, scale, timeline]
- **Task:** [Your goal, why it was hard]
- **Actions:**
  1. [Action 1]
  2. [Action 2]
  3. [Action 3]
- **Result:** [Metrics: X% improvement, Y users, Z weeks saved]
- **Reflection:** [What you learned, how applied later]

### Key Phrases
- **"phrase 1"** — context
- **"phrase 2"** — context

---
```

### Tags to Use
- `leadership` `conflict` `failure` `mentorship` `technical`
- `collaboration` `innovation` `ambiguity` `pressure` `architecture`
- `data-driven` `stakeholder` `influence` `rescue` `deadline`

### Question Mapping
Reference question numbers from `learning/questions-bank.md` (Q1-Q25)

## Requirements

- **Maximum 10 stories** — if more, pick the strongest ones that cover all topics
- Use C1-level English from improved session versions
- Include 3-5 key phrases per story from vocabulary
- Every story MUST have quantifiable results
- Keep STARR sections concise but complete
- Order stories by importance/strength

## After Creating

Respond with:
```
✅ Story Bank Updated: learning/2026-story-bank.md

Stories: X total (added: Y, updated: Z, skipped: W)
Topics covered: [list]
Total key phrases: N

Ready for daily read-aloud practice!
```
