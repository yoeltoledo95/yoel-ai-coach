import os
import json
import re
from typing import List, Dict, Any

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'exercise_library.txt')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'exercise_kb.json')

def parse_exercise_library():
    """Parse the exercise library text file and extract exercises"""
    exercises = []
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into sections by category
        sections = re.split(r'\n\s*\d+\.\d+\s*\.\s*', content)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract category name
            category_match = re.search(r'^([A-Za-z\s]+)', section.strip())
            if not category_match:
                continue
                
            category = category_match.group(1).strip()
            # Clean up category name
            if 'Foundational Movement Patterns' in category:
                category = 'Foundational Movement Patterns'
            elif 'Gym/Strength Training Exercises' in category:
                category = 'Gym/Strength Training'
            elif 'Yoga Exercises' in category:
                category = 'Yoga'
            elif 'Weightlifting Exercises' in category:
                category = 'Weightlifting'
            elif 'Flexibility Exercises' in category:
                category = 'Flexibility'
            
            print(f"Processing category: {category}")
            
            # Check if section has tabular format
            has_tabular = 'Category' in section and 'Name' in section
            print(f"  Has tabular format: {has_tabular}")
            
            if has_tabular:
                # Parse tabular format (Foundational Movement Patterns)
                tabular_exercises = parse_tabular_format(section, category)
                exercises.extend(tabular_exercises)
                print(f"  Extracted {len(tabular_exercises)} tabular exercises")
            else:
                # Parse bullet-point format (all other sections)
                bullet_exercises = parse_bullet_format(section, category)
                exercises.extend(bullet_exercises)
                print(f"  Extracted {len(bullet_exercises)} bullet exercises")
        
        print(f"\nTotal exercises extracted: {len(exercises)}")
        return exercises
        
    except Exception as e:
        print(f"Error parsing exercise library: {e}")
        return []

def parse_tabular_format(section: str, category: str) -> List[Dict[str, Any]]:
    """Parse tabular format exercises"""
    exercises = []
    
    # Find the table in this section
    table_start = section.find('Category')
    if table_start == -1:
        return []
    
    table_content = section[table_start:]
    lines = [line for line in table_content.split('\n') if line.strip()]
    
    # This is a vertical format where each exercise spans multiple lines
    # Format: Category, Name, Description, Tags, Progressions, Regressions, Contraindications, Cues, Equipment
    current_exercise = None
    exercise_data = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check if this is a new exercise category (Squat, Hinge, Lunge, etc.)
        if line in ['Squat', 'Hinge', 'Lunge', 'Push', 'Pull', 'Rotation', 'Gait']:
            # Save previous exercise if exists
            if current_exercise and exercise_data.get('name'):
                exercise = create_exercise_from_vertical_format(exercise_data, category)
                if exercise:
                    exercises.append(exercise)
            
            # Start new exercise
            current_exercise = line
            exercise_data = {'category': line}
            continue
        
        # If we have a current exercise, collect the data
        if current_exercise and line:
            # Determine which field this line represents based on position
            if 'name' not in exercise_data:
                exercise_data['name'] = line
            elif 'description' not in exercise_data:
                exercise_data['description'] = line
            elif 'tags' not in exercise_data:
                exercise_data['tags'] = [tag.strip() for tag in line.split(',') if tag.strip()]
            elif 'progressions' not in exercise_data:
                exercise_data['progressions'] = [p.strip() for p in line.split(',') if p.strip()]
            elif 'regressions' not in exercise_data:
                exercise_data['regressions'] = [r.strip() for r in line.split(',') if r.strip()]
            elif 'contraindications' not in exercise_data:
                exercise_data['contraindications'] = [c.strip() for c in line.split(',') if c.strip()]
            elif 'cues' not in exercise_data:
                exercise_data['cues'] = [cue.strip() for cue in line.split(';') if cue.strip()]
            elif 'equipment' not in exercise_data:
                exercise_data['equipment'] = [eq.strip() for eq in line.split(',') if eq.strip()]
    
    # Add the last exercise
    if current_exercise and exercise_data.get('name'):
        exercise = create_exercise_from_vertical_format(exercise_data, category)
        if exercise:
            exercises.append(exercise)
    
    return exercises

def parse_bullet_format(section: str, category: str) -> List[Dict[str, Any]]:
    """Parse bullet point format exercises"""
    exercises = []
    
    # Find bullet point exercises (lines starting with *)
    lines = section.split('\n')
    current_exercise = None
    
    for original_line in lines:
        line = original_line.strip()
        
        # Check if this is a new exercise (starts with * and no leading spaces in original)
        if line.startswith('* ') and not original_line.startswith('   *'):
            # Save previous exercise if exists
            if current_exercise and current_exercise.get('name'):
                # Add pattern, discipline, and muscles
                current_exercise['pattern'] = determine_pattern(category, current_exercise.get('tags', []))
                current_exercise['discipline'] = determine_discipline(category)
                primary_muscles, secondary_muscles = determine_muscles(current_exercise.get('tags', []))
                if primary_muscles:
                    current_exercise['primary_muscles'] = primary_muscles
                if secondary_muscles:
                    current_exercise['secondary_muscles'] = secondary_muscles
                exercises.append(current_exercise)
            
            # Start new exercise
            exercise_name = line[2:].strip()
            current_exercise = {
                'name': exercise_name,
                'category': category,
                'description': '',
                'tags': [],
                'progressions': [],
                'regressions': [],
                'contraindications': [],
                'cues': [],
                'equipment': []
            }
        
        # Parse exercise details (lines starting with 3 spaces and *)
        elif current_exercise and original_line.startswith('   * '):
            detail_line = original_line[5:].strip()
            
            if detail_line.startswith('Description:'):
                current_exercise['description'] = detail_line[12:].strip()
            elif detail_line.startswith('Tags:'):
                tags_str = detail_line[5:].strip()
                current_exercise['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            elif detail_line.startswith('Progressions:'):
                progressions_str = detail_line[13:].strip()
                current_exercise['progressions'] = [p.strip() for p in progressions_str.split(',') if p.strip()]
            elif detail_line.startswith('Regressions:'):
                regressions_str = detail_line[12:].strip()
                current_exercise['regressions'] = [r.strip() for r in regressions_str.split(',') if r.strip()]
            elif detail_line.startswith('Contraindications:'):
                contraindications_str = detail_line[18:].strip()
                current_exercise['contraindications'] = [c.strip() for c in contraindications_str.split(',') if c.strip()]
            elif detail_line.startswith('Cues:'):
                cues_str = detail_line[5:].strip()
                current_exercise['cues'] = [cue.strip() for cue in cues_str.split(';') if cue.strip()]
            elif detail_line.startswith('Equipment:'):
                equipment_str = detail_line[10:].strip()
                current_exercise['equipment'] = [eq.strip() for eq in equipment_str.split(',') if eq.strip()]
    
    # Add the last exercise
    if current_exercise and current_exercise.get('name'):
        # Add pattern, discipline, and muscles
        current_exercise['pattern'] = determine_pattern(category, current_exercise.get('tags', []))
        current_exercise['discipline'] = determine_discipline(category)
        primary_muscles, secondary_muscles = determine_muscles(current_exercise.get('tags', []))
        if primary_muscles:
            current_exercise['primary_muscles'] = primary_muscles
        if secondary_muscles:
            current_exercise['secondary_muscles'] = secondary_muscles
        exercises.append(current_exercise)
    
    return exercises

def create_exercise_from_tabular_row(row: List[str], category: str) -> Dict[str, Any]:
    """Create an exercise object from a tabular row"""
    try:
        if len(row) < 2:
            return None
        
        # Extract fields from the row - the format is: Category, Name, Description, Tags, Progressions, Regressions, Contraindications, Cues, Equipment
        exercise_name = row[1].strip() if len(row) > 1 else ""
        description = row[2].strip() if len(row) > 2 else ""
        tags_str = row[3].strip() if len(row) > 3 else ""
        progressions_str = row[4].strip() if len(row) > 4 else ""
        regressions_str = row[5].strip() if len(row) > 5 else ""
        contraindications_str = row[6].strip() if len(row) > 6 else ""
        cues_str = row[7].strip() if len(row) > 7 else ""
        equipment_str = row[8].strip() if len(row) > 8 else ""
        
        # Skip if no exercise name
        if not exercise_name:
            return None
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Parse progressions and regressions
        progressions = [p.strip() for p in progressions_str.split(',') if p.strip()]
        regressions = [r.strip() for r in regressions_str.split(',') if r.strip()]
        
        # Parse contraindications
        contraindications = [c.strip() for c in contraindications_str.split(',') if c.strip()]
        
        # Parse cues
        cues = [cue.strip() for cue in cues_str.split(';') if cue.strip()]
        
        # Parse equipment
        equipment = [eq.strip() for eq in equipment_str.split(',') if eq.strip()]
        
        # Determine pattern based on category and tags
        pattern = determine_pattern(category, tags)
        
        # Determine discipline based on category
        discipline = determine_discipline(category)
        
        # Determine primary and secondary muscles
        primary_muscles, secondary_muscles = determine_muscles(tags)
        
        return {
            'name': exercise_name,
            'category': category,
            'description': description,
            'tags': tags,
            'progressions': progressions,
            'regressions': regressions,
            'contraindications': contraindications,
            'cues': cues,
            'equipment': equipment,
            'pattern': pattern,
            'discipline': discipline,
            'primary_muscles': primary_muscles,
            'secondary_muscles': secondary_muscles
        }
        
    except Exception as e:
        print(f"Error creating exercise from row: {e}")
        return None

def create_exercise_from_vertical_format(exercise_data: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Create an exercise object from vertical format data"""
    try:
        exercise_name = exercise_data.get('name', '')
        description = exercise_data.get('description', '')
        tags = exercise_data.get('tags', [])
        progressions = exercise_data.get('progressions', [])
        regressions = exercise_data.get('regressions', [])
        contraindications = exercise_data.get('contraindications', [])
        cues = exercise_data.get('cues', [])
        equipment = exercise_data.get('equipment', [])
        
        # Skip if no exercise name
        if not exercise_name:
            return None
        
        # Determine pattern based on category and tags
        pattern = determine_pattern(category, tags)
        
        # Determine discipline based on category
        discipline = determine_discipline(category)
        
        # Determine primary and secondary muscles
        primary_muscles, secondary_muscles = determine_muscles(tags)
        
        return {
            'name': exercise_name,
            'category': category,
            'description': description,
            'tags': tags,
            'progressions': progressions,
            'regressions': regressions,
            'contraindications': contraindications,
            'cues': cues,
            'equipment': equipment,
            'pattern': pattern,
            'discipline': discipline,
            'primary_muscles': primary_muscles,
            'secondary_muscles': secondary_muscles
        }
        
    except Exception as e:
        print(f"Error creating exercise from vertical format: {e}")
        return None

def determine_pattern(category: str, tags: List[str]) -> str:
    """Determine the movement pattern based on category and tags"""
    category_lower = category.lower()
    tags_lower = [tag.lower() for tag in tags]
    
    if 'squat' in category_lower or any('squat' in tag for tag in tags_lower):
        return 'squat'
    elif 'hinge' in category_lower or any('hinge' in tag for tag in tags_lower):
        return 'hinge'
    elif 'lunge' in category_lower or any('lunge' in tag for tag in tags_lower):
        return 'lunge'
    elif 'push' in category_lower or any('push' in tag for tag in tags_lower):
        return 'push'
    elif 'pull' in category_lower or any('pull' in tag for tag in tags_lower):
        return 'pull'
    elif 'rotation' in category_lower or any('rotation' in tag for tag in tags_lower):
        return 'rotation'
    elif 'gait' in category_lower or any('gait' in tag for tag in tags_lower):
        return 'gait'
    else:
        return 'core'

def determine_discipline(category: str) -> str:
    """Determine the discipline based on category"""
    category_lower = category.lower()
    
    if 'yoga' in category_lower:
        return 'yoga'
    elif 'weightlifting' in category_lower:
        return 'weightlifting'
    elif 'flexibility' in category_lower:
        return 'flexibility'
    elif 'gym' in category_lower or 'strength' in category_lower:
        return 'strength'
    else:
        return 'general'

def determine_muscles(tags: List[str]) -> tuple:
    """Determine primary and secondary muscles from tags"""
    primary_muscles = []
    secondary_muscles = []
    
    muscle_mapping = {
        'quads': 'quadriceps',
        'glutes': 'glutes',
        'hamstrings': 'hamstrings',
        'core': 'core',
        'chest': 'pectorals',
        'shoulders': 'deltoids',
        'triceps': 'triceps',
        'biceps': 'biceps',
        'back': 'latissimus_dorsi',
        'lats': 'latissimus_dorsi',
        'calves': 'gastrocnemius',
        'abs': 'rectus_abdominis',
        'obliques': 'obliques',
        'traps': 'trapezius',
        'forearms': 'forearms',
        'adductors': 'adductors',
        'hip_flexors': 'hip_flexors'
    }
    
    for tag in tags:
        tag_lower = tag.lower()
        for key, muscle in muscle_mapping.items():
            if key in tag_lower:
                if len(primary_muscles) < 2:  # Limit primary muscles
                    primary_muscles.append(muscle)
                else:
                    secondary_muscles.append(muscle)
                break
    
    return primary_muscles, secondary_muscles

def save_exercises_to_json(exercises: List[Dict[str, Any]]):
    """Save exercises to JSON file"""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(exercises)} exercises to {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error saving exercises: {e}")

def main():
    """Main function to extract and save exercises"""
    print("🔍 Extracting exercises from exercise library...")
    exercises = parse_exercise_library()
    
    if exercises:
        save_exercises_to_json(exercises)
        print("✅ Successfully extracted exercises")
        
        # Show sample of extracted exercises
        print("\n📋 Sample exercises extracted:")
        for i, exercise in enumerate(exercises[:5], 1):
            print(f"  {i}. {exercise['name']} ({exercise['category']})")
        
        if len(exercises) > 5:
            print(f"  ... and {len(exercises) - 5} more exercises")
    else:
        print("❌ No exercises extracted")

if __name__ == "__main__":
    main() 