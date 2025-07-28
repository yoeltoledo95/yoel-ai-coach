#!/usr/bin/env python3
"""
Test script for enhanced AI coach with RAG integration
"""

import os
from dotenv import load_dotenv
load_dotenv()

from coach_core.ai import AICoach
from coach_core.mentor_brain import get_mentor_statistics

def test_enhanced_ai():
    """Test the enhanced AI coach with RAG integration"""
    print("🧪 Testing Enhanced AI Coach with RAG")
    print("=" * 50)
    
    # Initialize AI coach
    coach = AICoach()
    
    print(f"✅ AI Coach initialized")
    print(f"📊 Profile loaded: {bool(coach.profile)}")
    print(f"📈 Logs loaded: {len(coach.logs) if coach.logs else 0} entries")
    print(f"🤖 OpenAI client: {'✅' if coach.client else '❌'}")
    
    # Check RAG system status
    print("\n📚 RAG System Status:")
    stats = get_mentor_statistics()
    if 'error' not in stats:
        print(f"  • Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  • Unique mentors: {stats.get('unique_mentors', 0)}")
        print(f"  • Mentors: {', '.join(stats.get('mentors', []))}")
    else:
        print(f"  ❌ Error: {stats['error']}")
    
    # Test RAG-powered responses
    test_questions = [
        "I want to improve my handstand control",
        "How should I train for natural movement?",
        "My shoulder is bothering me during training",
        "What's the best way to build movement flow?",
        "I'm feeling tired, what should I do?"
    ]
    
    print("\n🤖 Testing RAG-Powered Responses:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        response = coach.get_mentor_powered_response(question)
        print(f"   Response: {response[:150]}...")
    
    # Test weekly plan generation
    print("\n📅 Testing RAG-Powered Weekly Plan:")
    weekly_plan = coach.get_weekly_plan()
    if "Error" not in weekly_plan:
        print("✅ Weekly plan generated successfully")
        print(f"   Length: {len(weekly_plan)} characters")
        print(f"   Preview: {weekly_plan[:200]}...")
    else:
        print(f"❌ Weekly plan failed: {weekly_plan}")
    
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
    
    print("\n" + "=" * 50)
    print("✅ Enhanced AI coach test completed")

if __name__ == "__main__":
    test_enhanced_ai() 