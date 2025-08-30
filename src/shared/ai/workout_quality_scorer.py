"""
Workout Quality Scoring System for AI Coach
Mentor-based validation with conversation-friendly metrics.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Core quality dimensions for workout assessment"""
    SAFETY = "safety"
    MENTOR_ALIGNMENT = "mentor_alignment"
    PERSONALIZATION = "personalization"
    STRUCTURE = "structure"
    COMMUNICATION = "communication"


@dataclass
class ExerciseQualityMetrics:
    """Quality metrics for individual exercises"""
    name: str
    joint_load: int  # 1-5 (1=very safe, 5=high load)
    complexity: int  # 1-5 (1=basic, 5=advanced)
    mentor_relevance: float  # 0-1 (how well it matches mentor principles)
    injury_safe: bool  # Safe for known injuries
    progression_appropriate: bool  # Matches user level


@dataclass
class WorkoutQualityScore:
    """Complete workout quality assessment"""
    overall_score: float  # 0-100
    dimension_scores: Dict[QualityDimension, float]
    recommendations: List[str]
    safety_flags: List[str]
    mentor_coverage: Dict[str, float]
    grade: str  # A+, A, B+, B, C+, C


class WorkoutQualityScorer:
    """Mentor-based workout quality scoring system"""
    
    def __init__(self):
        self.exercise_db = self._initialize_exercise_database()
        self.mentor_principles = self._initialize_mentor_principles()
        self.safety_rules = self._initialize_safety_rules()
        logger.info("🏋️ Workout quality scorer initialized")
    
    def _initialize_exercise_database(self) -> Dict[str, ExerciseQualityMetrics]:
        """Initialize exercise quality database"""
        
        # Sample exercise database - would be expanded with full exercise library
        exercises = {
            # Ben Patrick (Knees Over Toes) - Joint Health
            "tibialis_raise": ExerciseQualityMetrics(
                name="Tibialis Raise",
                joint_load=1,  # Very safe
                complexity=2,  # Simple movement
                mentor_relevance=1.0,  # Perfect Ben Patrick exercise
                injury_safe=True,
                progression_appropriate=True
            ),
            "reverse_nordic": ExerciseQualityMetrics(
                name="Reverse Nordic",
                joint_load=3,  # Moderate load on knees
                complexity=4,  # Advanced control required
                mentor_relevance=1.0,
                injury_safe=False,  # Not for acute knee issues
                progression_appropriate=False  # Advanced exercise
            ),
            "backward_sled_pull": ExerciseQualityMetrics(
                name="Backward Sled Pull",
                joint_load=2,  # Low impact
                complexity=2,  # Simple
                mentor_relevance=1.0,
                injury_safe=True,
                progression_appropriate=True
            ),
            
            # Tom Merrick - Flexibility/Bodyweight
            "pancake_stretch": ExerciseQualityMetrics(
                name="Pancake Stretch",
                joint_load=1,  # Very safe
                complexity=3,  # Moderate technique
                mentor_relevance=1.0,
                injury_safe=True,
                progression_appropriate=True
            ),
            "jefferson_curl": ExerciseQualityMetrics(
                name="Jefferson Curl",
                joint_load=2,  # Some spinal load
                complexity=4,  # Advanced control
                mentor_relevance=0.9,  # More Emmet Louis but Tom uses it
                injury_safe=True,  # When done properly
                progression_appropriate=False  # Advanced
            ),
            
            # Ido Portal - Movement
            "spinal_wave": ExerciseQualityMetrics(
                name="Spinal Wave",
                joint_load=1,  # Very safe
                complexity=4,  # High coordination
                mentor_relevance=1.0,
                injury_safe=True,
                progression_appropriate=True  # Scalable
            ),
            
            # Everydamnandré - Kettlebells
            "kettlebell_swing": ExerciseQualityMetrics(
                name="Kettlebell Swing",
                joint_load=3,  # Moderate load
                complexity=3,  # Technique important
                mentor_relevance=1.0,
                injury_safe=True,  # Generally safe
                progression_appropriate=True
            ),
            "turkish_getup": ExerciseQualityMetrics(
                name="Turkish Get-Up",
                joint_load=3,  # Shoulder load
                complexity=5,  # Very complex
                mentor_relevance=0.8,
                injury_safe=False,  # Not for shoulder issues
                progression_appropriate=False  # Advanced
            ),
            
            # Emmet Louis - Shoulders/Handbalancing
            "shoulder_shrugs": ExerciseQualityMetrics(
                name="Shoulder Shrugs",
                joint_load=2,  # Moderate
                complexity=2,  # Simple
                mentor_relevance=1.0,
                injury_safe=True,
                progression_appropriate=True
            ),
            "handstand_progression": ExerciseQualityMetrics(
                name="Handstand Progression",
                joint_load=4,  # High wrist/shoulder load
                complexity=5,  # Very advanced
                mentor_relevance=1.0,
                injury_safe=False,  # Not for wrist/shoulder issues
                progression_appropriate=False  # Advanced
            ),
            
            # Dylan Werner - Breathing/Recovery
            "4_7_8_breathing": ExerciseQualityMetrics(
                name="4-7-8 Breathing",
                joint_load=1,  # No physical load
                complexity=2,  # Simple technique
                mentor_relevance=1.0,
                injury_safe=True,
                progression_appropriate=True
            ),
            
            # General exercises
            "bodyweight_squat": ExerciseQualityMetrics(
                name="Bodyweight Squat",
                joint_load=2,  # Moderate knee load
                complexity=2,  # Basic movement
                mentor_relevance=0.6,  # General exercise
                injury_safe=False,  # Not for knee issues
                progression_appropriate=True
            ),
            "push_up": ExerciseQualityMetrics(
                name="Push-Up",
                joint_load=2,  # Moderate
                complexity=2,  # Basic
                mentor_relevance=0.5,  # General
                injury_safe=True,  # Generally safe
                progression_appropriate=True
            )
        }
        
        return exercises
    
    def _initialize_mentor_principles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mentor-specific principles for validation"""
        
        return {
            "ben_patrick": {
                "focus_areas": ["knee_health", "joint_longevity", "backward_movement"],
                "key_exercises": ["tibialis_raise", "reverse_nordic", "backward_sled_pull"],
                "principles": [
                    "Knees over toes movement is beneficial",
                    "Backward movement builds resilience", 
                    "Control eccentric movements",
                    "Full range of motion"
                ],
                "safety_priority": 0.9  # Very high safety focus
            },
            "tom_merrick": {
                "focus_areas": ["flexibility", "bodyweight_strength", "mobility"],
                "key_exercises": ["pancake_stretch", "jefferson_curl", "pike_progression"],
                "principles": [
                    "Active flexibility over passive",
                    "PNF stretching techniques",
                    "Progressive overload in flexibility",
                    "Strength through range of motion"
                ],
                "safety_priority": 0.8
            },
            "ido_portal": {
                "focus_areas": ["movement_quality", "exploration", "flow"],
                "key_exercises": ["spinal_wave", "locomotion", "hanging"],
                "principles": [
                    "Movement quality over quantity",
                    "Explore movement patterns",
                    "Listen to your body",
                    "Smooth transitions"
                ],
                "safety_priority": 0.85
            },
            "everydamnandre": {
                "focus_areas": ["strength", "power", "kettlebell_mastery"],
                "key_exercises": ["kettlebell_swing", "clean_press", "turkish_getup"],
                "principles": [
                    "Master basic patterns first",
                    "Power through hip drive",
                    "Mental toughness",
                    "Structured progression"
                ],
                "safety_priority": 0.7
            },
            "emmet_louis": {
                "focus_areas": ["shoulder_health", "handbalancing", "pressing_strength"],
                "key_exercises": ["shoulder_shrugs", "handstand_progression", "ring_work"],
                "principles": [
                    "Shoulder health is paramount",
                    "Progressive loading",
                    "Perfect form before progression",
                    "Active recovery"
                ],
                "safety_priority": 0.85
            },
            "dylan_werner": {
                "focus_areas": ["recovery", "breathing", "mindfulness"],
                "key_exercises": ["4_7_8_breathing", "yoga_flow", "meditation"],
                "principles": [
                    "Breath awareness",
                    "Recovery is training",
                    "Mind-body connection",
                    "Sustainable practice"
                ],
                "safety_priority": 0.95  # Highest safety focus
            }
        }
    
    def _initialize_safety_rules(self) -> Dict[str, List[str]]:
        """Initialize injury-specific safety rules"""
        
        return {
            "meniscus_tear": [
                "Avoid deep knee flexion under load",
                "No pivoting movements",
                "Prefer backward movement patterns",
                "Low impact exercises only",
                "Gradual progression essential"
            ],
            "shoulder_impingement": [
                "No overhead movements initially",
                "Focus on external rotation",
                "Avoid end-range internal rotation",
                "Progressive range building",
                "Strengthen posterior chain"
            ],
            "lower_back_pain": [
                "Avoid flexion under load",
                "Focus on hip hinge patterns",
                "Core stability emphasis",
                "Gradual loading progression"
            ]
        }
    
    def score_workout(self, 
                     workout_text: str,
                     user_profile: Dict[str, Any],
                     conversation_context: Dict[str, Any]) -> WorkoutQualityScore:
        """
        Score a complete workout based on multiple quality dimensions
        
        Args:
            workout_text: AI-generated workout text
            user_profile: User's profile including injuries, goals
            conversation_context: Context from conversation
            
        Returns:
            Complete workout quality assessment
        """
        
        # Extract exercises from workout text
        exercises = self._extract_exercises_from_text(workout_text)
        
        # Score each dimension
        dimension_scores = {}
        
        dimension_scores[QualityDimension.SAFETY] = self._score_safety(
            exercises, user_profile
        )
        
        dimension_scores[QualityDimension.MENTOR_ALIGNMENT] = self._score_mentor_alignment(
            exercises, workout_text, conversation_context
        )
        
        dimension_scores[QualityDimension.PERSONALIZATION] = self._score_personalization(
            workout_text, user_profile, conversation_context
        )
        
        dimension_scores[QualityDimension.STRUCTURE] = self._score_structure(
            workout_text, exercises
        )
        
        dimension_scores[QualityDimension.COMMUNICATION] = self._score_communication(
            workout_text
        )
        
        # Calculate overall score (weighted average)
        weights = {
            QualityDimension.SAFETY: 0.30,  # Highest priority
            QualityDimension.MENTOR_ALIGNMENT: 0.25,
            QualityDimension.PERSONALIZATION: 0.25,
            QualityDimension.STRUCTURE: 0.15,
            QualityDimension.COMMUNICATION: 0.05
        }
        
        overall_score = sum(
            dimension_scores[dim] * weight 
            for dim, weight in weights.items()
        )
        
        # Generate recommendations and flags
        recommendations = self._generate_recommendations(dimension_scores, exercises, user_profile)
        safety_flags = self._generate_safety_flags(exercises, user_profile)
        mentor_coverage = self._analyze_mentor_coverage(exercises, workout_text)
        grade = self._calculate_grade(overall_score)
        
        return WorkoutQualityScore(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            recommendations=recommendations,
            safety_flags=safety_flags,
            mentor_coverage=mentor_coverage,
            grade=grade
        )
    
    def _extract_exercises_from_text(self, workout_text: str) -> List[str]:
        """Extract exercise names from workout text"""
        
        found_exercises = []
        workout_lower = workout_text.lower()
        
        # Look for exercises in our database
        for exercise_key, exercise_data in self.exercise_db.items():
            exercise_name = exercise_data.name.lower()
            
            # Check for exact name matches or variations
            if exercise_name in workout_lower or exercise_key in workout_lower:
                found_exercises.append(exercise_key)
            
            # Check for partial matches (e.g., "tibialis" for "tibialis_raise")
            if len(exercise_name.split()) > 1:
                for word in exercise_name.split():
                    if len(word) > 4 and word in workout_lower:
                        found_exercises.append(exercise_key)
                        break
        
        return list(set(found_exercises))  # Remove duplicates
    
    def _score_safety(self, exercises: List[str], user_profile: Dict[str, Any]) -> float:
        """Score workout safety based on user injuries and exercise selection"""
        
        if not exercises:
            return 50.0  # Neutral score for empty workout
        
        total_safety_score = 0
        safety_violations = 0
        
        # Get user injuries
        injuries = user_profile.get('injuries', [])
        
        for exercise_key in exercises:
            if exercise_key not in self.exercise_db:
                continue
                
            exercise = self.exercise_db[exercise_key]
            
            # Base safety score (lower joint load = higher safety)
            exercise_safety = (6 - exercise.joint_load) * 20  # Scale to 0-100
            
            # Check injury compatibility
            for injury in injuries:
                if injury in self.safety_rules:
                    if not exercise.injury_safe:
                        exercise_safety *= 0.5  # Significant penalty
                        safety_violations += 1
                    
                    # Specific injury checks
                    if injury == "meniscus_tear" and exercise.joint_load > 3:
                        exercise_safety *= 0.3
                        safety_violations += 1
                    
                    if injury == "shoulder_impingement" and "handstand" in exercise.name.lower():
                        exercise_safety *= 0.2
                        safety_violations += 1
            
            total_safety_score += exercise_safety
        
        avg_safety = total_safety_score / len(exercises)
        
        # Apply penalty for multiple safety violations
        if safety_violations > 2:
            avg_safety *= 0.7
        elif safety_violations > 0:
            avg_safety *= 0.85
        
        return min(100, max(0, avg_safety))
    
    def _score_mentor_alignment(self, exercises: List[str], workout_text: str, context: Dict[str, Any]) -> float:
        """Score how well workout aligns with mentor principles"""
        
        if not exercises:
            return 50.0
        
        # Detect mentioned mentors in workout text
        mentioned_mentors = []
        workout_lower = workout_text.lower()
        
        mentor_names = {
            "ben patrick": "ben_patrick",
            "knees over toes": "ben_patrick", 
            "tom merrick": "tom_merrick",
            "ido portal": "ido_portal",
            "everydamnandre": "everydamnandre",
            "emmet louis": "emmet_louis",
            "dylan werner": "dylan_werner"
        }
        
        for name, key in mentor_names.items():
            if name in workout_lower:
                mentioned_mentors.append(key)
        
        if not mentioned_mentors:
            return 60.0  # Neutral score if no mentors mentioned
        
        total_alignment = 0
        
        for mentor_key in mentioned_mentors:
            mentor = self.mentor_principles[mentor_key]
            mentor_score = 0
            
            # Check if workout includes mentor's key exercises
            key_exercises_present = sum(
                1 for ex in exercises 
                if ex in mentor["key_exercises"]
            )
            
            if key_exercises_present > 0:
                mentor_score += 50 * (key_exercises_present / len(mentor["key_exercises"]))
            
            # Check for principle mentions in text
            principle_mentions = sum(
                1 for principle in mentor["principles"]
                if any(word in workout_lower for word in principle.lower().split()[:3])
            )
            
            if principle_mentions > 0:
                mentor_score += 30 * (principle_mentions / len(mentor["principles"]))
            
            # Bonus for appropriate mentor selection
            mentor_score += 20
            
            total_alignment += mentor_score
        
        avg_alignment = total_alignment / len(mentioned_mentors)
        return min(100, max(0, avg_alignment))
    
    def _score_personalization(self, workout_text: str, user_profile: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Score how well workout is personalized to user"""
        
        personalization_score = 0
        workout_lower = workout_text.lower()
        
        # Check for user name mention
        user_name = user_profile.get('name', '').lower()
        if user_name and user_name in workout_lower:
            personalization_score += 20
        
        # Check for goal alignment
        goals = user_profile.get('goals', [])
        goal_mentions = sum(
            1 for goal in goals 
            if goal.lower() in workout_lower
        )
        if goal_mentions > 0:
            personalization_score += 30 * min(1, goal_mentions / len(goals))
        
        # Check for injury acknowledgment
        injuries = user_profile.get('injuries', [])
        injury_mentions = sum(
            1 for injury in injuries
            if injury.replace('_', ' ') in workout_lower
        )
        if injury_mentions > 0:
            personalization_score += 25
        
        # Check for equipment consideration
        equipment = context.get('equipment_available', [])
        if equipment:
            equipment_mentions = sum(
                1 for item in equipment
                if item.lower() in workout_lower
            )
            if equipment_mentions > 0:
                personalization_score += 15
        
        # Check for time consideration
        time_available = context.get('time_available')
        if time_available and str(time_available) in workout_text:
            personalization_score += 10
        
        return min(100, personalization_score)
    
    def _score_structure(self, workout_text: str, exercises: List[str]) -> float:
        """Score workout structure and flow"""
        
        structure_score = 0
        workout_lower = workout_text.lower()
        
        # Check for proper phases
        phases = ['warm', 'main', 'cool']
        phase_mentions = sum(1 for phase in phases if phase in workout_lower)
        structure_score += 30 * (phase_mentions / len(phases))
        
        # Check for sets/reps specification
        if re.search(r'\d+\s*(sets?|reps?)', workout_lower):
            structure_score += 25
        
        # Check for timing information
        if re.search(r'\d+\s*(minutes?|mins?|seconds?|secs?)', workout_lower):
            structure_score += 20
        
        # Check for progression/modification mentions
        progression_words = ['progress', 'modify', 'adjust', 'scale', 'easier', 'harder']
        if any(word in workout_lower for word in progression_words):
            structure_score += 15
        
        # Bonus for logical exercise order
        if len(exercises) >= 3:
            structure_score += 10
        
        return min(100, structure_score)
    
    def _score_communication(self, workout_text: str) -> float:
        """Score communication quality and clarity"""
        
        communication_score = 0
        
        # Check length (not too short, not too long)
        word_count = len(workout_text.split())
        if 100 <= word_count <= 500:
            communication_score += 25
        elif 50 <= word_count < 100 or 500 < word_count <= 800:
            communication_score += 15
        else:
            communication_score += 5
        
        # Check for encouraging language
        encouraging_words = ['you', 'your', 'great', 'excellent', 'progress', 'awesome']
        encouragement_count = sum(1 for word in encouraging_words if word in workout_text.lower())
        communication_score += min(25, encouragement_count * 5)
        
        # Check for questions (engagement)
        question_count = workout_text.count('?')
        communication_score += min(20, question_count * 10)
        
        # Check for clear instructions
        instruction_words = ['start', 'begin', 'hold', 'focus', 'remember']
        instruction_count = sum(1 for word in instruction_words if word in workout_text.lower())
        communication_score += min(20, instruction_count * 4)
        
        # Bonus for natural flow
        if 'however' in workout_text.lower() or 'though' in workout_text.lower():
            communication_score += 10
        
        return min(100, communication_score)
    
    def _generate_recommendations(self, scores: Dict[QualityDimension, float], exercises: List[str], user_profile: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        if scores[QualityDimension.SAFETY] < 70:
            recommendations.append("Consider safer exercise alternatives for current injury status")
        
        if scores[QualityDimension.MENTOR_ALIGNMENT] < 60:
            recommendations.append("Include more mentor-specific principles and exercises")
        
        if scores[QualityDimension.PERSONALIZATION] < 70:
            recommendations.append("Reference user's specific goals and current state more explicitly")
        
        if scores[QualityDimension.STRUCTURE] < 60:
            recommendations.append("Improve workout structure with clear phases and timing")
        
        if scores[QualityDimension.COMMUNICATION] < 70:
            recommendations.append("Make communication more engaging and encouraging")
        
        return recommendations
    
    def _generate_safety_flags(self, exercises: List[str], user_profile: Dict[str, Any]) -> List[str]:
        """Generate safety warnings"""
        
        flags = []
        injuries = user_profile.get('injuries', [])
        
        for exercise_key in exercises:
            if exercise_key not in self.exercise_db:
                continue
                
            exercise = self.exercise_db[exercise_key]
            
            if not exercise.injury_safe and injuries:
                flags.append(f"⚠️ {exercise.name} may not be suitable with current injuries")
            
            if exercise.joint_load > 3 and "meniscus_tear" in injuries:
                flags.append(f"🚨 {exercise.name} involves high knee load - use caution")
            
            if "handstand" in exercise.name.lower() and "shoulder_impingement" in injuries:
                flags.append(f"🚨 {exercise.name} involves overhead position - avoid with shoulder issues")
        
        return flags
    
    def _analyze_mentor_coverage(self, exercises: List[str], workout_text: str) -> Dict[str, float]:
        """Analyze which mentors are represented in the workout"""
        
        coverage = {}
        
        for mentor_key, mentor_data in self.mentor_principles.items():
            score = 0
            
            # Check for exercise coverage
            exercise_matches = sum(
                1 for ex in exercises 
                if ex in mentor_data["key_exercises"]
            )
            if exercise_matches > 0:
                score += 0.6 * (exercise_matches / len(mentor_data["key_exercises"]))
            
            # Check for mention in text
            mentor_name = mentor_key.replace('_', ' ')
            if mentor_name in workout_text.lower():
                score += 0.4
            
            coverage[mentor_key] = min(1.0, score)
        
        return coverage
    
    def _calculate_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        else:
            return "C"


# Global workout quality scorer instance
workout_quality_scorer = WorkoutQualityScorer()
