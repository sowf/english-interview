#!/usr/bin/env python3
"""
Generates a nice Vocabulary.md from vocabulary.jsonl
"""

import json
from pathlib import Path
from collections import defaultdict

VOCAB_FILE = Path(__file__).parent.parent.parent / "learning/1-draft/vocabulary.jsonl"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "learning/1-draft/Vocabulary.md"

CATEGORY_NAMES = {
    "general": "General Professional",
    "technical": "Technical Decisions",
    "leadership": "Leadership & Mentorship",
    "conflict": "Conflict Resolution",
    "mentorship": "Mentorship & Onboarding",
    "teamwork": "Teamwork & Collaboration",
    "innovation": "Innovation & Process",
    "failure": "Handling Failure",
}

CATEGORY_EMOJI = {
    "general": "💼",
    "technical": "⚙️",
    "leadership": "👑",
    "conflict": "🤝",
    "mentorship": "🎓",
    "teamwork": "👥",
    "innovation": "💡",
    "failure": "📚",
}


def load_vocabulary() -> list[dict]:
    """Load vocabulary from JSONL file."""
    if not VOCAB_FILE.exists():
        print(f"❌ File not found: {VOCAB_FILE}")
        return []
    
    entries = []
    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def group_by_category(entries: list[dict]) -> dict[str, list[dict]]:
    """Group entries by category."""
    grouped = defaultdict(list)
    for entry in entries:
        cat = entry.get("c", "general")
        grouped[cat].append(entry)
    return grouped


def generate_markdown(entries: list[dict]) -> str:
    """Generate markdown content."""
    grouped = group_by_category(entries)
    
    lines = [
        "# Interview Vocabulary Bank",
        "",
        f"**Total phrases:** {len(entries)}",
        "",
        "---",
        "",
    ]
    
    # Sort categories by count (descending)
    sorted_cats = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
    
    for cat, items in sorted_cats:
        emoji = CATEGORY_EMOJI.get(cat, "📌")
        name = CATEGORY_NAMES.get(cat, cat.title())
        
        lines.append(f"## {emoji} {name} ({len(items)})")
        lines.append("")
        lines.append("| Phrase | Meaning |")
        lines.append("|--------|---------|")
        
        for item in items:
            phrase = item.get("p", "").replace("|", "\\|")
            meaning = item.get("m", "").replace("|", "\\|")
            lines.append(f"| **{phrase}** | {meaning} |")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    entries = load_vocabulary()
    
    if not entries:
        print("❌ No vocabulary entries found")
        return
    
    markdown = generate_markdown(entries)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✅ Generated {OUTPUT_FILE}")
    print(f"   Total phrases: {len(entries)}")
    
    # Show category breakdown
    grouped = group_by_category(entries)
    for cat, items in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
        name = CATEGORY_NAMES.get(cat, cat)
        print(f"   - {name}: {len(items)}")


if __name__ == "__main__":
    main()
