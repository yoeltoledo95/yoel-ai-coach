"""
Shared data models for the AI Coach application.
Provides request/response models with validation.
"""

from .requests import *
from .responses import *
from .validators import *

__all__ = [
    # Requests
    "ChatRequest",
    "UserProfileRequest", 
    "WorkoutRequest",
    "HealthCheckRequest",
    
    # Responses
    "ChatResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "UserProfileResponse",
    "WorkoutResponse",
    
    # Validators
    "validate_user_message",
    "validate_user_id",
    "sanitize_input",
]
