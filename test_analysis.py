#!/usr/bin/env python3
"""
Test script for analysis module functionality
"""

import json
from datetime import datetime, timedelta
from coach_core.analysis import analyze_patterns, calculate_recovery_score, calculate_training_volume

def test_analysis():
    """Test the analysis functionality"""
    print("🧪 Testing Analysis Module")
    print("=" * 50)
    
    # Sample logs for testing
    sample_logs = [
        {
            "date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
            "mood": "great",
            "energy": 8,
            "sleep_hours": 8.5,
            "soreness": 3,
            "training_done": "Mobility session - shoulder work",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 8
        },
        {
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "mood": "good",
            "energy": 7,
            "sleep_hours": 7.5,
            "soreness": 4,
            "training_done": "Strength training - squats and deadlifts",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 7
        },
        {
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "mood": "tired",
            "energy": 5,
            "sleep_hours": 6.5,
            "soreness": 6,
            "training_done": "Light mobility and stretching",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 5
        },
        {
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "mood": "good",
            "energy": 7,
            "sleep_hours": 8.0,
            "soreness": 4,
            "training_done": "Movement flow - handstands and mobility",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 7
        },
        {
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "mood": "excellent",
            "energy": 9,
            "sleep_hours": 8.5,
            "soreness": 2,
            "training_done": "Intense strength session - max effort",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 9
        },
        {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "mood": "good",
            "energy": 6,
            "sleep_hours": 7.0,
            "soreness": 5,
            "training_done": "Recovery day - light stretching",
            "nutrition": "Good",
            "hydration": "Good",
            "recovery_score": 6
        }
    ]
    
    print(f"📊 Analyzing {len(sample_logs)} days of training data")
    
    # Test pattern analysis
    analysis = analyze_patterns(sample_logs, days=7)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return
    
    print("✅ Pattern analysis completed successfully")
    print("\n📈 Key Insights:")
    
    # Training frequency
    training_freq = analysis.get('training_frequency', {})
    print(f"  • Training frequency: {training_freq.get('frequency', 0):.1%}")
    print(f"  • Consistency: {training_freq.get('consistency', 'unknown')}")
    
    # Recovery trends
    recovery = analysis.get('recovery_trends', {})
    print(f"  • Recovery trend: {recovery.get('trend', 'unknown')}")
    print(f"  • Average recovery: {recovery.get('average', 'N/A')}/10")
    
    # Mood patterns
    mood = analysis.get('mood_patterns', {})
    print(f"  • Dominant mood: {mood.get('dominant_mood', 'unknown')}")
    
    # Sleep quality
    sleep = analysis.get('sleep_quality', {})
    print(f"  • Sleep quality: {sleep.get('quality', 'unknown')}")
    print(f"  • Average sleep: {sleep.get('average_hours', 'N/A')} hours")
    
    # Energy levels
    energy = analysis.get('energy_levels', {})
    print(f"  • Energy trend: {energy.get('trend', 'unknown')}")
    print(f"  • Average energy: {energy.get('average', 'N/A')}/10")
    
    # Recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Test recovery score calculation
    print("\n🧮 Testing Recovery Score Calculation:")
    for i, log in enumerate(sample_logs[-2:], 1):
        score = calculate_recovery_score(log)
        print(f"  Day {i}: Recovery score = {score}/10")
    
    # Test training volume calculation
    print("\n🏋️ Testing Training Volume Calculation:")
    for i, log in enumerate(sample_logs[-2:], 1):
        volume = calculate_training_volume(log)
        print(f"  Day {i}: Training volume = {volume}/10")
    
    print("\n" + "=" * 50)
    print("✅ Analysis module test completed")

if __name__ == "__main__":
    test_analysis() 