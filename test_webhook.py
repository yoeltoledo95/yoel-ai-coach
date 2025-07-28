#!/usr/bin/env python3
"""
Test webhook processing
"""
import json
import requests

def test_webhook():
    """Test webhook message processing"""
    
    # Test data
    test_message = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "1234567890",
                        "phone_number_id": "740200925838968"
                    },
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": "1234567890"
                    }],
                    "messages": [{
                        "from": "1234567890",
                        "id": "test_message_id",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Hello, can you help me with a workout plan?"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    # Send test message
    response = requests.post(
        "http://localhost:8000/webhook",
        headers={"Content-Type": "application/json"},
        json=test_message
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_webhook() 