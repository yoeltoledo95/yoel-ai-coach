import os
import json
from typing import List, Dict, Any
from datetime import datetime
import openai
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.analysis import analyze_patterns
from coach_core.utils import detect_split

class AICoach:
    """Unified AI Coach agent for CLI and UI."""
    def __init__(self, profile_path: str = "yoel_profile.json", logs_path: str = "daily_logs.json"):
        self.profile_path = profile_path
        self.logs_path = logs_path
        self.profile = load_profile(profile_path)
        self.logs = load_logs(logs_path)
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.client = openai.OpenAI()

    def analyze_patterns(self) -> str:
        return analyze_patterns(self.logs)

    def get_ai_response(self, user_input: str) -> str:
        """Get intelligent response from GPT based on profile and logs."""
        if not self.client:
            return self.get_fallback_response(user_input)
        context = f"""
You are Yoel's personal AI fitness coach. You know him deeply and adapt to his needs.
PROFILE:
{json.dumps(self.profile, indent=2)}
RECENT PATTERNS:
{self.analyze_patterns()}
RECENT LOGS (last 3 days):
{json.dumps(self.logs[-3:], indent=2)}
INSTRUCTIONS:
- Be encouraging and motivating like a real coach
- Consider his injuries (shoulder issues, knee is fine now)
- Suggest training based on his goals (calisthenics, yoga, athletic)
- Recommend food based on his preferences and training
- Analyze patterns in his logs to give personalized advice
- Keep responses conversational and helpful
User says: {user_input}
Respond as Yoel's AI coach:
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Yoel's personal AI fitness coach. Be encouraging, knowledgeable, and personalized."},
                    {"role": "user", "content": context}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content or "I'm here to help with your training and nutrition!"
        except Exception as e:
            return self.get_fallback_response(user_input)

    def get_fallback_response(self, user_input: str) -> str:
        user_input = user_input.lower()
        if "tired" in user_input or "low energy" in user_input:
            return "I see you're feeling tired. Based on your goals, let's do some light mobility work and maybe some gentle yoga. No heavy training today - recovery is just as important as training! 💪"
        if "what should i train" in user_input or "workout" in user_input:
            return f"Looking at your {self.profile.get('training_preferences', {}).get('split', 'Push/Pull/Legs')} split, what day are you on? I can suggest specific exercises that work with your calisthenics and yoga preferences while being mindful of your shoulder."
        if "what should i eat" in user_input or "food" in user_input:
            return "For your goals and preferences, I'd suggest something with good protein and clean carbs. How about eggs with tahini and some vegetables? Or if you're post-workout, maybe some chicken with rice and fruit?"
        if "injury" in user_input or "pain" in user_input:
            return "I'm keeping an eye on your shoulder issues. Remember to do your band work and avoid exercises that cause pain. Your knee is doing well though - we can include more knee work gradually!"
        return "I'm here to help with your training, nutrition, and recovery! Try asking about what to train today, food suggestions, or how you're feeling. I'm learning from your daily logs to give you better advice over time." 