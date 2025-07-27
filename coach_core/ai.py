print('AI module loaded')
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.analysis import analyze_patterns, calculate_recovery_score, calculate_training_volume
from coach_core.utils import detect_split
from coach_core.mentor_brain import get_all_mentors_context, create_mentor_prompt, get_mentor_specialization, get_relevant_mentors_for_query, get_weekly_planning_context, get_mentor_context
from coach_core.prompt_engine import PromptEngine

logger = logging.getLogger(__name__)

# --- Exercise KB Integration ---
EXERCISE_KB_PATH = os.path.join(os.path.dirname(__file__), 'exercise_kb.json')
def load_exercise_kb() -> List[Dict[str, Any]]:
    with open(EXERCISE_KB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
exercise_kb = load_exercise_kb()

def find_exercise_by_name(name: str) -> Optional[Dict[str, Any]]:
    for ex in exercise_kb:
        if ex['name'].lower() == name.lower():
            return ex
    return None

def search_exercises_by_tag(tag: str) -> List[Dict[str, Any]]:
    tag = tag.lower()
    return [ex for ex in exercise_kb if any(tag in t.lower() for t in ex.get('tags', []))]

def search_exercises_by_pattern(pattern: str) -> List[Dict[str, Any]]:
    pattern = pattern.lower()
    return [ex for ex in exercise_kb if pattern in ex.get('pattern', '').lower()]

# --- Existing AI Coach class and logic below ---

class AICoach:
    """Mentor-Powered AI Coach - Synthesizing the world's best minds in movement and strength."""
    def __init__(self, model: Optional[str] = None):
        self.profile = load_profile()
        self.logs = load_logs()
        self.client = None
        self.mentors = get_all_mentors_context()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.feedback_history = []  # Store feedback in memory for now
        # Initialize OpenAI client with proper configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Error initializing OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No OPENAI_API_KEY found in environment variables")
            self.client = None

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze user patterns for AI context"""
        return analyze_patterns(self.logs)

    def log_feedback(self, feedback: str):
        """Store user feedback after a session."""
        self.feedback_history.append(feedback)
        # Optionally, persist to DB or file in the future

    def get_recent_feedback(self, n: int = 3) -> str:
        """Get the most recent n feedback entries as a string."""
        if not self.feedback_history:
            return ""
        return "\n".join(self.feedback_history[-n:])

    def get_mentor_powered_response(self, user_input: str, prompt_type: str = "daily_workout", feedback: Optional[str] = None, few_shot_examples: Optional[list] = None) -> str:
        """Get intelligent response from GPT using modular PromptEngine, with feedback loop."""
        if not self.client:
            logger.warning("⚠️ Using fallback response (no OpenAI client)")
            return self.get_fallback_response(user_input)
        try:
            patterns = self.analyze_patterns()
            prompt_engine = PromptEngine(self.profile, self.logs)
            # Use explicit feedback if provided, else use recent feedback
            feedback_block = feedback or self.get_recent_feedback(n=3)
            prompt = prompt_engine.build_prompt(
                user_input=user_input,
                prompt_type=prompt_type,
                patterns=patterns,
                feedback=feedback_block,
                few_shot_examples=few_shot_examples,
                detail_level="high"
            )
            logger.info(f"🤖 Sending modular prompt to OpenAI ({self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.8
            )
            result = response.choices[0].message.content
            if not result:
                return self.get_fallback_response(user_input)
            logger.info("✅ Received modular mentor-powered response from OpenAI")
            return result
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return self.get_fallback_response(user_input)

    def _create_user_context(self, user_input: str, patterns: Dict[str, Any]) -> str:
        """Create comprehensive user context"""
        recent_logs = self.logs[-3:] if self.logs else []
        # Calculate recovery and training volume for recent logs
        for log in recent_logs:
            if 'recovery_score' not in log or log['recovery_score'] is None:
                log['recovery_score'] = calculate_recovery_score(log)
            if 'training_volume' not in log or log['training_volume'] is None:
                log['training_volume'] = calculate_training_volume(log)
        context = f"""
YOEL'S PROFILE:
{json.dumps(self.profile, indent=2)}

RECENT PATTERNS ANALYSIS:
{json.dumps(patterns, indent=2)}

RECENT LOGS (last 3 days):
{json.dumps(recent_logs, indent=2)}

YOEL'S QUESTION/REQUEST:
{user_input}

Respond as Yoel's mentor-powered AI coach, drawing from the wisdom of the world's best movement and strength minds:"""
        return context

    def _create_system_prompt(self, mentor_context: str) -> str:
        """Create the system prompt with RAG-powered mentor knowledge"""
        return f"""You are Yoel's personal AI fitness coach, trained by the world's greatest minds in movement, strength, and performance.

You have access to the knowledge and philosophies of these mentors:

{mentor_context}

YOUR COACHING APPROACH:
- Synthesize the best insights from all mentors based on Yoel's specific needs
- Be encouraging, knowledgeable, and personalized
- Consider his injuries (shoulder issues, knee is fine now)
- Focus on his goals (calisthenics, yoga, athletic performance)
- Provide actionable, specific advice
- Ask follow-up questions to understand his needs better
- Be conversational and supportive like a real coach
- Reference specific mentor insights when relevant

YOUR PERSONALITY:
- Wise and knowledgeable like Dr. Andy Galpin
- Encouraging and patient like Patrick Beach
- Direct and motivating like Everydamnandré
- Safety-focused like SquatU
- Longevity-minded like KneesOverToesGuy
- Movement-focused like Ido Portal

Always provide specific, actionable advice that combines the best insights from these mentors."""

    def get_ai_response(self, user_input: str) -> str:
        """Get intelligent response from GPT based on profile and logs."""
        return self.get_mentor_powered_response(user_input)

    def get_fallback_response(self, user_input: str) -> str:
        """Enhanced fallback responses incorporating mentor wisdom and exercise KB"""
        user_input = user_input.lower()
        patterns = self.analyze_patterns()
        # Example: If user asks about a specific exercise, pull from KB
        for ex in exercise_kb:
            if ex['name'].lower() in user_input:
                return f"Here's information about {ex['name']} from the exercise library:\nDescription: {ex.get('description', 'N/A')}\nTags: {', '.join(ex.get('tags', []))}\nProgressions: {', '.join(ex.get('progressions', []))}\nRegressions: {', '.join(ex.get('regressions', []))}\nCues: {', '.join(ex.get('cues', []))}"
        # Otherwise, fallback to mentor-based advice
        if "tired" in user_input or "low energy" in user_input:
            return "I hear you're feeling tired. Let's take a page from Patrick Beach's book - movement should feel good and natural. Maybe some gentle mobility work or light yoga? And remember what Dylan Werner says: 'Control your body, control your mind.' Sometimes the best training is active recovery. 💪"
        if "what should i train" in user_input or "workout" in user_input:
            return f"Looking at your {self.profile.get('training_preferences', {}).get('split', 'Push/Pull/Legs')} split, what day are you on? I can suggest specific exercises that blend Dylan Werner's isometric control, SquatU's joint safety, and your calisthenics preferences while being mindful of your shoulder. What's your energy level today?"
        if "what should i eat" in user_input or "food" in user_input:
            return "For your goals and preferences, I'd suggest something with good protein and clean carbs - think Dr. Andy Galpin's science-based approach. How about eggs with tahini and some vegetables? Or if you're post-workout, maybe some chicken with rice and fruit? What's your current energy level?"
        if "injury" in user_input or "pain" in user_input:
            return "I'm keeping an eye on your shoulder issues - that's SquatU and KneesOverToesGuy territory. Remember to do your band work and avoid exercises that cause pain. Your knee is doing well though - we can include more knee work gradually! What specific movements are bothering you?"
        return "I'm here to help with your training, nutrition, and recovery! I draw from the wisdom of the world's best movement and strength minds and a comprehensive exercise library. Try asking about what to train today, food suggestions, or how you're feeling. I'm learning from your daily logs to give you better advice over time."

    def get_weekly_plan(self) -> str:
        """Generate a comprehensive weekly training plan using RAG-powered mentor knowledge"""
        if not self.client:
            return "Weekly planning requires OpenAI connection. Please check your API key."
        try:
            patterns = self.analyze_patterns()
            recent_logs = self.logs[-7:] if self.logs else []
            for log in recent_logs:
                if 'recovery_score' not in log or log['recovery_score'] is None:
                    log['recovery_score'] = calculate_recovery_score(log)
                if 'training_volume' not in log or log['training_volume'] is None:
                    log['training_volume'] = calculate_training_volume(log)
            planning_context = get_weekly_planning_context()
            planning_prompt = f"""Create a detailed weekly training plan for Yoel that synthesizes the best approaches from our mentors:

PROFILE: {json.dumps(self.profile, indent=2)}
RECENT PATTERNS: {json.dumps(patterns, indent=2)}
CURRENT LOGS: {json.dumps(recent_logs, indent=2)}

RAG-POWERED MENTOR KNOWLEDGE:
{planning_context}

MENTOR KNOWLEDGE TO INCORPORATE:
- Dylan Werner: Isometric control, yoga principles, balance work
- Patrick Beach: Fluid movement, natural motion, mobility
- SquatU: Joint safety, injury prevention, shoulder rehab
- KneesOverToesGuy: Bulletproofing, longevity, knee health
- Everydamnandré: Simplicity, mental toughness, consistency
- Ido Portal: Movement complexity, adaptability, creativity
- Dr. Andy Galpin: Science-based optimization, recovery, nutrition

Create a 7-day plan that:
1. Blends Dylan Werner's isometric control with Patrick Beach's fluid movement
2. Incorporates SquatU's joint safety and KneesOverToesGuy's bulletproofing
3. Uses Everydamnandré's simplicity and mental toughness
4. Includes Ido Portal's movement complexity and adaptability
5. Focuses on Yoel's calisthenics and yoga preferences
6. Considers his shoulder issues and current energy levels
7. Provides specific exercises, sets, reps, and progression
8. Adapts to his recent patterns and recovery needs

Format as a clear, actionable weekly plan with daily breakdowns."""
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a master coach synthesizing the world's best training methods. Create specific, actionable weekly plans."},
                    {"role": "user", "content": planning_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            result = response.choices[0].message.content
            if not result:
                return "Error generating weekly plan"
            logger.info("✅ Generated RAG-powered comprehensive weekly plan")
            return result
        except Exception as e:
            logger.error(f"❌ Error generating weekly plan: {e}")
            return f"Error generating weekly plan: {e}" 