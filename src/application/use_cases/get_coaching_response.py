"""
Use case: Get personalized coaching response
"""
from typing import Dict, Any, Optional
from domain.services.coaching_service import CoachingService
from infrastructure.external.openai_client import OpenAIClient
from shared.logging import get_logger

logger = get_logger(__name__)


class GetCoachingResponseUseCase:
    """Use case for getting personalized coaching responses"""
    
    def __init__(
        self, 
        coaching_service: CoachingService,
        ai_client: OpenAIClient
    ):
        self.coaching_service = coaching_service
        self.ai_client = ai_client
    
    def execute(
        self, 
        user_id: str, 
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute the use case"""
        try:
            logger.info(f"Getting coaching response for user {user_id}")
            
            # Get personalized response from coaching service
            response = self.coaching_service.get_personalized_response(
                user_id=user_id,
                user_input=user_input,
                context=context
            )
            
            # If coaching service returns a basic response, enhance it with AI
            if "Based on your profile" in response:
                # Get user context for AI enhancement
                user = self.coaching_service.user_repository.get_user(user_id)
                if user:
                    ai_context = {
                        "user_profile": user.profile.__dict__,
                        "recent_sessions": [s.__dict__ for s in user.get_recent_sessions(7)],
                        "patterns": self.coaching_service._analyze_user_patterns(user),
                        "mentor_context": self.coaching_service.mentor_repository.get_mentor_context(user_input)
                    }
                    
                    response = self.ai_client.generate_coaching_response(
                        user_input=user_input,
                        context=ai_context
                    )
            
            logger.info(f"Generated coaching response for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting coaching response for user {user_id}: {e}")
            return "I'm having trouble processing your request right now. Please try again later."
    
    def extract_user_info(self, user_input: str) -> Dict[str, Any]:
        """Extract structured information from user input"""
        extraction_keys = [
            "goals", "achievements", "struggles", "injuries", "weekly_reflection",
            "preferences", "feedback", "session_log", "questions", "mood",
            "intentions", "lifestyle", "milestones"
        ]
        
        try:
            return self.ai_client.extract_information(user_input, extraction_keys)
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
            return {key: None for key in extraction_keys}
    
    def analyze_sentiment(self, user_input: str) -> Dict[str, Any]:
        """Analyze sentiment and mood from user input"""
        try:
            return self.ai_client.analyze_sentiment(user_input)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "mood": "unknown",
                "energy_level": 5,
                "confidence": 0.5
            } 