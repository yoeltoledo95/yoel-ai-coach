import json
from datetime import datetime, timedelta
import os
from collections import defaultdict
import statistics

# Load your profile
def load_profile(path="yoel_profile.json"):
    with open(path, "r") as f:
        return json.load(f)

# Load daily logs
def load_logs(path="daily_logs.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Save logs
def save_logs(logs, path="daily_logs.json"):
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

# Detect training split from description
def detect_split(training_done):
    t = training_done.lower()
    if "push" in t:
        return "Push"
    elif "pull" in t:
        return "Pull"
    elif "leg" in t or "squat" in t or "deadlift" in t:
        return "Legs"
    elif "mobility" in t or "recovery" in t or "rest" in t:
        return "Recovery"
    elif t.strip() in ["", "none", "no", "rest"]:
        return "None"
    else:
        return "Other"

# Enhanced daily feedback logging
def log_daily_feedback():
    logs = load_logs()
    
    print("\n" + "="*50)
    print("📊 ENHANCED DAILY FEEDBACK")
    print("="*50)
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if already logged today
    existing_entry = next((log for log in logs if log.get("date") == today), None)
    if existing_entry:
        print(f"⚠️  You already logged today ({today}). Update existing entry? (y/n): ", end="")
        if input().lower() != 'y':
            return
        logs.remove(existing_entry)
    
    # Enhanced data collection
    entry = {
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "mood": input("😊 Mood today (1-10, or describe): ").strip(),
        "energy": input("⚡ Energy level (1-10): ").strip(),
        "sleep_hours": input("😴 Hours slept: ").strip(),
        "sleep_quality": input("🌙 Sleep quality (1-10): ").strip(),
        "stress_level": input("😰 Stress level (1-10): ").strip(),
        "soreness": input("💪 Sore muscles (comma-separated, or 'none'): ").strip(),
        "training_done": input("🏋️ Training completed: ").strip(),
        "training_quality": input("⭐ Training quality (1-10): ").strip(),
        "nutrition": input("🍽️ What did you eat today? ").strip(),
        "hydration": input("💧 Hydration level (1-10): ").strip(),
        "notes": input("📝 Additional notes: ").strip()
    }
    
    # Add calculated metrics
    entry["recovery_score"] = str(calculate_recovery_score(entry))
    entry["training_volume"] = estimate_training_volume(entry["training_done"])
    entry["split"] = detect_split(entry["training_done"])
    
    logs.append(entry)
    save_logs(logs)
    
    print(f"\n✅ Enhanced log saved for {today}")
    print(f"📈 Recovery Score: {entry['recovery_score']}/10")
    
    # Show recent trends
    show_recent_trends(logs)

# Calculate recovery score based on multiple factors
def calculate_recovery_score(entry):
    try:
        energy = float(entry.get("energy", 5))
        sleep_hours = float(entry.get("sleep_hours", 7))
        sleep_quality = float(entry.get("sleep_quality", 5))
        stress = float(entry.get("stress_level", 5))
        soreness = entry.get("soreness", "").lower()
        
        # Base score from energy and sleep
        score = (energy + sleep_quality) / 2
        
        # Sleep duration bonus/penalty
        if sleep_hours >= 7.5:
            score += 1
        elif sleep_hours < 6:
            score -= 1
        
        # Stress penalty
        if stress > 7:
            score -= 0.5
        
        # Soreness penalty
        if soreness != "none" and soreness:
            score -= 0.5
        
        return max(1, min(10, round(score, 1)))
    except:
        return 5.0

# Estimate training volume from description
def estimate_training_volume(training_done):
    training = training_done.lower()
    if any(word in training for word in ["heavy", "max", "intense", "failure"]):
        return "high"
    elif any(word in training for word in ["light", "mobility", "recovery", "walk"]):
        return "low"
    elif any(word in training for word in ["moderate", "medium", "normal"]):
        return "medium"
    else:
        return "unknown"

# Progressive overload tracking
def analyze_progression(logs, days=14):
    if len(logs) < 3:
        return None
    
    recent_logs = logs[-days:]
    progression_data = {
        "volume_trend": "stable",
        "quality_trend": "stable", 
        "recovery_trend": "stable",
        "suggestions": []
    }
    
    # Analyze training quality trend
    qualities = [float(log.get("training_quality", 5)) for log in recent_logs if log.get("training_quality")]
    if len(qualities) >= 3:
        recent_avg = statistics.mean(qualities[-3:])
        earlier_avg = statistics.mean(qualities[:-3]) if len(qualities) > 3 else qualities[0]
        if recent_avg > earlier_avg + 1:
            progression_data["quality_trend"] = "improving"
        elif recent_avg < earlier_avg - 1:
            progression_data["quality_trend"] = "declining"
    
    # Analyze volume trend
    volumes = [log.get("training_volume") for log in recent_logs if log.get("training_volume") != "unknown"]
    if len(volumes) >= 3:
        high_volume_days = sum(1 for v in volumes if v == "high")
        if high_volume_days >= len(volumes) * 0.7:
            progression_data["volume_trend"] = "high"
        elif high_volume_days <= len(volumes) * 0.3:
            progression_data["volume_trend"] = "low"
    
    # Analyze recovery trend
    recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
    if len(recovery_scores) >= 3:
        recent_recovery = statistics.mean(recovery_scores[-3:])
        if recent_recovery < 6:
            progression_data["recovery_trend"] = "poor"
            progression_data["suggestions"].append("Consider a deload week or more recovery time")
        elif recent_recovery > 8:
            progression_data["recovery_trend"] = "excellent"
            progression_data["suggestions"].append("Great recovery! You can push harder")
    
    # Generate suggestions
    if progression_data["quality_trend"] == "declining":
        progression_data["suggestions"].append("Training quality is declining - consider deload or technique focus")
    elif progression_data["volume_trend"] == "high" and progression_data["recovery_trend"] == "poor":
        progression_data["suggestions"].append("High volume with poor recovery - reduce volume or increase rest")
    elif progression_data["volume_trend"] == "low" and progression_data["recovery_trend"] == "excellent":
        progression_data["suggestions"].append("Good recovery with low volume - time to increase intensity")
    
    return progression_data

# Nutrition learning and suggestions
def analyze_nutrition_patterns(logs, days=7):
    if len(logs) < 2:
        return None
    
    recent_logs = logs[-days:]
    nutrition_data = {
        "common_foods": defaultdict(int),
        "energy_food_patterns": {"high_energy": [], "low_energy": []},
        "suggestions": []
    }
    
    for log in recent_logs:
        nutrition = log.get("nutrition", "").lower()
        energy = float(log.get("energy", 5))
        
        # Track common foods
        foods = [f.strip() for f in nutrition.split(",") if f.strip()]
        for food in foods:
            nutrition_data["common_foods"][food] += 1
        
        # Track energy-food patterns
        if energy >= 7:
            nutrition_data["energy_food_patterns"]["high_energy"].append(nutrition)
        elif energy <= 4:
            nutrition_data["energy_food_patterns"]["low_energy"].append(nutrition)
    
    # Generate nutrition suggestions
    top_foods = sorted(nutrition_data["common_foods"].items(), key=lambda x: x[1], reverse=True)[:5]
    if top_foods:
        nutrition_data["suggestions"].append(f"Your most common foods: {', '.join([f[0] for f in top_foods[:3]])}")
    
    if nutrition_data["energy_food_patterns"]["high_energy"]:
        high_energy_foods = set()
        for meal in nutrition_data["energy_food_patterns"]["high_energy"]:
            high_energy_foods.update([f.strip() for f in meal.split(",") if f.strip()])
        nutrition_data["suggestions"].append(f"Foods you eat on high-energy days: {', '.join(list(high_energy_foods)[:3])}")
    
    return nutrition_data

# Weekly summary generation
def generate_weekly_summary(logs):
    if len(logs) < 3:
        return "Not enough data for weekly summary yet."
    
    week_logs = logs[-7:]
    summary = {
        "total_days": len(week_logs),
        "training_days": sum(1 for log in week_logs if log.get("training_done") and log.get("training_done").lower() != "none"),
        "avg_energy": statistics.mean([float(log.get("energy", 5)) for log in week_logs if log.get("energy")]),
        "avg_recovery": statistics.mean([float(log.get("recovery_score", 5)) for log in week_logs if log.get("recovery_score")]),
        "avg_sleep": statistics.mean([float(log.get("sleep_hours", 7)) for log in week_logs if log.get("sleep_hours")]),
        "best_day": max(week_logs, key=lambda x: float(x.get("energy", 0))),
        "worst_day": min(week_logs, key=lambda x: float(x.get("energy", 10))),
        "split_counts": defaultdict(int)
    }
    
    for log in week_logs:
        split = log.get("split") or detect_split(log.get("training_done", ""))
        summary["split_counts"][split] += 1
    
    return summary

# Weekly split summary and progression/plateau detection
def show_weekly_split_summary(logs, days=7):
    if not logs:
        print("No logs to analyze.")
        return
    recent_logs = logs[-days:]
    split_counts = {"Push": 0, "Pull": 0, "Legs": 0, "Recovery": 0, "Other": 0, "None": 0}
    for log in recent_logs:
        split = log.get("split") or detect_split(log.get("training_done", ""))
        if split in split_counts:
            split_counts[split] += 1
        else:
            split_counts["Other"] += 1
    print("\n🗓️ Weekly Split Summary:")
    for split, count in split_counts.items():
        if count > 0:
            print(f"  {split}: {count} day(s)")
    # Imbalance detection
    main_splits = [split_counts["Push"], split_counts["Pull"], split_counts["Legs"]]
    if max(main_splits) - min(main_splits) > 1:
        print("⚠️  Imbalance detected: Consider balancing your Push/Pull/Legs days.")
    # Plateau detection
    volumes = [log.get("training_volume", "unknown") for log in recent_logs if log.get("training_volume") != "unknown"]
    qualities = [float(log.get("training_quality", 0)) for log in recent_logs if log.get("training_quality")]
    if volumes and all(v == volumes[0] for v in volumes) and len(volumes) > 2:
        print("⚠️  Plateau detected: Training volume hasn't changed recently.")
    if qualities and statistics.mean(qualities) < 6:
        print("⚠️  Training quality is low. Consider a deload or more recovery.")
    
    # Progression analysis
    progression = analyze_progression(logs, days)
    if progression and progression["suggestions"]:
        print("\n📈 Progression Analysis:")
        for suggestion in progression["suggestions"]:
            print(f"  💡 {suggestion}")

# Analyze and show recent trends
def show_recent_trends(logs, days=7):
    if len(logs) < 2:
        return
    
    recent_logs = logs[-days:]
    
    print(f"\n📊 TRENDS (Last {len(recent_logs)} days):")
    print("-" * 30)
    
    # Energy trends
    energies = [float(log.get("energy", 5)) for log in recent_logs if log.get("energy")]
    if energies:
        avg_energy = statistics.mean(energies)
        print(f"⚡ Average Energy: {avg_energy:.1f}/10")
        if avg_energy < 6:
            print("   💡 Consider lighter training or more recovery")
    
    # Sleep trends
    sleep_hours = [float(log.get("sleep_hours", 7)) for log in recent_logs if log.get("sleep_hours")]
    if sleep_hours:
        avg_sleep = statistics.mean(sleep_hours)
        print(f"😴 Average Sleep: {avg_sleep:.1f} hours")
        if avg_sleep < 7:
            print("   💤 Sleep optimization needed")
    
    # Recovery trends
    recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
    if recovery_scores:
        avg_recovery = statistics.mean(recovery_scores)
        print(f"🔄 Average Recovery: {avg_recovery:.1f}/10")
    
    # Training frequency
    training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
    print(f"🏋️ Training Days: {training_days}/{len(recent_logs)}")
    show_weekly_split_summary(logs, days)

# Enhanced response logic using logged data
def get_smart_response(user_input, profile, logs):
    user_input = user_input.lower()
    
    # Get recent data for context
    recent_logs = logs[-3:] if logs else []
    today_log = logs[-1] if logs else None
    
    if "tired" in user_input or "low energy" in user_input:
        if today_log and float(today_log.get("energy", 5)) < 6:
            return f"Based on your energy ({today_log.get('energy')}/10), let's keep it light: mobility work, band activation, maybe a short calisthenics circuit?"
        return "Let's keep it light today: mobility work, band activation, maybe a short calisthenics circuit?"
    
    if "what should i train" in user_input:
        # Analyze weekly split
        week_logs = logs[-7:] if logs else []
        split_counts = {"Push": 0, "Pull": 0, "Legs": 0}
        for log in week_logs:
            split = log.get("split") or detect_split(log.get("training_done", ""))
            if split in split_counts:
                split_counts[split] += 1
        # Suggest undertrained split
        splits = list(split_counts.items())
        min_split = min(splits, key=lambda x: x[1])[0]
        max_split = max(splits, key=lambda x: x[1])[0]
        if split_counts[min_split] < split_counts[max_split]:
            return f"You've done more {max_split} days recently. How about a {min_split} day to balance things out?"
        # Fallback to previous logic
        if recent_logs:
            recent_training = [log.get("training_done", "") for log in recent_logs]
            if any("push" in t.lower() for t in recent_training):
                return "You've been doing push work recently. How about a Pull day with rows, pull-ups, and some band work for your shoulder?"
            elif any("pull" in t.lower() for t in recent_training):
                return "Time for some Push work! Focus on dips, push-ups, and shoulder-friendly variations (no overhead barbell)."
            else:
                return "Based on your goals, a Push day with shoulder-friendly variations would be solid. Want some exercise ideas?"
        return "Based on your goals, a Push day with shoulder-friendly variations (no overhead barbell) would be solid. Want some exercise ideas?"

    if "what should i eat" in user_input:
        # Use nutrition analysis for smarter suggestions
        nutrition_data = analyze_nutrition_patterns(logs)
        if nutrition_data and nutrition_data["suggestions"]:
            return f"Based on your patterns: {nutrition_data['suggestions'][0]}. How about trying that today?"
        
        if today_log:
            energy = float(today_log.get("energy", 5))
            if energy < 6:
                return "Since you're low on energy, how about a protein-rich meal: eggs, tahini, vegetables, and some sourdough? Simple, high-protein, and clean."
            else:
                return "You've got good energy! How about a balanced meal: chicken, rice, vegetables, and some healthy fats?"
        return "How about eggs, tahini, vegetables, and some sourdough? Simple, high-protein, and clean."

    if "injury" in user_input:
        return f"Reminder: Be mindful of your shoulder ({profile['injuries']['shoulder']}). Knees are okay now, so we can include deep knee flexion work."

    if "how am i doing" in user_input or "progress" in user_input:
        if recent_logs:
            avg_energy = statistics.mean([float(log.get("energy", 5)) for log in recent_logs if log.get("energy")])
            avg_recovery = statistics.mean([float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")])
            return f"Looking at your recent data: Average energy {avg_energy:.1f}/10, recovery {avg_recovery:.1f}/10. {'Keep it up!' if avg_energy > 6 else 'Consider more recovery time.'}"
        return "I'm still learning about your patterns. Log your daily feedback to get personalized insights!"

    if "trends" in user_input or "stats" in user_input:
        show_recent_trends(logs)
        return ""

    if "weekly summary" in user_input or "week summary" in user_input:
        summary = generate_weekly_summary(logs)
        if isinstance(summary, dict):
            print(f"\n📅 WEEKLY SUMMARY:")
            print(f"Training Days: {summary['training_days']}/{summary['total_days']}")
            print(f"Average Energy: {summary['avg_energy']:.1f}/10")
            print(f"Average Recovery: {summary['avg_recovery']:.1f}/10")
            print(f"Average Sleep: {summary['avg_sleep']:.1f} hours")
            print(f"Best Day: {summary['best_day']['date']} (Energy: {summary['best_day']['energy']}/10)")
            print(f"Worst Day: {summary['worst_day']['date']} (Energy: {summary['worst_day']['energy']}/10)")
            print("Split Distribution:")
            for split, count in summary['split_counts'].items():
                if count > 0:
                    print(f"  {split}: {count} day(s)")
        else:
            print(summary)
        return ""

    if "progression" in user_input or "plateau" in user_input:
        progression = analyze_progression(logs)
        if progression:
            print(f"\n📈 PROGRESSION ANALYSIS:")
            print(f"Volume Trend: {progression['volume_trend']}")
            print(f"Quality Trend: {progression['quality_trend']}")
            print(f"Recovery Trend: {progression['recovery_trend']}")
            if progression['suggestions']:
                print("Suggestions:")
                for suggestion in progression['suggestions']:
                    print(f"  💡 {suggestion}")
        else:
            print("Not enough data for progression analysis yet.")
        return ""

    return "I'm still learning — try asking about food, training, recovery, trends, weekly summary, or progression!"

# Generate a smart greeting based on profile and recent data
def greet_user_smart(profile, logs):
    print(f"Welcome back, {profile['name']} 👋")
    print(f"You're training {profile['training_preferences']['days_per_week']} days/week with a {profile['training_preferences']['split']} split.")
    
    if logs:
        today_log = logs[-1]
        if today_log.get("date") == datetime.now().strftime("%Y-%m-%d"):
            energy = today_log.get("energy", "unknown")
            recovery = today_log.get("recovery_score", "unknown")
            print(f"📊 Today's data: Energy {energy}/10, Recovery {recovery}/10")
        else:
            print("💡 Don't forget to log today's feedback!")
    
    print(f"🎯 Today's focus: boosting energy + building muscle.\n")

# Main loop
def main():
    profile = load_profile()
    logs = load_logs()
    
    greet_user_smart(profile, logs)

    print("Available commands:")
    print("- 'I'm tired' / 'low energy'")
    print("- 'What should I train today?'")
    print("- 'What should I eat?'")
    print("- 'How am I doing?' / 'progress'")
    print("- 'trends' / 'stats'")
    print("- 'weekly summary' / 'week summary'")
    print("- 'progression' / 'plateau'")
    print("- 'log' to record your day")
    print("- 'exit' to quit")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("See you tomorrow 💪")
            break
        elif user_input.lower() == "log":
            log_daily_feedback()
            logs = load_logs()  # Reload logs after logging
        else:
            response = get_smart_response(user_input, profile, logs)
            if response:  # Only print if there's a response
                print(f"AI Coach: {response}")

if __name__ == "__main__":
    main()
