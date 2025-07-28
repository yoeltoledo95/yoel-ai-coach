"""
Mentor domain entity - represents fitness mentors in the coaching system
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class MentorSpecialization(Enum):
    STRENGTH_TRAINING = "strength_training"
    MOVEMENT_PATTERNS = "movement_patterns"
    RECOVERY = "recovery"
    MOBILITY = "mobility"
    ENDURANCE = "endurance"
    SPORTS_PERFORMANCE = "sports_performance"
    REHABILITATION = "rehabilitation"


@dataclass
class MentorPrinciple:
    """A key principle from a mentor"""
    principle_id: str
    title: str
    description: str
    context: Optional[str] = None


@dataclass
class MentorMethod:
    """A training method from a mentor"""
    method_id: str
    name: str
    description: str
    application: str
    key_points: List[str] = field(default_factory=list)


@dataclass
class Mentor:
    """Mentor entity representing fitness experts"""
    mentor_id: str
    name: str
    specialization: MentorSpecialization
    focus: str
    core_philosophy: str
    key_principles: List[MentorPrinciple] = field(default_factory=list)
    training_methods: List[MentorMethod] = field(default_factory=list)
    exercise_library: List[Dict[str, Any]] = field(default_factory=list)
    typical_session_flow: List[str] = field(default_factory=list)
    bio: Optional[str] = None
    credentials: List[str] = field(default_factory=list)
    
    def get_principles_summary(self) -> str:
        """Get a summary of key principles"""
        return "; ".join([p.title for p in self.key_principles[:3]])
    
    def get_methods_summary(self) -> str:
        """Get a summary of training methods"""
        return "; ".join([m.name for m in self.training_methods[:3]])
    
    def get_exercise_count(self) -> int:
        """Get number of exercises in mentor's library"""
        return len(self.exercise_library)
    
    def matches_user_goals(self, user_goals: List[str]) -> bool:
        """Check if mentor's specialization matches user goals"""
        goal_keywords = {
            "strength": ["strength", "power", "muscle"],
            "endurance": ["endurance", "cardio", "stamina"],
            "flexibility": ["flexibility", "mobility", "range"],
            "movement": ["movement", "patterns", "fundamentals"]
        }
        
        for goal in user_goals:
            for keyword_list in goal_keywords.values():
                if any(keyword in goal.lower() for keyword in keyword_list):
                    return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "mentor_id": self.mentor_id,
            "name": self.name,
            "specialization": self.specialization.value,
            "focus": self.focus,
            "core_philosophy": self.core_philosophy,
            "bio": self.bio,
            "credentials": self.credentials
        } 