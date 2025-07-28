"""
Custom exceptions for the AI coach application
"""


class CoachError(Exception):
    """Base exception for the coaching application"""
    pass


class ConfigurationError(CoachError):
    """Configuration-related errors"""
    pass


class AIError(CoachError):
    """AI/OpenAI related errors"""
    pass


class DatabaseError(CoachError):
    """Database-related errors"""
    pass


class UserNotFoundError(CoachError):
    """User not found error"""
    pass


class ExerciseNotFoundError(CoachError):
    """Exercise not found error"""
    pass


class MentorNotFoundError(CoachError):
    """Mentor not found error"""
    pass


class ValidationError(CoachError):
    """Data validation errors"""
    pass


class WhatsAppError(CoachError):
    """WhatsApp API related errors"""
    pass


class RAGError(CoachError):
    """RAG system related errors"""
    pass 