#!/usr/bin/env python3
"""
Test script for User Memory Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coach_core.user_memory import user_memory_db

def test_user_memory_db():
    """Test the user memory database functionality"""
    print("🧪 Testing User Memory Database...")
    
    # Test data
    test_user_id = "test_user_123"
    test_message = "I want to do a handstand and I'm feeling tired today"
    test_ai_response = "Let's work on your handstand progress! Since you're tired, we'll focus on mobility and preparation work."
    test_extracted_info = {
        "goals": "handstand",
        "mood": "tired",
        "achievements": None,
        "struggles": None,
        "injuries": None,
        "weekly_reflection": None,
        "preferences": None,
        "feedback": None,
        "session_log": None,
        "questions": None,
        "intentions": None,
        "lifestyle": None,
        "milestones": None
    }
    
    try:
        # Test 1: Store interaction
        print("📝 Testing interaction storage...")
        success = user_memory_db.store_interaction(
            user_id=test_user_id,
            raw_message=test_message,
            ai_response=test_ai_response,
            extracted_info=test_extracted_info
        )
        
        if success:
            print("✅ Interaction stored successfully")
        else:
            print("❌ Failed to store interaction")
            return False
        
        # Test 2: Get user profile
        print("👤 Testing user profile retrieval...")
        profile = user_memory_db.get_user_profile(test_user_id)
        if profile:
            print(f"✅ User profile found: {profile['user_id']}")
        else:
            print("❌ User profile not found")
            return False
        
        # Test 3: Get recent interactions
        print("💬 Testing recent interactions retrieval...")
        interactions = user_memory_db.get_user_recent_interactions(test_user_id, limit=5)
        if interactions:
            print(f"✅ Found {len(interactions)} recent interactions")
        else:
            print("❌ No interactions found")
            return False
        
        # Test 4: Get user goals
        print("🎯 Testing goals retrieval...")
        goals = user_memory_db.get_user_goals(test_user_id)
        if goals:
            print(f"✅ Found goals: {goals}")
        else:
            print("❌ No goals found")
            return False
        
        # Test 5: Get weekly interactions
        print("📅 Testing weekly interactions retrieval...")
        weekly = user_memory_db.get_weekly_interactions(test_user_id, days=7)
        if weekly:
            print(f"✅ Found {len(weekly)} interactions in the last 7 days")
        else:
            print("❌ No weekly interactions found")
            return False
        
        print("🎉 All tests passed! User Memory Database is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_user_memory_db() 