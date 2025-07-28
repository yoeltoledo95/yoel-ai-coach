"""
Use case: Create personalized weekly training plan
"""
from typing import Dict, Any
from domain.services.coaching_service import CoachingService
from infrastructure.external.openai_client import OpenAIClient
from shared.logging import get_logger

logger = get_logger(__name__)


class CreateWeeklyPlanUseCase:
    """Use case for creating personalized weekly training plans"""
    
    def __init__(
        self, 
        coaching_service: CoachingService,
        ai_client: OpenAIClient
    ):
        self.coaching_service = coaching_service
        self.ai_client = ai_client
    
    def execute(self, user_id: str) -> Dict[str, Any]:
        """Execute the use case"""
        try:
            logger.info(f"Creating weekly plan for user {user_id}")
            
            # Get user and analyze patterns
            user = self.coaching_service.user_repository.get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            patterns = self.coaching_service._analyze_user_patterns(user)
            
            # Create plan using coaching service with workout programming knowledge
            plan = self.coaching_service.create_weekly_plan(user_id)
            
            # Format the plan for AI response
            plan_summary = self._format_plan_for_ai(plan)
            
            # Enhance plan with AI using programming guidelines
            if not plan.get("detailed_plan"):
                enhanced_plan = self.ai_client.create_weekly_plan(
                    user_profile=user.profile.__dict__,
                    patterns=patterns,
                    programming_guidelines=plan.get("programming_guidelines", {}),
                    weekly_template=plan.get("weekly_template", {})
                )
                plan["detailed_plan"] = enhanced_plan
            
            logger.info(f"Created weekly plan for user {user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error creating weekly plan for user {user_id}: {e}")
            return {
                "error": "Failed to create weekly plan",
                "message": str(e)
            }
    
    def _format_plan_for_ai(self, plan: Dict[str, Any]) -> str:
        """Format plan data for AI processing"""
        summary = []
        
        # Add weekly template
        if "weekly_template" in plan:
            summary.append("Weekly Schedule:")
            for day, focus in plan["weekly_template"].items():
                summary.append(f"  {day.title()}: {focus}")
        
        # Add programming guidelines
        if "programming_guidelines" in plan:
            guidelines = plan["programming_guidelines"]
            summary.append(f"\nProgramming Guidelines:")
            summary.append(f"  Volume: {guidelines.get('volume', 'N/A')}")
            summary.append(f"  Intensity: {guidelines.get('intensity', 'N/A')}")
            summary.append(f"  Frequency: {guidelines.get('frequency', 'N/A')}")
        
        # Add key principles
        if "key_principles" in plan:
            summary.append(f"\nKey Principles:")
            for principle in plan["key_principles"]:
                summary.append(f"  • {principle}")
        
        return "\n".join(summary) 