import streamlit as st
from coach_core.data import load_profile, load_logs
from pages.daily_log import log_today_page, check_logged_today
from pages.ai_chat import ai_chat_page
from pages.settings import settings_page
from dotenv import load_dotenv
load_dotenv()

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
    
    # Load data using core modules
    profile = load_profile()
    logs = load_logs()
    
    # Check if logged today
    logged_today = check_logged_today(logs)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("📱 Navigation")
        page = st.radio("Choose:", ["AI Chat", "Daily Log", "Settings"])
    
    if page == "AI Chat":
        ai_chat_page(profile, logs)
    elif page == "Daily Log":
        log_today_page(logs, logged_today)
    elif page == "Settings":
        settings_page()

if __name__ == "__main__":
    main() 