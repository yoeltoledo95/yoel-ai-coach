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
                message_text = message_info.get("text", "")
                message_type = message_info.get("message_type")
                
                if not user_id or not message_text:
                    return 'OK', 200
                
                # Route message to appropriate use case
                response = self._route_message(user_id, message_text, message_type)
                
                # Send response back to user
                if response:
                    self.whatsapp_client.send_message(user_id, response)
                
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
    
    def _route_message(self, user_id: str, message: str, message_type: str) -> str:
        """Route message to appropriate use case"""
        try:
            message_lower = message.lower()
            
            # Extract information from message
            extracted_info = self.coaching_response_use_case.extract_user_info(message)
            sentiment = self.coaching_response_use_case.analyze_sentiment(message)
            
            # Route based on message content
            if any(keyword in message_lower for keyword in ["plan", "schedule", "weekly"]):
                # Create weekly plan
                plan = self.create_weekly_plan_use_case.execute(user_id)
                if "error" not in plan:
                    return f"Here's your personalized weekly plan:\n\n{plan.get('detailed_plan', 'Plan created successfully!')}"
                else:
                    return "I'm having trouble creating your weekly plan. Please try again later."
            
            elif any(keyword in message_lower for keyword in ["progress", "analysis", "stats", "pattern"]):
                # Analyze user patterns
                analysis = self.analyze_patterns_use_case.execute(user_id)
                if "error" not in analysis:
                    return self._format_analysis_response(analysis)
                else:
                    return "I'm having trouble analyzing your progress. Please try again later."
            
            else:
                # Get general coaching response
                return self.coaching_response_use_case.execute(user_id, message, {
                    "extracted_info": extracted_info,
                    "sentiment": sentiment
                })
                
        except Exception as e:
            logger.error(f"Error routing message for user {user_id}: {e}")
            return "I'm having trouble processing your message. Please try again later."
    
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