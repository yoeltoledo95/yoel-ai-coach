"""
Exercise repository interface - defines data access contract for exercises
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.exercise import Exercise, ExerciseCategory, ExerciseDifficulty


class ExerciseRepository(ABC):
    """Abstract interface for exercise data access"""
    
    @abstractmethod
    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get exercise by ID"""
        pass
    
    @abstractmethod
    def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """Get exercise by name"""
        pass
    
    @abstractmethod
    def get_all_exercises(self) -> List[Exercise]:
        """Get all exercises"""
        pass
    
    @abstractmethod
    def search_exercises(self, query: str) -> List[Exercise]:
        """Search exercises by query"""
        pass
    
    @abstractmethod
    def get_exercises_by_category(self, category: ExerciseCategory) -> List[Exercise]:
        """Get exercises by category"""
        pass
    
    @abstractmethod
    def get_exercises_by_difficulty(self, difficulty: ExerciseDifficulty) -> List[Exercise]:
        """Get exercises by difficulty level"""
        pass
    
    @abstractmethod
    def get_exercises_by_tags(self, tags: List[str]) -> List[Exercise]:
        """Get exercises by tags"""
        pass
    
    @abstractmethod
    def get_exercises_for_equipment(self, equipment: List[str]) -> List[Exercise]:
        """Get exercises that can be done with available equipment"""
        pass
    
    @abstractmethod
    def get_exercises_for_injuries(self, injuries: List[str]) -> List[Exercise]:
        """Get exercises suitable for users with specific injuries"""
        pass
    
    @abstractmethod
    def get_exercises_by_muscle_groups(self, muscle_groups: List[str]) -> List[Exercise]:
        """Get exercises targeting specific muscle groups"""
        pass
    
    @abstractmethod
    def add_exercise(self, exercise: Exercise) -> bool:
        """Add new exercise"""
        pass
    
    @abstractmethod
    def update_exercise(self, exercise: Exercise) -> bool:
        """Update existing exercise"""
        pass
    
    @abstractmethod
    def delete_exercise(self, exercise_id: str) -> bool:
        """Delete exercise"""
        pass
    
    @abstractmethod
    def get_exercise_statistics(self) -> Dict[str, Any]:
        """Get exercise library statistics"""
        pass 