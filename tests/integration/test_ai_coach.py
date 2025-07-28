#!/usr/bin/env python3
"""
Test script for enhanced AI coach functionality
"""

import os
from dotenv import load_dotenv
load_dotenv()

from coach_core.ai import AICoach

def test_ai_coach():
    """Test the enhanced AI coach functionality"""
    print("🧪 Testing Enhanced AI Coach")
    print("=" * 50)
    
    # Initialize AI coach
    coach = AICoach()
    
    print(f"✅ AI Coach initialized")
    print(f"📊 Profile loaded: {bool(coach.profile)}")
    print(f"📈 Logs loaded: {len(coach.logs) if coach.logs else 0} entries")
    print(f"🤖 OpenAI client: {'✅' if coach.client else '❌'}")
    
    # Test pattern analysis
    print("\n📊 Testing Pattern Analysis:")
    patterns = coach.analyze_patterns()
    if "error" not in patterns:
        print("✅ Pattern analysis working")
        training_freq = patterns.get('training_frequency', {})
        print(f"  • Training frequency: {training_freq.get('frequency', 0):.1%}")
        print(f"  • Consistency: {training_freq.get('consistency', 'unknown')}")
    else:
        print(f"❌ Pattern analysis failed: {patterns['error']}")
    
    # Test mentor-powered responses
    test_questions = [
        "I'm feeling tired today, what should I do?",
        "What should I train today?",
        "My shoulder is bothering me",
        "What should I eat for recovery?"
    ]
    
    print("\n🤖 Testing Mentor-Powered Responses:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        response = coach.get_mentor_powered_response(question)
        print(f"   Response: {response[:100]}...")
    
    # Test weekly plan generation
    print("\n📅 Testing Weekly Plan Generation:")
    weekly_plan = coach.get_weekly_plan()
    if "Error" not in weekly_plan:
        print("✅ Weekly plan generated successfully")
        print(f"   Length: {len(weekly_plan)} characters")
    else:
        print(f"❌ Weekly plan failed: {weekly_plan}")
    
    # Test relevant mentor selection
    print("\n🎯 Testing Relevant Mentor Selection:")
    test_inputs = [
        "I need help with yoga and balance",
        "My shoulder injury is flaring up",
        "I want to improve my movement flow",
        "What's the best way to train for longevity?"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        relevant_mentors = coach._get_relevant_mentors(test_input)
        print(f"{i}. Input: {test_input}")
        print(f"   Relevant mentors: {relevant_mentors}")
    
    print("\n" + "=" * 50)
    print("✅ AI Coach test completed")

if __name__ == "__main__":
    test_ai_coach() 