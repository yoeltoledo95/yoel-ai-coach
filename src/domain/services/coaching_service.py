"""
Coaching service - core business logic for AI coaching
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..entities.user import User, UserSession, UserLevel, UserGoal, UserProfile
from ..entities.exercise import Exercise
from ..entities.mentor import Mentor
from ..repositories.user_repository import UserRepository
from ..repositories.exercise_repository import ExerciseRepository
from ..repositories.mentor_repository import MentorRepository
from .configuration_service import ConfigurationService
from shared.exceptions import ConfigurationError
from shared.logging import get_logger

logger = get_logger(__name__)


class WorkoutProgrammingService:
    """Service for creating workout programs based on best practices"""
    
    def __init__(self, config_service: ConfigurationService):
        self.config_service = config_service
        self.programming_rules = self.config_service.get_workout_programming_rules()
    
    def get_programming_guidelines(self, focus_area: str) -> Dict[str, Any]:
        """Get programming guidelines for a specific focus area"""
        return self.config_service.get_programming_guidelines(focus_area)
    
    def create_weekly_template(self, user_profile: UserProfile) -> Dict[str, str]:
        """Create a weekly workout template based on user goals"""
        template = self.programming_rules.get("workout_programming_rules", {}).get("weekly_plan_template", {})
        
        # Customize based on user goals
        if UserGoal.STRENGTH in user_profile.goals:
            # Emphasize strength days
            template["monday"] = "Strength (Heavy) + Mobility"
            template["thursday"] = "Strength (Moderate) + Flexibility"
        elif UserGoal.FLEXIBILITY in user_profile.goals:
            # Add more flexibility focus
            template["wednesday"] = "Flexibility + Joint Health"
            template["saturday"] = "Full-Body Mobility + Flexibility"
        
        return template
    
    def get_exercise_recommendations(self, focus_area: str, user_level: UserLevel) -> List[str]:
        """Get exercise recommendations for a focus area and user level"""
        guidelines = self.get_programming_guidelines(focus_area)
        
        if focus_area == "muscle_hypertrophy":
            exercises = ["squat", "bench press", "deadlift", "row", "overhead press"]
            if user_level == UserLevel.ADVANCED:
                exercises.extend(["dips", "pull-ups", "lunges", "shoulder press"])
        elif focus_area == "flexibility_range_of_motion":
            exercises = ["dynamic stretching", "static stretching", "yoga", "pilates", "foam rolling"]
        elif focus_area == "movement_quality_complexity":
            exercises = ["bear crawl", "crab walk", "animal walks", "hand balancing", "hanging"]
        elif focus_area == "joint_health_prehab_rehab":
            exercises = ["step-up", "leg extension", "balance drills", "reverse sled drag", "tibialis raises"]
        else:
            exercises = []
        
        return exercises


class CoachingService:
    """Core coaching business logic"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        exercise_repository: ExerciseRepository,
        mentor_repository: MentorRepository,
        ai_client=None,
    ):
        self.user_repository = user_repository
        self.exercise_repository = exercise_repository
        self.mentor_repository = mentor_repository
# Simplified: removed unused workout programming service
        self.ai_client = ai_client
    
    def get_personalized_response(
        self, 
        user_id: str, 
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get personalized coaching response"""
        
        # Check if this is a known user (like Yoel)
        known_user = self._identify_known_user(user_id)
        
        user = self.user_repository.get_user(user_id)
        
        # Handle new user onboarding
        if not user:
            return self._handle_new_user_onboarding(user_id, user_input, known_user)
        
        # Check for profile update requests first
        profile_update_response = self.process_profile_update_request(user_id, user_input)
        if profile_update_response:
            return profile_update_response
        
        # Get relevant mentor context
        mentor_context = self.mentor_repository.get_mentor_context(user_input)
        
        # Get user patterns
        patterns = self._analyze_user_patterns(user)
        
        # Get recent feedback to inform response
        recent_feedback = self._get_recent_feedback(user_id)
        
        # Build response context
        response_context = {
            "user_profile": user.profile,
            "recent_sessions": user.get_recent_sessions(7),
            "mentor_context": mentor_context,
            "patterns": patterns,
            "user_input": user_input,
            "recent_feedback": recent_feedback,
            "additional_context": context or {},
            "known_user": known_user
        }
        
        return self._generate_response(response_context)
    
    def _identify_known_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Identify known users like Yoel based on WhatsApp ID or other identifiers"""
        
        # Known user mappings
        known_users = {
            "972527506098": {  # Yoel's WhatsApp ID from logs
                "user_id": "yoel",
                "name": "Yoel",
                "age": 30,
                "goals": ["push to handstand", "pancake flexibility", "fix muscular imbalances", "boost energy", "build muscle", "strength", "endurance", "mobility"],
                "training_preferences": {
                    "split": "4-6 days per week",
                    "training_days": 5,
                    "preferred_style": "calisthenics",
                    "secondary_activities": ["kettlebells", "yoga", "band work", "athletic movement"],
                    "no_machines": True,
                    "focus": "movement quality over quantity"
                },
                "specific_skills": {
                    "push_to_handstand": "in progress",
                    "pancake": "working on hip mobility and hamstring flexibility",
                    "muscular_imbalances": "shoulder issues, working on symmetry",
                    "athletic_movement": "focus on natural patterns"
                },
                "injury_history": {
                    "shoulder": "ongoing issues, needs careful management",
                    "knee": "recovered, can do more work now"
                },
                "mentor_influences": [
                    "Ido Portal - movement complexity and natural patterns",
                    "Emmet Louis - end-range mobility strength",
                    "Tom Merrick - clean calisthenics and flexibility",
                    "Dylan Werner - isometric strength and body control",
                    "Patrick Beach - fluid mobility and breath connection"
                ],
                "nutrition_preferences": {
                    "diet": "flexible, focuses on protein and clean carbs",
                    "favorites": ["eggs with tahini", "chicken with rice", "vegetables"]
                },
                "recovery_needs": {
                    "sleep_target": 7.5,
                    "stress_management": "important",
                    "mobility_work": "daily",
                    "active_recovery": "movement-based recovery"
                }
            },
            "yoel_user": {  # Web interface user ID for Yoel
                "user_id": "yoel",
                "name": "Yoel",
                "age": 30,
                "goals": ["push to handstand", "pancake flexibility", "fix muscular imbalances", "boost energy", "build muscle", "strength", "endurance", "mobility"],
                "training_preferences": {
                    "split": "4-6 days per week",
                    "training_days": 5,
                    "preferred_style": "calisthenics",
                    "secondary_activities": ["kettlebells", "yoga", "band work", "athletic movement"],
                    "no_machines": True,
                    "focus": "movement quality over quantity"
                },
                "specific_skills": {
                    "push_to_handstand": "in progress",
                    "pancake": "working on hip mobility and hamstring flexibility",
                    "muscular_imbalances": "shoulder issues, working on symmetry",
                    "athletic_movement": "focus on natural patterns"
                },
                "injury_history": {
                    "shoulder": "ongoing issues, needs careful management",
                    "knee": "recovered, can do more work now"
                },
                "mentor_influences": [
                    "Ido Portal - movement complexity and natural patterns",
                    "Emmet Louis - end-range mobility strength",
                    "Tom Merrick - clean calisthenics and flexibility",
                    "Dylan Werner - isometric strength and body control",
                    "Patrick Beach - fluid mobility and breath connection"
                ],
                "nutrition_preferences": {
                    "diet": "flexible, focuses on protein and clean carbs",
                    "favorites": ["eggs with tahini", "chicken with rice", "vegetables"]
                },
                "recovery_needs": {
                    "sleep_target": 7.5,
                    "stress_management": "important",
                    "mobility_work": "daily",
                    "active_recovery": "movement-based recovery"
                }
            }
        }
        
        return known_users.get(user_id)
    
    def _handle_new_user_onboarding(self, user_id: str, user_input: str, known_user: Optional[Dict[str, Any]] = None) -> str:
        """Handle onboarding for new users using AI-generated responses"""
        
        # If this is a known user, create their profile immediately
        if known_user:
            new_user = self._create_known_user_profile(user_id, known_user)
            if new_user:
                # Use AI to generate a personalized greeting
                greeting_context = {
                    "user_id": user_id,
                    "user_input": user_input,
                    "onboarding_stage": "known_user_greeting",
                    "user_profile": new_user.profile,
                    "known_user": known_user,
                    "mentor_context": self.mentor_repository.get_mentor_context("welcome back known user")
                }
                return self._generate_ai_response(greeting_context)
        
        # Create a new user profile if this is an onboarding response
        onboarding_keywords = [
            "let's go", "yes", "okay", "sure", "start", "begin", "ready", 
            "go ahead", "proceed", "continue", "next", "ok", "alright"
        ]
        
        user_input_lower = user_input.lower().strip()
        
        # If user is ready to start onboarding, create profile and begin
        if any(keyword in user_input_lower for keyword in onboarding_keywords):
            # Create a new user profile
            new_user = self._create_new_user_profile(user_id)
            
            if new_user:
                # Use AI to generate a natural onboarding response
                onboarding_context = {
                    "user_id": user_id,
                    "user_input": user_input,
                    "onboarding_stage": "profile_created",
                    "user_profile": new_user.profile,
                    "mentor_context": self.mentor_repository.get_mentor_context("onboarding introduction")
                }
                
                return self._generate_ai_response(onboarding_context)
            else:
                return "I'm having trouble setting up your profile. Please try again in a moment."
        
        # Use AI to generate a natural welcome message
        welcome_context = {
            "user_id": user_id,
            "user_input": user_input,
            "onboarding_stage": "initial_greeting",
            "mentor_context": self.mentor_repository.get_mentor_context("welcome new user")
        }
        
        return self._generate_ai_response(welcome_context)
    
    def _generate_ai_response(self, context: Dict[str, Any]) -> str:
        """Generate AI response for natural conversation"""
        try:
            # Require injected AI client (no mock/factory)
            if not self.ai_client:
                raise ConfigurationError("AI client not configured in CoachingService")

            ai_client = self.ai_client

            # Build prompt for AI
            prompt = self._build_ai_prompt(context)
            
            # Generate response using AI
            response = ai_client.generate_coaching_response(
                user_input=context.get("user_input", ""),
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Fallback to basic response
            if context.get("onboarding_stage") == "profile_created":
                return ("Great! Let's get to know you better. I'm your AI fitness coach, and I'm here to help you achieve your goals.\n\n"
                       "To create your personalized program, I need to know:\n\n"
                       "1. **Your fitness goals** (e.g., strength, flexibility, endurance, weight loss)\n"
                       "2. **Your current fitness level** (beginner, intermediate, advanced)\n"
                       "3. **Any injuries or limitations** I should know about\n"
                       "4. **Your preferred training style** (calisthenics, weights, yoga, etc.)\n\n"
                       "Just tell me about yourself and your goals!")
            else:
                return ("👋 Welcome! I'm your AI fitness coach, and I'm excited to help you on your fitness journey!\n\n"
                       "I don't have your profile yet, so let's start by getting to know you.\n\n"
                       "Are you ready to create your personalized fitness program? Just say 'Let's go' or 'Yes' to get started!")
    
    def _build_ai_prompt(self, context: Dict[str, Any]) -> str:
        """Build AI prompt for natural conversation"""
        
        onboarding_stage = context.get("onboarding_stage")
        user_input = context.get("user_input", "")
        mentor_context = context.get("mentor_context", "")
        known_user = context.get("known_user")
        
        if onboarding_stage == "known_user_greeting":
            user_name = known_user.get("name", "there")
            return f"""You are an AI fitness coach greeting a known user named {user_name}.

User message: "{user_input}"

User profile: {known_user}

Mentor context: {mentor_context}

Generate a warm, personalized response that:
1. Greets {user_name} by name
2. Shows you remember their preferences and goals
3. Asks how they're doing or what they'd like to work on today
4. Keep it conversational and natural, like talking to a friend
5. Reference their specific goals and training style

Make it feel like a natural conversation with someone you know well."""
        
        elif onboarding_stage == "initial_greeting":
            return f"""You are a friendly, enthusiastic AI fitness coach welcoming a new user. 

User message: "{user_input}"

Mentor context: {mentor_context}

Generate a warm, welcoming response that:
1. Introduces yourself as their AI fitness coach
2. Explains you're here to help them achieve their fitness goals
3. Mentions you need to get to know them first
4. Asks if they're ready to start (but don't be pushy)
5. Keep it conversational and natural, like talking to a friend

Make it feel like a natural conversation, not a script."""
        
        elif onboarding_stage == "profile_created":
            return f"""You are an AI fitness coach who just created a new user profile. 

User message: "{user_input}"

Mentor context: {mentor_context}

Generate a response that:
1. Acknowledges their readiness to start
2. Explains you're excited to help them
3. Ask them to tell you about their fitness goals and preferences
4. Keep it conversational and encouraging
5. Don't list specific questions - just ask them to share about themselves

Make it feel like a natural conversation with a knowledgeable fitness coach."""
        
        else:
            return f"""You are an AI fitness coach responding to a user message.

User message: "{user_input}"

Mentor context: {mentor_context}

Generate a natural, helpful response that addresses their message appropriately."""
    
    def _create_new_user_profile(self, user_id: str, user_name: str = "User") -> Optional[User]:
        """Create a new user profile with minimal defaults - let AI gather real info"""
        try:
            from ..entities.user import UserProfile, UserLevel, UserGoal
            
            # Create minimal profile - AI will gather real information
            default_profile = UserProfile(
                name=user_name,
                age=None,  # Let AI ask for real age
                goals=[],  # Let AI ask for real goals
                level=UserLevel.BEGINNER,  # Will be updated based on conversation
                training_preferences={
                    "split": "Not specified",
                    "training_days": 0,
                    "preferred_style": "Not specified",
                    "secondary_activities": []
                },
                injury_history={},
                nutrition_preferences={
                    "diet": "Not specified",
                    "favorites": []
                },
                recovery_needs={
                    "sleep_target": None,
                    "stress_management": "Not specified",
                    "mobility_work": "Not specified"
                }
            )
            
            # Create user entity
            user = User(
                profile=default_profile,
                sessions=[],
                weekly_plans=[],
                feedback_history=[]
            )
            
            # Save user to repository
            success = self.user_repository.add_user(user, user_id)
            
            if success:
                logger.info(f"Created new user profile for {user_id}")
                return user
            else:
                logger.error(f"Failed to create user profile for {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating new user profile: {e}")
            return None
    
    def _create_known_user_profile(self, user_id: str, known_user: Dict[str, Any]) -> Optional[User]:
        """Create a profile for a known user like Yoel"""
        try:
            logger.info(f"Creating known user profile for {user_id}")
            from ..entities.user import UserProfile, UserLevel, UserGoal
            
            # Create profile from known user data
            logger.info(f"Creating UserProfile with goals: {known_user['goals']}")
            profile = UserProfile(
                name=known_user["name"],
                age=known_user["age"],
                goals=[UserGoal(goal) for goal in known_user["goals"]],
                level=UserLevel.INTERMEDIATE,  # Yoel is intermediate
                training_preferences=known_user["training_preferences"],
                injury_history=known_user["injury_history"],
                nutrition_preferences=known_user["nutrition_preferences"],
                recovery_needs=known_user["recovery_needs"]
            )
            
            logger.info(f"Created UserProfile: {profile}")
            
            # Create user entity (without user_id parameter)
            user = User(
                profile=profile,
                sessions=[],
                weekly_plans=[],
                feedback_history=[]
            )
            
            logger.info(f"Created User entity: {user}")
            
            # Save user to repository with WhatsApp ID
            success = self.user_repository.add_user(user, user_id)
            
            logger.info(f"User saved to repository: {success}")
            
            if success:
                logger.info(f"Created known user profile for {known_user['name']} ({user_id})")
                return user
            else:
                logger.error(f"Failed to create known user profile for {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating known user profile: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def create_weekly_plan(self, user_id: str) -> Dict[str, Any]:
        """Create personalized weekly training plan using workout programming best practices"""
        user = self.user_repository.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get planning context from mentors
        planning_context = self.mentor_repository.get_weekly_planning_context()
        
        # Analyze user patterns
        patterns = self._analyze_user_patterns(user)
        
        # Create weekly template based on user goals
        weekly_template = self.workout_programming.create_weekly_template(user.profile)
        
        # Get programming guidelines for user's primary goals
        primary_goal = user.profile.goals[0] if user.profile.goals else UserGoal.STRENGTH
        guidelines = self.workout_programming.get_programming_guidelines(
            self._map_goal_to_focus_area(primary_goal)
        )
        
        # Get suitable exercises with programming recommendations
        exercises = self._get_suitable_exercises_with_programming(user, guidelines)
        
        # Create comprehensive plan
        plan = {
            "week_start": datetime.now().strftime("%Y-%m-%d"),
            "user_id": user_id,
            "goals": [goal.value for goal in user.profile.goals],
            "weekly_template": weekly_template,
            "programming_guidelines": guidelines,
            "exercises": exercises,
            "planning_context": planning_context,
            "patterns": patterns,
            "key_principles": self.workout_programming.programming_rules.get("workout_programming_rules", {}).get("key_principles", []),
            "created_at": datetime.now().isoformat()
        }
        
        # Save plan
        self.user_repository.save_weekly_plan(user_id, plan)
        
        return plan
    
    def log_training_session(
        self, 
        user_id: str, 
        session_data: Dict[str, Any]
    ) -> bool:
        """Log a training session"""
        user = self.user_repository.get_user(user_id)
        if not user:
            return False
        
        session = UserSession(
            session_id=f"session_{datetime.now().timestamp()}",
            user_id=user_id,
            date=datetime.now(),
            exercises=session_data.get("exercises", []),
            duration=session_data.get("duration"),
            intensity=session_data.get("intensity"),
            notes=session_data.get("notes"),
            mood=session_data.get("mood"),
            energy_level=session_data.get("energy_level"),
            soreness=session_data.get("soreness")
        )
        
        return self.user_repository.add_user_session(user_id, session)
    
    def analyze_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Analyze user training progress"""
        user = self.user_repository.get_user(user_id)
        if not user:
            return {}
        
        recent_sessions = user.get_recent_sessions(30)
        
        analysis = {
            "total_sessions": len(recent_sessions),
            "avg_duration": self._calculate_avg_duration(recent_sessions),
            "frequency": self._calculate_training_frequency(recent_sessions),
            "intensity_trend": self._analyze_intensity_trend(recent_sessions),
            "mood_trend": self._analyze_mood_trend(recent_sessions),
            "energy_trend": self._analyze_energy_trend(recent_sessions),
            "recommendations": self._generate_recommendations(user, recent_sessions)
        }
        
        return analysis
    
    def _analyze_user_patterns(self, user: User) -> Dict[str, Any]:
        """Analyze user training patterns"""
        recent_sessions = user.get_recent_sessions(14)
        
        return {
            "training_frequency": len(recent_sessions) / 2,  # sessions per week
            "preferred_intensity": self._get_most_common_intensity(recent_sessions),
            "common_mood": self._get_most_common_mood(recent_sessions),
            "avg_energy": self._calculate_avg_energy(recent_sessions),
            "avg_soreness": self._calculate_avg_soreness(recent_sessions)
        }
    
    def _get_suitable_exercises(self, user: User) -> List[Exercise]:
        """Get exercises suitable for user"""
        # Get exercises matching user level and goals
        suitable_exercises = []
        
        for goal in user.profile.goals:
            exercises = self.exercise_repository.get_exercises_by_tags([goal.value])
            suitable_exercises.extend(exercises)
        
        # Filter by injuries
        if user.profile.injury_history:
            safe_exercises = []
            for exercise in suitable_exercises:
                if all(exercise.is_suitable_for_injury(injury) for injury in user.profile.injury_history.keys()):
                    safe_exercises.append(exercise)
            suitable_exercises = safe_exercises
        
        return suitable_exercises[:10]  # Limit to 10 exercises
    
    def _generate_response(self, context: Dict[str, Any]) -> str:
        """Generate coaching response based on context"""
        # This would integrate with AI service
        # For now, return a basic response
        return f"Based on your profile and recent activity, here's my advice: {context['user_input']}"
    
    def _calculate_avg_duration(self, sessions: List[UserSession]) -> float:
        """Calculate average session duration"""
        durations = [s.duration for s in sessions if s.duration]
        return sum(durations) / len(durations) if durations else 0
    
    def _calculate_training_frequency(self, sessions: List[UserSession]) -> float:
        """Calculate training frequency (sessions per week)"""
        if not sessions:
            return 0
        days_span = (sessions[-1].date - sessions[0].date).days + 1
        return len(sessions) / (days_span / 7)
    
    def _get_most_common_intensity(self, sessions: List[UserSession]) -> Optional[str]:
        """Get most common training intensity"""
        intensities = [s.intensity for s in sessions if s.intensity]
        if not intensities:
            return None
        return max(set(intensities), key=intensities.count)
    
    def _get_most_common_mood(self, sessions: List[UserSession]) -> Optional[str]:
        """Get most common mood"""
        moods = [s.mood for s in sessions if s.mood]
        if not moods:
            return None
        return max(set(moods), key=moods.count)
    
    def _calculate_avg_energy(self, sessions: List[UserSession]) -> float:
        """Calculate average energy level"""
        energies = [s.energy_level for s in sessions if s.energy_level]
        return sum(energies) / len(energies) if energies else 0
    
    def _calculate_avg_soreness(self, sessions: List[UserSession]) -> float:
        """Calculate average soreness level"""
        soreness_levels = [s.soreness for s in sessions if s.soreness]
        return sum(soreness_levels) / len(soreness_levels) if soreness_levels else 0
    
    def _analyze_intensity_trend(self, sessions: List[UserSession]) -> str:
        """Analyze intensity trend"""
        if len(sessions) < 2:
            return "insufficient_data"
        
        recent_intensities = [s.intensity for s in sessions[-5:] if s.intensity]
        if len(recent_intensities) < 2:
            return "insufficient_data"
        
        # Simple trend analysis
        return "increasing" if len(set(recent_intensities)) > 1 else "stable"
    
    def _analyze_mood_trend(self, sessions: List[UserSession]) -> str:
        """Analyze mood trend"""
        if len(sessions) < 2:
            return "insufficient_data"
        
        recent_moods = [s.mood for s in sessions[-5:] if s.mood]
        if len(recent_moods) < 2:
            return "insufficient_data"
        
        return "improving" if len(set(recent_moods)) > 1 else "stable"
    
    def _analyze_energy_trend(self, sessions: List[UserSession]) -> str:
        """Analyze energy trend"""
        if len(sessions) < 2:
            return "insufficient_data"
        
        recent_energies = [s.energy_level for s in sessions[-5:] if s.energy_level]
        if len(recent_energies) < 2:
            return "insufficient_data"
        
        avg_energy = sum(recent_energies) / len(recent_energies)
        return "high" if avg_energy > 7 else "moderate" if avg_energy > 4 else "low"
    
    def _generate_recommendations(self, user: User, sessions: List[UserSession]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if len(sessions) < 3:
            recommendations.append("Start with 2-3 sessions per week to build consistency")
        
        if user.profile.injury_history:
            recommendations.append("Focus on exercises that don't aggravate your injuries")
        
        avg_energy = self._calculate_avg_energy(sessions)
        if avg_energy < 5:
            recommendations.append("Consider reducing intensity to improve energy levels")
        
        return recommendations
    
    def _map_goal_to_focus_area(self, goal: UserGoal) -> str:
        """Map user goal to workout programming focus area"""
        mapping = {
            UserGoal.STRENGTH: "muscle_hypertrophy",
            UserGoal.ENDURANCE: "vitality_longevity_balance",
            UserGoal.FLEXIBILITY: "flexibility_range_of_motion",
            UserGoal.MOBILITY: "mobility_recovery_practices",
            UserGoal.JOINT_HEALTH: "joint_health_prehab_rehab",
            UserGoal.MOVEMENT_QUALITY: "movement_quality_complexity"
        }
        return mapping.get(goal, "muscle_hypertrophy")
    
    def _get_suitable_exercises_with_programming(self, user: User, guidelines: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get exercises with programming recommendations based on guidelines"""
        exercises = self._get_suitable_exercises(user)
        
        # Enhance exercises with programming info
        enhanced_exercises = []
        for exercise in exercises:
            enhanced_exercise = {
                "exercise": exercise,
                "programming": {
                    "sets": guidelines.get("programming", {}).get("sets", "3-5"),
                    "reps": guidelines.get("programming", {}).get("reps", "6-12"),
                    "frequency": guidelines.get("frequency", "2-3x/week"),
                    "intensity": guidelines.get("intensity", "Moderate"),
                    "notes": guidelines.get("techniques", "")
                }
            }
            enhanced_exercises.append(enhanced_exercise)
        
        return enhanced_exercises 

    def _get_recent_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent workout feedback for user"""
        try:
            # This would integrate with the database feedback methods
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting recent feedback: {e}")
            return []
    
    def save_workout_feedback(
        self, 
        user_id: str, 
        workout_date: str, 
        feedback_type: str, 
        feedback_text: str = None,
        workout_summary: str = None,
        exercises_completed: List[str] = None,
        exercises_skipped: List[str] = None,
        difficulty_rating: int = None,
        enjoyment_rating: int = None
    ) -> bool:
        """Save workout feedback from user"""
        try:
            # This would integrate with the database
            # For now, just log the feedback
            logger.info(f"Workout feedback saved: {feedback_type} - {feedback_text}")
            return True
        except Exception as e:
            logger.error(f"Error saving workout feedback: {e}")
            return False
    
    def update_exercise_progression(
        self, 
        user_id: str, 
        exercise_name: str, 
        current_variation: str, 
        progression_level: int = 1,
        notes: str = None
    ) -> bool:
        """Update exercise progression for user"""
        try:
            # This would integrate with the database
            logger.info(f"Exercise progression updated: {exercise_name} -> {current_variation}")
            return True
        except Exception as e:
            logger.error(f"Error updating exercise progression: {e}")
            return False
    
    def get_exercise_progression(self, user_id: str, exercise_name: str) -> Optional[Dict[str, Any]]:
        """Get current exercise progression for user"""
        try:
            # This would integrate with the database
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"Error getting exercise progression: {e}")
            return None 

    def update_user_goals(self, user_id: str, new_goals: List[str]) -> bool:
        """Update user goals"""
        try:
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found for goal update")
                return False
            
            # Convert string goals to UserGoal enums
            from ..entities.user import UserGoal
            goal_enums = []
            for goal_str in new_goals:
                try:
                    goal_enums.append(UserGoal(goal_str.lower()))
                except ValueError:
                    logger.warning(f"Invalid goal: {goal_str}")
            
            # Update user profile
            user.profile.goals = goal_enums
            user.profile.updated_at = datetime.now()
            
            # Save updated user
            success = self.user_repository.save_user(user)
            
            if success:
                logger.info(f"Updated goals for user {user_id}: {new_goals}")
                return True
            else:
                logger.error(f"Failed to save updated goals for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user goals: {e}")
            return False
    
    def update_user_preferences(self, user_id: str, preference_type: str, new_preferences: Dict[str, Any]) -> bool:
        """Update user preferences (training, nutrition, recovery, etc.)"""
        try:
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found for preference update")
                return False
            
            # Update the appropriate preference section
            if preference_type == "training":
                user.profile.training_preferences = new_preferences
            elif preference_type == "nutrition":
                user.profile.nutrition_preferences = new_preferences
            elif preference_type == "recovery":
                user.profile.recovery_needs = new_preferences
            elif preference_type == "injuries":
                user.profile.injury_history = new_preferences
            else:
                logger.error(f"Invalid preference type: {preference_type}")
                return False
            
            user.profile.updated_at = datetime.now()
            
            # Save updated user
            success = self.user_repository.save_user(user)
            
            if success:
                logger.info(f"Updated {preference_type} preferences for user {user_id}")
                return True
            else:
                logger.error(f"Failed to save updated preferences for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def update_user_level(self, user_id: str, new_level: str) -> bool:
        """Update user fitness level"""
        try:
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found for level update")
                return False
            
            from ..entities.user import UserLevel
            try:
                user.profile.level = UserLevel(new_level.lower())
            except ValueError:
                logger.error(f"Invalid user level: {new_level}")
                return False
            
            user.profile.updated_at = datetime.now()
            
            # Save updated user
            success = self.user_repository.save_user(user)
            
            if success:
                logger.info(f"Updated level for user {user_id} to {new_level}")
                return True
            else:
                logger.error(f"Failed to save updated level for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user level: {e}")
            return False
    
    def get_user_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of user profile for display"""
        try:
            user = self.user_repository.get_user(user_id)
            if not user:
                return {"error": "User not found"}
            
            return {
                "name": user.profile.name,
                "age": user.profile.age,
                "level": user.profile.level.value,
                "goals": [goal.value for goal in user.profile.goals],
                "training_preferences": user.profile.training_preferences,
                "injury_history": user.profile.injury_history,
                "nutrition_preferences": user.profile.nutrition_preferences,
                "recovery_needs": user.profile.recovery_needs,
                "last_updated": user.profile.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile summary: {e}")
            return {"error": str(e)}
    
    def process_profile_update_request(self, user_id: str, user_input: str) -> str:
        """Process user requests to update their profile"""
        user_input_lower = user_input.lower()
        
        # Check for goal update requests - improved detection
        if any(keyword in user_input_lower for keyword in [
            "change goal", "update goal", "new goal", "different goal", 
            "set new goals", "want to set", "update my goals", "change my goals",
            "new goals", "different goals", "modify goals", "write new goals",
            "set goals", "update goals", "change goals"
        ]):
            # Extract goals from user input using more sophisticated parsing
            goals = self._extract_goals_from_input(user_input)
            
            if goals:
                success = self.update_user_goals(user_id, goals)
                if success:
                    return f"Excellent! I've updated your goals to: {', '.join(goals)}. Your training program will now focus on these areas."
                else:
                    return "I'm having trouble updating your goals. Please try again."
            else:
                return "I didn't catch what goals you'd like to change. Could you specify which goals you want to focus on?"
        
        # Check for level update requests
        elif any(keyword in user_input_lower for keyword in ["change level", "update level", "beginner", "intermediate", "advanced"]):
            level = None
            if "beginner" in user_input_lower:
                level = "beginner"
            elif "intermediate" in user_input_lower:
                level = "intermediate"
            elif "advanced" in user_input_lower:
                level = "advanced"
            
            if level:
                success = self.update_user_level(user_id, level)
                if success:
                    return f"Perfect! I've updated your fitness level to {level}. Your workouts will be adjusted accordingly."
                else:
                    return "I'm having trouble updating your level. Please try again."
            else:
                return "I didn't catch what level you'd like to change to. Could you specify beginner, intermediate, or advanced?"
        
        # Check for training preference updates
        elif any(keyword in user_input_lower for keyword in ["change training", "update training", "different training", "training style"]):
            # This would need more sophisticated parsing, but for now return a helpful message
            return ("I can help you update your training preferences! You can tell me about:\n"
                   "• Your preferred training split (e.g., Push/Pull/Legs, Full Body)\n"
                   "• Number of training days per week\n"
                   "• Preferred training style (calisthenics, weights, yoga, etc.)\n"
                   "Just let me know what you'd like to change!")
        
        # Check for injury updates
        elif any(keyword in user_input_lower for keyword in ["injury", "pain", "hurt", "problem"]):
            return ("I can help you update your injury information. Please tell me:\n"
                   "• What specific injuries or pain you're experiencing\n"
                   "• Which body parts are affected\n"
                   "• Any limitations this creates\n"
                   "This will help me provide safer, more appropriate exercises.")
        
        # Show current profile
        elif any(keyword in user_input_lower for keyword in ["show profile", "my profile", "current profile", "what's my profile"]):
            profile = self.get_user_profile_summary(user_id)
            if "error" not in profile:
                return (f"Here's your current profile:\n\n"
                       f"**Name:** {profile['name']}\n"
                       f"**Level:** {profile['level']}\n"
                       f"**Goals:** {', '.join(profile['goals'])}\n"
                       f"**Training:** {profile['training_preferences'].get('split', 'Not set')} split, {profile['training_preferences'].get('training_days', 'Not set')} days/week\n"
                       f"**Injuries:** {', '.join(profile['injury_history'].keys()) if profile['injury_history'] else 'None reported'}\n\n"
                       f"To update any of these, just tell me what you'd like to change!")
            else:
                return "I'm having trouble accessing your profile. Please try again."
        
        else:
            return ("I can help you update your profile! You can:\n"
                   "• Change your goals (strength, flexibility, etc.)\n"
                   "• Update your fitness level (beginner, intermediate, advanced)\n"
                   "• Modify training preferences\n"
                   "• Update injury information\n"
                   "• View your current profile\n\n"
                   "Just tell me what you'd like to change!")
    
    def _extract_goals_from_input(self, user_input: str) -> List[str]:
        """Extract goals from user input using more sophisticated parsing"""
        user_input_lower = user_input.lower()
        goals = []
        
        logger.info(f"Extracting goals from input: {user_input}")
        
        # Basic fitness goals
        goal_mappings = {
            "strength": ["strength", "strong", "muscle", "power"],
            "endurance": ["endurance", "stamina", "cardio", "cardiovascular"],
            "flexibility": ["flexibility", "flexible", "stretching", "mobility"],
            "mobility": ["mobility", "joint health", "range of motion"],
            "weight_loss": ["weight loss", "lose weight", "fat loss", "slim"],
            "muscle_gain": ["muscle gain", "build muscle", "muscle building"],
            "fitness": ["fitness", "general fitness", "overall fitness"],
            "balance": ["balance", "stability", "coordination"],
            "recovery": ["recovery", "rehabilitation", "healing"],
            "sport_specific": ["sport", "athletic", "performance"],
            "longevity": ["longevity", "health", "wellness", "lifestyle"]
        }
        
        # Check for basic goals
        for goal, keywords in goal_mappings.items():
            if any(keyword in user_input_lower for keyword in keywords):
                goals.append(goal)
        
        # Check for specific skills/achievements
        skill_goals = {
            "pancake_stretch": ["pancake stretch", "pancake", "splits"],
            "handstand": ["handstand", "press to handstand", "handstand press"],
            "pull_ups": ["pull ups", "pullups", "chin ups"],
            "push_ups": ["push ups", "pushups"],
            "muscle_ups": ["muscle ups", "muscleup"],
            "planche": ["planche", "planche progressions"],
            "front_lever": ["front lever", "front lever progressions"],
            "back_lever": ["back lever", "back lever progressions"]
        }
        
        for skill, keywords in skill_goals.items():
            if any(keyword in user_input_lower for keyword in keywords):
                goals.append(skill)
        
        # Check for training frequency goals
        if any(freq in user_input_lower for freq in ["6 times", "6 days", "6x", "six times", "six days", "workout 6"]):
            goals.append("high_frequency_training")
        
        if any(freq in user_input_lower for freq in ["5 times", "5 days", "5x", "five times", "five days"]):
            goals.append("moderate_frequency_training")
        
        # Check for body part specific goals
        body_part_goals = {
            "shoulder_health": ["shoulder", "shoulders", "shoulder health"],
            "knee_health": ["knee", "knees", "knee health"],
            "core_strength": ["core", "abs", "abdominal"],
            "back_strength": ["back", "posture", "spinal"]
        }
        
        for body_part, keywords in body_part_goals.items():
            if any(keyword in user_input_lower for keyword in keywords):
                goals.append(body_part)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_goals = []
        for goal in goals:
            if goal not in seen:
                seen.add(goal)
                unique_goals.append(goal)
        
        logger.info(f"Extracted goals: {unique_goals}")
        return unique_goals 