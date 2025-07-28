#!/usr/bin/env python3
"""
Fix push-up exercises that were incorrectly assigned to Dylan Werner
These should be Tom Merrick (calisthenics) not Dylan Werner (yoga)
"""
import json
from pathlib import Path

# Push-up exercises that should be Tom Merrick, not Dylan Werner
PUSHUP_EXERCISES = [
    "Wall Push-Up",
    "Incline Push-Up", 
    "Kneeling Push-Up",
    "Close Grip Push-Up",
    "Decline Push-Up",
    "Wide Grip Push-Up",
    "Parallette Push-Up",
    "Uneven Push-Up",
    "One-Handed Push-Up",
    "Dynamic Push-Up",
    "Pike Push-Up",
    "Diamond Push-Up",
    "Archer Push-Up",
    "Pseudo Planche Push-Up",
    "Handstand Push-Up"
]

def fix_pushup_mentors():
    """Fix push-up exercises mentor assignment"""
    
    exercise_file = Path("data/exercises/exercise_kb.json")
    with open(exercise_file, 'r', encoding='utf-8') as f:
        exercises = json.load(f)
    
    print(f"📖 Loaded {len(exercises)} exercises")
    
    changes_made = 0
    
    for exercise in exercises:
        if (exercise['name'] in PUSHUP_EXERCISES and 
            exercise.get('mentor') == 'dylan_werner'):
            
            exercise['mentor'] = 'tom_merrick'
            changes_made += 1
            print(f"✅ Fixed '{exercise['name']}' mentor: dylan_werner -> tom_merrick")
    
    # Save updated exercises
    with open(exercise_file, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Summary:")
    print(f"✅ Fixed {changes_made} push-up exercises mentor assignment")
    print(f"💾 Saved updated exercise knowledge base")

if __name__ == "__main__":
    fix_pushup_mentors() 