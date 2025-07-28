#!/usr/bin/env python3
"""
Merge original exercises with external exercises
"""
import json
import os
from pathlib import Path

def merge_exercises():
    """Merge original exercises with external exercises"""
    
    # Paths
    original_path = Path("data/exercises/exercise_kb.json")
    external_path = Path("data/exercises/external_exercises.json")
    output_path = Path("data/exercises/exercise_kb.json")
    
    # Load original exercises
    with open(original_path, 'r', encoding='utf-8') as f:
        original_exercises = json.load(f)
    
    # Load external exercises
    with open(external_path, 'r', encoding='utf-8') as f:
        external_exercises = json.load(f)
    
    print(f"📊 Original exercises: {len(original_exercises)}")
    print(f"📊 External exercises: {len(external_exercises)}")
    
    # Merge exercises
    all_exercises = original_exercises + external_exercises
    
    # Remove duplicates based on name
    seen_names = set()
    unique_exercises = []
    duplicates = []
    
    for exercise in all_exercises:
        name = exercise.get('name', '').lower()
        if name not in seen_names:
            seen_names.add(name)
            unique_exercises.append(exercise)
        else:
            duplicates.append(exercise.get('name', 'Unknown'))
    
    print(f"⚠️ Skipped {len(duplicates)} duplicates: {', '.join(duplicates[:5])}{'...' if len(duplicates) > 5 else ''}")
    print(f"✅ Total unique exercises: {len(unique_exercises)}")
    
    # Save merged exercises
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_exercises, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(unique_exercises)} exercises to {output_path}")
    
    # Clean up external file
    os.remove(external_path)
    print(f"🗑️ Removed temporary file: {external_path}")
    
    return len(unique_exercises)

if __name__ == "__main__":
    total = merge_exercises()
    print(f"\n🎉 Successfully merged exercises! Total: {total}") 