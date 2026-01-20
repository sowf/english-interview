#!/usr/bin/env python3
"""
Create Anki deck from vocabulary.jsonl

Usage:
    pip install -r scripts/anki/requirements.txt
    python scripts/anki/create_cards.py

Input:  learning/1-draft/vocabulary.jsonl
Output: learning/3-mastery/anki/interview_vocabulary.apkg
"""

import json
import random
from pathlib import Path

try:
    import genanki
except ImportError:
    print("❌ genanki not installed. Run:")
    print("   pip install -r scripts/anki/requirements.txt")
    exit(1)


# Unique IDs for the model and deck (generated once, keep stable)
MODEL_ID = 1607392319
DECK_ID = 2059400110

# Card model: Front = context, Back = phrase
VOCABULARY_MODEL = genanki.Model(
    MODEL_ID,
    "Interview Vocabulary",
    fields=[
        {"name": "Context"},
        {"name": "Phrase"},
        {"name": "Category"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="category">{{Category}}</div><div class="context">{{Context}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer"><div class="phrase">{{Phrase}}</div>',
        },
    ],
    css="""
    .card {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 20px;
        text-align: center;
        padding: 20px;
    }
    .category {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .context {
        font-size: 18px;
        color: #333;
    }
    .phrase {
        font-size: 22px;
        font-weight: bold;
        color: #1a73e8;
    }
    """,
)


def main():
    # Paths
    root = Path(__file__).parent.parent.parent
    input_file = root / "learning" / "1-draft" / "vocabulary.jsonl"
    output_dir = root / "learning" / "3-mastery" / "anki"
    output_file = output_dir / "interview_vocabulary.apkg"

    # Ensure output dir exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read vocabulary
    phrases = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                phrases.append(json.loads(line))

    if not phrases:
        print("❌ No phrases found in vocabulary.jsonl")
        return

    # Create deck
    deck = genanki.Deck(DECK_ID, "Interview Vocabulary")

    # Add notes
    for item in phrases:
        phrase = item.get("p", "")
        meaning = item.get("m", "")
        category = item.get("c", "general")

        note = genanki.Note(
            model=VOCABULARY_MODEL,
            fields=[meaning, phrase, category],
        )
        deck.add_note(note)

    # Save package
    genanki.Package(deck).write_to_file(str(output_file))

    print(f"✅ Created Anki deck: {output_file}")
    print(f"   Total cards: {len(phrases)}")
    print()
    print("📥 To use:")
    print(f"   Double-click {output_file.name} to open in Anki")
    print("   Or: Anki → File → Import → select the file")


if __name__ == "__main__":
    main()
