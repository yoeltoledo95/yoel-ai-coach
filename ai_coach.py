import json
import os
from datetime import datetime
import openai
from typing import List, Dict, Any

class AICoach:
    def __init__(self, profile_path="yoel_profile.json", logs_path="log_entry.json"):
        self.profile_path = profile_path
        self.logs_path = logs_path
        self.profile = self.load_profile()
        self.logs = self.load_logs()
        
        # Set up OpenAI (you'll need to add your API key)
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.client = openai.OpenAI()
    
    def load_profile(self) -> Dict[str, Any]:
        """Load user profile from JSON file"""
        try:
            with open(self.profile_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Profile file {self.profile_path} not found!")
            return {}
    
    def load_logs(self) -> List[Dict[str, Any]]:
        """Load daily logs from JSON file"""
        try:
            with open(self.logs_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_logs(self):
        """Save logs back to file"""
        with open(self.logs_path, "w") as f:
            json.dump(self.logs, f, indent=2)
    
    def analyze_patterns(self) -> str:
        """Analyze patterns in user's logs for AI context"""
        if not self.logs:
            return "No training history available yet."
        
        # Analyze recent patterns
        recent_logs = self.logs[-7:]  # Last 7 days
        
        energy_trend = []
        training_frequency = 0
        common_soreness = []
        
        for log in recent_logs:
            if 'energy' in log and log['energy'].isdigit():
                energy_trend.append(int(log['energy']))
            if log.get('training_done') and log['training_done'].strip():
                training_frequency += 1
            if log.get('soreness') and log['soreness'] != 'none':
                common_soreness.append(log['soreness'])
        
        analysis = f"Recent Analysis:\n"
        if energy_trend:
            avg_energy = sum(energy_trend) / len(energy_trend)
            analysis += f"- Average energy: {avg_energy:.1f}/10\n"
        analysis += f"- Training frequency: {training_frequency} days in last week\n"
        
        if common_soreness:
            analysis += f"- Common soreness: {', '.join(set(common_soreness))}\n"
        
        return analysis
    
    def get_ai_response(self, user_input: str) -> str:
        """Get intelligent response from GPT based on profile and logs"""
        if not self.client:
            return self.get_fallback_response(user_input)
        
        # Build context for AI
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
            print(f"AI Error: {e}")
            return self.get_fallback_response(user_input)
    
    def get_fallback_response(self, user_input: str) -> str:
        """Fallback responses when AI is not available"""
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
    
    def log_daily_feedback(self):
        """Enhanced daily logging with AI insights"""
        print("\n🔁 Daily Feedback Log:")
        print("Let's track your day and I'll give you insights!")
        
        mood = input("Mood today (e.g. good, low, energized, anxious): ").strip()
        energy = input("Energy level (1-10): ").strip()
        soreness = input("Sore muscles today (comma-separated, or 'none'): ").strip()
        sleep = input("How many hours did you sleep? ").strip()
        training_done = input("What training did you do today? ").strip()
        notes = input("Any extra notes? ").strip()
        
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "mood": mood,
            "energy": energy,
            "soreness": soreness,
            "sleep_hours": sleep,
            "training_done": training_done,
            "notes": notes
        }
        
        self.logs.append(entry)
        self.save_logs()
        
        # Give AI insights on the log
        print("\n🤖 AI Analysis:")
        if self.client:
            insight_prompt = f"Based on this log entry: {json.dumps(entry)}, and considering Yoel's profile and previous patterns, give a brief insight or suggestion for tomorrow."
            try:
                insight = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are Yoel's AI coach. Give brief, helpful insights."},
                        {"role": "user", "content": insight_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                print(insight.choices[0].message.content)
            except:
                print("✅ Log saved! I'm learning from your patterns.")
        else:
            print("✅ Log saved! I'm learning from your patterns.")
    
    def run(self):
        """Main interaction loop"""
        print(f"Welcome back, {self.profile.get('name', 'Yoel')} 👋")
        print("Your AI Coach is ready to help!")
        
        if self.logs:
            print(f"📊 I've analyzed {len(self.logs)} days of your training data.")
        
        print("\nCommands:")
        print("- Type anything to chat with your AI coach")
        print("- 'log' to record your day")
        print("- 'patterns' to see your recent trends")
        print("- 'exit' to quit")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Keep up the great work! See you tomorrow 💪")
                break
            elif user_input.lower() == "log":
                self.log_daily_feedback()
            elif user_input.lower() == "patterns":
                print("\n📈 Your Recent Patterns:")
                print(self.analyze_patterns())
            else:
                response = self.get_ai_response(user_input)
                print(f"\nAI Coach: {response}")

if __name__ == "__main__":
    coach = AICoach()
    coach.run() 