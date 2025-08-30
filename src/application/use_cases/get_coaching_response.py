"""
Use case: Get personalized coaching response
"""
from typing import Dict, Any, Optional, List
from domain.services.coaching_service import CoachingService
from infrastructure.external.openai_client import OpenAIClient
from infrastructure.external.prompt_engine import PromptEngine
from shared.ai.personality_engine import personality_engine
from shared.ai.advanced_prompts import advanced_prompt_engine
from infrastructure.database.sqlite.user_memory_store import UserMemoryStore
from shared.logging import get_logger

logger = get_logger(__name__)


class GetCoachingResponseUseCase:
    """Use case for getting personalized coaching responses"""
    
    def __init__(
        self, 
        coaching_service: CoachingService,
        ai_client: OpenAIClient,
        user_memory_store: UserMemoryStore
    ):
        self.coaching_service = coaching_service
        self.ai_client = ai_client
        self.user_memory_store = user_memory_store
    
    def execute(
        self, 
        user_id: str, 
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_name: str = "User"
    ) -> str:
        """Execute the use case"""
        try:
            logger.info(f"Getting coaching response for user {user_id}")
            
            # Build dynamic context with layered knowledge retrieval
            dynamic_context = self._build_dynamic_context(user_id, user_input, context, user_name)
            
            # Debug: Log the dynamic context
            logger.info(f"Dynamic context for user {user_id}: {dynamic_context}")
            
            # Enhanced AI response generation
            user_id = dynamic_context.get("user_id", user_id)
            
            # Get personality context
            personality_context = personality_engine.get_personality_context(
                user_id=user_id,
                emotional_context=self._detect_emotional_context(user_input, dynamic_context)
            )
            
            # Determine optimal prompt type
            prompt_type = advanced_prompt_engine.get_prompt_type_from_context(
                user_input, dynamic_context
            )
            
            # Build advanced multi-layered prompt
            built = advanced_prompt_engine.build_advanced_prompt(
                prompt_type=prompt_type,
                context=dynamic_context,
                personality_context=personality_context,
                user_input=user_input
            )

            # Send via OpenAI client
            response = self.ai_client.generate_from_prompt(
                system_prompt=built["system"],
                user_message=built["user"]
            )
            
            # Enhance response naturalness
            response = personality_engine.enhance_response_naturalness(response)
            
            # Store the conversation in user memory
            conversation_context = context or {}
            intent = conversation_context.get("intent") if conversation_context else None
            self.user_memory_store.store_conversation(
                user_id=user_id,
                message=user_input,
                response=response,
                context=dynamic_context,
                intent=intent
            )
            
            # Update user profile based on conversation feedback
            self._update_user_profile_from_conversation(user_id, user_input, dynamic_context)
            
            logger.info(f"Generated coaching response for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting coaching response for user {user_id}: {e}")
            return "I'm having trouble processing your request right now. Please try again later."
    
    def _build_dynamic_context(self, user_id: str, user_input: str, context: Optional[Dict[str, Any]] = None, user_name: str = "User") -> Dict[str, Any]:
        """Build dynamic context with layered knowledge retrieval"""
        try:
            # Get user profile and history
            user = self.coaching_service.user_repository.get_user(user_id)
            
            # Create user profile if it doesn't exist
            if not user:
                logger.info(f"Creating new user profile for {user_id} ({user_name})")
                user = self.coaching_service._create_new_user_profile(user_id, user_name)
                if not user:
                    logger.error(f"Failed to create user profile for {user_id}")
                    return {"user_input": user_input}
            
            # Update user profile with information from conversation
            self._update_user_profile_from_conversation(user_id, user_input, {})
            
            # Convert user profile to JSON-serializable format
            user_profile = {}
            if user and user.profile:
                profile = user.profile
                user_profile = {
                    "name": profile.name,
                    "age": profile.age,
                    "goals": [goal.value if hasattr(goal, 'value') else str(goal) for goal in profile.goals],
                    "level": profile.level.value if hasattr(profile.level, 'value') else str(profile.level),
                    "training_preferences": profile.training_preferences,
                    "injury_history": profile.injury_history,
                    "nutrition_preferences": profile.nutrition_preferences,
                    "recovery_needs": profile.recovery_needs
                }
            recent_sessions = [s.__dict__ for s in user.get_recent_sessions(7)] if user else []
            
            # Analyze user patterns
            patterns = self.coaching_service._analyze_user_patterns(user) if user else {}
            
            # Get relevant mentor knowledge based on user input and context
            mentor_context = self._get_relevant_mentor_knowledge(user_input, user_profile, patterns)
            logger.info(f"Mentor context for user {user_id}: {mentor_context[:200]}...")
            
            # Get relevant exercise knowledge
            exercise_context = self._get_relevant_exercise_knowledge(user_input, user_profile)
            
            # Get user memory and evolving context
            user_memory = self._get_user_memory(user_id, user_input)
            
            # Build conversation context
            conversation_context = context or {}
            if conversation_context.get("goal_setting"):
                conversation_context["intent"] = "goal_setting"
            elif conversation_context.get("follow_up_question"):
                conversation_context["intent"] = "follow_up_question"
            
            return {
                "user_profile": user_profile,
                "recent_sessions": recent_sessions,
                "patterns": patterns,
                "mentor_context": mentor_context,
                "exercise_context": exercise_context,
                "user_memory": user_memory,
                "conversation_context": conversation_context,
                "user_input": user_input
            }
            
        except Exception as e:
            logger.error(f"Error building dynamic context: {e}")
            return {"user_input": user_input}
    
    def _get_relevant_mentor_knowledge(self, user_input: str, user_profile: Dict[str, Any], patterns: Dict[str, Any]) -> str:
        """Get relevant mentor knowledge based on user input and context"""
        try:
            # Determine relevant mentors based on user input and profile
            relevant_mentors = self._identify_relevant_mentors(user_input, user_profile, patterns)
            
            # Get mentor context from RAG system
            mentor_context = self.coaching_service.mentor_repository.get_mentor_context(
                user_input, 
                mentor_names=relevant_mentors
            )
            
            return mentor_context
            
        except Exception as e:
            logger.error(f"Error getting mentor knowledge: {e}")
            return ""
    
    def _identify_relevant_mentors(self, user_input: str, user_profile: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Identify which mentors are most relevant to this conversation"""
        user_input_lower = user_input.lower()
        
        # Comprehensive mentor mapping for all 7 mentors
        mentor_mapping = {
            # Goal setting and planning
            "goal": ["dylan_werner", "ido_portal", "tom_merrick"],
            "plan": ["dylan_werner", "ido_portal", "tom_merrick"],
            "routine": ["dylan_werner", "ido_portal", "tom_merrick"],
            
            # Strength and power
            "strength": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "power": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "muscle": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "push": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "pull": ["dylan_werner", "tom_merrick", "everydamnandré"],
            
            # Mobility and flexibility
            "mobility": ["dylan_werner", "ido_portal", "kneesovertoesguy"],
            "flexibility": ["dylan_werner", "tom_merrick", "ido_portal"],
            "stretch": ["dylan_werner", "tom_merrick", "ido_portal"],
            "pancake": ["dylan_werner", "tom_merrick", "ido_portal"],
            "split": ["dylan_werner", "tom_merrick", "ido_portal"],
            
            # Movement and skills
            "movement": ["ido_portal", "dylan_werner", "tom_merrick"],
            "handstand": ["dylan_werner", "ido_portal", "tom_merrick"],
            "balance": ["dylan_werner", "ido_portal", "tom_merrick"],
            "skill": ["dylan_werner", "ido_portal", "tom_merrick"],
            "flow": ["ido_portal", "dylan_werner"],
            
            # Injury and joint health
            "injury": ["dylan_werner", "kneesovertoesguy", "tom_merrick"],
            "knee": ["kneesovertoesguy", "dylan_werner"],
            "shoulder": ["dylan_werner", "tom_merrick"],
            "back": ["dylan_werner", "kneesovertoesguy"],
            "joint": ["kneesovertoesguy", "dylan_werner"],
            "pain": ["kneesovertoesguy", "dylan_werner"],
            
            # Progression and form
            "progression": ["dylan_werner", "ido_portal", "tom_merrick"],
            "form": ["dylan_werner", "tom_merrick", "ido_portal"],
            "technique": ["dylan_werner", "tom_merrick", "ido_portal"],
            "cues": ["dylan_werner", "tom_merrick"],
            
            # Recovery and wellness
            "recovery": ["dylan_werner", "tom_merrick", "ido_portal"],
            "rest": ["dylan_werner", "tom_merrick"],
            "wellness": ["dylan_werner", "ido_portal"],
            
            # Advanced movements
            "planche": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "front lever": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "muscle up": ["dylan_werner", "tom_merrick", "everydamnandré"],
            "press": ["dylan_werner", "tom_merrick", "everydamnandré"],
            
            # Cardio and conditioning
            "cardio": ["everydamnandré", "tom_merrick"],
            "conditioning": ["everydamnandré", "tom_merrick"],
            "endurance": ["everydamnandré", "tom_merrick"],
            
            # Mindset and philosophy
            "mindset": ["ido_portal", "dylan_werner"],
            "philosophy": ["ido_portal", "dylan_werner"],
            "play": ["ido_portal", "dylan_werner"]
        }
        
        relevant_mentors = []
        for keyword, mentors in mentor_mapping.items():
            if keyword in user_input_lower:
                relevant_mentors.extend(mentors)
        
        # Add all mentors if none identified (for comprehensive knowledge)
        if not relevant_mentors:
            relevant_mentors = ["dylan_werner", "ido_portal", "tom_merrick", "kneesovertoesguy", "everydamnandré"]
        
        # Ensure we get a good mix of mentors (3-5 mentors)
        unique_mentors = list(set(relevant_mentors))
        if len(unique_mentors) > 5:
            # Prioritize based on keyword frequency
            mentor_counts = {}
            for mentor in relevant_mentors:
                mentor_counts[mentor] = mentor_counts.get(mentor, 0) + 1
            
            # Sort by frequency and take top 5
            unique_mentors = sorted(unique_mentors, key=lambda x: mentor_counts.get(x, 0), reverse=True)[:5]
        
        return unique_mentors
    
    def _get_relevant_exercise_knowledge(self, user_input: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant exercise knowledge based on user input and profile"""
        try:
            # Extract exercise-related keywords from user input
            exercise_keywords = self._extract_exercise_keywords(user_input)
            
            # Get relevant exercises from exercise repository
            relevant_exercises = []
            if exercise_keywords:
                # Join keywords into a search query
                search_query = " ".join(exercise_keywords)
                relevant_exercises = self.coaching_service.exercise_repository.search_exercises(search_query)
            
            # Convert Exercise objects to dictionaries for JSON serialization
            exercise_dicts = []
            for exercise in relevant_exercises[:5]:  # Top 5 most relevant
                exercise_dicts.append({
                    "name": exercise.name,
                    "description": exercise.description,
                    "category": exercise.category.value if hasattr(exercise.category, 'value') else str(exercise.category),
                    "difficulty": exercise.difficulty.value if hasattr(exercise.difficulty, 'value') else str(exercise.difficulty),
                    "tags": exercise.tags,
                    "equipment": exercise.equipment,
                    "muscle_groups": exercise.muscle_groups,
                    "cues": exercise.cues,
                    "source": exercise.source
                })
            
            return {
                "relevant_exercises": exercise_dicts,
                "user_preferences": user_profile.get("training_preferences", {}),
                "injury_considerations": user_profile.get("injury_history", {})
            }
            
        except Exception as e:
            logger.error(f"Error getting exercise knowledge: {e}")
            return {}
    
    def _extract_exercise_keywords(self, user_input: str) -> List[str]:
        """Extract exercise-related keywords from user input"""
        user_input_lower = user_input.lower()
        
        # Common exercise keywords
        exercise_keywords = [
            "push-up", "pull-up", "squat", "deadlift", "plank", "handstand",
            "mobility", "flexibility", "strength", "cardio", "balance",
            "core", "legs", "arms", "shoulders", "back", "chest"
        ]
        
        found_keywords = [keyword for keyword in exercise_keywords if keyword in user_input_lower]
        return found_keywords
    
    def _get_user_memory(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """Get evolving user memory and context"""
        try:
            # Get comprehensive user memory summary
            memory_summary = self.user_memory_store.get_user_memory_summary(user_id)
            
            return {
                "recent_conversations": memory_summary.get("recent_conversations", []),
                "user_feedback": memory_summary.get("user_feedback", {}),
                "progress_milestones": memory_summary.get("progress_milestones", []),
                "conversation_patterns": memory_summary.get("conversation_patterns", {}),
                "feedback_patterns": memory_summary.get("feedback_patterns", {}),
                "last_interaction": memory_summary.get("last_interaction"),
                "current_context": user_input
            }
            
        except Exception as e:
            logger.error(f"Error getting user memory: {e}")
            return {}
    
    def extract_user_info(self, user_input: str) -> Dict[str, Any]:
        """Extract structured information from user input"""
        extraction_keys = [
            "goals", "achievements", "struggles", "injuries", "weekly_reflection",
            "preferences", "feedback", "session_log", "questions", "mood",
            "intentions", "lifestyle", "milestones"
        ]
        
        try:
            return self.ai_client.extract_information(user_input, extraction_keys)
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
            return {key: None for key in extraction_keys}
    
    def analyze_sentiment(self, user_input: str) -> Dict[str, Any]:
        """Analyze sentiment and mood from user input"""
        try:
            return self.ai_client.analyze_sentiment(user_input)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "mood": "unknown",
                "energy_level": 5,
                "confidence": 0.5
            }
    
    def _update_user_profile_from_conversation(self, user_id: str, user_input: str, context: Dict[str, Any]):
        """Update user profile based on conversation feedback"""
        try:
            user_input_lower = user_input.lower()
            user = self.coaching_service.user_repository.get_user(user_id)
            
            if not user:
                return
            
            # Check for level corrections
            if any(phrase in user_input_lower for phrase in ["not a beginner", "not beginner", "intermediate", "advanced", "experienced"]):
                if "intermediate" in user_input_lower:
                    user.profile.level = "intermediate"
                elif "advanced" in user_input_lower:
                    user.profile.level = "advanced"
                else:
                    user.profile.level = "intermediate"  # Default if not beginner
                logger.info(f"Updated user {user_id} level to {user.profile.level}")
            
            # Check for goal corrections
            if any(phrase in user_input_lower for phrase in ["not my goals", "these are not my goals", "wrong goals", "different goals"]):
                # Clear current goals - AI will ask for real goals
                user.profile.goals = []
                logger.info(f"Cleared goals for user {user_id} - will ask for real goals")
            
            # Extract goals from user input and recent conversations
            goals = self._extract_goals_from_input(user_input)
            
            # If no goals found in current input, check recent conversations
            if not goals:
                goals = self._extract_goals_from_conversation_history(user_id)
            
            if goals:
                user.profile.goals = goals
                logger.info(f"Updated user {user_id} goals to: {[goal.value for goal in goals]}")
            
            # Extract injury information
            injury_info = self._extract_injury_info_from_input(user_input)
            if injury_info:
                user.profile.injury_history.update(injury_info)
                logger.info(f"Updated user {user_id} injury history: {injury_info}")
            
            # Save updated user
            self.coaching_service.user_repository.save_user(user, user_id)
            
        except Exception as e:
            logger.error(f"Error updating user profile from conversation: {e}")
    
    def _extract_goals_from_input(self, user_input: str) -> List:
        """Extract fitness goals from user input"""
        try:
            from domain.entities.user import UserGoal
            
            user_input_lower = user_input.lower()
            goals = []
            
            # Map common goal phrases to UserGoal enums
            goal_mapping = {
                "shoulder": "mobility",
                "knee": "mobility", 
                "handstand": "skill",
                "press to handstand": "skill",
                "pancake": "flexibility",
                "pancake stretch": "flexibility",
                "flexibility": "flexibility",
                "strength": "strength",
                "muscle": "strength",
                "endurance": "endurance",
                "cardio": "endurance",
                "weight loss": "weight_loss",
                "weight management": "weight_loss",
                "mobility": "mobility",
                "skill": "skill",
                "balance": "skill",
                "coordination": "skill",
                "joint health": "mobility",
                "joint": "mobility"
            }
            
            for phrase, goal in goal_mapping.items():
                if phrase in user_input_lower:
                    if goal not in goals:
                        goals.append(goal)
            
            # Convert string goals to UserGoal enums
            from domain.entities.user import UserGoal
            enum_goals = []
            for goal_str in goals:
                try:
                    if goal_str == "mobility":
                        enum_goals.append(UserGoal.MOBILITY)
                    elif goal_str == "skill":
                        enum_goals.append(UserGoal.SKILL)
                    elif goal_str == "flexibility":
                        enum_goals.append(UserGoal.FLEXIBILITY)
                    elif goal_str == "strength":
                        enum_goals.append(UserGoal.STRENGTH)
                    elif goal_str == "endurance":
                        enum_goals.append(UserGoal.ENDURANCE)
                    elif goal_str == "weight_loss":
                        enum_goals.append(UserGoal.WEIGHT_LOSS)
                except Exception as e:
                    logger.error(f"Error converting goal {goal_str} to enum: {e}")
            
            return enum_goals
            
        except Exception as e:
            logger.error(f"Error extracting goals from input: {e}")
            return []
    
    def _extract_goals_from_conversation_history(self, user_id: str) -> List:
        """Extract fitness goals from recent conversation history"""
        try:
            from domain.entities.user import UserGoal
            
            # Get recent conversations from user memory
            user_memory = self.user_memory_store.get_user_memory_summary(user_id)
            recent_conversations = user_memory.get('recent_conversations', [])
            
            goals = []
            goal_mapping = {
                "shoulder": UserGoal.MOBILITY,
                "knee": UserGoal.MOBILITY,
                "handstand": UserGoal.SKILL,
                "pancake": UserGoal.FLEXIBILITY,
                "flexibility": UserGoal.FLEXIBILITY,
                "strength": UserGoal.STRENGTH,
                "muscle": UserGoal.STRENGTH,
                "endurance": UserGoal.ENDURANCE,
                "cardio": UserGoal.ENDURANCE,
                "weight loss": UserGoal.WEIGHT_LOSS,
                "weight management": UserGoal.WEIGHT_LOSS,
                "mobility": UserGoal.MOBILITY,
                "skill": UserGoal.SKILL,
                "balance": UserGoal.SKILL,
                "coordination": UserGoal.SKILL
            }
            
            # Check last 10 conversations for goal mentions
            for conv in recent_conversations[-10:]:
                message = conv.get('message', '').lower()
                for phrase, goal in goal_mapping.items():
                    if phrase in message and goal not in goals:
                        goals.append(goal)
            
            # Also check AI responses for goal confirmations
            for conv in recent_conversations[-10:]:
                response = conv.get('response', '').lower()
                if any(phrase in response for phrase in ['goal', 'objectives', 'targets']):
                    # If AI mentioned goals in response, check the user's message
                    user_msg = conv.get('message', '').lower()
                    for phrase, goal in goal_mapping.items():
                        if phrase in user_msg and goal not in goals:
                            goals.append(goal)
            
            return goals
            
        except Exception as e:
            logger.error(f"Error extracting goals from conversation history: {e}")
            return []
    
    def _extract_injury_info_from_input(self, user_input: str) -> Dict[str, Any]:
        """Extract injury information from user input"""
        try:
            user_input_lower = user_input.lower()
            injury_info = {}
            
            # Check for knee injuries
            if "meniscus" in user_input_lower or "meniscal" in user_input_lower:
                if "left knee" in user_input_lower:
                    injury_info["left_knee"] = "past meniscus tear - no ongoing pain, building capacity through ATG training"
                elif "right knee" in user_input_lower:
                    injury_info["right_knee"] = "past meniscus tear - no ongoing pain, building capacity through ATG training"
                else:
                    injury_info["knee"] = "past meniscus tear - no ongoing pain, building capacity through ATG training"
            
            # Check for shoulder injuries and pain
            if any(term in user_input_lower for term in ["shoulder pain", "biceps tendon", "trapezius", "rotator cuff"]):
                shoulder_details = []
                
                if "biceps tendon" in user_input_lower:
                    shoulder_details.append("biceps tendon pain (long head) - aggravated by forward arm movement and bear crawl")
                
                if "trapezius" in user_input_lower or "upper trap" in user_input_lower:
                    shoulder_details.append("upper trapezius pain - radiating from shoulder to neck during overhead pressing")
                
                if "protraction" in user_input_lower or "punching" in user_input_lower:
                    shoulder_details.append("trapezius discomfort during shoulder protraction")
                
                if "rotator cuff" in user_input_lower:
                    shoulder_details.append("possible rotator cuff involvement (supraspinatus/infraspinatus tension)")
                
                if "scapular" in user_input_lower or "scapula" in user_input_lower:
                    shoulder_details.append("scapular instability or trap dominance")
                
                if shoulder_details:
                    injury_info["shoulder"] = "; ".join(shoulder_details)
            
            # Check for specific movement aggravations
            if "bear crawl" in user_input_lower:
                injury_info["movement_limitations"] = injury_info.get("movement_limitations", "") + "; bear crawl aggravates shoulder"
            
            if "overhead" in user_input_lower and "press" in user_input_lower:
                injury_info["movement_limitations"] = injury_info.get("movement_limitations", "") + "; overhead pressing aggravates shoulder"
            
            # Check for other common injuries
            if "back" in user_input_lower and ("pain" in user_input_lower or "injury" in user_input_lower):
                injury_info["back"] = "back pain/injury"
            
            if "ankle" in user_input_lower and ("sprain" in user_input_lower or "injury" in user_input_lower):
                injury_info["ankle"] = "ankle sprain/injury"
            
            if "wrist" in user_input_lower and ("pain" in user_input_lower or "injury" in user_input_lower):
                injury_info["wrist"] = "wrist pain/injury"
            
            return injury_info
            
        except Exception as e:
            logger.error(f"Error extracting injury info from input: {e}")
            return {}
    
    def _detect_emotional_context(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """Detect emotional context from user input and conversation history"""
        input_lower = user_input.lower()
        
        # Analyze for emotional indicators
        if any(word in input_lower for word in ['excited', 'amazing', 'awesome', 'great', 'fantastic']):
            return 'excitement'
        elif any(word in input_lower for word in ['pain', 'hurt', 'concerned', 'worried', 'afraid']):
            return 'concern'
        elif any(word in input_lower for word in ['tired', 'unmotivated', 'struggle', 'difficult']):
            return 'support'
        elif any(word in input_lower for word in ['achieved', 'progress', 'better', 'improved']):
            return 'celebration'
        elif any(word in input_lower for word in ['curious', 'wondering', 'why', 'how', 'explain']):
            return 'curiosity'
        else:
            return None 