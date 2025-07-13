import streamlit as st
from datetime import datetime
from coach_core.data import load_logs, save_logs
from coach_core.utils import calculate_recovery_score, estimate_training_volume, detect_split

def check_logged_today(logs):
    today = datetime.now().strftime("%Y-%m-%d")
    return any(log.get("date") == today for log in logs)

def get_yesterday_defaults(logs):
    """Get yesterday's values as defaults"""
    if not logs:
        return {}
    
    yesterday = logs[-1]
    return {
        "mood": yesterday.get("mood", "5"),
        "energy": yesterday.get("energy", "5"),
        "sleep_hours": yesterday.get("sleep_hours", "7.0"),
        "sleep_quality": yesterday.get("sleep_quality", "5"),
        "stress_level": yesterday.get("stress_level", "5"),
        "soreness": yesterday.get("soreness", "none"),
        "hydration": yesterday.get("hydration", "5"),
        "training_done": yesterday.get("training_done", ""),
        "training_quality": yesterday.get("training_quality", "5"),
        "nutrition": yesterday.get("nutrition", ""),
        "notes": yesterday.get("notes", "")
    }

def log_today_page(logs, logged_today):
    st.header("📊 Daily Log")
    st.markdown("Welcome to your daily tracking! Log your mood, training, and nutrition for today.")
    
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
            
            soreness_options = ["none", "Shoulders", "Chest", "Back", "Arms", "Legs", "Core", "Full Body"]
            # Handle soreness defaults properly
            soreness_default = []
            if defaults.get("soreness"):
                soreness_text = defaults.get("soreness", "").strip().lower()
                if soreness_text and soreness_text != "none":
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
        
        # Calculate metrics using core utils
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