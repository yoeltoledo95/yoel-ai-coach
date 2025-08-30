"""
Request models with validation for AI Coach API endpoints.
"""
import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
import html


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Unique user identifier"
    )
    
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="User message to the AI coach"
    )
    
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Optional session identifier"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for the conversation"
    )
    
    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v):
        """Sanitize message content"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        
        # Remove potentially dangerous characters
        sanitized = html.escape(v.strip())
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\.\?\!\,\'\-]', sanitized)) / len(sanitized)
        if special_char_ratio > 0.3:
            raise ValueError("Message contains too many special characters")
        
        return sanitized
    
    @field_validator('user_id')
    @classmethod
    @classmethod
    def validate_user_id(cls, v):
        """Validate user ID format"""
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()


class UserProfileRequest(BaseModel):
    """Request model for user profile operations"""
    
    user_id: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$')
    name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=13, le=120)
    goals: Optional[List[str]] = Field(None, max_items=10)
    experience_level: Optional[str] = Field(None, pattern=r'^(beginner|intermediate|advanced)$')
    injuries: Optional[List[str]] = Field(None, max_items=20)
    equipment: Optional[List[str]] = Field(None, max_items=50)
    
    @field_validator('goals')
    @classmethod
    @classmethod
    def validate_goals(cls, v):
        """Validate goals list"""
        if v:
            for goal in v:
                if not goal or not goal.strip():
                    raise ValueError("Goals cannot be empty")
                if len(goal) > 100:
                    raise ValueError("Individual goals must be under 100 characters")
        return v
    
    @field_validator('name')
    @classmethod
    @classmethod
    def validate_name(cls, v):
        """Validate name format"""
        if v:
            sanitized = html.escape(v.strip())
            if not re.match(r'^[a-zA-Z\s\-\'\.]+$', sanitized):
                raise ValueError("Name contains invalid characters")
            return sanitized
        return v


class WorkoutRequest(BaseModel):
    """Request model for workout generation"""
    
    user_id: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$')
    workout_type: Optional[str] = Field(
        None, 
        pattern=r'^(strength|cardio|flexibility|mixed|recovery)$'
    )
    duration: Optional[int] = Field(None, ge=5, le=180)  # 5 minutes to 3 hours
    intensity: Optional[str] = Field(
        None,
        pattern=r'^(low|moderate|high)$'
    )
    focus_areas: Optional[List[str]] = Field(None, max_items=5)
    equipment: Optional[List[str]] = Field(None, max_items=20)
    
    @field_validator('focus_areas')
    @classmethod
    @classmethod
    def validate_focus_areas(cls, v):
        """Validate focus areas"""
        if v:
            valid_areas = {
                'chest', 'back', 'shoulders', 'arms', 'legs', 'core', 
                'cardio', 'flexibility', 'balance', 'power', 'endurance'
            }
            for area in v:
                if area.lower() not in valid_areas:
                    raise ValueError(f"Invalid focus area: {area}")
        return v


class HealthCheckRequest(BaseModel):
    """Request model for health check endpoints"""
    
    include_metrics: bool = Field(default=False)
    check_dependencies: bool = Field(default=True)
