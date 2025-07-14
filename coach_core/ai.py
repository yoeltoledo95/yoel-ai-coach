print('AI module loaded')
import os
import json
from typing import List, Dict, Any
from datetime import datetime
import openai
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.analysis import analyze_patterns
from coach_core.utils import detect_split
from coach_core.mentor_brain import get_all_mentors_context, create_mentor_prompt, get_mentor_specialization

class AICoach:
    """Mentor-Powered AI Coach - Synthesizing the world's best minds in movement and strength."""
    def __init__(self):
        self.profile = load_profile()
        self.logs = load_logs()
        self.client = None
        self.mentors = get_all_mentors_context()
        
        # Initialize OpenAI client with proper configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                # Use minimal configuration to avoid proxy issues
                self.client = openai.OpenAI(
                    api_key=api_key,
                    # Don't pass any proxy or http_client settings
                )
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                self.client = None
        else:
            print("⚠️ No OPENAI_API_KEY found in environment variables")
            self.client = None

    def analyze_patterns(self) -> str:
        return analyze_patterns(self.logs)

    def get_mentor_powered_response(self, user_input: str) -> str:
        """Get intelligent response from GPT using mentor knowledge base."""
        if not self.client:
            print("⚠️ Using fallback response (no OpenAI client)")
            return self.get_fallback_response(user_input)
        
        # Create comprehensive mentor context
        mentor_context = self._create_mentor_context()
        
        # Build the system prompt with mentor knowledge
        system_prompt = f"""You are Yoel's personal AI fitness coach, trained by the world's greatest minds in movement, strength, and performance.

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

YOUR PERSONALITY:
- Wise and knowledgeable like Dr. Andy Galpin
- Encouraging and patient like Patrick Beach
- Direct and motivating like Everydamnandré
- Safety-focused like SquatU
- Longevity-minded like KneesOverToesGuy
- Movement-focused like Ido Portal

Always provide specific, actionable advice that combines the best insights from these mentors."""

        # Create user context with profile and logs
        user_context = f"""
YOEL'S PROFILE:
{json.dumps(self.profile, indent=2)}

RECENT PATTERNS:
{self.analyze_patterns()}

RECENT LOGS (last 3 days):
{json.dumps(self.logs[-3:], indent=2)}

YOEL'S QUESTION/REQUEST:
{user_input}

Respond as Yoel's mentor-powered AI coach, drawing from the wisdom of the world's best movement and strength minds:"""

        try:
            print("🤖 Sending request to OpenAI with mentor knowledge...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                max_tokens=500,
                temperature=0.8
            )
            result = response.choices[0].message.content or "I'm here to help with your training and nutrition!"
            print("✅ Received mentor-powered response from OpenAI")
            return result
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self.get_fallback_response(user_input)

    def _create_mentor_context(self) -> str:
        """Create comprehensive mentor context for the AI"""
        context_parts = []
        
        for mentor_id, mentor in self.mentors.items():
            context_parts.append(f"""
{mentor['name']} - {mentor['focus']}:
Philosophy: {mentor['core_philosophy']}
Key Principles: {', '.join(mentor['key_principles'][:3])}
Training Methods: {', '.join(mentor['training_methods'][:3])}
Motivational Style: {mentor['motivational_style']}
""")
        
        return "\n".join(context_parts)

    def get_ai_response(self, user_input: str) -> str:
        """Get intelligent response from GPT based on profile and logs."""
        return self.get_mentor_powered_response(user_input)

    def get_fallback_response(self, user_input: str) -> str:
        """Fallback responses when OpenAI is not available"""
        user_input = user_input.lower()
        
        # Enhanced fallback responses incorporating mentor wisdom
        if "tired" in user_input or "low energy" in user_input:
            return "I hear you're feeling tired. Let's take a page from Patrick Beach's book - movement should feel good and natural. Maybe some gentle mobility work or light yoga? And remember what Dylan Werner says: 'Control your body, control your mind.' Sometimes the best training is active recovery. 💪"
        
        if "what should i train" in user_input or "workout" in user_input:
            return f"Looking at your {self.profile.get('training_preferences', {}).get('split', 'Push/Pull/Legs')} split, what day are you on? I can suggest specific exercises that blend Dylan Werner's isometric control, SquatU's joint safety, and your calisthenics preferences while being mindful of your shoulder. What's your energy level today?"
        
        if "what should i eat" in user_input or "food" in user_input:
            return "For your goals and preferences, I'd suggest something with good protein and clean carbs - think Dr. Andy Galpin's science-based approach. How about eggs with tahini and some vegetables? Or if you're post-workout, maybe some chicken with rice and fruit? What's your current energy level?"
        
        if "injury" in user_input or "pain" in user_input:
            return "I'm keeping an eye on your shoulder issues - that's SquatU and KneesOverToesGuy territory. Remember to do your band work and avoid exercises that cause pain. Your knee is doing well though - we can include more knee work gradually! What specific movements are bothering you?"
        
        return "I'm here to help with your training, nutrition, and recovery! I draw from the wisdom of the world's best movement and strength minds. Try asking about what to train today, food suggestions, or how you're feeling. I'm learning from your daily logs to give you better advice over time."

    def get_weekly_plan(self) -> str:
        """Generate a weekly training plan using mentor knowledge"""
        if not self.client:
            return "Weekly planning requires OpenAI connection. Please check your API key."
        
        # Create a comprehensive weekly planning prompt
        planning_prompt = f"""Create a weekly training plan for Yoel that synthesizes the best approaches from our mentors:

PROFILE: {json.dumps(self.profile, indent=2)}
RECENT PATTERNS: {self.analyze_patterns()}
CURRENT LOGS: {json.dumps(self.logs[-7:], indent=2)}

Create a 7-day plan that:
1. Blends Dylan Werner's isometric control with Patrick Beach's fluid movement
2. Incorporates SquatU's joint safety and KneesOverToesGuy's bulletproofing
3. Uses Everydamnandré's simplicity and mental toughness
4. Includes Ido Portal's movement complexity and adaptability
5. Focuses on Yoel's calisthenics and yoga preferences
6. Considers his shoulder issues and current energy levels
7. Provides specific exercises, sets, reps, and progression

Format as a clear, actionable weekly plan."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a master coach synthesizing the world's best training methods. Create specific, actionable weekly plans."},
                    {"role": "user", "content": planning_prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content or "Error generating weekly plan"
        except Exception as e:
            return f"Error generating weekly plan: {e}" 