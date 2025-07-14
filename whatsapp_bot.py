#!/usr/bin/env python3
"""
Yoel's AI Coach - WhatsApp Bot (V2)
Movement-focused AI fitness coach via WhatsApp
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import Flask, request, jsonify
from coach_core.ai import AICoach
from coach_core.data import load_profile, load_logs, save_logs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# WhatsApp interactions file
WHATSAPP_INTERACTIONS_FILE = "whatsapp_interactions.json"

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
    # This will be implemented when you set up Meta developer account
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # TODO: Add your verify token here
    verify_token = "YOUR_VERIFY_TOKEN"
    
    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            return challenge
        else:
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
                    
                    # Get AI response
                    ai_response = whatsapp_coach.handle_message(user_message, user_id)
                    
                    # TODO: Send response back via WhatsApp API
                    logger.info(f"User {user_id}: {user_message}")
                    logger.info(f"AI Response: {ai_response}")
                    
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
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Yoel's AI Coach WhatsApp Bot (V2)")
    logger.info("📱 Movement-focused AI fitness coach")
    logger.info("🔄 Weekly coaching loop: Monday plan → daily feedback → Sunday reflection")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 