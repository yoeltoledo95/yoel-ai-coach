#!/usr/bin/env python3
"""
Test workout plan request
"""
import requests
import json

def test_workout_plan():
    """Test workout plan request"""
    
    test_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "messages": [{
                        "from": "1234567890",
                        "id": "test_id",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "I need a workout plan"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/webhook",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_workout_plan() 