"""
WhatsApp client with proper error handling
"""
import logging
import requests
from typing import Dict, Any, Optional
from shared.exceptions import WhatsAppError, ConfigurationError
from infrastructure.config.settings import config

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp client with error handling"""
    
    def __init__(self):
        if not config.whatsapp.api_token:
            raise ConfigurationError("WhatsApp API token is required")
        
        self.api_token = config.whatsapp.api_token
        self.phone_number_id = config.whatsapp.phone_number_id
        self.api_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
    
    def send_message(self, phone_number: str, message: str) -> bool:
        """Send a WhatsApp message"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ WhatsApp message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"❌ Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ WhatsApp API timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending WhatsApp message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending WhatsApp message: {e}")
            return False
    
    def send_template_message(
        self, 
        phone_number: str, 
        template_name: str, 
        parameters: Dict[str, Any]
    ) -> bool:
        """Send a WhatsApp template message"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": str(value)}
                                for value in parameters.values()
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ WhatsApp template message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"❌ Failed to send WhatsApp template message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp template message: {e}")
            return False
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook for WhatsApp API"""
        try:
            if mode == "subscribe" and token == config.whatsapp.webhook_secret:
                logger.info("✅ Webhook verification successful")
                return challenge
            else:
                logger.warning("⚠️ Webhook verification failed")
                return None
        except Exception as e:
            logger.error(f"❌ Error verifying webhook: {e}")
            return None
    
    def process_webhook_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook message"""
        try:
            # Debug: Log the entire webhook payload
            logger.info(f"🔍 Raw webhook payload: {message_data}")
            
            # Extract message information
            entry = message_data.get("entry", [{}])[0]
            logger.info(f"🔍 Entry: {entry}")
            
            changes = entry.get("changes", [{}])[0]
            logger.info(f"🔍 Changes: {changes}")
            
            value = changes.get("value", {})
            logger.info(f"🔍 Value: {value}")
            
            # Check if this is a status update (not a user message)
            if "statuses" in value:
                logger.debug("Ignoring status update webhook")
                return {"error": "Status update - not a user message"}
            
            # Check if this is a message
            messages = value.get("messages", [])
            logger.info(f"🔍 Messages: {messages}")
            
            if not messages:
                logger.debug("No user messages found in webhook")
                return {"error": "No messages found in webhook"}
            
            message = messages[0]
            logger.info(f"🔍 Individual message: {message}")
            
            message_type = message.get("type", "text")
            
            # Only process text messages for now
            if message_type != "text":
                logger.info(f"Ignoring non-text message type: {message_type}")
                return {"error": f"Unsupported message type: {message_type}"}
            
            # Extract text content
            text_content = ""
            if message_type == "text":
                text_content = message.get("text", {}).get("body", "")
            
            if not text_content.strip():
                logger.debug("Empty text message")
                return {"error": "Empty message content"}
            
            # Extract user ID - try different possible fields
            user_id = message.get("from")
            if not user_id:
                # Try alternative fields that might contain the user ID
                user_id = message.get("sender", {}).get("id") if isinstance(message.get("sender"), dict) else None
                if not user_id:
                    user_id = message.get("author", {}).get("id") if isinstance(message.get("author"), dict) else None
                if not user_id:
                    user_id = message.get("contact", {}).get("wa_id") if isinstance(message.get("contact"), dict) else None
            
            # Extract user name from contacts
            user_name = "User"
            contacts = value.get("contacts", [])
            if contacts:
                contact = contacts[0]
                profile = contact.get("profile", {})
                user_name = profile.get("name", "User")
            
            logger.info(f"🔍 Extracted user_id: {user_id}")
            logger.info(f"🔍 Extracted user_name: {user_name}")
            logger.info(f"Processing message from {user_id}: {text_content[:50]}...")
            
            return {
                "user_id": user_id,
                "user_name": user_name,
                "message_type": message_type,
                "timestamp": message.get("timestamp"),
                "text": text_content,
                "media_id": message.get("image", {}).get("id") if message_type == "image" else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing webhook message: {e}")
            return {"error": f"Failed to process webhook message: {e}"} 