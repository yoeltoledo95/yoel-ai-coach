import streamlit as st
import pandas as pd
import plotly.express as px
import statistics
from coach_core.data import load_logs
from coach_core.utils import detect_split

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
                st.warning("⚠️ Your recovery scores are low. Consider more rest days.")
            elif avg_recovery > 8:
                st.success("✅ Great recovery! You're managing your training load well.")
        
        # Training frequency
        training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
        if training_days >= 5:
            st.info("🏋️ You're training frequently. Make sure to include recovery days!")
        elif training_days <= 2:
            st.warning("⚠️ Low training frequency. Consider adding more training days.") 