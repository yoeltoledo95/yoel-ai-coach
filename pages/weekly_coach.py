import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.ai import AICoach

def weekly_coach_page():
    """WhatsApp-style weekly coaching interface"""
    
    # Load data
    profile = load_profile()
    logs = load_logs()
    
    # Initialize AI coach
    ai_coach = AICoach()
    
    # Page styling for WhatsApp look
    st.markdown("""
    <style>
    .chat-container {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .message {
        margin: 10px 0;
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 80%;
    }
    .user-message {
        background-color: #dcf8c6;
        margin-left: auto;
        text-align: right;
    }
    .coach-message {
        background-color: white;
        margin-right: auto;
    }
    .week-status {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💬 Weekly Coach")
    st.markdown("---")
    
    # Get current week info
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Week status display
    with st.container():
        st.markdown(f"""
        <div class="week-status">
        <h4>📅 Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d')}</h4>
        <p>Current day: {today.strftime('%A, %B %d')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Initialize session state for chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'weekly_plan' not in st.session_state:
        st.session_state.weekly_plan = None
    
    if 'feedback_log' not in st.session_state:
        st.session_state.feedback_log = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="message user-message">
            <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message coach-message">
            <strong>Coach:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input("💬 Type your message...", key="user_input")
    
    with col2:
        if st.button("Send", key="send_button"):
            if user_input.strip():
                # Add user message to chat
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Get AI response
                response = get_coach_response(user_input, profile, logs, ai_coach)
                
                # Add coach response to chat
                st.session_state.chat_history.append({
                    'role': 'coach',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                st.rerun()
    
    # Quick action buttons
    st.markdown("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Get Weekly Plan", key="get_plan"):
            plan = generate_weekly_plan(profile, logs, ai_coach)
            st.session_state.weekly_plan = plan
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': f"Here's your weekly plan:\n\n{plan}",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
    
    with col2:
        if st.button("📝 Log Feedback", key="log_feedback"):
            show_feedback_form()
    
    with col3:
        if st.button("🔄 Sunday Reflection", key="reflection"):
            reflection = generate_sunday_reflection(profile, logs, ai_coach)
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': f"Sunday Reflection:\n\n{reflection}",
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
    
    # Display current weekly plan if available
    if st.session_state.weekly_plan:
        st.markdown("### 📋 Current Weekly Plan")
        st.text_area("Plan", st.session_state.weekly_plan, height=200, disabled=True)

def get_coach_response(user_input: str, profile: Dict, logs: List, ai_coach: AICoach) -> str:
    """Get contextual coach response based on input"""
    
    user_input_lower = user_input.lower()
    
    # Handle specific coaching scenarios
    if "plan" in user_input_lower or "workout" in user_input_lower:
        return generate_weekly_plan(profile, logs, ai_coach)
    
    elif "feedback" in user_input_lower or "felt" in user_input_lower:
        return process_feedback(user_input, profile, logs, ai_coach)
    
    elif "reflection" in user_input_lower or "sunday" in user_input_lower:
        return generate_sunday_reflection(profile, logs, ai_coach)
    
    elif "help" in user_input_lower or "what" in user_input_lower:
        return get_help_message()
    
    else:
        # Use AI coach for general conversation
        return ai_coach.get_ai_response(user_input)

def generate_weekly_plan(profile: Dict, logs: List, ai_coach: AICoach) -> str:
    """Generate movement-focused weekly plan"""
    
    # Create movement-focused prompt
    prompt = f"""Create a 7-day movement training plan for Yoel that focuses ONLY on movement, strength, and mobility (no nutrition).

PROFILE: {json.dumps(profile, indent=2)}
RECENT LOGS: {json.dumps(logs[-7:], indent=2)}

Create a plan that:
1. Focuses on calisthenics, yoga, and athletic movement
2. Considers shoulder issues (avoid painful movements)
3. Includes mobility and flexibility work
4. Has 3-4 training days with active recovery
5. Provides specific exercises and progressions
6. Adapts to energy levels and recovery needs

Format as a clear, actionable weekly plan with specific exercises."""

    try:
        response = ai_coach.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movement-focused coach. Create specific, actionable weekly training plans focused only on movement, strength, and mobility."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content or "Error generating weekly plan"
    except Exception as e:
        return f"Error generating weekly plan: {e}"

def process_feedback(user_input: str, profile: Dict, logs: List, ai_coach: AICoach) -> str:
    """Process user feedback and update plan accordingly"""
    
    # Simple feedback processing
    feedback_keywords = {
        "felt great": "positive",
        "too easy": "needs_progression", 
        "too hard": "needs_regression",
        "shoulder tight": "injury_concern",
        "tired": "recovery_needed",
        "energized": "positive"
    }
    
    feedback_type = "general"
    for keyword, ftype in feedback_keywords.items():
        if keyword in user_input.lower():
            feedback_type = ftype
            break
    
    # Store feedback
    feedback_entry = {
        'date': datetime.now().isoformat(),
        'feedback': user_input,
        'type': feedback_type
    }
    
    if 'feedback_log' not in st.session_state:
        st.session_state.feedback_log = []
    
    st.session_state.feedback_log.append(feedback_entry)
    
    # Generate response based on feedback type
    responses = {
        "positive": "Great! Keep up the momentum. The plan is working well for you.",
        "needs_progression": "Perfect! Let's increase the challenge next week. I'll adjust the plan to be more demanding.",
        "needs_regression": "No problem! Let's dial it back a bit. Recovery is just as important as training.",
        "injury_concern": "Important feedback! Let's modify the plan to avoid shoulder stress. I'll focus on lower body and core work.",
        "recovery_needed": "Listen to your body! Let's add more recovery days and lighter sessions.",
        "general": "Thanks for the feedback! I'll use this to improve your plan for next week."
    }
    
    return responses.get(feedback_type, responses["general"])

def generate_sunday_reflection(profile: Dict, logs: List, ai_coach: AICoach) -> str:
    """Generate Sunday reflection and plan evolution"""
    
    # Get recent feedback
    recent_feedback = st.session_state.get('feedback_log', [])
    
    prompt = f"""Generate a Sunday reflection for Yoel's movement training week.

PROFILE: {json.dumps(profile, indent=2)}
RECENT LOGS: {json.dumps(logs[-7:], indent=2)}
RECENT FEEDBACK: {json.dumps(recent_feedback, indent=2)}

Create a reflection that:
1. Summarizes the week's training
2. Acknowledges feedback and progress
3. Identifies what worked and what didn't
4. Suggests improvements for next week
5. Maintains motivation and focus on movement goals

Be encouraging, specific, and actionable."""

    try:
        response = ai_coach.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive movement coach doing a Sunday reflection. Be encouraging and specific."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        return response.choices[0].message.content or "Error generating reflection"
    except Exception as e:
        return f"Error generating reflection: {e}"

def show_feedback_form():
    """Show simple feedback form"""
    
    st.markdown("### 📝 Quick Feedback")
    
    feedback_type = st.selectbox(
        "How did your training feel?",
        ["Select...", "Felt great!", "Too easy", "Too hard", "Shoulder tight", "Tired", "Energized"]
    )
    
    additional_notes = st.text_area("Additional notes (optional)")
    
    if st.button("Submit Feedback"):
        if feedback_type != "Select...":
            feedback_text = f"{feedback_type}"
            if additional_notes:
                feedback_text += f" - {additional_notes}"
            
            # Process feedback
            response = process_feedback(feedback_text, {}, [], AICoach())
            
            # Add to chat
            st.session_state.chat_history.append({
                'role': 'user',
                'content': f"Feedback: {feedback_text}",
                'timestamp': datetime.now().isoformat()
            })
            
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            st.rerun()

def get_help_message() -> str:
    """Get help message for the coaching interface"""
    
    return """Here's how I can help you:

📋 **Get Weekly Plan** - I'll create a 7-day movement training plan tailored to your goals and current state

📝 **Log Feedback** - Tell me how training felt ("felt great", "too easy", "shoulder tight", etc.) and I'll adjust the plan

🔄 **Sunday Reflection** - Let's review the week and plan improvements for next week

💬 **Chat** - Ask me anything about your training, movement, or goals

Just type naturally like you're texting a coach! I learn from your feedback to make each week better than the last."""

if __name__ == "__main__":
    weekly_coach_page() 