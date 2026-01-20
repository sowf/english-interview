---
description: Pick 4 English grammar exercises from english-grammar.at
---

Run the script to select English grammar exercises:

```bash
cd scripts/english-grammar.at && python exercise_picker.py --type grammar --count 4
```

After running, format the output as a markdown table:

| # | Code | Exercise | Level | Link |
|---|------|----------|-------|------|
| 1 | CODE | Exercise Name | Level | [Open](url) |

When user says "done", mark exercises as completed:

```bash
cd scripts/english-grammar.at && python exercise_picker.py --complete
```
