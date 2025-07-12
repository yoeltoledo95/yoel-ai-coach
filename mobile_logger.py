import streamlit as st
import json
import pandas as pd
import plotly.express as px
import statistics
from datetime import datetime
import os
import openai
from typing import List, Dict, Any

# Load data functions
def load_profile(path="yoel_profile.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Profile file {path} not found!")
        return {}

def load_logs(path="daily_logs.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_logs(logs, path="daily_logs.json"):
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

# AI Coach class (integrated from ai_coach.py)
class AICoach:
    def __init__(self, profile_path="yoel_profile.json", logs_path="daily_logs.json"):
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
            return {}
    
    def load_logs(self) -> List[Dict[str, Any]]:
        """Load daily logs from JSON file"""
        try:
            with open(self.logs_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
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

# Initialize AI Coach
ai_coach = AICoach()

# Helper functions
def detect_split(training_done):
    if not training_done or training_done.lower() == "none/rest day":
        return "Rest"
    elif "push" in training_done.lower():
        return "Push"
    elif "pull" in training_done.lower():
        return "Pull"
    elif "legs" in training_done.lower():
        return "Legs"
    elif "yoga" in training_done.lower():
        return "Yoga"
    elif "mobility" in training_done.lower() or "recovery" in training_done.lower():
        return "Recovery"
    else:
        return "Other"

def calculate_recovery_score(entry):
    """Calculate recovery score based on various factors"""
    score = 5.0  # Base score
    
    # Energy level (0-10)
    if 'energy' in entry:
        try:
            energy = float(entry['energy'])
            score += (energy - 5) * 0.3
        except:
            pass
    
    # Sleep hours
    if 'sleep_hours' in entry:
        try:
            sleep = float(entry['sleep_hours'])
            if 7 <= sleep <= 9:
                score += 1.0
            elif 6 <= sleep < 7 or 9 < sleep <= 10:
                score += 0.5
            elif sleep < 6:
                score -= 1.0
        except:
            pass
    
    # Sleep quality
    if 'sleep_quality' in entry:
        try:
            quality = float(entry['sleep_quality'])
            score += (quality - 5) * 0.2
        except:
            pass
    
    # Stress level (inverse)
    if 'stress_level' in entry:
        try:
            stress = float(entry['stress_level'])
            score -= (stress - 5) * 0.2
        except:
            pass
    
    # Training quality
    if 'training_quality' in entry:
        try:
            training_quality = float(entry['training_quality'])
            score += (training_quality - 5) * 0.1
        except:
            pass
    
    # Hydration
    if 'hydration' in entry:
        try:
            hydration = float(entry['hydration'])
            score += (hydration - 5) * 0.1
        except:
            pass
    
    return max(0, min(10, score))

def estimate_training_volume(training_done):
    if not training_done or training_done.lower() == "none/rest day":
        return "none"
    elif "heavy" in training_done.lower():
        return "high"
    elif "moderate" in training_done.lower():
        return "medium"
    elif "light" in training_done.lower() or "mobility" in training_done.lower() or "recovery" in training_done.lower():
        return "low"
    else:
        return "medium"

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

def quick_log(logs, preset):
    """Create a quick log entry based on preset"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if preset == "Great Day":
        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "mood": "8",
            "energy": "8",
            "sleep_hours": "7.5",
            "sleep_quality": "8",
            "stress_level": "3",
            "soreness": "none",
            "training_done": "Push Day - Moderate",
            "training_quality": "8",
            "nutrition": "eggs, chicken, vegetables, tahini",
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
            "sleep_hours": "6.5",
            "sleep_quality": "6",
            "stress_level": "5",
            "soreness": "shoulders, chest",
            "training_done": "Mobility/Recovery",
            "training_quality": "6",
            "nutrition": "eggs, toast, fruit",
            "hydration": "7",
            "notes": "Recovery day needed",
            "recovery_score": "5.5",
            "training_volume": "low",
            "split": "Recovery"
        }
    else:  # Rest Day
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
            "nutrition": "light meals, lots of water",
            "hydration": "8",
            "notes": "Rest day",
            "recovery_score": "7.0",
            "training_volume": "none",
            "split": "Rest"
        }
    
    # Calculate metrics
    entry["recovery_score"] = str(calculate_recovery_score(entry))
    entry["training_volume"] = estimate_training_volume(entry["training_done"])
    entry["split"] = detect_split(entry["training_done"])
    
    # Remove existing entry for today if it exists
    logs = [log for log in logs if log.get("date") != today]
    logs.append(entry)
    save_logs(logs)
    
    return entry

# Enhanced AI response function (now uses the true AI agent)
def get_enhanced_response(user_input, profile, logs):
    """Get response from the true AI agent"""
    return ai_coach.get_ai_response(user_input)

# Page config for mobile
st.set_page_config(
    page_title="Yoel's AI Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        page = st.radio("Choose:", ["Quick Log", "Full Log", "View Trends", "AI Chat", "Pattern Analysis", "Settings"])
    
    if page == "Quick Log":
        quick_log_page(logs, logged_today)
    elif page == "Full Log":
        log_today_page(logs, logged_today)
    elif page == "View Trends":
        view_trends_page(logs)
    elif page == "AI Chat":
        ai_chat_page(profile, logs)
    elif page == "Pattern Analysis":
        pattern_analysis_page(logs)
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
    
    # Show AI status
    if ai_coach.client:
        st.success("✅ Connected to GPT - Full AI intelligence available!")
    else:
        st.info("ℹ️ Using smart fallback responses. Add OPENAI_API_KEY for full AI features.")
    
    # Pattern Analysis Section
    st.subheader("📊 Your Recent Patterns")
    if logs:
        pattern_analysis = ai_coach.analyze_patterns()
        st.text(pattern_analysis)
        
        # Show recent logs summary
        if len(logs) >= 3:
            recent_logs = logs[-3:]
            st.subheader("📝 Recent Activity")
            for log in recent_logs:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Date", log.get("date", "Unknown"))
                with col2:
                    st.metric("Energy", f"{log.get('energy', 'N/A')}/10")
                with col3:
                    st.metric("Training", log.get("training_done", "None").split(" - ")[0] if " - " in log.get("training_done", "") else log.get("training_done", "None"))
    else:
        st.warning("No training history available yet. Start logging to see patterns!")
    
    st.markdown("---")
    
    # Enhanced Chat Interface
    st.subheader("💬 Chat with Your AI Coach")
    
    # Chat history (simple implementation)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**AI Coach:** {message['content']}")
    
    # Input and response
    user_input = st.text_input("Ask your AI coach:", placeholder="What should I train today? I'm tired... What should I eat?")
    
    if user_input:
        # Get AI response
        response = ai_coach.get_ai_response(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display response
        st.write(f"**AI Coach:** {response}")
        
        # Clear input (refresh to show new message)
        st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💪 Training Advice"):
            response = ai_coach.get_ai_response("What should I train today?")
            st.session_state.chat_history.append({"role": "user", "content": "What should I train today?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.write(f"**AI Coach:** {response}")
    
    with col2:
        if st.button("🍽️ Nutrition Tips"):
            response = ai_coach.get_ai_response("What should I eat today?")
            st.session_state.chat_history.append({"role": "user", "content": "What should I eat today?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.write(f"**AI Coach:** {response}")
    
    with col3:
        if st.button("📊 Pattern Analysis"):
            pattern_analysis = ai_coach.analyze_patterns()
            st.session_state.chat_history.append({"role": "user", "content": "Show me my patterns"})
            st.session_state.chat_history.append({"role": "assistant", "content": pattern_analysis})
            st.write(f"**AI Coach:** {pattern_analysis}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def pattern_analysis_page(logs):
    st.header("📊 Advanced Pattern Analysis")
    
    if not logs:
        st.warning("No data to analyze yet. Start logging to see patterns!")
        return
    
    # AI Coach pattern analysis
    pattern_analysis = ai_coach.analyze_patterns()
    st.subheader("🤖 AI Analysis")
    st.text(pattern_analysis)
    
    # Detailed metrics
    st.subheader("📈 Detailed Metrics")
    recent_logs = logs[-7:] if len(logs) >= 7 else logs
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Energy analysis
        energies = [float(log.get("energy", 5)) for log in recent_logs if log.get("energy")]
        if energies:
            avg_energy = statistics.mean(energies)
            energy_trend = "📈" if energies[-1] > energies[0] else "📉" if energies[-1] < energies[0] else "➡️"
            st.metric("⚡ Energy Trend", f"{energy_trend} {avg_energy:.1f}/10")
    
    with col2:
        # Recovery analysis
        recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
        if recovery_scores:
            avg_recovery = statistics.mean(recovery_scores)
            st.metric("🔄 Recovery", f"{avg_recovery:.1f}/10")
    
    with col3:
        # Training frequency
        training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
        st.metric("🏋️ Training Days", f"{training_days}/{len(recent_logs)}")
    
    # Soreness analysis
    st.subheader("💪 Soreness Patterns")
    all_soreness = []
    for log in recent_logs:
        if log.get("soreness") and log.get("soreness") != "none":
            all_soreness.extend([s.strip() for s in log.get("soreness", "").split(",")])
    
    if all_soreness:
        soreness_counts = {}
        for soreness in all_soreness:
            soreness_counts[soreness] = soreness_counts.get(soreness, 0) + 1
        
        st.write("Most common soreness areas:")
        for area, count in sorted(soreness_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"• {area}: {count} times")
    else:
        st.info("No soreness recorded recently. Great recovery!")
    
    # Training split analysis
    st.subheader("🏋️ Training Split Analysis")
    split_counts = {"Push": 0, "Pull": 0, "Legs": 0, "Recovery": 0, "Other": 0}
    for log in recent_logs:
        split = log.get("split") or detect_split(log.get("training_done", ""))
        if split in split_counts:
            split_counts[split] += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Push Days", split_counts["Push"])
    with col2:
        st.metric("Pull Days", split_counts["Pull"])
    with col3:
        st.metric("Legs Days", split_counts["Legs"])
    
    # AI Insights
    st.subheader("🤖 AI Insights")
    if ai_coach.client:
        st.success("✅ Full AI analysis available with GPT")
        insight_prompt = f"Based on this training data: {json.dumps(recent_logs, indent=2)}, provide 3 specific insights about Yoel's training patterns and suggestions for improvement."
        try:
            insight_response = ai_coach.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Yoel's AI coach. Provide specific, actionable insights."},
                    {"role": "user", "content": insight_prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            st.write(insight_response.choices[0].message.content)
        except:
            st.info("AI insights temporarily unavailable. Using pattern analysis instead.")
    else:
        st.info("Add OPENAI_API_KEY for AI-powered insights!")
        
        # Manual insights
        if recovery_scores and statistics.mean(recovery_scores) < 6:
            st.warning("⚠️ Your recovery scores are low. Consider more rest days.")
        if training_days >= 5:
            st.info("🏋️ You're training frequently. Make sure to include recovery days!")
        if energies and statistics.mean(energies) < 6:
            st.warning("⚠️ Your energy levels are low. Consider lighter training or more rest.")

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