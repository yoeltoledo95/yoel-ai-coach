#!/usr/bin/env python3
"""
Yoel's AI Coach - WhatsApp Bot (V2)
Movement-focused AI fitness coach via WhatsApp
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import Flask, request, jsonify
from coach_core.ai import AICoach
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.user_memory import user_memory_db
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# WhatsApp API Configuration
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')  # Add your phone number ID here
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# WhatsApp interactions file
WHATSAPP_INTERACTIONS_FILE = "whatsapp_interactions.json"

# Extraction categories
EXTRACTION_KEYS = [
    "goals", "achievements", "struggles", "injuries", "weekly_reflection",
    "preferences", "feedback", "session_log", "questions", "mood",
    "intentions", "lifestyle", "milestones"
]

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_whatsapp_interactions() -> List[Dict[str, Any]]:
    """Load WhatsApp interactions from file"""
    try:
        with open(WHATSAPP_INTERACTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_whatsapp_interactions(interactions: List[Dict[str, Any]]):
    """Save WhatsApp interactions to file"""
    try:
        with open(WHATSAPP_INTERACTIONS_FILE, "w") as f:
            json.dump(interactions, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving WhatsApp interactions: {e}")

def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """Send a WhatsApp message using Meta's Cloud API"""
    try:
        headers = {
            'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp message sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"❌ Failed to send WhatsApp message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {e}")
        return False

def ai_extract_info(user_message):
    prompt = (
        "Extract all relevant fitness coaching information from the following message.\n"
        f"Return a JSON object with these keys: {', '.join(EXTRACTION_KEYS)}.\n"
        "If a category is not present, return null for that key.\n"
        f"Message: '{user_message}'"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        extracted = json.loads(response['choices'][0]['message']['content'])
    except Exception as e:
        logger.error(f"Error parsing extraction JSON: {e}")
        extracted = {key: None for key in EXTRACTION_KEYS}
    return extracted

def log_raw_message(user_id, user_message):
    logger.info(f"User {user_id} message: {user_message}")
    # Optionally, append to a file or database

def log_extracted_info(user_id, extracted_info):
    logger.info(f"Extracted info for {user_id}: {json.dumps(extracted_info, indent=2)}")
    # Optionally, append to a file or database

def update_database(user_id, user_message, ai_response, extracted_info):
    """Update user memory database with extracted information"""
    try:
        # Store the interaction in the database
        success = user_memory_db.store_interaction(
            user_id=user_id,
            raw_message=user_message,
            ai_response=ai_response,
            extracted_info=extracted_info
        )
        
        if success:
            logger.info(f"✅ Updated database for user {user_id}")
        else:
            logger.error(f"❌ Failed to update database for user {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Error updating database: {e}")

class WhatsAppCoach:
    """WhatsApp AI Fitness Coach"""
    
    def __init__(self):
        self.ai_coach = AICoach()
        self.profile = load_profile()
        self.logs = load_logs()
        
    def handle_message(self, user_message: str, user_id: str) -> str:
        """Handle incoming WhatsApp message and return AI response"""
        try:
            # Get AI response using existing coaching brain
            response = self.ai_coach.get_ai_response(user_message)
            
            # Log the interaction
            self._log_interaction(user_id, user_message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return "Sorry, I'm having trouble right now. Let me know how your movement feels today!"
    
    def _log_interaction(self, user_id: str, user_message: str, ai_response: str):
        """Log the WhatsApp interaction"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response
        }
        
        # Load existing interactions and add new one
        interactions = load_whatsapp_interactions()
        interactions.append(interaction)
        save_whatsapp_interactions(interactions)
    
    def get_weekly_plan(self, user_id: str) -> str:
        """Generate weekly movement plan"""
        try:
            # Use existing AI coach to generate weekly plan
            return self.ai_coach.get_weekly_plan()
        except Exception as e:
            logger.error(f"Error generating weekly plan: {e}")
            return "I'll generate your weekly plan soon. For now, focus on gentle movement and listen to your body!"

# Initialize the WhatsApp coach
whatsapp_coach = WhatsAppCoach()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp API"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Use environment variable for verify token
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "yoel_secret_token")

    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            logger.info("✅ Webhook verification successful")
            return challenge, 200
        else:
            logger.error("❌ Webhook verification failed")
            return 'Forbidden', 403

    return 'Bad Request', 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        # Extract message data
        if 'entry' in data and len(data['entry']) > 0:
            entry = data['entry'][0]
            if 'changes' in entry and len(entry['changes']) > 0:
                change = entry['changes'][0]
                if 'value' in change and 'messages' in change['value']:
                    message = change['value']['messages'][0]
                    user_id = message['from']
                    user_message = message['text']['body']

                    # 1. Log raw message
                    log_raw_message(user_id, user_message)

                    # 2. Extract info using OpenAI
                    extracted_info = ai_extract_info(user_message)

                    # 3. Log extracted info
                    log_extracted_info(user_id, extracted_info)

                    # 4. Get AI response (existing logic)
                    ai_response = whatsapp_coach.handle_message(user_message, user_id)

                    # 5. Update database with all information
                    update_database(user_id, user_message, ai_response, extracted_info)

                    # Send response back via WhatsApp API
                    if send_whatsapp_message(user_id, ai_response):
                        logger.info(f"✅ User {user_id}: {user_message}")
                        logger.info(f"✅ AI Response sent: {ai_response}")
                    else:
                        logger.error(f"❌ Failed to send response to {user_id}")

                    return jsonify({'status': 'success'})

        return jsonify({'status': 'no_message'})
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'whatsapp_token_configured': bool(WHATSAPP_API_TOKEN),
        'phone_number_id_configured': bool(WHATSAPP_PHONE_NUMBER_ID)
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Yoel's AI Coach WhatsApp Bot (V2)")
    logger.info("📱 Movement-focused AI fitness coach")
    logger.info("🔄 Weekly coaching loop: Monday plan → daily feedback → Sunday reflection")
    
    if WHATSAPP_API_TOKEN:
        logger.info("✅ WhatsApp API token configured")
    else:
        logger.warning("⚠️ WhatsApp API token not configured")
    
    if WHATSAPP_PHONE_NUMBER_ID:
        logger.info("✅ WhatsApp Phone Number ID configured")
    else:
        logger.warning("⚠️ WhatsApp Phone Number ID not configured")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True) 