"""
OpenAI client with proper error handling and retry logic
"""
import logging
import time
from typing import Dict, Any, Optional, List
import openai
from openai import OpenAI
from shared.exceptions import AIError, ConfigurationError
from infrastructure.config.settings import config

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client with error handling and retry logic"""
    
    def __init__(self):
        if not config.openai.api_key:
            raise ConfigurationError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=config.openai.api_key)
        self.model = config.openai.model
        self.max_tokens = config.openai.max_tokens
        self.temperature = config.openai.temperature
        self.timeout = config.openai.timeout
    
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
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=self.timeout
                )
                
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    raise AIError("Empty response from OpenAI")
                    
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                else:
                    raise AIError(f"Rate limit exceeded after {max_retries} attempts: {e}")
                    
            except openai.APIError as e:
                if attempt < max_retries - 1:
                    wait_time = 1 * (attempt + 1)  # Linear backoff
                    logger.warning(f"API error, waiting {wait_time}s before retry: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise AIError(f"OpenAI API error after {max_retries} attempts: {e}")
                    
            except Exception as e:
                raise AIError(f"Unexpected error calling OpenAI: {e}")
        
        raise AIError(f"Failed to generate response after {max_retries} attempts")
    
    def extract_information(
        self, 
        text: str, 
        extraction_keys: List[str]
    ) -> Dict[str, Any]:
        """Extract structured information from text"""
        prompt = f"""
        Extract all relevant information from the following text.
        Return a JSON object with these keys: {', '.join(extraction_keys)}.
        If a category is not present, return null for that key.
        
        Text: "{text}"
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts structured information from text."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.generate_response(messages)
            # Parse JSON response
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {key: None for key in extraction_keys}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and mood from text"""
        prompt = f"""
        Analyze the sentiment and mood from this text. Return a JSON object with:
        - sentiment: positive, negative, or neutral
        - mood: specific mood (e.g., excited, tired, motivated, frustrated)
        - energy_level: 1-10 scale
        - confidence: 0-1 scale
        
        Text: "{text}"
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes sentiment and mood."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.generate_response(messages)
            import json
            return json.loads(response)
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
        system_prompt = f"""
        You are an AI fitness coach with expertise from world-class trainers.
        Provide personalized, encouraging, and PRACTICAL advice.
        
        IMPORTANT: Be VERY SPECIFIC and ACTIONABLE.
        - Give exact exercises, sets, reps, and weights when applicable
        - Provide specific form cues and technique details
        - Include exact durations and rest periods
        - Avoid vague suggestions like "do some mobility" or "quick warm-up"
        
        User Context:
        - Profile: {context.get('user_profile', {})}
        - Recent Sessions: {context.get('recent_sessions', [])}
        - Patterns: {context.get('patterns', {})}
        - Mentor Context: {context.get('mentor_context', '')}
        
        Respond to: "{user_input}"
        
        Format guidelines:
        • Use short paragraphs (2-3 sentences max)
        • Use bullet points for specific exercises and sets
        • Use emojis sparingly but effectively
        • Keep it conversational and encouraging
        • Focus on SPECIFIC, ACTIONABLE advice
        • Include exact numbers: sets, reps, weights, durations
        • Provide specific form cues and technique notes
        """
        
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