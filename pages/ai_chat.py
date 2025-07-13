import streamlit as st
import json
from coach_core.data import load_profile, load_logs
from coach_core.ai import AICoach

def ai_chat_page(profile, logs):
    st.header("💬 Chat with Your AI Coach")
    
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
        # Get AI response using core AI module
        ai_coach = AICoach()
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
            ai_coach = AICoach()
            response = ai_coach.get_ai_response("What should I train today?")
            st.session_state.chat_history.append({"role": "user", "content": "What should I train today?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.write(f"**AI Coach:** {response}")
    
    with col2:
        if st.button("🍽️ Nutrition Tips"):
            ai_coach = AICoach()
            response = ai_coach.get_ai_response("What should I eat today?")
            st.session_state.chat_history.append({"role": "user", "content": "What should I eat today?"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.write(f"**AI Coach:** {response}")
    
    with col3:
        if st.button("📊 Pattern Analysis"):
            ai_coach = AICoach()
            pattern_analysis = ai_coach.analyze_patterns()
            st.session_state.chat_history.append({"role": "user", "content": "Show me my patterns"})
            st.session_state.chat_history.append({"role": "assistant", "content": pattern_analysis})
            st.write(f"**AI Coach:** {pattern_analysis}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun() 