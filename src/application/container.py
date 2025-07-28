"""
Dependency injection container for the AI coach application
"""
from typing import Dict, Any
from domain.repositories.user_repository import UserRepository
from domain.repositories.exercise_repository import ExerciseRepository
from domain.repositories.mentor_repository import MentorRepository
from domain.services.coaching_service import CoachingService
from infrastructure.database.sqlite.database import CoachDatabase
from infrastructure.database.sqlite.exercise_repository import SQLiteExerciseRepository
from infrastructure.database.vector_store.rag_system import MentorRAGSystem
from infrastructure.external.openai_client import OpenAIClient
from infrastructure.external.whatsapp_client import WhatsAppClient
from infrastructure.external.prompt_engine import PromptEngine
from application.use_cases.get_coaching_response import GetCoachingResponseUseCase
from application.use_cases.create_weekly_plan import CreateWeeklyPlanUseCase
from application.use_cases.analyze_user_patterns import AnalyzeUserPatternsUseCase
from application.interfaces.whatsapp_interface import WhatsAppInterface
from shared.logging import get_logger

logger = get_logger(__name__)


class MockUserRepository(UserRepository):
    """Mock user repository for development"""
    
    def __init__(self):
        self._users = {}  # In-memory user storage
    
    def get_user(self, user_id: str):
        """Get user by ID"""
        return self._users.get(user_id)
    
    def add_user(self, user, user_id: str = None):
        """Add a new user"""
        if user_id:
            self._users[user_id] = user
        return True
    
    def save_user(self, user, user_id: str = None):
        """Save user"""
        if user_id:
            self._users[user_id] = user
        return True
    
    def update_user(self, user):
        """Update user - no-op for now"""
        return True
    
    def delete_user(self, user_id: str):
        """Delete user - no-op for now"""
        return True
    
    def update_user_profile(self, user_id: str, profile):
        """Update user profile - no-op for now"""
        return True
    
    def add_user_session(self, user_id: str, session):
        """Add a new session for user - no-op for now"""
        return True
    
    def get_user_sessions(self, user_id: str, days: int = 7):
        """Get user sessions from last N days - returns empty list for now"""
        return []
    
    def get_user_feedback(self, user_id: str, limit: int = 10):
        """Get recent user feedback - returns empty list for now"""
        return []
    
    def add_user_feedback(self, user_id: str, feedback: str):
        """Add user feedback - no-op for now"""
        return True
    
    def get_weekly_plan(self, user_id: str):
        """Get current weekly plan for user - returns None for now"""
        return None
    
    def save_weekly_plan(self, user_id: str, plan):
        """Save weekly plan for user - no-op for now"""
        return True
    
    def get_user_statistics(self, user_id: str):
        """Get user training statistics - returns empty dict for now"""
        return {}


class MockMentorRepository(MentorRepository):
    """Mock mentor repository for development"""
    
    def get_mentor(self, mentor_id: str):
        """Get mentor by ID - returns None for now"""
        return None
    
    def get_mentor_by_name(self, name: str):
        """Get mentor by name - returns None for now"""
        return None
    
    def get_all_mentors(self):
        """Get all mentors - returns empty list for now"""
        return []
    
    def get_mentors_by_specialization(self, specialization):
        """Get mentors by specialization - returns empty list for now"""
        return []
    
    def search_mentors(self, query: str):
        """Search mentors - returns empty list for now"""
        return []
    
    def get_relevant_mentors_for_query(self, query: str):
        """Get relevant mentors for query - returns empty list for now"""
        return []
    
    def get_mentor_context(self, query: str, mentor_names=None):
        """Get mentor context - returns placeholder for now"""
        return "Focus on proper form and progressive overload."
    
    def get_weekly_planning_context(self):
        """Get weekly planning context - returns placeholder for now"""
        return "Plan balanced workouts with proper recovery."
    
    def get_mentor_statistics(self):
        """Get mentor statistics - returns empty dict for now"""
        return {}


class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._services = {}
        self._configure_services()
    
    def _configure_services(self):
        """Configure all services and dependencies"""
        try:
            # Database
            self._services['database'] = CoachDatabase()
            
            # Repositories
            self._services['user_repository'] = MockUserRepository()
            self._services['exercise_repository'] = SQLiteExerciseRepository()
            self._services['mentor_repository'] = MockMentorRepository()
            
            # External services
            self._services['openai_client'] = OpenAIClient()
            self._services['whatsapp_client'] = WhatsAppClient()
            
            # RAG system
            self._services['rag_system'] = MentorRAGSystem()
            
            # Services
            self._services['coaching_service'] = CoachingService(
                user_repository=self._services['user_repository'],
                exercise_repository=self._services['exercise_repository'],
                mentor_repository=self._services['mentor_repository']
            )
            
            # Use cases
            self._services['get_coaching_response_use_case'] = GetCoachingResponseUseCase(
                coaching_service=self._services['coaching_service'],
                ai_client=self._services['openai_client']
            )
            
            self._services['create_weekly_plan_use_case'] = CreateWeeklyPlanUseCase(
                coaching_service=self._services['coaching_service'],
                ai_client=self._services['openai_client']
            )
            
            self._services['analyze_patterns_use_case'] = AnalyzeUserPatternsUseCase(
                coaching_service=self._services['coaching_service']
            )
            
            # Interface
            self._services['whatsapp_interface'] = WhatsAppInterface(
                coaching_response_use_case=self._services['get_coaching_response_use_case'],
                create_weekly_plan_use_case=self._services['create_weekly_plan_use_case'],
                analyze_patterns_use_case=self._services['analyze_patterns_use_case'],
                whatsapp_client=self._services['whatsapp_client']
            )
            
            logger.info("✅ Container configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Error configuring container: {e}")
            raise
    
    def get_service(self, service_name: str):
        """Get a service by name"""
        return self._services.get(service_name)
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all services"""
        return self._services.copy()
    
    def add_service(self, name: str, service: Any):
        """Add a service to the container"""
        self._services[name] = service
    
    def initialize(self):
        """Initialize the container - no-op for now"""
        pass
    
    def get_whatsapp_client(self):
        """Get WhatsApp client"""
        return self._services.get('whatsapp_client')
    
    def get_coaching_response_use_case(self):
        """Get coaching response use case"""
        return self._services.get('get_coaching_response_use_case')
    
    def get_create_weekly_plan_use_case(self):
        """Get create weekly plan use case"""
        return self._services.get('create_weekly_plan_use_case')
    
    def get_analyze_user_patterns_use_case(self):
        """Get analyze user patterns use case"""
        return self._services.get('analyze_patterns_use_case')

# Create a global container instance
container = Container() 