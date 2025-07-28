"""
SQLite implementation of exercise repository
"""
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.entities.exercise import Exercise, ExerciseCategory, ExerciseDifficulty, ExerciseVariation
from domain.repositories.exercise_repository import ExerciseRepository

logger = logging.getLogger(__name__)

class SQLiteExerciseRepository(ExerciseRepository):
    """SQLite implementation of exercise repository"""
    
    def __init__(self, exercise_kb_path: str = "data/exercises/exercise_kb.json"):
        self.exercise_kb_path = Path(exercise_kb_path)
        self.exercises = self._load_exercises()
    
    def _load_exercises(self) -> List[Exercise]:
        """Load exercises from knowledge base"""
        try:
            if not self.exercise_kb_path.exists():
                # Try relative to current directory
                self.exercise_kb_path = Path("../data/exercises/exercise_kb.json")
            
            with open(self.exercise_kb_path, 'r', encoding='utf-8') as f:
                exercise_data = json.load(f)
            
            exercises = []
            for data in exercise_data:
                exercise = self._create_exercise_entity(data)
                if exercise:
                    exercises.append(exercise)
            
            logger.info(f"✅ Loaded {len(exercises)} exercises from knowledge base")
            return exercises
            
        except Exception as e:
            logger.error(f"❌ Error loading exercises: {e}")
            return []
    
    def _create_exercise_entity(self, data: Dict[str, Any]) -> Optional[Exercise]:
        """Create Exercise entity from data"""
        try:
            # Map category string to enum
            category_str = data.get('category', '').lower()
            category = self._map_category(category_str)
            
            # Map difficulty (default to intermediate)
            difficulty = ExerciseDifficulty.INTERMEDIATE
            
            # Create progressions and regressions
            progressions = []
            for prog in data.get('progressions', []):
                progressions.append(ExerciseVariation(
                    name=prog,
                    description=f"Progression of {data['name']}",
                    difficulty=ExerciseDifficulty.ADVANCED
                ))
            
            regressions = []
            for reg in data.get('regressions', []):
                regressions.append(ExerciseVariation(
                    name=reg,
                    description=f"Regression of {data['name']}",
                    difficulty=ExerciseDifficulty.BEGINNER
                ))
            
            return Exercise(
                exercise_id=data.get('name', '').lower().replace(' ', '_'),
                name=data.get('name', ''),
                description=data.get('description', ''),
                category=category,
                difficulty=difficulty,
                tags=data.get('tags', []),
                equipment=data.get('equipment', []),
                muscle_groups=data.get('primary_muscles', []) + data.get('secondary_muscles', []),
                cues=data.get('cues', []),
                progressions=progressions,
                regressions=regressions,
                contraindications=data.get('contraindications', []),
                source=data.get('mentor', 'Unknown')
            )
            
        except Exception as e:
            logger.error(f"Error creating exercise entity: {e}")
            return None
    
    def _map_category(self, category_str: str) -> ExerciseCategory:
        """Map category string to enum"""
        mapping = {
            'foundational movement patterns': ExerciseCategory.FOUNDATIONAL_MOVEMENT,
            'strength training': ExerciseCategory.STRENGTH_TRAINING,
            'calisthenics': ExerciseCategory.BODYWEIGHT,
            'yoga': ExerciseCategory.YOGA,
            'weightlifting': ExerciseCategory.WEIGHTLIFTING,
            'flexibility': ExerciseCategory.FLEXIBILITY,
            'cardio': ExerciseCategory.CARDIO
        }
        return mapping.get(category_str, ExerciseCategory.STRENGTH_TRAINING)
    
    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get exercise by ID"""
        for exercise in self.exercises:
            if exercise.exercise_id == exercise_id:
                return exercise
        return None
    
    def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """Get exercise by name"""
        for exercise in self.exercises:
            if exercise.name.lower() == name.lower():
                return exercise
        return None
    
    def get_all_exercises(self) -> List[Exercise]:
        """Get all exercises"""
        return self.exercises
    
    def search_exercises(self, query: str) -> List[Exercise]:
        """Search exercises by query"""
        query_lower = query.lower()
        results = []
        
        for exercise in self.exercises:
            # Search in name, description, tags
            if (query_lower in exercise.name.lower() or
                query_lower in exercise.description.lower() or
                any(query_lower in tag.lower() for tag in exercise.tags)):
                results.append(exercise)
        
        return results
    
    def get_exercises_by_category(self, category: ExerciseCategory) -> List[Exercise]:
        """Get exercises by category"""
        return [ex for ex in self.exercises if ex.category == category]
    
    def get_exercises_by_difficulty(self, difficulty: ExerciseDifficulty) -> List[Exercise]:
        """Get exercises by difficulty level"""
        return [ex for ex in self.exercises if ex.difficulty == difficulty]
    
    def get_exercises_by_tags(self, tags: List[str]) -> List[Exercise]:
        """Get exercises by tags"""
        results = []
        for exercise in self.exercises:
            exercise_tags = [tag.lower() for tag in exercise.tags]
            if any(tag.lower() in exercise_tags for tag in tags):
                results.append(exercise)
        return results
    
    def get_exercises_for_equipment(self, equipment: List[str]) -> List[Exercise]:
        """Get exercises that can be done with available equipment"""
        results = []
        for exercise in self.exercises:
            if exercise.matches_equipment(equipment):
                results.append(exercise)
        return results
    
    def get_exercises_for_injuries(self, injuries: List[str]) -> List[Exercise]:
        """Get exercises suitable for users with specific injuries"""
        results = []
        for exercise in self.exercises:
            if all(exercise.is_suitable_for_injury(injury) for injury in injuries):
                results.append(exercise)
        return results
    
    def get_exercises_by_muscle_groups(self, muscle_groups: List[str]) -> List[Exercise]:
        """Get exercises targeting specific muscle groups"""
        results = []
        for exercise in self.exercises:
            exercise_muscles = [muscle.lower() for muscle in exercise.muscle_groups]
            if any(muscle.lower() in exercise_muscles for muscle in muscle_groups):
                results.append(exercise)
        return results
    
    def get_exercises_by_mentor(self, mentor_name: str) -> List[Exercise]:
        """Get exercises associated with a specific mentor"""
        results = []
        for exercise in self.exercises:
            if exercise.source:
                # Handle multiple mentors (comma-separated)
                exercise_mentors = [m.strip().lower() for m in exercise.source.split(',')]
                if mentor_name.lower() in exercise_mentors:
                    results.append(exercise)
        return results
    
    def get_exercises_by_movement_pattern(self, pattern: str) -> List[Exercise]:
        """Get exercises by movement pattern (push, pull, hinge, squat, etc.)"""
        pattern_lower = pattern.lower()
        results = []
        
        for exercise in self.exercises:
            # Check tags for movement patterns
            if any(pattern_lower in tag.lower() for tag in exercise.tags):
                results.append(exercise)
            # Check name for common patterns
            elif pattern_lower in exercise.name.lower():
                results.append(exercise)
        
        return results
    
    def get_recommended_exercises(
        self, 
        user_goals: List[str], 
        user_level: str, 
        available_equipment: List[str],
        injuries: List[str] = None
    ) -> List[Exercise]:
        """Get recommended exercises based on user profile"""
        # Start with all exercises
        candidates = self.exercises.copy()
        
        # Filter by equipment
        candidates = [ex for ex in candidates if ex.matches_equipment(available_equipment)]
        
        # Filter by injuries
        if injuries:
            candidates = [ex for ex in candidates if all(ex.is_suitable_for_injury(injury) for injury in injuries)]
        
        # Filter by goals
        goal_exercises = []
        for goal in user_goals:
            goal_exercises.extend(self.get_exercises_by_tags([goal]))
        
        # Combine and remove duplicates
        seen_ids = set()
        recommended = []
        for exercise in goal_exercises + candidates:
            if exercise.exercise_id not in seen_ids:
                recommended.append(exercise)
                seen_ids.add(exercise.exercise_id)
        
        # Sort by relevance (goal matches first)
        recommended.sort(key=lambda x: x in goal_exercises, reverse=True)
        
        return recommended[:10]  # Return top 10
    
    def add_exercise(self, exercise: Exercise) -> bool:
        """Add new exercise to the knowledge base"""
        try:
            # For now, just add to memory (would need to persist to file)
            self.exercises.append(exercise)
            logger.info(f"Added exercise: {exercise.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding exercise: {e}")
            return False
    
    def update_exercise(self, exercise: Exercise) -> bool:
        """Update existing exercise"""
        try:
            for i, existing_exercise in enumerate(self.exercises):
                if existing_exercise.exercise_id == exercise.exercise_id:
                    self.exercises[i] = exercise
                    logger.info(f"Updated exercise: {exercise.name}")
                    return True
            logger.warning(f"Exercise not found for update: {exercise.name}")
            return False
        except Exception as e:
            logger.error(f"Error updating exercise: {e}")
            return False
    
    def delete_exercise(self, exercise_id: str) -> bool:
        """Delete exercise"""
        try:
            for i, exercise in enumerate(self.exercises):
                if exercise.exercise_id == exercise_id:
                    deleted_exercise = self.exercises.pop(i)
                    logger.info(f"Deleted exercise: {deleted_exercise.name}")
                    return True
            logger.warning(f"Exercise not found for deletion: {exercise_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting exercise: {e}")
            return False
    
    def get_exercise_statistics(self) -> Dict[str, Any]:
        """Get exercise library statistics"""
        try:
            total_exercises = len(self.exercises)
            
            # Count by category
            category_counts = {}
            for exercise in self.exercises:
                category = exercise.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by difficulty
            difficulty_counts = {}
            for exercise in self.exercises:
                difficulty = exercise.difficulty.value
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            
            # Count by equipment
            equipment_counts = {}
            for exercise in self.exercises:
                for equipment in exercise.equipment:
                    equipment_counts[equipment] = equipment_counts.get(equipment, 0) + 1
            
            return {
                "total_exercises": total_exercises,
                "by_category": category_counts,
                "by_difficulty": difficulty_counts,
                "by_equipment": equipment_counts,
                "sources": list(set(ex.source for ex in self.exercises if ex.source))
            }
        except Exception as e:
            logger.error(f"Error getting exercise statistics: {e}")
            return {} 