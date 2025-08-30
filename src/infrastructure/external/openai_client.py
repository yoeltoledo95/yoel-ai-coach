"""
OpenAI client with proper error handling and retry logic
"""
import logging
import time
from typing import Dict, Any, Optional, List
import openai
from openai import OpenAI
from shared.exceptions import OpenAIError, ConfigurationError
from infrastructure.config.settings import config

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client with error handling and retry logic"""
    
    def __init__(self):
        if not getattr(config, 'openai_api_key', None):
            raise ConfigurationError("OpenAI API key is required")

        self.client = OpenAI(api_key=getattr(config, 'openai_api_key', ''))
        self.model = getattr(config, 'openai_model', 'gpt-4o-mini')
        self.max_tokens = getattr(config, 'openai_max_tokens', 2000)
        self.temperature = getattr(config, 'openai_temperature', 0.7)
        self.timeout = getattr(config, 'openai_timeout', 30)
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_retries: int = 3
    ) -> str:
        """Generate AI response with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=min(self.max_tokens, 900),
                    temperature=self.temperature,
                    timeout=self.timeout
                )
                
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    raise OpenAIError("Empty response from OpenAI")
                    
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                else:
                    raise OpenAIError(f"Rate limit exceeded after {max_retries} attempts: {e}")
                    
            except openai.APIError as e:
                if attempt < max_retries - 1:
                    wait_time = 1 * (attempt + 1)  # Linear backoff
                    logger.warning(f"API error, waiting {wait_time}s before retry: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise OpenAIError(f"OpenAI API error after {max_retries} attempts: {e}")
                    
            except Exception as e:
                raise OpenAIError(f"Unexpected error calling OpenAI: {e}")
        
        raise OpenAIError(f"Failed to generate response after {max_retries} attempts")

    def generate_from_prompt(
        self,
        system_prompt: str,
        user_message: str,
        max_retries: int = 3
    ) -> str:
        """Convenience method to send prebuilt prompts/messages."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        return self.generate_response(messages, max_retries=max_retries)
    
    def extract_information(
        self, 
        text: str, 
        extraction_keys: List[str]
    ) -> Dict[str, Any]:
        """Extract structured information from text"""
        prompt = f"""
        Extract all relevant information from the following text.
        Return ONLY a valid JSON object with these keys: {', '.join(extraction_keys)}.
        If a category is not present, return null for that key.
        Do not include any additional text, only the JSON object.
        
        Text: "{text}"
        
        JSON Response:
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts structured information from text. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.generate_response(messages)
            # Clean response and parse JSON
            import json
            import re
            
            # Remove any non-JSON text before parsing
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                logger.error(f"No JSON found in response: {response}")
                return {key: None for key in extraction_keys}
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {key: None for key in extraction_keys}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and mood from text"""
        prompt = f"""
        Analyze the sentiment and mood from this text. Return ONLY a valid JSON object with:
        - sentiment: positive, negative, or neutral
        - mood: specific mood (e.g., excited, tired, motivated, frustrated)
        - energy_level: 1-10 scale
        - confidence: 0-1 scale
        
        Text: "{text}"
        
        JSON Response:
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes sentiment and mood. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.generate_response(messages)
            import json
            import re
            
            # Remove any non-JSON text before parsing
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                logger.error(f"No JSON found in sentiment response: {response}")
                return {
                    "sentiment": "neutral",
                    "mood": "unknown",
                    "energy_level": 5,
                    "confidence": 0.5
                }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "mood": "unknown",
                "energy_level": 5,
                "confidence": 0.5
            }
    
    def generate_coaching_response(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> str:
        """Generate personalized coaching response"""
        
        # Debug: Log the context being used
        logger.info(f"Generating coaching response with context keys: {list(context.keys())}")
        logger.info(f"User profile in context: {context.get('user_profile', {})}")
        logger.info(f"Mentor context in context: {context.get('mentor_context', '')[:100]}...")
        
        # Build dynamic system prompt based on context
        system_prompt = self._build_dynamic_system_prompt(context)
        
        # Build user message with layered context
        user_message = self._build_user_message(user_input, context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.generate_response(messages)
    
    def _build_dynamic_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build dynamic system prompt based on context"""
        
        # Use the unified prompt engine instead of duplicating logic
        from infrastructure.external.prompt_engine import PromptEngine
        
        user_profile = context.get('user_profile', {})
        recent_sessions = context.get('recent_sessions', [])
        
        # Create prompt engine instance
        prompt_engine = PromptEngine(profile=user_profile, logs=recent_sessions)
        
        # Build simplified system prompt
        base_prompt = """You are Yoel's personal fitness coach. You know him well and care about his progress. Talk to him naturally like a real coach would - encouraging, practical, and genuinely helpful."""
        
        # Add mentor context if available
        mentor_context = context.get('mentor_context', '')
        if mentor_context:
            base_prompt += f"""
            
            MENTOR KNOWLEDGE:
            {mentor_context}
            
            Use this mentor knowledge naturally in conversation - reference mentors by name when relevant."""
        
        # Add conversation intent guidance
        conversation_context = context.get('conversation_context', {})
        if conversation_context.get('intent') == 'goal_setting':
            base_prompt += """
            
            GOAL SETTING MODE:
            - Help user set specific, measurable, achievable goals
            - Consider their current level and preferences
            - Provide clear progression paths
            - Ask clarifying questions to understand their vision
            - Reference their previous goals and progress
            """
        elif conversation_context.get('intent') == 'follow_up_question':
            base_prompt += """
            
            FOLLOW-UP MODE:
            - Provide detailed explanations for your recommendations
            - Reference specific mentor principles and reasoning
            - Explain the "why" behind your suggestions
            - Connect to their personal context and goals
            - Address their specific concerns or confusion
            """
        
        # Add personalized guidance based on user profile
        user_profile = context.get('user_profile', {})
        if user_profile:
            # Check if profile is incomplete (new user)
            goals = user_profile.get('goals', [])
            level = user_profile.get('level', 'Unknown')
            age = user_profile.get('age')
            
            if not goals or level == 'beginner' or age is None:
                base_prompt += f"""
                
                NEW USER PROFILE GATHERING:
                - User name: {user_profile.get('name', 'User')}
                - Profile is incomplete - need to gather real information
                - Ask specific questions about their fitness goals, experience level, and preferences
                - Don't assume anything - ask for their actual goals and experience
                - If they mention they're not a beginner, update your understanding
                - If they say goals are wrong, ask what their real goals are
                - Be conversational and gather information naturally
                """
            else:
                base_prompt += f"""
                
                PERSONALIZATION GUIDANCE:
                - User name: {user_profile.get('name', 'User')}
                - Current goals: {goals}
                - Fitness level: {level}
                - Injury considerations: {user_profile.get('injury_history', {})}
                - Always reference their specific goals and level
                - Consider their injury history when making recommendations
                """
        
        # Add conversation memory guidance
        user_memory = context.get('user_memory', {})
        recent_conversations = user_memory.get('recent_conversations', [])
        if recent_conversations:
            base_prompt += """
            
            CONVERSATION MEMORY:
            - Remember previous exchanges in this conversation
            - Don't ask for information already provided
            - Build on previous recommendations
            - Reference specific exercises or techniques mentioned before
            - Maintain consistency with earlier advice
            - If the user has stated their goals in previous messages, use those goals
            - If the user has provided specific fitness objectives, incorporate them into your responses
            - Don't reset to generic menus if the user has already shared their goals
            - When asked about goals, reference the user's saved goals from their profile
            - If user asks "What are my goals?" or similar, list their actual saved goals
            """
        
        # Get advanced personality context
        user_id = context.get('user_id', 'yoel_user')
        emotional_context = self._detect_emotional_context(context)
        
        personality_context = personality_engine.get_personality_context(
            user_id=user_id,
            emotional_context=emotional_context
        )
        
        # Add enhanced personality instructions
        base_prompt += f"""
        
        ADVANCED PERSONALITY INSTRUCTIONS:
        {personality_context.get('personality_instructions', '')}
        
        EMOTIONAL INTELLIGENCE:
        Current emotional context: {emotional_context or 'neutral'}
        Response approach: {personality_context.get('emotional_intelligence', {}).get(emotional_context, 'Be natural and supportive')}
        
        CONVERSATION PATTERNS:
        {self._format_conversation_patterns(personality_context.get('conversation_patterns', {}))}
        """
        
        return base_prompt
    
    def _detect_emotional_context(self, context: Dict[str, Any]) -> Optional[str]:
        """Detect emotional context from user message and conversation history"""
        user_message = context.get('user_message', '')
        if not user_message:
            return None
        
        message_lower = user_message.lower()
        
        # Detect emotional indicators
        if any(word in message_lower for word in ['excited', 'amazing', 'awesome', 'great']):
            return 'excitement'
        elif any(word in message_lower for word in ['pain', 'hurt', 'concerned', 'worried']):
            return 'concern'
        elif any(word in message_lower for word in ['tired', 'unmotivated', 'struggle']):
            return 'support'
        elif any(word in message_lower for word in ['achieved', 'progress', 'better']):
            return 'celebration'
        elif any(word in message_lower for word in ['curious', 'wondering', 'why', 'how']):
            return 'curiosity'
        else:
            return None
    
    def _format_conversation_patterns(self, patterns: Dict[str, List[str]]) -> str:
        """Format conversation patterns for inclusion in prompt"""
        if not patterns:
            return "Use natural, conversational language"
        
        formatted = []
        for pattern_type, examples in patterns.items():
            if examples:
                formatted.append(f"{pattern_type.title()}: {examples[0]}")
        
        return "\n".join(formatted)
    
    def _build_user_message(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build user message with layered context"""
        
        user_message = f"User message: {user_input}\n\n"
        
        # Add user profile context
        user_profile = context.get('user_profile', {})
        if user_profile:
            user_message += f"USER PROFILE:\n"
            user_message += f"- Name: {user_profile.get('name', 'User')}\n"
            user_message += f"- Goals: {user_profile.get('goals', [])}\n"
            user_message += f"- Level: {user_profile.get('level', 'Unknown')}\n"
            user_message += f"- Training preferences: {user_profile.get('training_preferences', {})}\n"
            user_message += f"- Injury history: {user_profile.get('injury_history', {})}\n"
            user_message += f"- Age: {user_profile.get('age', 'Unknown')}\n\n"
        
        # Add recent patterns
        patterns = context.get('patterns', {})
        if patterns:
            user_message += f"RECENT TRAINING PATTERNS:\n"
            user_message += f"- Training frequency: {patterns.get('frequency', 'Unknown')} sessions/week\n"
            user_message += f"- Average session duration: {patterns.get('avg_duration', 'Unknown')} minutes\n"
            user_message += f"- Common intensity: {patterns.get('most_common_intensity', 'Unknown')}\n"
            user_message += f"- Energy trends: {patterns.get('energy_trend', 'Unknown')}\n"
            user_message += f"- Mood trends: {patterns.get('mood_trend', 'Unknown')}\n\n"
        
        # Add relevant exercises
        exercise_context = context.get('exercise_context', {})
        relevant_exercises = exercise_context.get('relevant_exercises', [])
        if relevant_exercises:
            user_message += f"RELEVANT EXERCISES FOR USER'S GOALS:\n"
            for exercise in relevant_exercises[:5]:  # Top 5 most relevant
                user_message += f"- {exercise.get('name', 'Unknown')}: {exercise.get('description', '')[:150]}...\n"
            user_message += "\n"
        
        # Add user memory context
        user_memory = context.get('user_memory', {})
        recent_conversations = user_memory.get('recent_conversations', [])
        if recent_conversations:
            user_message += f"RECENT CONVERSATION HISTORY:\n"
            for conv in recent_conversations[-5:]:  # Last 5 conversations
                user_message += f"- User: {conv.get('message', '')}\n"
                user_message += f"- AI: {conv.get('response', '')[:100]}...\n"
            user_message += "\n"
            
            # Extract goals mentioned in recent conversations
            mentioned_goals = []
            for conv in recent_conversations:
                message = conv.get('message', '').lower()
                if any(goal in message for goal in ['shoulder', 'knee', 'handstand', 'pancake', 'flexibility', 'strength']):
                    mentioned_goals.append(conv.get('message', ''))
            
            if mentioned_goals:
                user_message += f"GOALS MENTIONED IN PREVIOUS CONVERSATIONS:\n"
                for goal in mentioned_goals[-3:]:  # Last 3 goal mentions
                    user_message += f"- {goal}\n"
                user_message += "\n"
            
            # Extract injury information from recent conversations
            mentioned_injuries = []
            for conv in recent_conversations:
                message = conv.get('message', '').lower()
                if any(injury in message for injury in ['meniscus', 'rotator cuff', 'scapula', 'impingement', 'tear', 'injury']):
                    mentioned_injuries.append(conv.get('message', ''))
            
            if mentioned_injuries:
                user_message += f"INJURIES MENTIONED IN PREVIOUS CONVERSATIONS:\n"
                for injury in mentioned_injuries[-3:]:  # Last 3 injury mentions
                    user_message += f"- {injury}\n"
                user_message += "\n"
        
        # Add conversation patterns
        conversation_patterns = user_memory.get('conversation_patterns', {})
        if conversation_patterns:
            user_message += f"CONVERSATION PATTERNS:\n"
            user_message += f"- Common intents: {conversation_patterns.get('common_intents', {})}\n"
            user_message += f"- Total conversations: {conversation_patterns.get('total_conversations', 0)}\n\n"
        
        # Add feedback patterns
        feedback_patterns = user_memory.get('feedback_patterns', {})
        if feedback_patterns:
            user_message += f"USER FEEDBACK PATTERNS:\n"
            user_message += f"- Common feedback types: {feedback_patterns.get('common_feedback_types', {})}\n"
            user_message += f"- Average rating: {feedback_patterns.get('average_rating', 0):.1f}/10\n\n"
        
        return user_message
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        return self.generate_response(messages)
    
    def create_weekly_plan(
        self, 
        user_profile: Dict[str, Any], 
        patterns: Dict[str, Any],
        programming_guidelines: Dict[str, Any] = None,
        weekly_template: Dict[str, Any] = None
    ) -> str:
        """Create personalized weekly training plan"""
        prompt = f"""
        Create a VERY SPECIFIC and PRECISE weekly training plan for this user:
        
        User Profile: {user_profile}
        Training Patterns: {patterns}
        """
        
        if programming_guidelines:
            prompt += f"\nProgramming Guidelines: {programming_guidelines}"
        
        if weekly_template:
            prompt += f"\nWeekly Template: {weekly_template}"
        
        prompt += """
        
        FORMAT THE PLAN LIKE THIS - BE VERY SPECIFIC:
        
        🏋️ WEEKLY WORKOUT PLAN
        
        📅 MONDAY - [Specific Day Type]
        • Warm-up: [EXACT exercises and duration]
          - [Exercise 1]: [specific sets/reps]
          - [Exercise 2]: [specific sets/reps]
        • Main Workout:
          - [Exercise 1]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 2]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 3]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 4]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
        • Cool-down: [EXACT exercises and duration]
        
        📅 TUESDAY - [Specific Day Type]
        • Warm-up: [EXACT exercises and duration]
          - [Exercise 1]: [specific sets/reps]
          - [Exercise 2]: [specific sets/reps]
        • Main Workout:
          - [Exercise 1]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 2]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 3]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 4]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
        • Cool-down: [EXACT exercises and duration]
        
        📅 WEDNESDAY - REST DAY
        • Light mobility: [EXACT exercises]
          - [Exercise 1]: [duration]
          - [Exercise 2]: [duration]
        
        📅 THURSDAY - [Specific Day Type]
        • Warm-up: [EXACT exercises and duration]
          - [Exercise 1]: [specific sets/reps]
          - [Exercise 2]: [specific sets/reps]
        • Main Workout:
          - [Exercise 1]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 2]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 3]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 4]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
        • Cool-down: [EXACT exercises and duration]
        
        📅 FRIDAY - [Specific Day Type]
        • Warm-up: [EXACT exercises and duration]
          - [Exercise 1]: [specific sets/reps]
          - [Exercise 2]: [specific sets/reps]
        • Main Workout:
          - [Exercise 1]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 2]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 3]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 4]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
        • Cool-down: [EXACT exercises and duration]
        
        📅 SATURDAY - [Specific Day Type]
        • Warm-up: [EXACT exercises and duration]
          - [Exercise 1]: [specific sets/reps]
          - [Exercise 2]: [specific sets/reps]
        • Main Workout:
          - [Exercise 1]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 2]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 3]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
          - [Exercise 4]: [EXACT sets] x [EXACT reps] @ [weight if applicable]
        • Cool-down: [EXACT exercises and duration]
        
        📅 SUNDAY - REST DAY
        • Light mobility: [EXACT exercises]
          - [Exercise 1]: [duration]
          - [Exercise 2]: [duration]
        
        💡 SPECIFIC PROGRESSION NOTES:
        • [EXACT progression details]
        • [EXACT form cues]
        • [EXACT recovery tips]
        
        🎯 WEEKLY SPECIFIC GOALS:
        • [EXACT goal 1 with numbers]
        • [EXACT goal 2 with numbers]
        • [EXACT goal 3 with numbers]
        
        IMPORTANT: Be VERY SPECIFIC with:
        - Exact exercise names
        - Exact sets and reps (e.g., "3 sets x 8 reps")
        - Exact weights when applicable (e.g., "3 sets x 8 reps @ 50kg")
        - Exact durations for warm-ups and cool-downs
        - Exact rest periods between sets
        - Specific form cues and technique notes
        
        NO VAGUE SUGGESTIONS like "do some mobility" or "quick warm-up"
        """
        
        messages = [
            {"role": "system", "content": "You are an expert fitness coach creating VERY SPECIFIC and PRECISE training plans. Always provide exact exercises, sets, reps, and weights. Never give vague suggestions."},
            {"role": "user", "content": prompt}
        ]
        
        return self.generate_response(messages) 