import streamlit as st
import json
from coach_core.data import load_profile, load_logs
from coach_core.ai import AICoach

def ai_chat_page(profile, logs):
    st.header("🧠 Mentor-Powered AI Coach")
    st.markdown("""
    **Your AI coach is trained by the world's greatest minds in movement, strength, and performance:**
    
    🧘 **Dylan Werner** - Isometric strength & body control  
    🌊 **Patrick Beach** - Fluid mobility & breath connection  
    🦍 **Everydamnandré** - Gritty kettlebell conditioning  
    🧠 **SquatU** - Biomechanics & joint safety  
    🦵 **KneesOverToesGuy** - Bulletproofing & longevity  
    🧱 **JTM_FIT** - Aesthetic movement & core strength  
    🕊️ **Ido Portal** - Movement complexity & adaptability  
    🧘 **Emmet Louis** - End-range mobility strength  
    📐 **Tom Merrick** - Clean calisthenics & flexibility  
    💪 **Austin Dunham** - High-volume calisthenics  
    📊 **FitnessFAQs** - Evidence-based strength  
    ⚡ **Chris Barnard** - Speed, power & athleticism  
    🧩 **Marcus Filly** - Tempo & unilateral work  
    🧬 **Dr. Andy Galpin** - Performance science  
    🎙️ **Joe Rogan** - Wisdom-seeking & experimentation
    """)
    
    # Initialize chat history safely
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history with better error handling
    if st.session_state.chat_history:
        st.subheader("📝 Chat History")
        for i, message in enumerate(st.session_state.chat_history):
            try:
                if isinstance(message, dict) and "role" in message and "content" in message:
                    if message["role"] == "user":
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**AI Coach:** {message['content']}")
                else:
                    # Skip invalid messages
                    continue
            except Exception as e:
                st.error(f"Error displaying message: {e}")
                continue
    
    # Chat input
    st.subheader("💬 Ask Your Mentor-Powered Coach")
    
    # Add some suggested questions
    st.markdown("**Try asking:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What should I train today?"):
            st.session_state.user_input = "What should I train today? I want to focus on calisthenics and yoga."
        if st.button("How should I eat for my goals?"):
            st.session_state.user_input = "What should I eat to support my training and recovery?"
        if st.button("Help with my shoulder issues"):
            st.session_state.user_input = "My shoulder is bothering me, what should I do?"
    
    with col2:
        if st.button("I'm feeling tired"):
            st.session_state.user_input = "I'm feeling tired and low energy today"
        if st.button("Weekly training plan"):
            st.session_state.user_input = "Generate a weekly training plan for me"
        if st.button("Recovery advice"):
            st.session_state.user_input = "How should I recover and what mobility work should I do?"
    
    # Chat input
    user_input = st.text_area("Your message:", key="user_input", height=100)
    
    # Send button
    if st.button("🚀 Send to Mentor-Powered Coach", type="primary"):
        if user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input.strip()
            })
            
            # Get AI response
            try:
                ai_coach = AICoach()
                
                # Check if it's a weekly plan request
                if "weekly" in user_input.lower() or "plan" in user_input.lower():
                    response = ai_coach.get_weekly_plan()
                else:
                    response = ai_coach.get_ai_response(user_input.strip())
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                st.success("✅ Response received from mentor-powered coach!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error getting response: {e}")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "Sorry, I'm having trouble connecting to my mentor knowledge base. Please try again."
                })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Mentor knowledge showcase
    with st.expander("🧠 Explore Mentor Knowledge"):
        st.markdown("""
        **Your AI coach synthesizes wisdom from these movement masters:**
        
        **Dylan Werner** - "Mastery through stillness and control. Build strength through isometric holds."
        
        **Patrick Beach** - "Movement should flow naturally. Connect breath to movement."
        
        **Everydamnandré** - "Simple, hard work builds character. Kettlebells and basic movements done consistently."
        
        **SquatU** - "Move correctly first, then add load. Biomechanics and joint health are the foundation."
        
        **KneesOverToesGuy** - "Build bulletproof joints through progressive loading. Longevity over short-term gains."
        
        **Ido Portal** - "Movement is life. Develop complexity, adaptability, and natural movement patterns."
        
        **Dr. Andy Galpin** - "Science-based training with focus on muscle physiology and optimal recovery."
        
        Ask your coach anything about training, nutrition, recovery, or movement - they'll draw from this collective wisdom!
        """) 