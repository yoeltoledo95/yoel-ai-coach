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
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()
from coach_core.ai import AICoach
from coach_core.data import load_profile, load_logs, save_logs
from coach_core.user_memory import user_memory_db
import openai
from pathlib import Path

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

# Initialize OpenAI client (new API)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        content = response.choices[0].message.content
        if content is not None:
            extracted = json.loads(content)
        else:
            extracted = {key: None for key in EXTRACTION_KEYS}
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

def download_whatsapp_image(media_id: str) -> Optional[bytes]:
    """Download image from WhatsApp API using media_id"""
    try:
        # Step 1: Get the media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {'Authorization': f'Bearer {WHATSAPP_API_TOKEN}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"❌ Failed to get media URL: {response.status_code}")
            return None
            
        media_data = response.json()
        media_url = media_data.get('url')
        
        if not media_url:
            logger.error("❌ No media URL in response")
            return None
        
        # Step 2: Download the actual image
        image_response = requests.get(media_url, headers=headers)
        if image_response.status_code != 200:
            logger.error(f"❌ Failed to download image: {image_response.status_code}")
            return None
            
        return image_response.content
        
    except Exception as e:
        logger.error(f"❌ Error downloading image: {e}")
        return None

def save_training_image(user_id: str, image_data: bytes, caption: str = "") -> Optional[str]:
    """Save training image to disk and return file path"""
    try:
        # Create training_images directory if it doesn't exist
        training_dir = Path("training_images")
        training_dir.mkdir(exist_ok=True)
        
        # Create user-specific subdirectory
        user_dir = training_dir / user_id
        user_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"training_{timestamp}.jpg"
        filepath = user_dir / filename
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"✅ Saved training image: {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"❌ Error saving training image: {e}")
        return None

def handle_training_image(message: Dict[str, Any], user_id: str):
    """Handle incoming training image from WhatsApp"""
    try:
        # Extract image data from WhatsApp message
        image_data = message.get('image', {})
        media_id = image_data.get('id')
        caption = image_data.get('caption', '')
        mime_type = image_data.get('mime_type', 'image/jpeg')
        
        if not media_id:
            logger.error("❌ No media_id in image message")
            send_whatsapp_message(user_id, "Sorry, I couldn't process that image. Please try again.")
            return
        
        logger.info(f"📸 Processing training image from {user_id}")
        logger.info(f"📝 Caption: {caption}")
        
        # Download the image
        image_bytes = download_whatsapp_image(media_id)
        if not image_bytes:
            send_whatsapp_message(user_id, "Sorry, I couldn't download your training image. Please try again.")
            return
        
        # Save the image
        image_path = save_training_image(user_id, image_bytes, caption)
        if not image_path:
            send_whatsapp_message(user_id, "Sorry, I couldn't save your training image. Please try again.")
            return
        
        # Create training log entry
        training_log = {
            "type": "training_image",
            "image_path": image_path,
            "caption": caption,
            "timestamp": datetime.now().isoformat(),
            "mime_type": mime_type
        }
        
        # Store in database
        success = user_memory_db.store_training_image(user_id, training_log)
        
        if success:
            # Generate AI response about the training image
            ai_response = generate_training_image_response(caption, user_id)
            send_whatsapp_message(user_id, ai_response)
            logger.info(f"✅ Training image logged for {user_id}")
        else:
            send_whatsapp_message(user_id, "I saved your training image but had trouble logging it. Your progress is still recorded!")
            
    except Exception as e:
        logger.error(f"❌ Error handling training image: {e}")
        send_whatsapp_message(user_id, "Sorry, I encountered an error processing your training image. Please try again.")

def generate_training_image_response(caption: str, user_id: str) -> str:
    """Generate AI response for training image"""
    try:
        # Get user context for personalized response
        user_profile = user_memory_db.get_user_profile(user_id)
        recent_interactions = user_memory_db.get_user_recent_interactions(user_id, limit=5)
        
        context = f"User sent a training image with caption: '{caption}'. "
        if user_profile:
            context += f"User goals: {user_profile.get('current_goals', 'Not specified')}. "
        
        prompt = (
            f"{context}\n\n"
            "This is a training image from a WhatsApp fitness coaching session. "
            "Provide a brief, encouraging response that acknowledges their training effort. "
            "Keep it under 100 words and focus on motivation and progress tracking."
        )
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        return content if content else "Great training! Keep up the excellent work! 💪"
        
    except Exception as e:
        logger.error(f"❌ Error generating training image response: {e}")
        return "Great training! I've logged your progress. Keep pushing forward! 💪"

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
                    
                    # Handle different message types
                    if message.get('type') == 'text':
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

                    elif message.get('type') == 'image':
                        # Handle image message for training logs
                        handle_training_image(message, user_id)
                        
                    else:
                        logger.info(f"Received unsupported message type: {message.get('type')}")

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