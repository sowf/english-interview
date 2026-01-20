#!/usr/bin/env python3
"""
English Grammar Exercise Picker
Parses https://www.english-grammar.at and selects 3-5 random exercises.
Tracks completion history to avoid repeating the same exercises.
"""

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.english-grammar.at"
HISTORY_FILE = Path(__file__).parent / "exercise_history.json"
TODAY_FILE = Path(__file__).parent / "today_exercises.json"

# Exercise categories (type -> list of site categories)
EXERCISE_TYPES = {
    "grammar": ["Grammar", "Tenses", "Gerund - Infinitive", "Adjective - Adverb", 
                "If-Clauses", "Modal Verbs", "Passive Voice", "Reported Speech",
                "Definite and Indefinite Articles", "Prepositions", 
                "Connectives and Linking Words", "Quantifiers", "Question and Negations",
                "Relative Pronouns", "Indefinite Pronouns", "Possessive Pronouns",
                "Phrasal Verbs", "Word Order", "Common Mistakes"],
    "vocabulary": ["Vocabulary", "Open Cloze", "Missing Word Cloze", "Word Formation",
                   "Multiple Choice Cloze", "Prefixes and Suffixes", 
                   "Key Word Transformation", "Editing - One Word Too Many",
                   "Collocations", "General Vocabulary"],
    "listening": ["Listening", "Advanced Listening"],
}


@dataclass
class Exercise:
    code: str
    name: str
    level: str
    category: str
    url: str


def parse_exercises() -> list[Exercise]:
    """Parses the page and extracts all Online Exercises."""
    print("🌐 Loading page...")
    
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    exercises = []
    
    # Pattern for parsing exercises: CODE - Name Level
    # Example: "GV085 - Law, Crime PunishmentAdvanced" (level may be concatenated)
    exercise_pattern = re.compile(
        r'^([A-Z]+\d+)\s*[-–]\s*(.+?)\s*(Elementary|Intermediate|Advanced)$'
    )
    
    # Find the "Online Exercises" section
    online_exercises_section = None
    for h3 in soup.find_all('h3'):
        if 'Online Exercises' in h3.get_text() and 'New' not in h3.get_text():
            online_exercises_section = h3
            break
    
    if not online_exercises_section:
        print("⚠️ Online Exercises section not found, parsing entire page")
        online_exercises_section = soup
    
    # Iterate over all elements after the Online Exercises heading
    current_section = "Online Exercises"
    current_category = "General"
    
    # Collect all elements for parsing
    all_elements = soup.find_all(['h3', 'h4', 'li'])
    
    in_online_exercises = False
    
    for element in all_elements:
        # Track sections (h3)
        if element.name == 'h3':
            section_text = element.get_text(strip=True)
            if section_text == 'Online Exercises':
                in_online_exercises = True
                continue
            elif section_text in ['Worksheets', 'Writing', 'More Links']:
                in_online_exercises = False
                continue
        
        # Skip if not in Online Exercises section
        if not in_online_exercises:
            continue
        
        # Update category if found h4
        if element.name == 'h4':
            category_text = element.get_text(strip=True)
            if category_text and not category_text.startswith('New'):
                current_category = category_text
            continue
        
        # Parse li elements
        if element.name == 'li':
            text = element.get_text(strip=True)
            match = exercise_pattern.match(text)
            
            if match:
                code, name, level = match.groups()
                
                # Find link inside li
                link = element.find('a')
                if link and link.get('href'):
                    url = urljoin(BASE_URL, link.get('href'))
                else:
                    url = BASE_URL
                
                exercises.append(Exercise(
                    code=code,
                    name=name.strip(),
                    level=level,
                    category=current_category,
                    url=url
                ))
    
    # If Online Exercises is empty, parse "New Online Exercises" as fallback
    if not exercises:
        print("⚠️ Parsing New Online Exercises section...")
        in_new_exercises = False
        
        for element in all_elements:
            if element.name == 'h3':
                section_text = element.get_text(strip=True)
                if 'New Online Exercises' in section_text:
                    in_new_exercises = True
                    continue
                elif section_text and 'Exercises' not in section_text:
                    in_new_exercises = False
            
            if not in_new_exercises:
                continue
            
            if element.name == 'li':
                text = element.get_text(strip=True)
                match = exercise_pattern.match(text)
                
                if match:
                    code, name, level = match.groups()
                    link = element.find('a')
                    url = urljoin(BASE_URL, link.get('href')) if link and link.get('href') else BASE_URL
                    
                    exercises.append(Exercise(
                        code=code,
                        name=name.strip(),
                        level=level,
                        category="New",
                        url=url
                    ))
    
    # Remove duplicates by code
    seen_codes = set()
    unique_exercises = []
    for ex in exercises:
        if ex.code not in seen_codes:
            seen_codes.add(ex.code)
            unique_exercises.append(ex)
    
    print(f"✅ Found {len(unique_exercises)} exercises")
    return unique_exercises


def load_history() -> dict:
    """Loads completion history from file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completions": {}, "sessions": []}


def save_history(history: dict) -> None:
    """Saves completion history."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_completion_count(history: dict, code: str) -> int:
    """Returns the number of times an exercise was completed."""
    return history.get("completions", {}).get(code, 0)


def select_exercises(
    exercises: list[Exercise],
    history: dict,
    count: int = 4,
    max_elementary: int = 1
) -> list[Exercise]:
    """
    Selects random exercises based on history.
    
    - Prioritizes exercises that were completed less often
    - Maximum max_elementary exercises at Elementary level
    """
    
    # Group by completion count
    completion_groups: dict[int, list[Exercise]] = {}
    
    for ex in exercises:
        completions = get_completion_count(history, ex.code)
        if completions not in completion_groups:
            completion_groups[completions] = []
        completion_groups[completions].append(ex)
    
    selected: list[Exercise] = []
    elementary_count = 0
    
    # Sort groups by completion count (fewer = higher priority)
    sorted_completion_counts = sorted(completion_groups.keys())
    
    attempts = 0
    max_attempts = 1000
    
    while len(selected) < count and attempts < max_attempts:
        attempts += 1
        
        # Select from group with lowest completion count
        for comp_count in sorted_completion_counts:
            available = [
                ex for ex in completion_groups[comp_count]
                if ex not in selected
            ]
            
            # Filter by Elementary limit
            if elementary_count >= max_elementary:
                available = [ex for ex in available if ex.level != "Elementary"]
            
            if available:
                choice = random.choice(available)
                selected.append(choice)
                
                if choice.level == "Elementary":
                    elementary_count += 1
                
                break
    
    random.shuffle(selected)
    return selected


def mark_as_completed(codes: list[str]) -> None:
    """Marks exercises as completed."""
    history = load_history()
    
    for code in codes:
        if code not in history["completions"]:
            history["completions"][code] = 0
        history["completions"][code] += 1
    
    # Add session record
    history["sessions"].append({
        "date": datetime.now().isoformat(),
        "exercises": codes
    })
    
    save_history(history)
    print(f"✅ Marked {len(codes)} exercises as completed")


def filter_by_type(exercises: list[Exercise], exercise_type: str) -> list[Exercise]:
    """Filters exercises by type (grammar/vocabulary/listening)."""
    if exercise_type not in EXERCISE_TYPES:
        print(f"⚠️ Unknown type '{exercise_type}', using all exercises")
        return exercises
    
    allowed_categories = EXERCISE_TYPES[exercise_type]
    filtered = [ex for ex in exercises if ex.category in allowed_categories]
    
    # If nothing found by category, try filtering by exercise code
    if not filtered:
        # Exercise codes often indicate the type:
        # T = Tenses, GI = Gerund-Infinitive, AD = Adjectives, IF = If-clauses, etc.
        grammar_codes = ['T', 'GI', 'AD', 'IF', 'M', 'PA', 'RS', 'ART', 'PREP', 'CON', 
                        'QF', 'QN', 'RP', 'IP', 'PRO', 'PV', 'CM']
        vocabulary_codes = ['OC', 'MWC', 'WF', 'MCC', 'PS', 'KWT', 'ED', 'COLL', 'GV']
        listening_codes = ['LI', 'LIS']
        
        code_map = {
            "grammar": grammar_codes,
            "vocabulary": vocabulary_codes,
            "listening": listening_codes,
        }
        
        allowed_code_prefixes = code_map.get(exercise_type, [])
        filtered = [
            ex for ex in exercises 
            if any(ex.code.startswith(prefix) for prefix in allowed_code_prefixes)
        ]
    
    return filtered


def save_today_exercises(exercises: list[Exercise], exercise_type: str = "grammar") -> None:
    """Saves today's exercises to file."""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "type": exercise_type,
        "exercises": [asdict(ex) for ex in exercises]
    }
    
    with open(TODAY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_exercises(exercises: list[Exercise], history: dict) -> None:
    """Pretty prints the list of exercises."""
    print("\n" + "=" * 60)
    print("📚 TODAY'S EXERCISES")
    print("=" * 60 + "\n")
    
    for i, ex in enumerate(exercises, 1):
        completions = get_completion_count(history, ex.code)
        level_emoji = {
            "Elementary": "🟢",
            "Intermediate": "🟡", 
            "Advanced": "🔴"
        }.get(ex.level, "⚪")
        
        print(f"{i}. {level_emoji} [{ex.code}] {ex.name}")
        print(f"   Level: {ex.level} | Category: {ex.category}")
        print(f"   Previous completions: {completions}")
        print(f"   🔗 {ex.url}")
        print()
    
    print("=" * 60)
    print(f"📊 Total: {len(exercises)} exercises")
    elementary = sum(1 for ex in exercises if ex.level == "Elementary")
    intermediate = sum(1 for ex in exercises if ex.level == "Intermediate")
    advanced = sum(1 for ex in exercises if ex.level == "Advanced")
    print(f"   🟢 Elementary: {elementary} | 🟡 Intermediate: {intermediate} | 🔴 Advanced: {advanced}")
    print("=" * 60 + "\n")


def show_stats() -> None:
    """Shows completion statistics."""
    history = load_history()
    
    print("\n📊 COMPLETION STATISTICS\n")
    
    completions = history.get("completions", {})
    sessions = history.get("sessions", [])
    
    if not completions:
        print("No completed exercises yet")
        return
    
    total_completions = sum(completions.values())
    unique_exercises = len(completions)
    
    print(f"Total completions: {total_completions}")
    print(f"Unique exercises: {unique_exercises}")
    print(f"Sessions: {len(sessions)}")
    
    # Top 5 most frequently completed
    top_5 = sorted(completions.items(), key=lambda x: x[1], reverse=True)[:5]
    if top_5:
        print("\nTop 5 most completed:")
        for code, count in top_5:
            print(f"  {code}: {count} times")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="English Grammar Exercise Picker")
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=4,
        help="Number of exercises (default: 4)"
    )
    parser.add_argument(
        "--type", "-t",
        type=str,
        default="grammar",
        choices=["grammar", "vocabulary", "listening"],
        help="Exercise type: grammar, vocabulary, listening (default: grammar)"
    )
    parser.add_argument(
        "--max-elementary", "-e",
        type=int,
        default=1,
        help="Maximum Elementary exercises (default: 1)"
    )
    parser.add_argument(
        "--complete", "-d",
        action="store_true",
        help="Mark today's exercises as completed"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show completion statistics"
    )
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
        return
    
    if args.complete:
        if TODAY_FILE.exists():
            with open(TODAY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            codes = [ex["code"] for ex in data.get("exercises", [])]
            if codes:
                mark_as_completed(codes)
            else:
                print("❌ No exercises to mark")
        else:
            print("❌ Today's exercises file not found. Generate exercises first.")
        return
    
    # Main mode - generate exercises
    exercises = parse_exercises()
    
    if not exercises:
        print("❌ Failed to find exercises on the page")
        return
    
    # Filter by type
    exercise_type = args.type
    filtered_exercises = filter_by_type(exercises, exercise_type)
    
    type_names = {"grammar": "📖 Grammar", "vocabulary": "📝 Vocabulary", "listening": "🎧 Listening"}
    print(f"\n{type_names.get(exercise_type, exercise_type)}: found {len(filtered_exercises)} exercises")
    
    if not filtered_exercises:
        print(f"❌ No exercises found for type '{exercise_type}'")
        return
    
    history = load_history()
    
    # Select count from 3 to 5, if not explicitly set
    count = args.count
    if count < 3:
        count = 3
    elif count > 5:
        count = 5
    
    selected = select_exercises(
        filtered_exercises,
        history,
        count=count,
        max_elementary=args.max_elementary
    )
    
    print_exercises(selected, history)
    save_today_exercises(selected, exercise_type)
    
    print(f"💾 Saved to {TODAY_FILE}")
    print("\n📝 After completing, run: python exercise_picker.py --complete")


if __name__ == "__main__":
    main()
