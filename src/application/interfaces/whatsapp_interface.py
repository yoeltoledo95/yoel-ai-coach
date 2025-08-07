"""
WhatsApp interface - handles incoming messages and routes to use cases
"""
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
from infrastructure.external.whatsapp_client import WhatsAppClient
from application.use_cases.get_coaching_response import GetCoachingResponseUseCase
from application.use_cases.create_weekly_plan import CreateWeeklyPlanUseCase
from application.use_cases.analyze_user_patterns import AnalyzeUserPatternsUseCase
from shared.logging import get_logger

logger = get_logger(__name__)


class WhatsAppInterface:
    """WhatsApp interface for handling messages"""
    
    def __init__(
        self,
        whatsapp_client: WhatsAppClient,
        coaching_response_use_case: GetCoachingResponseUseCase,
        create_weekly_plan_use_case: CreateWeeklyPlanUseCase,
        analyze_patterns_use_case: AnalyzeUserPatternsUseCase
    ):
        self.whatsapp_client = whatsapp_client
        self.coaching_response_use_case = coaching_response_use_case
        self.create_weekly_plan_use_case = create_weekly_plan_use_case
        self.analyze_patterns_use_case = analyze_patterns_use_case
        
        # Conversation memory for context
        self.conversation_memory = {}
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/webhook', methods=['GET'])
        def verify_webhook():
            """Verify webhook for WhatsApp API"""
            try:
                mode = request.args.get('hub.mode')
                token = request.args.get('hub.verify_token')
                challenge = request.args.get('hub.challenge')
                
                if mode and token and challenge:
                    result = self.whatsapp_client.verify_webhook(mode, token, challenge)
                    if result:
                        return challenge
                
                return 'Forbidden', 403
                
            except Exception as e:
                logger.error(f"Error verifying webhook: {e}")
                return 'Internal Server Error', 500
        
        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            """Handle incoming webhook messages"""
            try:
                data = request.get_json()
                
                # Process the webhook message
                message_info = self.whatsapp_client.process_webhook_message(data)
                
                if "error" in message_info:
                    logger.error(f"Error processing webhook: {message_info['error']}")
                    return 'OK', 200
                
                # Extract message details
                user_id = message_info.get("user_id")
                user_name = message_info.get("user_name", "User")
                message_text = message_info.get("text", "")
                message_type = message_info.get("message_type")
                
                if not user_id or not message_text:
                    return 'OK', 200
                
                # Route message to appropriate use case
                response = self._route_message(user_id, message_text, message_type, user_name)
                
                # Send response back to user (only once)
                if response and response.strip():
                    success = self.whatsapp_client.send_message(user_id, response)
                    if not success:
                        logger.error(f"Failed to send message to user {user_id}")
                
                return 'OK', 200
                
            except Exception as e:
                logger.error(f"Error handling webhook: {e}")
                return 'Internal Server Error', 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "service": "AI Coach WhatsApp Bot"
            })
    
    def _route_message(self, user_id: str, message: str, message_type: str, user_name: str = "User") -> str:
        """Route message to appropriate use case"""
        try:
            message_lower = message.lower().strip()
            
            # Update conversation memory
            if user_id not in self.conversation_memory:
                self.conversation_memory[user_id] = {}
            
            self.conversation_memory[user_id]["last_message"] = message
            self.conversation_memory[user_id]["timestamp"] = "now"
            
            # Handle greetings first
            greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "sup", "what's up"]
            if any(greeting in message_lower for greeting in greetings):
                return self._handle_greeting(user_id, message)
            
            # Route based on message content
            if any(keyword in message_lower for keyword in ["plan", "schedule", "weekly"]):
                # Create weekly plan
                plan = self.create_weekly_plan_use_case.execute(user_id)
                if "error" not in plan:
                    return f"Here's your personalized weekly plan:\n\n{plan.get('detailed_plan', 'Plan created successfully!')}"
                else:
                    return "I'm having trouble creating your weekly plan. Please try again later."
            
            elif any(keyword in message_lower for keyword in ["goal", "goals", "set goal", "new goal", "target"]):
                # Handle goal setting with AI
                context = self.conversation_memory.get(user_id, {})
                context["goal_setting"] = True
                return self.coaching_response_use_case.execute(user_id, message, {
                    "conversation_context": context
                }, user_name)
            
            elif any(keyword in message_lower for keyword in ["progress", "analysis", "stats", "pattern"]):
                # Analyze user patterns
                analysis = self.analyze_patterns_use_case.execute(user_id)
                if "error" not in analysis:
                    return self._format_analysis_response(analysis)
                else:
                    return "I'm having trouble analyzing your progress. Please try again later."
            
            elif message_lower in ["?", "what", "how", "why", "explain"]:
                # Handle follow-up questions with AI
                context = self.conversation_memory.get(user_id, {})
                return self.coaching_response_use_case.execute(user_id, message, {
                    "conversation_context": context,
                    "follow_up_question": True
                }, user_name)
            
            else:
                # Get general coaching response
                return self.coaching_response_use_case.execute(user_id, message, {}, user_name)
                
        except Exception as e:
            logger.error(f"Error routing message for user {user_id}: {e}")
            return "I'm having trouble processing your message. Please try again later."
    
    def _handle_greeting(self, user_id: str, message: str) -> str:
        """Handle greeting messages"""
        return f"""Hey there! 👋 

I'm your AI fitness coach, ready to help you crush your fitness goals! 

What would you like to work on today?
• 💪 Get a personalized workout plan
• 📊 Check your progress and patterns  
• 🎯 Set new goals or update your profile
• ❓ Ask me anything about fitness and movement

Just let me know what you need!"""
    
    def _format_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Format analysis response for WhatsApp"""
        response = "📊 Your Training Analysis:\n\n"
        
        if "total_sessions" in analysis:
            response += f"• Total sessions: {analysis['total_sessions']}\n"
        
        if "frequency" in analysis:
            response += f"• Training frequency: {analysis['frequency']:.1f} sessions/week\n"
        
        if "avg_duration" in analysis:
            response += f"• Average session duration: {analysis['avg_duration']:.0f} minutes\n"
        
        if "recommendations" in analysis:
            response += "\n💡 Recommendations:\n"
            for rec in analysis['recommendations'][:3]:  # Top 3 recommendations
                response += f"• {rec}\n"
        
        return response
    

    
    def run(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """Run the Flask application"""
        logger.info(f"Starting WhatsApp interface on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug) 