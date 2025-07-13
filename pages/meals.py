import streamlit as st
from datetime import datetime
from coach_core.data import load_logs, save_logs

def log_meals_page(logs):
    st.header("🍽️ Log Your Meals")
    
    # Check if we have a log for today
    today = datetime.now().strftime("%Y-%m-%d")
    today_log = next((log for log in logs if log.get("date") == today), None)
    
    if not today_log:
        st.warning("⚠️ No daily log found for today. Please complete your daily log first!")
        st.info("💡 Go to 'Daily Log' to log your training, mood, and other activities for today.")
        return
    
    st.success(f"✅ Found your daily log for {today}")
    
    # Get current nutrition and notes
    current_nutrition = today_log.get("nutrition", "")
    current_notes = today_log.get("notes", "")
    
    # Display current status
    st.subheader("📊 Current Status")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🍽️ Meals Logged", "Yes" if current_nutrition.strip() else "No")
    with col2:
        st.metric("📝 Notes Added", "Yes" if current_notes.strip() else "No")
    
    # Quick meal suggestions
    st.subheader("🍽️ Quick Meal Suggestions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🥚 Breakfast"):
            suggested_meal = "Eggs with tahini, vegetables, and toast"
            st.session_state.suggested_meal = suggested_meal
    
    with col2:
        if st.button("🍗 Lunch"):
            suggested_meal = "Chicken with rice, vegetables, and fruit"
            st.session_state.suggested_meal = suggested_meal
    
    with col3:
        if st.button("🥗 Dinner"):
            suggested_meal = "Salad with protein, vegetables, and healthy fats"
            st.session_state.suggested_meal = suggested_meal
    
    # Display suggested meal if available
    if hasattr(st.session_state, 'suggested_meal'):
        st.info(f"💡 Suggested: {st.session_state.suggested_meal}")
    
    # Update nutrition and notes
    st.subheader("📝 Update Your Meals & Notes")
    
    # Pre-fill with current data
    new_nutrition = st.text_area(
        "🍽️ What did you eat today? (Add to existing meals)",
        value=current_nutrition,
        height=120,
        placeholder="e.g., Breakfast: eggs with tahini and vegetables\nLunch: chicken with rice and salad\nDinner: fish with quinoa and vegetables"
    )
    
    new_notes = st.text_area(
        "📝 Additional notes about your meals or day",
        value=current_notes,
        height=100,
        placeholder="e.g., Felt great after lunch, energy was high for training"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Updates", type="primary"):
            # Update the existing log entry
            today_log["nutrition"] = new_nutrition
            today_log["notes"] = new_notes
            
            # Save to file using core module
            save_logs(logs)
            st.success("✅ Meals and notes updated successfully!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset to Original"):
            st.rerun()
    
    # Show recent meal history
    if len(logs) > 1:
        st.subheader("📅 Recent Meal History")
        recent_logs = logs[-5:]  # Last 5 days
        
        for log in recent_logs:
            if log.get("nutrition") and log.get("nutrition").strip():
                st.write(f"**{log['date']}:** {log['nutrition'][:100]}{'...' if len(log['nutrition']) > 100 else ''}")
                if log.get("notes"):
                    st.write(f"*Notes: {log['notes'][:50]}{'...' if len(log['notes']) > 50 else ''}*")
                st.markdown("---") 