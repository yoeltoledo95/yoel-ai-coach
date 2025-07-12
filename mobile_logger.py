import streamlit as st
import json
from datetime import datetime, timedelta
import os
from collections import defaultdict
import statistics
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page config for mobile
st.set_page_config(
    page_title="Yoel's AI Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load your profile
def load_profile(path="yoel_profile.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

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

# Calculate recovery score
def calculate_recovery_score(entry):
    try:
        energy = float(entry.get("energy", 5))
        sleep_hours = float(entry.get("sleep_hours", 7))
        sleep_quality = float(entry.get("sleep_quality", 5))
        stress = float(entry.get("stress_level", 5))
        soreness = entry.get("soreness", "").lower()
        
        score = (energy + sleep_quality) / 2
        
        if sleep_hours >= 7.5:
            score += 1
        elif sleep_hours < 6:
            score -= 1
        
        if stress > 7:
            score -= 0.5
        
        if soreness != "none" and soreness:
            score -= 0.5
        
        return max(1, min(10, round(score, 1)))
    except:
        return 5.0

# Estimate training volume
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

# Check if logged today
def check_logged_today(logs):
    today = datetime.now().strftime("%Y-%m-%d")
    return any(log.get("date") == today for log in logs)

# Get yesterday's values as defaults
def get_yesterday_defaults(logs):
    if not logs:
        return {}
    
    yesterday = logs[-1]
    return {
        "mood": yesterday.get("mood", ""),
        "energy": yesterday.get("energy", ""),
        "sleep_hours": yesterday.get("sleep_hours", ""),
        "sleep_quality": yesterday.get("sleep_quality", ""),
        "stress_level": yesterday.get("stress_level", ""),
        "soreness": yesterday.get("soreness", ""),
        "training_done": yesterday.get("training_done", ""),
        "training_quality": yesterday.get("training_quality", ""),
        "nutrition": yesterday.get("nutrition", ""),
        "hydration": yesterday.get("hydration", ""),
        "notes": yesterday.get("notes", "")
    }

# Quick log function
def quick_log(logs, preset):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Remove existing entry for today
    logs = [log for log in logs if log.get("date") != today]
    
    if preset == "Great Day":
        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "mood": "8",
            "energy": "8",
            "sleep_hours": "8.0",
            "sleep_quality": "8",
            "stress_level": "3",
            "soreness": "none",
            "training_done": "Push Day - Moderate",
            "training_quality": "8",
            "nutrition": "eggs, oatmeal, chicken, vegetables",
            "hydration": "8",
            "notes": "Feeling great today!",
            "recovery_score": "8.0",
            "training_volume": "medium",
            "split": "Push"
        }
    elif preset == "Recovery Day":
        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "mood": "6",
            "energy": "5",
            "sleep_hours": "7.0",
            "sleep_quality": "6",
            "stress_level": "5",
            "soreness": "shoulders, chest",
            "training_done": "Mobility/Recovery",
            "training_quality": "6",
            "nutrition": "light meals, lots of water",
            "hydration": "7",
            "notes": "Recovery day needed",
            "recovery_score": "5.5",
            "training_volume": "low",
            "split": "Recovery"
        }
    elif preset == "Rest Day":
        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "mood": "7",
            "energy": "6",
            "sleep_hours": "8.0",
            "sleep_quality": "7",
            "stress_level": "4",
            "soreness": "none",
            "training_done": "None/Rest Day",
            "training_quality": "5",
            "nutrition": "normal meals",
            "hydration": "7",
            "notes": "Rest day",
            "recovery_score": "7.0",
            "training_volume": "low",
            "split": "None"
        }
    
    logs.append(entry)
    save_logs(logs)
    return entry

# Enhanced AI response function
def get_enhanced_response(user_input, profile, logs):
    user_input = user_input.lower()
    
    # Get recent context
    recent_logs = logs[-3:] if logs else []
    recent_energy = [float(log.get("energy", 5)) for log in recent_logs if log.get("energy")]
    recent_recovery = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
    
    avg_energy = statistics.mean(recent_energy) if recent_energy else 5
    avg_recovery = statistics.mean(recent_recovery) if recent_recovery else 5
    
    # Training suggestions based on recent patterns
    if "train" in user_input or "workout" in user_input:
        if recent_logs:
            recent_training = [log.get("training_done", "") for log in recent_logs]
            recent_splits = [log.get("split", "") for log in recent_logs]
            
            # Check for imbalances
            push_count = sum(1 for split in recent_splits if "Push" in split)
            pull_count = sum(1 for split in recent_splits if "Pull" in split)
            legs_count = sum(1 for split in recent_splits if "Legs" in split)
            
            if avg_energy < 6 or avg_recovery < 6:
                return "💡 You've been feeling low energy lately. I suggest a light mobility session or yoga. Focus on recovery and maybe some band work for shoulder health."
            elif push_count > pull_count:
                return "💪 You've been doing more push work. Time for a Pull day! Try: rows, pull-ups, band pull-aparts, and some rear delt work for shoulder balance."
            elif pull_count > push_count:
                return "💪 You've been doing more pull work. Time for a Push day! Focus on dips, push-ups, and shoulder-friendly pressing movements."
            elif legs_count < 1:
                return "🦵 You haven't trained legs recently. How about a Legs day? Squats, lunges, and some knee-over-toes work for your goals."
            else:
                return "🎯 You're in a good rhythm! Based on your goals, I'd suggest a Push day with focus on handstand progressions and shoulder strength."
        else:
            return "💪 Great to start training! Based on your goals, let's begin with a Push day. Focus on dips, push-ups, and shoulder-friendly movements."
    
    elif "eat" in user_input or "nutrition" in user_input:
        if profile and profile.get("diet"):
            diet_style = profile["diet"].get("style", "minimal processed foods")
            if "intermittent" in diet_style.lower() or profile["diet"].get("intermittent_fasting"):
                return "🍽️ For your IF schedule, try: eggs with tahini, chicken with vegetables, and some healthy fats. Keep it simple and clean!"
            else:
                return "🍽️ Based on your preferences: eggs, chicken, vegetables, tahini, and some quality carbs. Simple, high-protein, and clean!"
        return "🍽️ How about eggs, tahini, vegetables, and some sourdough? Simple, high-protein, and clean."
    
    elif "tired" in user_input or "energy" in user_input or "recovery" in user_input:
        if avg_energy < 6:
            return "😴 You've been feeling low energy. Let's prioritize recovery: more sleep, light mobility work, and maybe a rest day. Your body needs it!"
        else:
            return "⚡ Your energy has been good! Keep up the momentum with your training. Maybe try a moderate intensity session today."
    
    elif "sleep" in user_input:
        recent_sleep = [float(log.get("sleep_hours", 7)) for log in recent_logs if log.get("sleep_hours")]
        avg_sleep = statistics.mean(recent_sleep) if recent_sleep else 7
        if avg_sleep < 7:
            return "😴 Your sleep has been below 7 hours. Try to get 7-8 hours tonight. Sleep is crucial for muscle building and recovery!"
        else:
            return "😴 Your sleep looks good! Keep up the consistent sleep schedule."
    
    elif "sore" in user_input or "pain" in user_input:
        recent_soreness = [log.get("soreness", "") for log in recent_logs if log.get("soreness")]
        if any("shoulder" in s.lower() for s in recent_soreness):
            return "⚠️ I notice shoulder soreness in your recent logs. Let's be careful with pressing movements. Focus on mobility, band work, and maybe some light pull exercises."
        else:
            return "💪 Some soreness is normal! Make sure to warm up properly and maybe do some light mobility work today."
    
    elif "goal" in user_input or "progress" in user_input:
        if profile and profile.get("goals"):
            goals = profile["goals"]
            if "handstand" in str(goals).lower():
                return "🎯 For your handstand goal: focus on shoulder strength, core stability, and wrist flexibility. Practice wall walks and holds regularly!"
            elif "pancake" in str(goals).lower():
                return "🎯 For your pancake goal: work on hip flexibility, hamstring mobility, and adductor strength. Practice straddle stretches daily!"
            else:
                return "🎯 Keep focusing on your goals! Consistency is key. Track your progress and celebrate small wins!"
        return "🎯 Stay focused on your goals! Consistency and patience will get you there."
    
    else:
        return "🤖 I'm here to help! Ask me about training, nutrition, recovery, or your progress. I'm learning from your logs to give better advice!"

# Main app
def main():
    st.title("💪 Yoel's AI Coach")
    st.markdown("---")
    
    # Load data
    profile = load_profile()
    logs = load_logs()
    
    # Check if logged today
    logged_today = check_logged_today(logs)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("📱 Quick Actions")
        page = st.radio("Choose:", ["Quick Log", "Full Log", "View Trends", "AI Chat", "Settings"])
    
    if page == "Quick Log":
        quick_log_page(logs, logged_today)
    elif page == "Full Log":
        log_today_page(logs, logged_today)
    elif page == "View Trends":
        view_trends_page(logs)
    elif page == "AI Chat":
        ai_chat_page(profile, logs)
    elif page == "Settings":
        settings_page()

def log_today_page(logs, logged_today):
    st.header("📊 Daily Log")
    
    if logged_today:
        st.warning("⚠️ You've already logged today! You can update your entry below.")
    
    # Get defaults from yesterday
    defaults = get_yesterday_defaults(logs)
    
    with st.form("daily_log"):
        st.subheader("How are you feeling?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mood_options = ["1 - Terrible", "2 - Bad", "3 - Meh", "4 - Okay", "5 - Neutral", 
                           "6 - Good", "7 - Great", "8 - Excellent", "9 - Amazing", "10 - Perfect"]
            mood = st.selectbox("😊 Mood", mood_options, 
                               index=int(defaults.get("mood", "5")) - 1 if defaults.get("mood") and str(defaults.get("mood")).isdigit() else 4)
            
            energy_options = ["1 - Exhausted", "2 - Very Low", "3 - Low", "4 - Below Average", "5 - Average",
                             "6 - Above Average", "7 - Good", "8 - High", "9 - Very High", "10 - Energized"]
            energy = st.selectbox("⚡ Energy Level", energy_options,
                                 index=int(defaults.get("energy", "5")) - 1 if defaults.get("energy") and str(defaults.get("energy")).isdigit() else 4)
            
            sleep_hours = st.number_input("😴 Hours Slept", min_value=0.0, max_value=24.0, value=float(defaults.get("sleep_hours", 7.0)), step=0.5)
            
            sleep_quality_options = ["1 - Terrible", "2 - Bad", "3 - Poor", "4 - Fair", "5 - Okay",
                                   "6 - Good", "7 - Very Good", "8 - Great", "9 - Excellent", "10 - Perfect"]
            sleep_quality = st.selectbox("🌙 Sleep Quality", sleep_quality_options,
                                        index=int(defaults.get("sleep_quality", "5")) - 1 if defaults.get("sleep_quality") and str(defaults.get("sleep_quality")).isdigit() else 4)
        
        with col2:
            stress_options = ["1 - No Stress", "2 - Very Low", "3 - Low", "4 - Mild", "5 - Moderate",
                             "6 - High", "7 - Very High", "8 - Extreme", "9 - Overwhelming", "10 - Breaking Point"]
            stress_level = st.selectbox("😰 Stress Level", stress_options,
                                       index=int(defaults.get("stress_level", "5")) - 1 if defaults.get("stress_level") and str(defaults.get("stress_level")).isdigit() else 4)
            
            soreness_options = ["None", "Shoulders", "Chest", "Back", "Arms", "Legs", "Core", "Full Body"]
            # Handle soreness defaults properly
            soreness_default = []
            if defaults.get("soreness"):
                soreness_text = defaults.get("soreness", "").lower()
                if soreness_text != "none" and soreness_text:
                    # Split by comma and clean up
                    soreness_parts = [part.strip() for part in soreness_text.split(",")]
                    soreness_default = [opt for opt in soreness_options if any(part in opt.lower() for part in soreness_parts)]
            soreness = st.multiselect("💪 Sore Muscles", soreness_options, default=soreness_default)
            
            hydration_options = ["1 - Dehydrated", "2 - Very Low", "3 - Low", "4 - Below Average", "5 - Average",
                               "6 - Above Average", "7 - Good", "8 - High", "9 - Very High", "10 - Perfect"]
            hydration = st.selectbox("💧 Hydration", hydration_options,
                                    index=int(defaults.get("hydration", "5")) - 1 if defaults.get("hydration") and str(defaults.get("hydration")).isdigit() else 4)
        
        st.subheader("🏋️ Training")
        
        col1, col2 = st.columns(2)
        
        with col1:
            training_options = [
                "None/Rest Day",
                "Push Day - Heavy",
                "Push Day - Moderate", 
                "Push Day - Light",
                "Pull Day - Heavy",
                "Pull Day - Moderate",
                "Pull Day - Light",
                "Legs Day - Heavy",
                "Legs Day - Moderate", 
                "Legs Day - Light",
                "Yoga",
                "Mobility/Recovery",
                "Cardio",
                "Other"
            ]
            training_done = st.selectbox("Training Completed", training_options,
                                        index=0 if not defaults.get("training_done") else 
                                        next((i for i, opt in enumerate(training_options) if opt.lower() in defaults.get("training_done", "").lower()), 0))
            
            training_quality_options = ["1 - Terrible", "2 - Bad", "3 - Poor", "4 - Fair", "5 - Okay",
                                      "6 - Good", "7 - Very Good", "8 - Great", "9 - Excellent", "10 - Perfect"]
            training_quality = st.selectbox("⭐ Training Quality", training_quality_options,
                                           index=int(defaults.get("training_quality", "5")) - 1 if defaults.get("training_quality") and str(defaults.get("training_quality")).isdigit() else 4)
        
        with col2:
            nutrition = st.text_area("🍽️ What did you eat today?", value=defaults.get("nutrition", ""), height=100)
            notes = st.text_area("📝 Additional notes", value=defaults.get("notes", ""), height=100)
        
        # Extract numeric values from selections
        mood_value = mood.split(" - ")[0]
        energy_value = energy.split(" - ")[0]
        sleep_quality_value = sleep_quality.split(" - ")[0]
        stress_value = stress_level.split(" - ")[0]
        hydration_value = hydration.split(" - ")[0]
        training_quality_value = training_quality.split(" - ")[0]
        
        # Create entry
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "mood": mood_value,
            "energy": energy_value,
            "sleep_hours": str(sleep_hours),
            "sleep_quality": sleep_quality_value,
            "stress_level": stress_value,
            "soreness": ", ".join(soreness) if soreness else "none",
            "training_done": training_done,
            "training_quality": training_quality_value,
            "nutrition": nutrition,
            "hydration": hydration_value,
            "notes": notes
        }
        
        # Calculate metrics
        entry["recovery_score"] = str(calculate_recovery_score(entry))
        entry["training_volume"] = estimate_training_volume(training_done)
        entry["split"] = detect_split(training_done)
        
        submitted = st.form_submit_button("💾 Save Log", type="primary")
        
        if submitted:
            # Remove existing entry for today if it exists
            logs = [log for log in logs if log.get("date") != entry["date"]]
            logs.append(entry)
            save_logs(logs)
            
            st.success(f"✅ Log saved for {entry['date']}")
            st.info(f"📈 Recovery Score: {entry['recovery_score']}/10")
            
            # Show quick insights
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Energy", f"{energy_value}/10")
            with col2:
                st.metric("Recovery", f"{entry['recovery_score']}/10")
            with col3:
                st.metric("Training", training_done.split(" - ")[0] if " - " in training_done else training_done)

def view_trends_page(logs):
    st.header("📊 Trends & Analysis")
    
    if not logs:
        st.warning("No data to analyze yet. Start logging to see trends!")
        return
    
    # Recent trends
    recent_logs = logs[-7:]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        energies = [float(log.get("energy", 5)) for log in recent_logs if log.get("energy")]
        if energies:
            avg_energy = statistics.mean(energies)
            st.metric("⚡ Avg Energy", f"{avg_energy:.1f}/10")
    
    with col2:
        recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
        if recovery_scores:
            avg_recovery = statistics.mean(recovery_scores)
            st.metric("🔄 Avg Recovery", f"{avg_recovery:.1f}/10")
    
    with col3:
        sleep_hours = [float(log.get("sleep_hours", 7)) for log in recent_logs if log.get("sleep_hours")]
        if sleep_hours:
            avg_sleep = statistics.mean(sleep_hours)
            st.metric("😴 Avg Sleep", f"{avg_sleep:.1f}h")
    
    # Enhanced visualizations
    if len(logs) >= 3:
        st.subheader("📈 Progress Charts")
        
        # Create DataFrame for plotting
        df = pd.DataFrame(logs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Energy and Recovery trends
        col1, col2 = st.columns(2)
        
        with col1:
            if 'energy' in df.columns:
                fig_energy = px.line(df, x='date', y='energy', title='Energy Level Trend',
                                   labels={'energy': 'Energy Level', 'date': 'Date'})
                fig_energy.update_layout(height=300)
                st.plotly_chart(fig_energy, use_container_width=True)
        
        with col2:
            if 'recovery_score' in df.columns:
                fig_recovery = px.line(df, x='date', y='recovery_score', title='Recovery Score Trend',
                                     labels={'recovery_score': 'Recovery Score', 'date': 'Date'})
                fig_recovery.update_layout(height=300)
                st.plotly_chart(fig_recovery, use_container_width=True)
        
        # Training split visualization
        st.subheader("🏋️ Training Split Analysis")
        split_counts = {"Push": 0, "Pull": 0, "Legs": 0, "Recovery": 0, "Other": 0, "None": 0}
        for log in recent_logs:
            split = log.get("split") or detect_split(log.get("training_done", ""))
            if split in split_counts:
                split_counts[split] += 1
        
        # Filter out zero counts for cleaner chart
        non_zero_splits = {k: v for k, v in split_counts.items() if v > 0}
        
        if non_zero_splits:
            fig_split = px.pie(values=list(non_zero_splits.values()), 
                              names=list(non_zero_splits.keys()),
                              title='Training Split Distribution (Last 7 Days)')
            st.plotly_chart(fig_split, use_container_width=True)
    
    # Quick insights
    st.subheader("💡 Quick Insights")
    
    if recent_logs:
        # Energy trend
        if len(recent_logs) >= 3:
            recent_energy = [float(log.get("energy", 5)) for log in recent_logs[-3:]]
            if recent_energy:
                energy_trend = "📈 Improving" if recent_energy[-1] > recent_energy[0] else "📉 Declining" if recent_energy[-1] < recent_energy[0] else "➡️ Stable"
                st.info(f"Energy trend: {energy_trend}")
        
        # Recovery pattern
        recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
        if recovery_scores:
            avg_recovery = statistics.mean(recovery_scores)
            if avg_recovery < 6:
                st.warning("⚠️ Your recovery scores are low. Consider more rest days or lighter training.")
            elif avg_recovery > 8:
                st.success("✅ Great recovery! You're managing your training load well.")
        
        # Training frequency
        training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
        if training_days >= 5:
            st.info("🏋️ You're training frequently. Make sure to include recovery days!")
        elif training_days <= 2:
            st.info("💪 You could increase training frequency if you're feeling good.")
    
    # Split summary
    st.subheader("🗓️ Weekly Split Summary")
    split_counts = {"Push": 0, "Pull": 0, "Legs": 0, "Recovery": 0, "Other": 0, "None": 0}
    for log in recent_logs:
        split = log.get("split") or detect_split(log.get("training_done", ""))
        if split in split_counts:
            split_counts[split] += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Push", split_counts["Push"])
    with col2:
        st.metric("Pull", split_counts["Pull"])
    with col3:
        st.metric("Legs", split_counts["Legs"])
    
    # Training days
    training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
    st.metric("🏋️ Training Days", f"{training_days}/{len(recent_logs)}")

def ai_chat_page(profile, logs):
    st.header("🤖 AI Coach Chat")
    
    if not profile:
        st.error("Profile not found. Please check yoel_profile.json")
        return
    
    # Simple chat interface
    user_input = st.text_input("Ask your AI coach:", placeholder="What should I train today?")
    
    if user_input:
        # Simple response logic (you can enhance this)
        response = get_enhanced_response(user_input, profile, logs)
        st.write(f"**AI Coach:** {response}")

def quick_log_page(logs, logged_today):
    st.header("⚡ Quick Log")
    
    if logged_today:
        st.warning("⚠️ You've already logged today! You can update your entry below.")
    
    st.subheader("Choose a preset:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😊 Great Day", type="primary"):
            entry = quick_log(logs, "Great Day")
            st.success(f"✅ Quick log saved: {entry['training_done']}")
            st.info(f"📈 Recovery Score: {entry['recovery_score']}/10")
    
    with col2:
        if st.button("🔄 Recovery Day"):
            entry = quick_log(logs, "Recovery Day")
            st.success(f"✅ Quick log saved: {entry['training_done']}")
            st.info(f"📈 Recovery Score: {entry['recovery_score']}/10")
    
    with col3:
        if st.button("😴 Rest Day"):
            entry = quick_log(logs, "Rest Day")
            st.success(f"✅ Quick log saved: {entry['training_done']}")
            st.info(f"📈 Recovery Score: {entry['recovery_score']}/10")
    
    st.markdown("---")
    st.info("💡 Use Quick Log for fast logging, or go to 'Full Log' for detailed tracking!")

def settings_page():
    st.header("⚙️ Settings")
    st.info("Settings and reminders coming soon!")

if __name__ == "__main__":
    main() 