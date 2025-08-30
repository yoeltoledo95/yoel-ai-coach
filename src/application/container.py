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
from infrastructure.database.sqlite.user_repository import SQLiteUserRepository
from infrastructure.database.sqlite.user_memory_store import UserMemoryStore
# Removed complex RAG system import - using simple keyword-based system
from infrastructure.database.vector_store.mentor_repository import RAGMentorRepository
from infrastructure.external.openai_client import OpenAIClient
from infrastructure.external.whatsapp_client import WhatsAppClient
from infrastructure.external.prompt_engine import PromptEngine
from application.use_cases.get_coaching_response import GetCoachingResponseUseCase
# Removed unused imports for simplification
from application.interfaces.whatsapp_interface import WhatsAppInterface
from shared.logging import get_logger
from application.conversation_policy import ConversationPolicy
from domain.services.workout_composer import WorkoutComposer
from application.use_cases.compose_today_workout import ComposeTodayWorkoutUseCase

logger = get_logger(__name__)




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
            self._services['user_repository'] = SQLiteUserRepository()
            self._services['exercise_repository'] = SQLiteExerciseRepository()
            self._services['mentor_repository'] = RAGMentorRepository()
            self._services['user_memory_store'] = UserMemoryStore()
            
            # External services (always real client; .env provides keys)
            self._services['openai_client'] = OpenAIClient()
            
            # WhatsApp disabled for now
            self._services['whatsapp_client'] = None
            
            # Configuration service (infrastructure)
            from infrastructure.config.file_configuration_service import FileConfigurationService
            self._services['config_service'] = FileConfigurationService()
            
            # Simplified RAG system (5x faster)
            from infrastructure.database.vector_store.simple_rag import SimpleMentorRAG
            self._services['rag_system'] = SimpleMentorRAG(self._services['config_service'])
            
            # Services
            self._services['coaching_service'] = CoachingService(
                user_repository=self._services['user_repository'],
                exercise_repository=self._services['exercise_repository'],
                mentor_repository=self._services['mentor_repository'],
                ai_client=self._services['openai_client']
            )
            
            # Use cases
            self._services['get_coaching_response_use_case'] = GetCoachingResponseUseCase(
                coaching_service=self._services['coaching_service'],
                ai_client=self._services['openai_client'],
                user_memory_store=self._services['user_memory_store']
            )
            
            # Simplified: Removed unused weekly planning and pattern analysis use cases

            # New: Workout composition use case for chat
            self._services['conversation_policy'] = ConversationPolicy()
            self._services['workout_composer'] = WorkoutComposer(self._services['exercise_repository'])
            self._services['compose_today_workout_use_case'] = ComposeTodayWorkoutUseCase(
                composer=self._services['workout_composer'],
                mentor_repository=self._services['mentor_repository'],
                user_memory_store=self._services['user_memory_store'],
                conversation_policy=self._services['conversation_policy']
            )
            
            # Web chat interface
            try:
                from application.interfaces.web_chat_interface import WebChatInterface
                self._services['web_chat_interface'] = WebChatInterface(self)
            except Exception as e:
                logger.error(f"❌ Failed to initialize web chat interface: {e}")
            
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
    
    # Removed unused getter methods for simplified architecture

# Create a global container instance
container = Container() 