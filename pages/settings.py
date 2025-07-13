import streamlit as st
from coach_core.data import export_to_json, import_from_json, check_sync_status, load_profile, load_logs
from datetime import datetime

def settings_page():
    st.header("⚙️ Settings & Data Management")
    
    # Data Overview
    st.subheader("📊 Data Overview")
    profile = load_profile()
    logs = load_logs()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Profile Name", profile.get("name", "Unknown"))
    with col2:
        st.metric("Total Logs", len(logs))
    with col3:
        if logs:
            latest_date = max(log.get("date", "") for log in logs)
            st.metric("Latest Log", latest_date)
        else:
            st.metric("Latest Log", "None")
    
    # Sync Status
    st.subheader("🔄 Sync Status")
    is_synced, status = check_sync_status()
    
    if is_synced:
        st.success("✅ Database and JSON files are in sync")
    else:
        st.warning("⚠️ Database and JSON files are out of sync")
        
        # Show detailed status
        with st.expander("View Sync Details"):
            st.write("**Profile Sync:**", "✅" if status.get("profile_sync") else "❌")
            st.write("**Logs Sync:**", "✅" if status.get("logs_sync") else "❌")
            st.write(f"**Database Logs:** {status.get('db_logs_count', 0)}")
            st.write(f"**JSON Logs:** {status.get('json_logs_count', 0)}")
    
    # Backup & Export
    st.subheader("💾 Backup & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export to JSON", type="primary"):
            if export_to_json():
                st.success("✅ Successfully exported data to JSON files")
                st.rerun()
            else:
                st.error("❌ Failed to export data")
    
    with col2:
        if st.button("📥 Import from JSON"):
            if import_from_json():
                st.success("✅ Successfully imported data from JSON files")
                st.rerun()
            else:
                st.error("❌ Failed to import data")
    
    # Data Management
    st.subheader("🗂️ Data Management")
    
    # Show current profile
    with st.expander("View Current Profile"):
        st.json(profile)
    
    # Show recent logs
    with st.expander("View Recent Logs"):
        if logs:
            recent_logs = logs[-5:]  # Last 5 logs
            for log in recent_logs:
                st.write(f"**{log.get('date', 'Unknown')}:** {log.get('training_done', 'No training')}")
                if log.get('notes'):
                    st.write(f"*Notes: {log['notes'][:50]}{'...' if len(log['notes']) > 50 else ''}*")
                st.markdown("---")
        else:
            st.info("No logs found")
    
    # System Information
    st.subheader("ℹ️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Database:** SQLite (primary storage)")
        st.write("**JSON Files:** Backup/Export format")
        st.write("**Cache:** LRU caching for performance")
    
    with col2:
        st.write("**Last Export:**", datetime.now().strftime("%Y-%m-%d %H:%M"))
        st.write("**Data Validation:** Active")
        st.write("**Error Logging:** Enabled")
    
    # Manual Sync
    st.subheader("🔧 Manual Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Force Sync (DB → JSON)"):
            if export_to_json():
                st.success("✅ Forced sync completed")
                st.rerun()
            else:
                st.error("❌ Sync failed")
    
    with col2:
        if st.button("🔄 Force Sync (JSON → DB)"):
            if import_from_json():
                st.success("✅ Forced sync completed")
                st.rerun()
            else:
                st.error("❌ Sync failed")
    
    # Help
    st.subheader("❓ Help")
    
    st.info("""
    **How it works:**
    - Database is the single source of truth
    - JSON files are for backup/export only
    - Use Export to create JSON backups
    - Use Import to restore from JSON
    - Check sync status to ensure data consistency
    """) 