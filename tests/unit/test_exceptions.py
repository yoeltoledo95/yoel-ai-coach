"""
Unit tests for custom exception hierarchy.
Tests exception structure, inheritance, and context handling.
"""
import pytest
from shared.exceptions import *


class TestBaseException:
    """Test base CoachingError exception"""
    
    def test_basic_exception_creation(self):
        """Test basic exception with message only"""
        error = CoachingError("Something went wrong")
        
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.error_code == "CoachingError"
        assert error.context == {}
    
    def test_exception_with_code_and_context(self):
        """Test exception with error code and context"""
        context = {"user_id": "123", "operation": "workout_generation"}
        error = CoachingError("Operation failed", "OPERATION_ERROR", context)
        
        assert error.message == "Operation failed"
        assert error.error_code == "OPERATION_ERROR"
        assert error.context == context
    
    def test_exception_to_dict(self):
        """Test converting exception to dictionary"""
        context = {"field": "email", "value": "invalid"}
        error = CoachingError("Validation failed", "VALIDATION_ERROR", context)
        
        error_dict = error.to_dict()
        
        expected = {
            "error": "VALIDATION_ERROR",
            "message": "Validation failed",
            "context": context
        }
        assert error_dict == expected


class TestValidationError:
    """Test ValidationError exception"""
    
    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from CoachingError"""
        error = ValidationError("Invalid input")
        
        assert isinstance(error, CoachingError)
        assert isinstance(error, ValidationError)
    
    def test_validation_error_with_context(self):
        """Test ValidationError with field context"""
        context = {"field": "message", "reason": "too_long"}
        error = ValidationError("Message too long", "VALIDATION_ERROR", context)
        
        assert error.message == "Message too long"
        assert error.context["field"] == "message"
        assert error.context["reason"] == "too_long"


class TestUserErrors:
    """Test user-related exceptions"""
    
    def test_user_not_found_error(self):
        """Test UserNotFoundError structure"""
        error = UserNotFoundError("user123")
        
        assert "user123" in error.message
        assert error.error_code == "USER_NOT_FOUND"
        assert error.context["user_id"] == "user123"
        assert isinstance(error, UserError)
        assert isinstance(error, CoachingError)
    
    def test_user_profile_error(self):
        """Test UserProfileError"""
        error = UserProfileError("Profile update failed")
        
        assert error.message == "Profile update failed"
        assert isinstance(error, UserError)


class TestMentorErrors:
    """Test mentor-related exceptions"""
    
    def test_mentor_context_error(self):
        """Test MentorContextError structure"""
        query = "strength training"
        mentors = ["tom_merrick", "dylan_werner"]
        error = MentorContextError(query, mentors)
        
        assert query in error.message
        assert error.error_code == "MENTOR_CONTEXT_ERROR"
        assert error.context["query"] == query
        assert error.context["available_mentors"] == mentors
        assert isinstance(error, MentorError)


class TestWorkoutErrors:
    """Test workout-related exceptions"""
    
    def test_workout_generation_error(self):
        """Test WorkoutGenerationError structure"""
        reason = "insufficient user data"
        user_context = {"goals": [], "experience": None}
        error = WorkoutGenerationError(reason, user_context)
        
        assert reason in error.message
        assert error.error_code == "WORKOUT_GENERATION_ERROR"
        assert error.context["reason"] == reason
        assert error.context["user_context"] == user_context
        assert isinstance(error, WorkoutError)
    
    def test_exercise_not_found_error(self):
        """Test ExerciseNotFoundError structure"""
        exercise_name = "Super Advanced Push-up"
        error = ExerciseNotFoundError(exercise_name)
        
        assert exercise_name in error.message
        assert error.error_code == "EXERCISE_NOT_FOUND"
        assert error.context["exercise_name"] == exercise_name
        assert isinstance(error, WorkoutError)


class TestAIServiceErrors:
    """Test AI service-related exceptions"""
    
    def test_openai_error(self):
        """Test OpenAIError structure"""
        message = "Rate limit exceeded"
        status_code = 429
        api_error = "rate_limit_exceeded"
        
        error = OpenAIError(message, status_code, api_error)
        
        assert message in error.message
        assert error.error_code == "OPENAI_ERROR"
        assert error.context["status_code"] == status_code
        assert error.context["api_error"] == api_error
        assert isinstance(error, AIServiceError)
    
    def test_rag_system_error(self):
        """Test RAGSystemError"""
        error = RAGSystemError("Vector search failed")
        
        assert error.message == "Vector search failed"
        assert isinstance(error, AIServiceError)


class TestDatabaseErrors:
    """Test database-related exceptions"""
    
    def test_connection_error(self):
        """Test ConnectionError"""
        error = ConnectionError("Database connection failed")
        
        assert error.message == "Database connection failed"
        assert isinstance(error, DatabaseError)
    
    def test_query_error(self):
        """Test QueryError structure"""
        query = "SELECT * FROM users WHERE id = ?"
        error_details = "Syntax error in SQL"
        
        error = QueryError(query, error_details)
        
        assert error_details in error.message
        assert error.error_code == "QUERY_ERROR"
        assert error.context["query"] == query
        assert error.context["error_details"] == error_details
        assert isinstance(error, DatabaseError)


class TestSecurityErrors:
    """Test security-related exceptions"""
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        reason = "Invalid token"
        error = AuthenticationError(reason)
        
        assert reason in error.message
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.context["reason"] == reason
        assert isinstance(error, SecurityError)
    
    def test_authorization_error(self):
        """Test AuthorizationError structure"""
        required_permission = "admin"
        user_permissions = ["user", "read"]
        
        error = AuthorizationError(required_permission, user_permissions)
        
        assert required_permission in error.message
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert error.context["required_permission"] == required_permission
        assert error.context["user_permissions"] == user_permissions
        assert isinstance(error, SecurityError)
    
    def test_rate_limit_error(self):
        """Test RateLimitError structure"""
        limit = 100
        window = "hour"
        reset_time = "2024-01-01T15:00:00Z"
        
        error = RateLimitError(limit, window, reset_time)
        
        assert str(limit) in error.message
        assert window in error.message
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.context["limit"] == limit
        assert error.context["window"] == window
        assert error.context["reset_time"] == reset_time
        assert isinstance(error, SecurityError)


class TestConfigurationErrors:
    """Test configuration-related exceptions"""
    
    def test_configuration_error(self):
        """Test ConfigurationError structure"""
        config_key = "OPENAI_API_KEY"
        issue = "missing required environment variable"
        
        error = ConfigurationError(config_key, issue)
        
        assert config_key in error.message
        assert issue in error.message
        assert error.error_code == "CONFIGURATION_ERROR"
        assert error.context["config_key"] == config_key
        assert error.context["issue"] == issue
        assert isinstance(error, CoachingError)


class TestExternalServiceErrors:
    """Test external service-related exceptions"""
    
    def test_external_service_error(self):
        """Test ExternalServiceError structure"""
        service_name = "OpenAI"
        error_details = "Service temporarily unavailable"
        retry_after = 60
        
        error = ExternalServiceError(service_name, error_details, retry_after)
        
        assert service_name in error.message
        assert error_details in error.message
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"
        assert error.context["service_name"] == service_name
        assert error.context["error_details"] == error_details
        assert error.context["retry_after"] == retry_after
        assert isinstance(error, CoachingError)
