#!/usr/bin/env python3
"""
Fix exercise mentor mapping - map website sources to actual mentors
Support multiple mentors per exercise
"""
import json
import os
from pathlib import Path

# Mapping from website sources to actual mentors
SOURCE_TO_MENTOR_MAPPING = {
    # Website sources -> Actual mentors
    "StrengthLog": "tom_merrick",  # General strength training
    "DIE RINGE": "ido_portal",     # Movement complexity and rings
    "White Coat Trainer": "tom_merrick",  # Calisthenics and bodyweight exercises
    "Everydamnandre": "everydamnandre",  # Kettlebell and conditioning
    "KneesOverToesGuy": "kneesovertoesguy",  # Joint health
    "Emmet Louis": "emmet_louis",  # Mobility and flexibility
    "Patrick Beach": "patrick_beach",  # Natural movement and mobility
}

# Valid mentors from mentor_brain.py
VALID_MENTORS = {
    "dylan_werner",
    "ido_portal", 
    "patrick_beach",
    "tom_merrick",
    "everydamnandre",
    "kneesovertoesguy",
    "emmet_louis"
}

# Multi-mentor assignments for exercises that span multiple philosophies
MULTI_MENTOR_EXERCISES = {
    "Bodyweight Squat": ["tom_merrick", "ido_portal"],  # Strength + Movement
    "Push-up": ["tom_merrick", "ido_portal"],  # Calisthenics + Movement
    "Pull-up": ["tom_merrick", "ido_portal"],  # Calisthenics + Movement
    "Handstand": ["ido_portal", "dylan_werner"],  # Movement + Control
    "Plank": ["tom_merrick", "dylan_werner"],  # Strength + Control
    "Downward-Facing Dog (Adho Mukha Svanasana)": ["dylan_werner", "emmet_louis"],  # Yoga + Mobility
    "Cat-Cow Pose (Marjaryasana-Bitilasana)": ["dylan_werner", "ido_portal"],  # Yoga + Movement
    "Walking": ["ido_portal", "patrick_beach"],  # Movement + Natural
    "Good Morning": ["tom_merrick", "kneesovertoesguy"],  # Strength + Joint Health
    "Forward Lunge": ["tom_merrick", "ido_portal"],  # Strength + Movement
    "Russian Twist": ["tom_merrick", "ido_portal"],  # Strength + Movement
    "Seated Spinal Twist": ["dylan_werner", "emmet_louis"],  # Yoga + Mobility
}

def fix_exercise_mentors():
    """Fix mentor mapping in exercise knowledge base"""
    
    # Load exercise data
    exercise_file = Path("data/exercises/exercise_kb.json")
    if not exercise_file.exists():
        print("❌ Exercise file not found")
        return
    
    with open(exercise_file, 'r', encoding='utf-8') as f:
        exercises = json.load(f)
    
    print(f"📖 Loaded {len(exercises)} exercises")
    
    # Track changes
    changes_made = 0
    removed_mentors = 0
    multi_mentor_added = 0
    
    for exercise in exercises:
        exercise_name = exercise['name']
        current_mentor = exercise.get('mentor', '')
        
        # Check if this exercise should have multiple mentors
        if exercise_name in MULTI_MENTOR_EXERCISES:
            exercise['mentor'] = ','.join(MULTI_MENTOR_EXERCISES[exercise_name])
            multi_mentor_added += 1
            print(f"✅ Added multi-mentor '{exercise['mentor']}' to {exercise_name}")
            continue
        
        if current_mentor:
            # Check if it's already a valid mentor
            if current_mentor in VALID_MENTORS:
                # Already correct
                continue
            elif current_mentor in SOURCE_TO_MENTOR_MAPPING:
                # Map to correct mentor
                exercise['mentor'] = SOURCE_TO_MENTOR_MAPPING[current_mentor]
                changes_made += 1
                print(f"✅ Mapped '{current_mentor}' -> '{SOURCE_TO_MENTOR_MAPPING[current_mentor]}' for {exercise_name}")
            else:
                # Unknown source, remove mentor field
                removed_mentors += 1
                print(f"⚠️ Removed unknown mentor '{current_mentor}' from {exercise_name}")
                exercise.pop('mentor', None)
        else:
            # No mentor field, add based on exercise characteristics
            suggested_mentor = suggest_mentor_for_exercise(exercise)
            if suggested_mentor:
                exercise['mentor'] = suggested_mentor
                changes_made += 1
                print(f"✅ Added mentor '{suggested_mentor}' to {exercise_name}")
    
    # Save updated exercises
    with open(exercise_file, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Summary:")
    print(f"✅ Mapped {changes_made} exercises to correct mentors")
    print(f"✅ Added {multi_mentor_added} multi-mentor assignments")
    print(f"⚠️ Removed {removed_mentors} unknown mentor sources")
    print(f"💾 Saved updated exercise knowledge base")

def suggest_mentor_for_exercise(exercise):
    """Suggest mentor based on exercise characteristics"""
    name = exercise['name'].lower()
    tags = [tag.lower() for tag in exercise.get('tags', [])]
    category = exercise.get('category', '').lower()
    
    # Dylan Werner - yoga, control, balance
    if any(word in name for word in ['yoga', 'balance', 'control', 'flow']):
        return 'dylan_werner'
    if any(tag in tags for tag in ['yoga', 'balance', 'control']):
        return 'dylan_werner'
    
    # Ido Portal - movement complexity, rings, locomotion
    if any(word in name for word in ['crawl', 'locomotion', 'rings', 'handstand', 'movement']):
        return 'ido_portal'
    if any(tag in tags for tag in ['movement', 'complex', 'rings']):
        return 'ido_portal'
    
    # Tom Merrick - calisthenics, bodyweight
    if any(word in name for word in ['pushup', 'pullup', 'dip', 'calisthenic']):
        return 'tom_merrick'
    if any(tag in tags for tag in ['calisthenics', 'bodyweight']):
        return 'tom_merrick'
    
    # Everydamnandre - kettlebell, conditioning
    if any(word in name for word in ['kettlebell', 'swing', 'clean', 'snatch']):
        return 'everydamnandre'
    if any(tag in tags for tag in ['kettlebell', 'conditioning']):
        return 'everydamnandre'
    
    # KneesOverToesGuy - joint health, knee/ankle
    if any(word in name for word in ['knee', 'ankle', 'tibialis', 'sled']):
        return 'kneesovertoesguy'
    if any(tag in tags for tag in ['joint', 'knee', 'ankle']):
        return 'kneesovertoesguy'
    
    # Emmet Louis - mobility, flexibility
    if any(word in name for word in ['mobility', 'flexibility', 'stretch', 'range']):
        return 'emmet_louis'
    if any(tag in tags for tag in ['mobility', 'flexibility']):
        return 'emmet_louis'
    
    # Patrick Beach - natural movement, fluid
    if any(word in name for word in ['natural', 'fluid', 'flow']):
        return 'patrick_beach'
    if any(tag in tags for tag in ['natural', 'fluid']):
        return 'patrick_beach'
    
    # Default based on category
    if 'strength' in category:
        return 'tom_merrick'
    elif 'flexibility' in category:
        return 'emmet_louis'
    elif 'movement' in category:
        return 'ido_portal'
    
    return None

if __name__ == "__main__":
    fix_exercise_mentors() 