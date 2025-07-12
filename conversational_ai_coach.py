import json
import os
import re
from datetime import datetime
import openai
from typing import List, Dict, Any, Optional

class ConversationalAICoach:
    def __init__(self, profile_path="yoel_profile.json", logs_path="daily_logs.json"):
        self.profile_path = profile_path
        self.logs_path = logs_path
        self.profile = self.load_profile()
        self.logs = self.load_logs()
        self.conversation_history = []
        
        # Set up OpenAI
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
    
    def extract_training_info(self, user_input: str) -> Dict[str, Any]:
        """Extract training information from natural language"""
        if not self.client:
            return {}
        
        extraction_prompt = f"""
Extract training information from this user input. Return ONLY a JSON object with these fields:
- training_done: string (what training was done)
- energy: number 1-10 (energy level)
- mood: string (mood description)
- soreness: string (sore muscles, comma-separated, or "none")
- sleep_hours: number (hours slept)
- nutrition: string (what was eaten)
- notes: string (any additional notes)

User input: "{user_input}"

Return only the JSON object, no other text:
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a fitness data extraction tool. Return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            if content:
                extracted_data = json.loads(content.strip())
            else:
                return {}
            
            # Add timestamp and date
            extracted_data["date"] = datetime.now().strftime("%Y-%m-%d")
            extracted_data["timestamp"] = datetime.now().isoformat()
            
            return extracted_data
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return {}
    
    def should_auto_log(self, user_input: str) -> bool:
        """Determine if the input should trigger auto-logging"""
        # Keywords that indicate training/activity logging
        training_keywords = [
            "train", "workout", "exercise", "push", "pull", "legs", "yoga",
            "did", "completed", "finished", "worked out", "lifted", "ran",
            "energy", "tired", "sore", "mood", "slept", "ate", "nutrition"
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in training_keywords)
    
    def auto_log_conversation(self, user_input: str, ai_response: str):
        """Automatically log conversation data"""
        if not self.should_auto_log(user_input):
            return
        
        # Extract training info
        extracted_data = self.extract_training_info(user_input)
        if not extracted_data:
            return
        
        # Check if we already have a log for today
        today = datetime.now().strftime("%Y-%m-%d")
        existing_log = next((log for log in self.logs if log.get("date") == today), None)
        
        if existing_log:
            # Update existing log with new information
            for key, value in extracted_data.items():
                if key not in ["date", "timestamp"] and value:
                    existing_log[key] = value
        else:
            # Create new log entry
            self.logs.append(extracted_data)
        
        # Save to file
        self.save_logs()
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "extracted_data": extracted_data
        })
    
    def get_contextual_response(self, user_input: str) -> str:
        """Get AI response with conversation context"""
        if not self.client:
            return self.get_fallback_response(user_input)
        
        # Build rich context
        context = f"""
You are Yoel's personal AI fitness coach. You have a deep understanding of his training patterns and preferences.

PROFILE:
{json.dumps(self.profile, indent=2)}

RECENT CONVERSATIONS (last 5):
{json.dumps(self.conversation_history[-5:], indent=2)}

RECENT LOGS (last 3 days):
{json.dumps(self.logs[-3:], indent=2)}

PATTERNS ANALYSIS:
{self.analyze_patterns()}

INSTRUCTIONS:
- Be conversational and encouraging
- If the user mentions training/activity, acknowledge it and provide insights
- Consider his injuries (shoulder issues, knee is fine)
- Suggest next steps based on his goals (calisthenics, yoga, athletic)
- Keep responses natural and helpful
- If they're logging activity, confirm what you understood

User says: "{user_input}"

Respond as Yoel's AI coach:
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Yoel's personal AI fitness coach. Be conversational, encouraging, and knowledgeable."},
                    {"role": "user", "content": context}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content or "I'm here to help with your training and nutrition!"
        except Exception as e:
            print(f"AI Error: {e}")
            return self.get_fallback_response(user_input)
    
    def analyze_patterns(self) -> str:
        """Analyze patterns in user's logs"""
        if not self.logs:
            return "No training history available yet."
        
        recent_logs = self.logs[-7:]
        
        energy_trend = []
        training_frequency = 0
        common_soreness = []
        
        for log in recent_logs:
            if 'energy' in log and str(log['energy']).isdigit():
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
    
    def get_fallback_response(self, user_input: str) -> str:
        """Fallback responses when AI is not available"""
        user_input = user_input.lower()
        
        if "tired" in user_input or "low energy" in user_input:
            return "I see you're feeling tired. Based on your goals, let's do some light mobility work and maybe some gentle yoga. No heavy training today - recovery is just as important as training! 💪"
        
        if "what should i train" in user_input or "workout" in user_input:
            return f"Looking at your {self.profile.get('training_preferences', {}).get('split', 'Push/Pull/Legs')} split, what day are you on? I can suggest specific exercises that work with your calisthenics and yoga preferences while being mindful of your shoulder."
        
        if "what should i eat" in user_input or "food" in user_input:
            return "For your goals and preferences, I'd suggest something with good protein and clean carbs. How about eggs with tahini and some vegetables? Or if you're post-workout, maybe some chicken with rice and fruit?"
        
        return "I'm here to help with your training, nutrition, and recovery! Just tell me about your day and I'll help track your progress."
    
    def run(self):
        """Main conversational interface"""
        print(f"Welcome back, {self.profile.get('name', 'Yoel')} 👋")
        print("Your Conversational AI Coach is ready!")
        print("Just tell me about your day - I'll understand and log everything automatically!")
        
        if self.logs:
            print(f"📊 I've analyzed {len(self.logs)} days of your training data.")
        
        print("\n💬 Just chat naturally - I'll extract and log your training info automatically!")
        print("Commands:")
        print("- Type anything to chat (I'll auto-log training info)")
        print("- 'patterns' to see your recent trends")
        print("- 'status' to see what I've logged today")
        print("- 'exit' to quit")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Keep up the great work! See you tomorrow 💪")
                break
            
            if user_input.lower() == "patterns":
                print(f"\n📈 Your Recent Patterns:\n{self.analyze_patterns()}")
                continue
            
            if user_input.lower() == "status":
                today = datetime.now().strftime("%Y-%m-%d")
                today_log = next((log for log in self.logs if log.get("date") == today), None)
                if today_log:
                    print(f"\n📊 Today's Log ({today}):")
                    for key, value in today_log.items():
                        if key not in ["date", "timestamp"] and value:
                            print(f"  {key}: {value}")
                else:
                    print(f"\n📊 No log yet for {today}")
                continue
            
            # Get AI response
            ai_response = self.get_contextual_response(user_input)
            print(f"\nAI Coach: {ai_response}")
            
            # Auto-log if it's training-related
            self.auto_log_conversation(user_input, ai_response)

if __name__ == "__main__":
    coach = ConversationalAICoach()
    coach.run() 