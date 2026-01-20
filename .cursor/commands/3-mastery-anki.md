---
description: Generate Anki flashcard deck from vocabulary.jsonl
---

# 3-Mastery: Create Anki Cards

Generate Anki deck from your vocabulary.

## Setup (once)

```bash
pip install -r scripts/anki/requirements.txt
```

## Generate Deck

```bash
python scripts/anki/create_cards.py
```

Creates `learning/3-mastery/anki/interview_vocabulary.apkg`

## Import

Double-click `interview_vocabulary.apkg` to open in Anki — done!

## Card Format

- **Front:** `[category]` + context when to use
- **Back:** The phrase to remember

## Daily Practice

- 10 new cards/day
- Review all due cards
- ~10 minutes total
