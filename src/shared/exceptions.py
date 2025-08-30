"""
Custom exception hierarchy for AI Coach application.
Provides structured error handling with clear error categories and context.
"""
from typing import Optional, Dict, Any


class CoachingError(Exception):
    """Base exception for all coaching-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "context": self.context
        }


class ValidationError(CoachingError):
    """Raised when input validation fails"""
    pass


class UserError(CoachingError):
    """Base class for user-related errors"""
    pass


class UserNotFoundError(UserError):
    """Raised when user cannot be found"""
    
    def __init__(self, user_id: str):
        super().__init__(
            f"User not found: {user_id}",
            error_code="USER_NOT_FOUND",
            context={"user_id": user_id}
        )


class UserProfileError(UserError):
    """Raised when user profile operations fail"""
    pass


class MentorError(CoachingError):
    """Base class for mentor-related errors"""
    pass


class MentorContextError(MentorError):
    """Raised when mentor context cannot be retrieved"""
    
    def __init__(self, query: str, available_mentors: Optional[list] = None):
        super().__init__(
            f"Failed to retrieve mentor context for query: {query}",
            error_code="MENTOR_CONTEXT_ERROR",
            context={"query": query, "available_mentors": available_mentors}
        )


class WorkoutError(CoachingError):
    """Base class for workout-related errors"""
    pass


class WorkoutGenerationError(WorkoutError):
    """Raised when workout generation fails"""
    
    def __init__(self, reason: str, user_context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Workout generation failed: {reason}",
            error_code="WORKOUT_GENERATION_ERROR",
            context={"reason": reason, "user_context": user_context}
        )


class ExerciseNotFoundError(WorkoutError):
    """Raised when specific exercise cannot be found"""
    
    def __init__(self, exercise_name: str):
        super().__init__(
            f"Exercise not found: {exercise_name}",
            error_code="EXERCISE_NOT_FOUND",
            context={"exercise_name": exercise_name}
        )


class AIServiceError(CoachingError):
    """Base class for AI service errors"""
    pass


class OpenAIError(AIServiceError):
    """Raised when OpenAI API calls fail"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, api_error: Optional[str] = None):
        super().__init__(
            f"OpenAI API error: {message}",
            error_code="OPENAI_ERROR",
            context={"status_code": status_code, "api_error": api_error}
        )


class RAGSystemError(AIServiceError):
    """Raised when RAG system operations fail"""
    pass


class DatabaseError(CoachingError):
    """Base class for database-related errors"""
    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass


class QueryError(DatabaseError):
    """Raised when database query fails"""
    
    def __init__(self, query: str, error_details: str):
        super().__init__(
            f"Database query failed: {error_details}",
            error_code="QUERY_ERROR",
            context={"query": query, "error_details": error_details}
        )


class SecurityError(CoachingError):
    """Base class for security-related errors"""
    pass


class AuthenticationError(SecurityError):
    """Raised when authentication fails"""
    
    def __init__(self, reason: str = "Invalid credentials"):
        super().__init__(
            f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_ERROR",
            context={"reason": reason}
        )


class AuthorizationError(SecurityError):
    """Raised when user lacks required permissions"""
    
    def __init__(self, required_permission: str, user_permissions: Optional[list] = None):
        super().__init__(
            f"Insufficient permissions. Required: {required_permission}",
            error_code="AUTHORIZATION_ERROR",
            context={"required_permission": required_permission, "user_permissions": user_permissions}
        )


class RateLimitError(SecurityError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str, reset_time: Optional[str] = None):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED",
            context={"limit": limit, "window": window, "reset_time": reset_time}
        )


class ConfigurationError(CoachingError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, config_key: str, issue: str):
        super().__init__(
            f"Configuration error for '{config_key}': {issue}",
            error_code="CONFIGURATION_ERROR",
            context={"config_key": config_key, "issue": issue}
        )


class ExternalServiceError(CoachingError):
    """Raised when external service calls fail"""
    
    def __init__(self, service_name: str, error_details: str, retry_after: Optional[int] = None):
        super().__init__(
            f"External service '{service_name}' error: {error_details}",
            error_code="EXTERNAL_SERVICE_ERROR",
            context={"service_name": service_name, "error_details": error_details, "retry_after": retry_after}
        )