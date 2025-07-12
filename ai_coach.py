import json
from datetime import datetime
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.ai import AICoach

def log_daily_feedback(ai_coach):
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
    
    ai_coach.logs.append(entry)
    save_logs(ai_coach.logs)
    
    # Give AI insights on the log
    print("\n🤖 AI Analysis:")
    if ai_coach.client:
        insight_prompt = f"Based on this log entry: {json.dumps(entry)}, and considering Yoel's profile and previous patterns, give a brief insight or suggestion for tomorrow."
        try:
            insight = ai_coach.client.chat.completions.create(
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

def run():
    """Main interaction loop"""
    ai_coach = AICoach()
    
    print(f"Welcome back, {ai_coach.profile.get('name', 'Yoel')} 👋")
    print("Your AI Coach is ready to help!")
    
    if ai_coach.logs:
        print(f"📊 I've analyzed {len(ai_coach.logs)} days of your training data.")
    
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
        
        if user_input.lower() == "log":
            log_daily_feedback(ai_coach)
            continue
        
        if user_input.lower() == "patterns":
            print(f"\n📈 Your Recent Patterns:\n{ai_coach.analyze_patterns()}")
            continue
        
        # Get AI response
        response = ai_coach.get_ai_response(user_input)
        print(f"\nAI Coach: {response}")

if __name__ == "__main__":
    run() 