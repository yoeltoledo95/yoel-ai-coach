"""
Use case: Analyze user training patterns
"""
from typing import Dict, Any
from domain.services.coaching_service import CoachingService
from shared.logging import get_logger

logger = get_logger(__name__)


class AnalyzeUserPatternsUseCase:
    """Use case for analyzing user training patterns"""
    
    def __init__(self, coaching_service: CoachingService):
        self.coaching_service = coaching_service
    
    def execute(self, user_id: str) -> Dict[str, Any]:
        """Execute the use case"""
        try:
            logger.info(f"Analyzing patterns for user {user_id}")
            
            # Analyze user progress
            analysis = self.coaching_service.analyze_user_progress(user_id)
            
            # Add additional insights
            user = self.coaching_service.user_repository.get_user(user_id)
            if user:
                analysis["user_profile"] = {
                    "goals": user.get_goals_summary(),
                    "level": user.profile.level.value,
                    "injury_history": user.profile.injury_history
                }
            
            logger.info(f"Completed pattern analysis for user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for user {user_id}: {e}")
            return {
                "error": "Failed to analyze patterns",
                "message": str(e)
            } 