#!/usr/bin/env python3
"""
Import External Exercises from Multiple Sources
Adds exercises from StrengthLog, DIE RINGE, and White Coat Trainer to exercise_kb.json
"""

import json
import os
import re
from typing import List, Dict, Any, Set
from datetime import datetime

# File paths
EXERCISE_KB_PATH = os.path.join(os.path.dirname(__file__), 'exercise_kb.json')
BACKUP_PATH = os.path.join(os.path.dirname(__file__), 'exercise_kb_backup.json')

def load_existing_exercises() -> List[Dict[str, Any]]:
    """Load existing exercises from JSON"""
    try:
        with open(EXERCISE_KB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No existing exercise_kb.json found, starting fresh")
        return []

def backup_existing_exercises():
    """Create backup of existing exercises"""
    if os.path.exists(EXERCISE_KB_PATH):
        import shutil
        shutil.copy2(EXERCISE_KB_PATH, BACKUP_PATH)
        print(f"✅ Backup created: {BACKUP_PATH}")

def get_existing_exercise_names(exercises: List[Dict[str, Any]]) -> Set[str]:
    """Get set of existing exercise names for deduplication"""
    return {ex['name'].strip().lower() for ex in exercises}

def normalize_exercise_name(name: str) -> str:
    """Normalize exercise name for better matching"""
    # Remove common variations and standardize
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    
    # Common variations
    variations = {
        'push up': 'push-up',
        'pushup': 'push-up',
        'pull up': 'pull-up',
        'pullup': 'pull-up',
        'sit up': 'sit-up',
        'situp': 'sit-up',
        'chin up': 'chin-up',
        'chinup': 'chin-up',
        'dip': 'dips',
        'squat': 'squats',
        'lunge': 'lunges',
        'deadlift': 'deadlifts',
        'bench press': 'bench press',
        'overhead press': 'overhead press',
        'shoulder press': 'shoulder press'
    }
    
    for variant, standard in variations.items():
        if variant in name:
            name = name.replace(variant, standard)
    
    return name

def is_duplicate_exercise(new_name: str, existing_names: Set[str]) -> bool:
    """Check if exercise is a duplicate"""
    normalized_new = normalize_exercise_name(new_name)
    normalized_existing = {normalize_exercise_name(name) for name in existing_names}
    
    return normalized_new in normalized_existing

# ============================================================================
# STRENGTHLOG EXERCISES
# ============================================================================

STRENGTHLOG_EXERCISES = [
    # Chest Exercises
    {
        "name": "Assisted Dip",
        "description": "A dip variation using assistance to build strength for full dips",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Upper Body"],
        "progressions": ["Full Dips", "Weighted Dips"],
        "regressions": ["Band-Assisted Dips", "Negative Dips"],
        "contraindications": "Shoulder injuries, elbow pain",
        "cues": ["Keep chest up", "Control the movement", "Full range of motion"],
        "equipment": ["Dip Bars", "Resistance Bands"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Band-Assisted Bench Press",
        "description": "Bench press with resistance band assistance for building strength",
        "category": "Strength Training", 
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Barbell"],
        "progressions": ["Full Bench Press", "Weighted Bench Press"],
        "regressions": ["Dumbbell Bench Press", "Push-ups"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Retract scapula", "Drive through feet", "Control the bar"],
        "equipment": ["Barbell", "Bench", "Resistance Bands"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Bar Dip",
        "description": "Classic dip exercise using parallel bars for upper body strength",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Bodyweight"],
        "progressions": ["Weighted Dips", "Ring Dips"],
        "regressions": ["Assisted Dips", "Negative Dips"],
        "contraindications": "Shoulder injuries, elbow pain",
        "cues": ["Keep body straight", "Full range of motion", "Control descent"],
        "equipment": ["Dip Bars"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Bench Press",
        "description": "Fundamental compound exercise for chest, shoulders, and triceps",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Barbell"],
        "progressions": ["Weighted Bench Press", "Paused Bench Press"],
        "regressions": ["Dumbbell Bench Press", "Push-ups"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Retract scapula", "Drive through feet", "Control the bar"],
        "equipment": ["Barbell", "Bench", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Close-Grip Bench Press",
        "description": "Bench press variation with hands closer together to emphasize triceps",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Barbell"],
        "progressions": ["Weighted Close-Grip", "Paused Close-Grip"],
        "regressions": ["Regular Bench Press", "Dumbbell Close-Grip"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Hands shoulder-width apart", "Focus on triceps", "Control movement"],
        "equipment": ["Barbell", "Bench", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Decline Bench Press",
        "description": "Bench press on decline bench to target lower chest",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Barbell"],
        "progressions": ["Weighted Decline Press", "Paused Decline Press"],
        "regressions": ["Flat Bench Press", "Dumbbell Decline Press"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Secure feet", "Control the bar", "Full range of motion"],
        "equipment": ["Barbell", "Decline Bench", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Incline Bench Press",
        "description": "Bench press on incline bench to target upper chest",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Barbell"],
        "progressions": ["Weighted Incline Press", "Paused Incline Press"],
        "regressions": ["Flat Bench Press", "Dumbbell Incline Press"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Set incline angle", "Control the bar", "Full range of motion"],
        "equipment": ["Barbell", "Incline Bench", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Push-Up",
        "description": "Classic bodyweight exercise for chest, shoulders, and triceps",
        "category": "Strength Training",
        "tags": ["Chest", "Triceps", "Shoulders", "Compound", "Bodyweight"],
        "progressions": ["Decline Push-ups", "Weighted Push-ups"],
        "regressions": ["Incline Push-ups", "Knee Push-ups"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Full body alignment", "Control movement", "Full range of motion"],
        "equipment": ["None"],
        "mentor": "StrengthLog"
    },
    
    # Shoulder Exercises
    {
        "name": "Arnold Press",
        "description": "Dumbbell shoulder press with rotation for comprehensive shoulder development",
        "category": "Strength Training",
        "tags": ["Shoulders", "Triceps", "Compound", "Dumbbell"],
        "progressions": ["Weighted Arnold Press", "Standing Arnold Press"],
        "regressions": ["Seated Arnold Press", "Regular Dumbbell Press"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Rotate palms", "Control movement", "Full range of motion"],
        "equipment": ["Dumbbells"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Dumbbell Front Raise",
        "description": "Isolation exercise for anterior deltoids",
        "category": "Strength Training",
        "tags": ["Shoulders", "Isolation", "Dumbbell"],
        "progressions": ["Weighted Front Raises", "Cable Front Raises"],
        "regressions": ["Lighter Dumbbells", "Seated Front Raises"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Control movement", "Avoid swinging", "Full range of motion"],
        "equipment": ["Dumbbells"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Dumbbell Lateral Raise",
        "description": "Isolation exercise for lateral deltoids",
        "category": "Strength Training",
        "tags": ["Shoulders", "Isolation", "Dumbbell"],
        "progressions": ["Weighted Lateral Raises", "Cable Lateral Raises"],
        "regressions": ["Lighter Dumbbells", "Seated Lateral Raises"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Thumbs down", "Control movement", "Avoid swinging"],
        "equipment": ["Dumbbells"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Dumbbell Shoulder Press",
        "description": "Compound shoulder exercise with dumbbells",
        "category": "Strength Training",
        "tags": ["Shoulders", "Triceps", "Compound", "Dumbbell"],
        "progressions": ["Weighted Shoulder Press", "Standing Shoulder Press"],
        "regressions": ["Seated Shoulder Press", "Arnold Press"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Control movement", "Full range of motion", "Keep core tight"],
        "equipment": ["Dumbbells"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Overhead Press",
        "description": "Barbell shoulder press for compound upper body strength",
        "category": "Strength Training",
        "tags": ["Shoulders", "Triceps", "Compound", "Barbell"],
        "progressions": ["Weighted Overhead Press", "Push Press"],
        "regressions": ["Dumbbell Shoulder Press", "Seated Overhead Press"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Brace core", "Control movement", "Full range of motion"],
        "equipment": ["Barbell", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    
    # Back Exercises
    {
        "name": "Barbell Row",
        "description": "Compound back exercise with barbell",
        "category": "Strength Training",
        "tags": ["Back", "Biceps", "Compound", "Barbell"],
        "progressions": ["Weighted Barbell Row", "Paused Barbell Row"],
        "regressions": ["Dumbbell Row", "Cable Row"],
        "contraindications": "Lower back injuries, shoulder issues",
        "cues": ["Keep back straight", "Pull elbows back", "Control movement"],
        "equipment": ["Barbell"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Dumbbell Row",
        "description": "Unilateral back exercise with dumbbells",
        "category": "Strength Training",
        "tags": ["Back", "Biceps", "Compound", "Dumbbell"],
        "progressions": ["Weighted Dumbbell Row", "Renegade Row"],
        "regressions": ["Cable Row", "Machine Row"],
        "contraindications": "Lower back injuries, shoulder issues",
        "cues": ["Keep back straight", "Pull elbow back", "Control movement"],
        "equipment": ["Dumbbells", "Bench"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Lat Pulldown",
        "description": "Cable machine exercise for lat development",
        "category": "Strength Training",
        "tags": ["Back", "Biceps", "Compound", "Cable"],
        "progressions": ["Weighted Lat Pulldown", "Wide-Grip Pulldown"],
        "regressions": ["Assisted Pull-ups", "Cable Row"],
        "contraindications": "Shoulder injuries, neck issues",
        "cues": ["Pull to chest", "Squeeze shoulder blades", "Control movement"],
        "equipment": ["Cable Machine"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Pull-Up",
        "description": "Classic bodyweight back exercise",
        "category": "Strength Training",
        "tags": ["Back", "Biceps", "Compound", "Bodyweight"],
        "progressions": ["Weighted Pull-ups", "Muscle-ups"],
        "regressions": ["Assisted Pull-ups", "Lat Pulldown"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Full range of motion", "Control movement", "Engage back"],
        "equipment": ["Pull-up Bar"],
        "mentor": "StrengthLog"
    },
    
    # Leg Exercises
    {
        "name": "Barbell Squat",
        "description": "Fundamental compound leg exercise",
        "category": "Strength Training",
        "tags": ["Legs", "Compound", "Barbell"],
        "progressions": ["Weighted Squats", "Paused Squats"],
        "regressions": ["Goblet Squats", "Bodyweight Squats"],
        "contraindications": "Knee injuries, lower back issues",
        "cues": ["Keep chest up", "Drive through heels", "Full depth"],
        "equipment": ["Barbell", "Squat Rack"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Barbell Deadlift",
        "description": "Compound posterior chain exercise",
        "category": "Strength Training",
        "tags": ["Legs", "Back", "Compound", "Barbell"],
        "progressions": ["Weighted Deadlifts", "Deficit Deadlifts"],
        "regressions": ["Romanian Deadlifts", "Dumbbell Deadlifts"],
        "contraindications": "Lower back injuries, hip issues",
        "cues": ["Keep back straight", "Drive through heels", "Control movement"],
        "equipment": ["Barbell"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Leg Press",
        "description": "Machine-based leg exercise",
        "category": "Strength Training",
        "tags": ["Legs", "Compound", "Machine"],
        "progressions": ["Weighted Leg Press", "Single-Leg Press"],
        "regressions": ["Bodyweight Squats", "Goblet Squats"],
        "contraindications": "Knee injuries, hip issues",
        "cues": ["Full range of motion", "Control movement", "Keep back flat"],
        "equipment": ["Leg Press Machine"],
        "mentor": "StrengthLog"
    },
    {
        "name": "Romanian Deadlift",
        "description": "Hip hinge exercise focusing on hamstrings and glutes",
        "category": "Strength Training",
        "tags": ["Legs", "Back", "Compound", "Barbell"],
        "progressions": ["Weighted RDL", "Single-Leg RDL"],
        "regressions": ["Good Mornings", "Dumbbell RDL"],
        "contraindications": "Lower back injuries, hip issues",
        "cues": ["Hinge at hips", "Keep bar close", "Feel hamstrings"],
        "equipment": ["Barbell"],
        "mentor": "StrengthLog"
    }
]

# ============================================================================
# DIE RINGE CALISTHENICS EXERCISES
# ============================================================================

DIERINGE_EXERCISES = [
    {
        "name": "Passive Hang",
        "description": "Basic hanging position to build grip strength and shoulder decompression",
        "category": "Calisthenics",
        "tags": ["Grip", "Shoulders", "Back", "Bodyweight"],
        "progressions": ["Active Hang", "L-Sit Hang", "One-Arm Hang"],
        "regressions": ["Assisted Hang", "Shorter Duration"],
        "contraindications": "Shoulder injuries, wrist issues",
        "cues": ["Relax shoulders", "Full grip", "Breathe naturally"],
        "equipment": ["Pull-up Bar"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Support Hold",
        "description": "Holding position on rings or bars to build support strength",
        "category": "Calisthenics",
        "tags": ["Shoulders", "Triceps", "Core", "Bodyweight"],
        "progressions": ["Ring Support", "L-Sit Support", "Planche Lean"],
        "regressions": ["Bar Support", "Assisted Support"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Lock elbows", "Keep body straight", "Engage core"],
        "equipment": ["Rings", "Parallel Bars"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Hollow Body Hold",
        "description": "Core exercise to build body tension and control",
        "category": "Calisthenics",
        "tags": ["Core", "Bodyweight", "Isolation"],
        "progressions": ["Hollow Body Rocks", "Hollow Body Pull-ups"],
        "regressions": ["Tuck Hollow", "Shorter Duration"],
        "contraindications": "Lower back injuries",
        "cues": ["Press lower back to ground", "Lift shoulders and legs", "Hold tension"],
        "equipment": ["None"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "L-Sit",
        "description": "Advanced core exercise requiring compression and shoulder strength",
        "category": "Calisthenics",
        "tags": ["Core", "Shoulders", "Hip Flexors", "Bodyweight"],
        "progressions": ["Straddle L-Sit", "V-Sit", "Manna"],
        "regressions": ["Tuck L-Sit", "Assisted L-Sit"],
        "contraindications": "Shoulder injuries, hip issues",
        "cues": ["Press through shoulders", "Lift hips high", "Point toes"],
        "equipment": ["Parallel Bars", "Rings"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Handstand",
        "description": "Inverted balance skill requiring shoulder strength and body control",
        "category": "Calisthenics",
        "tags": ["Shoulders", "Balance", "Core", "Bodyweight"],
        "progressions": ["Handstand Walks", "One-Arm Handstand", "Handstand Push-ups"],
        "regressions": ["Wall Handstand", "Crow Pose"],
        "contraindications": "Shoulder injuries, wrist issues, vertigo",
        "cues": ["Point fingers", "Hollow body", "Look at hands"],
        "equipment": ["None", "Wall"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Muscle Up",
        "description": "Advanced transition from pull-up to dip on rings or bar",
        "category": "Calisthenics",
        "tags": ["Back", "Chest", "Shoulders", "Bodyweight"],
        "progressions": ["Ring Muscle Up", "Strict Muscle Up"],
        "regressions": ["Assisted Muscle Up", "Pull-up to Support"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Explosive pull", "Transition quickly", "Control dip"],
        "equipment": ["Rings", "Pull-up Bar"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Back Lever",
        "description": "Advanced static hold with body horizontal and back facing ground",
        "category": "Calisthenics",
        "tags": ["Back", "Shoulders", "Core", "Bodyweight"],
        "progressions": ["Full Back Lever", "One-Arm Back Lever"],
        "regressions": ["Tuck Back Lever", "Advanced Tuck Back Lever"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Pull with back", "Point toes", "Keep body straight"],
        "equipment": ["Rings"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Front Lever",
        "description": "Advanced static hold with body horizontal and chest facing ground",
        "category": "Calisthenics",
        "tags": ["Back", "Shoulders", "Core", "Bodyweight"],
        "progressions": ["Full Front Lever", "One-Arm Front Lever"],
        "regressions": ["Tuck Front Lever", "Advanced Tuck Front Lever"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Pull with lats", "Point toes", "Keep body straight"],
        "equipment": ["Rings", "Pull-up Bar"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Human Flag",
        "description": "Advanced static hold with body perpendicular to pole",
        "category": "Calisthenics",
        "tags": ["Core", "Shoulders", "Bodyweight"],
        "progressions": ["Full Human Flag", "One-Arm Human Flag"],
        "regressions": ["Tuck Human Flag", "Assisted Human Flag"],
        "contraindications": "Shoulder injuries, core issues",
        "cues": ["Grip pole tight", "Engage obliques", "Keep body straight"],
        "equipment": ["Pole"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "Planche",
        "description": "Advanced static hold with body horizontal and arms straight",
        "category": "Calisthenics",
        "tags": ["Shoulders", "Core", "Bodyweight"],
        "progressions": ["Full Planche", "One-Arm Planche"],
        "regressions": ["Tuck Planche", "Advanced Tuck Planche"],
        "contraindications": "Shoulder injuries, wrist issues",
        "cues": ["Lean forward", "Point fingers", "Keep body straight"],
        "equipment": ["Parallel Bars", "Floor"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "One Arm Pull Up",
        "description": "Advanced unilateral pulling exercise",
        "category": "Calisthenics",
        "tags": ["Back", "Biceps", "Bodyweight"],
        "progressions": ["Strict One Arm Pull Up", "One Arm Chin Up"],
        "regressions": ["Assisted One Arm Pull Up", "Archer Pull Up"],
        "contraindications": "Shoulder injuries, elbow issues",
        "cues": ["Grip tight", "Pull with back", "Control movement"],
        "equipment": ["Pull-up Bar"],
        "mentor": "DIE RINGE"
    },
    {
        "name": "One Arm Push Up",
        "description": "Advanced unilateral pushing exercise",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Strict One Arm Push Up", "One Arm Handstand Push Up"],
        "regressions": ["Assisted One Arm Push Up", "Archer Push Up"],
        "contraindications": "Shoulder injuries, wrist issues",
        "cues": ["Wide stance", "Keep body straight", "Control movement"],
        "equipment": ["None"],
        "mentor": "DIE RINGE"
    }
]

# ============================================================================
# WHITE COAT TRAINER CALISTHENICS EXERCISES
# ============================================================================

WHITECOATTRAINER_EXERCISES = [
    {
        "name": "Wall Push-Up",
        "description": "Beginner push-up variation against wall for building strength",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight", "Beginner"],
        "progressions": ["Incline Push-up", "Knee Push-up", "Standard Push-up"],
        "regressions": ["Assisted Wall Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Keep body straight", "Control movement", "Full range of motion"],
        "equipment": ["Wall"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Incline Push-Up",
        "description": "Push-up variation with hands elevated to reduce difficulty",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Standard Push-up", "Decline Push-up"],
        "regressions": ["Wall Push-up", "Knee Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Keep body straight", "Control movement", "Full range of motion"],
        "equipment": ["Bench", "Box", "Stairs"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Kneeling Push-Up",
        "description": "Push-up variation on knees to reduce body weight load",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Standard Push-up", "Incline Push-up"],
        "regressions": ["Wall Push-up", "Assisted Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Keep body straight", "Control movement", "Full range of motion"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Close Grip Push-Up",
        "description": "Push-up with hands close together to emphasize triceps",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Diamond Push-up", "Close Grip Dips"],
        "regressions": ["Standard Push-up", "Incline Close Grip Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Hands close together", "Keep elbows in", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Decline Push-Up",
        "description": "Push-up with feet elevated to increase difficulty",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Handstand Push-up", "One Arm Push-up"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Keep body straight", "Control movement", "Full range of motion"],
        "equipment": ["Bench", "Box", "Stairs"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Wide Grip Push-Up",
        "description": "Push-up with hands wide apart to emphasize chest",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Wide Grip Dips", "Ring Push-up"],
        "regressions": ["Standard Push-up", "Incline Wide Grip Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Hands wide apart", "Keep body straight", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Parallette Push-Up",
        "description": "Push-up on parallettes for increased range of motion",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Ring Push-up", "Handstand Push-up"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Grip parallettes tight", "Keep body straight", "Full range of motion"],
        "equipment": ["Parallettes"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Uneven Push-Up",
        "description": "Push-up with one hand elevated to work each side differently",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["One Arm Push-up", "Archer Push-up"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Keep body straight", "Control movement", "Switch sides"],
        "equipment": ["Box", "Bench"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "One-Handed Push-Up",
        "description": "Advanced unilateral push-up variation",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight", "Advanced"],
        "progressions": ["One Arm Handstand Push-up"],
        "regressions": ["Archer Push-up", "Uneven Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Wide stance", "Keep body straight", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Dynamic Push-Up",
        "description": "Explosive push-up variation for power development",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight", "Plyometric"],
        "progressions": ["Clap Push-up", "Plyo Push-up"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Explosive push", "Land softly", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Pike Push-Up",
        "description": "Push-up variation with hips elevated to target shoulders",
        "category": "Calisthenics",
        "tags": ["Shoulders", "Triceps", "Core", "Bodyweight"],
        "progressions": ["Handstand Push-up", "Wall Handstand Push-up"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Elevate hips", "Point head toward ground", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Diamond Push-Up",
        "description": "Push-up with hands forming diamond shape to emphasize triceps",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight"],
        "progressions": ["Close Grip Dips", "Ring Diamond Push-up"],
        "regressions": ["Close Grip Push-up", "Standard Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Form diamond with hands", "Keep elbows in", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Archer Push-Up",
        "description": "Advanced push-up variation with one arm extended",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight", "Advanced"],
        "progressions": ["One Arm Push-up", "Planche Push-up"],
        "regressions": ["Uneven Push-up", "Standard Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Extend one arm", "Keep body straight", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Pseudo Planche Push-Up",
        "description": "Push-up with body leaned forward to simulate planche position",
        "category": "Calisthenics",
        "tags": ["Chest", "Triceps", "Shoulders", "Bodyweight", "Advanced"],
        "progressions": ["Planche Push-up", "Planche Lean"],
        "regressions": ["Standard Push-up", "Incline Push-up"],
        "contraindications": "Shoulder injuries, wrist pain",
        "cues": ["Lean forward", "Point fingers", "Control movement"],
        "equipment": ["None"],
        "mentor": "White Coat Trainer"
    },
    {
        "name": "Handstand Push-Up",
        "description": "Advanced push-up variation performed in handstand position",
        "category": "Calisthenics",
        "tags": ["Shoulders", "Triceps", "Core", "Bodyweight", "Advanced"],
        "progressions": ["One Arm Handstand Push-up", "Handstand Walk"],
        "regressions": ["Wall Handstand Push-up", "Pike Push-up"],
        "contraindications": "Shoulder injuries, wrist pain, vertigo",
        "cues": ["Stable handstand", "Control movement", "Full range of motion"],
        "equipment": ["Wall"],
        "mentor": "White Coat Trainer"
    }
]

def import_external_exercises():
    """Import exercises from all three sources with deduplication"""
    print("🔄 Starting external exercise import...")
    
    # Load existing exercises
    existing_exercises = load_existing_exercises()
    existing_names = get_existing_exercise_names(existing_exercises)
    
    print(f"📊 Found {len(existing_exercises)} existing exercises")
    
    # Create backup
    backup_existing_exercises()
    
    # Combine all new exercises
    all_new_exercises = []
    all_new_exercises.extend(STRENGTHLOG_EXERCISES)
    all_new_exercises.extend(DIERINGE_EXERCISES)
    all_new_exercises.extend(WHITECOATTRAINER_EXERCISES)
    
    print(f"📚 Found {len(all_new_exercises)} potential new exercises")
    
    # Filter out duplicates
    new_exercises = []
    duplicates = []
    
    for exercise in all_new_exercises:
        if is_duplicate_exercise(exercise['name'], existing_names):
            duplicates.append(exercise['name'])
        else:
            new_exercises.append(exercise)
            existing_names.add(exercise['name'].lower())
    
    print(f"✅ Found {len(new_exercises)} new exercises to add")
    print(f"⚠️ Skipped {len(duplicates)} duplicates")
    
    if duplicates:
        print("📋 Duplicates found:")
        for dup in duplicates[:10]:  # Show first 10
            print(f"  - {dup}")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
    
    # Add new exercises to existing list
    final_exercises = existing_exercises + new_exercises
    
    # Save updated exercise library
    with open(EXERCISE_KB_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_exercises, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(final_exercises)} total exercises to {EXERCISE_KB_PATH}")
    
    # Print summary by source
    print("\n📊 Summary by source:")
    sources = {}
    for ex in final_exercises:
        mentor = ex.get('mentor', 'Unknown')
        sources[mentor] = sources.get(mentor, 0) + 1
    
    for source, count in sources.items():
        print(f"  {source}: {count} exercises")
    
    print(f"\n🎉 Successfully imported {len(new_exercises)} new exercises!")
    return new_exercises

if __name__ == "__main__":
    import_external_exercises() 