"""
User domain entity - represents a user in the coaching system
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class UserLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserGoal(Enum):
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    GENERAL_FITNESS = "general_fitness"
    MOBILITY = "mobility"
    MOVEMENT_QUALITY = "movement_quality"
    JOINT_HEALTH = "joint_health"
    LONGEVITY = "longevity"
    SKILL = "skill"  # Generic skill development goal
    # New goal types
    BALANCE = "balance"
    RECOVERY = "recovery"
    SPORT_SPECIFIC = "sport_specific"
    PANCAKE_STRETCH = "pancake_stretch"
    HANDSTAND = "handstand"
    PULL_UPS = "pull_ups"
    PUSH_UPS = "push_ups"
    MUSCLE_UPS = "muscle_ups"
    PLANCHE = "planche"
    FRONT_LEVER = "front_lever"
    BACK_LEVER = "back_lever"
    HIGH_FREQUENCY_TRAINING = "high_frequency_training"
    MODERATE_FREQUENCY_TRAINING = "moderate_frequency_training"
    SHOULDER_HEALTH = "shoulder_health"
    KNEE_HEALTH = "knee_health"
    CORE_STRENGTH = "core_strength"
    BACK_STRENGTH = "back_strength"


@dataclass
class UserProfile:
    """User profile information"""
    name: str
    age: Optional[int] = None
    level: UserLevel = UserLevel.BEGINNER
    goals: List[UserGoal] = field(default_factory=list)
    training_preferences: Dict[str, Any] = field(default_factory=dict)
    injury_history: Dict[str, Any] = field(default_factory=dict)
    nutrition_preferences: Dict[str, Any] = field(default_factory=dict)
    recovery_needs: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserSession:
    """A single training session"""
    session_id: str
    user_id: str
    date: datetime
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    duration: Optional[int] = None  # minutes
    intensity: Optional[str] = None  # low, medium, high
    notes: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[int] = None  # 1-10
    soreness: Optional[int] = None  # 1-10


@dataclass
class User:
    """Main user entity"""
    profile: UserProfile
    sessions: List[UserSession] = field(default_factory=list)
    weekly_plans: List[Dict[str, Any]] = field(default_factory=list)
    feedback_history: List[str] = field(default_factory=list)
    
    def add_session(self, session: UserSession) -> None:
        """Add a new training session"""
        self.sessions.append(session)
        self.profile.updated_at = datetime.now()
    
    def get_recent_sessions(self, days: int = 7) -> List[UserSession]:
        """Get sessions from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.sessions if s.date >= cutoff_date]
    
    def get_goals_summary(self) -> str:
        """Get a summary of user goals"""
        return ", ".join([goal.value for goal in self.profile.goals])
    
    def has_injury(self, injury: str) -> bool:
        """Check if user has a specific injury"""
        return injury.lower() in [i.lower() for i in self.profile.injury_history.keys()] 