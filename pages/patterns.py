import streamlit as st
import statistics
import json
from coach_core.data import load_logs
from coach_core.ai import AICoach
from coach_core.utils import detect_split

def pattern_analysis_page(logs):
    st.header("📊 Advanced Pattern Analysis")
    
    if not logs:
        st.warning("No data to analyze yet. Start logging to see patterns!")
        return
    
    # AI Coach pattern analysis using core module
    ai_coach = AICoach()
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