"""
Exercise domain entity - represents exercises in the coaching system
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ExerciseCategory(Enum):
    FOUNDATIONAL_MOVEMENT = "foundational_movement"
    STRENGTH_TRAINING = "strength_training"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    YOGA = "yoga"
    WEIGHTLIFTING = "weightlifting"
    BODYWEIGHT = "bodyweight"


class ExerciseDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class ExerciseVariation:
    """Exercise progression or regression"""
    name: str
    description: str
    difficulty: ExerciseDifficulty
    equipment: List[str] = field(default_factory=list)
    cues: List[str] = field(default_factory=list)


@dataclass
class Exercise:
    """Exercise entity with comprehensive information"""
    exercise_id: str
    name: str
    description: str
    category: ExerciseCategory
    difficulty: ExerciseDifficulty
    tags: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    muscle_groups: List[str] = field(default_factory=list)
    cues: List[str] = field(default_factory=list)
    progressions: List[ExerciseVariation] = field(default_factory=list)
    regressions: List[ExerciseVariation] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    source: Optional[str] = None  # Where this exercise came from
    created_at: Optional[str] = None
    
    def get_appropriate_variation(self, user_level: str) -> Optional[ExerciseVariation]:
        """Get appropriate variation based on user level"""
        if user_level == "beginner":
            return self.regressions[0] if self.regressions else None
        elif user_level == "advanced":
            return self.progressions[0] if self.progressions else None
        return None
    
    def is_suitable_for_injury(self, injury: str) -> bool:
        """Check if exercise is suitable for someone with a specific injury"""
        return injury.lower() not in [c.lower() for c in self.contraindications]
    
    def matches_equipment(self, available_equipment: List[str]) -> bool:
        """Check if exercise can be done with available equipment"""
        if not self.equipment:  # No equipment required
            return True
        return any(eq.lower() in [ae.lower() for ae in available_equipment] 
                  for eq in self.equipment)
    
    def get_cues_summary(self) -> str:
        """Get a summary of key cues"""
        return "; ".join(self.cues[:3])  # Top 3 cues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "exercise_id": self.exercise_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "tags": self.tags,
            "equipment": self.equipment,
            "muscle_groups": self.muscle_groups,
            "cues": self.cues,
            "contraindications": self.contraindications,
            "source": self.source
        } 