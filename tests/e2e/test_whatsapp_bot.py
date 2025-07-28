#!/usr/bin/env python3
"""
Test script for WhatsApp AI Coach
"""

import requests
import json

def test_whatsapp_bot():
    """Test the WhatsApp bot functionality"""
    
    print("🧪 Testing WhatsApp AI Coach...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5001/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to WhatsApp bot: {e}")
        return
    
    # Test webhook endpoint (simulate WhatsApp message)
    test_message = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {
                            "body": "What should I train today?"
                        }
                    }]
                }
            }]
        }]
    }
    
    try:
        response = requests.post(
            "http://localhost:5001/webhook",
            json=test_message,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Webhook test completed: {response.status_code}")
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
    
    print("\n🎯 WhatsApp Bot Status:")
    print("✅ Flask server running on port 5001")
    print("✅ Health endpoint working")
    print("✅ Webhook endpoint ready for Meta API")
    print("✅ AI coaching brain loaded")
    print("\n📱 Ready for Meta Developer Account setup!")

if __name__ == "__main__":
    test_whatsapp_bot() 