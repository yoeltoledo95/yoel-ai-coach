"""
Response models for AI Coach API endpoints.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status values"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    
    status: ResponseStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class ChatResponse(BaseResponse):
    """Response model for chat endpoint"""
    
    response: str = Field(..., description="AI coach response")
    mentors_used: List[str] = Field(default_factory=list, description="Mentors referenced in response")
    intent: Optional[str] = Field(None, description="Detected user intent")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence score")
    session_id: Optional[str] = None
    
    # Performance metrics
    response_time_ms: Optional[int] = Field(None, ge=0)
    tokens_used: Optional[int] = Field(None, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "response": "Great question! Based on your recent push workout, let's focus on pull movements today...",
                "mentors_used": ["tom_merrick", "dylan_werner"],
                "intent": "workout_request",
                "confidence": 0.95,
                "response_time_ms": 850,
                "tokens_used": 245
            }
        }


class ErrorResponse(BaseResponse):
    """Response model for errors"""
    
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "message": "Message contains invalid characters",
                "details": {
                    "field": "message",
                    "invalid_chars": ["<", ">"]
                }
            }
        }


class UserProfileResponse(BaseResponse):
    """Response model for user profile operations"""
    
    user_id: str
    profile: Optional[Dict[str, Any]] = None
    created: bool = Field(default=False, description="Whether profile was created")
    updated: bool = Field(default=False, description="Whether profile was updated")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "user_id": "yoel_user",
                "profile": {
                    "name": "Yoel",
                    "age": 30,
                    "goals": ["handstand", "flexibility"],
                    "experience_level": "intermediate"
                },
                "updated": True
            }
        }


class WorkoutResponse(BaseResponse):
    """Response model for workout generation"""
    
    workout: Dict[str, Any] = Field(..., description="Generated workout plan")
    duration_minutes: int = Field(..., ge=5, le=180)
    intensity: str = Field(..., pattern=r'^(low|moderate|high)$')
    equipment_needed: List[str] = Field(default_factory=list)
    safety_notes: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "workout": {
                    "warmup": ["arm circles", "leg swings"],
                    "main": ["push-ups", "squats", "planks"],
                    "cooldown": ["stretching"]
                },
                "duration_minutes": 45,
                "intensity": "moderate",
                "equipment_needed": ["bodyweight"],
                "safety_notes": ["Stop if you feel pain"]
            }
        }


class HealthCheckResponse(BaseResponse):
    """Response model for health check endpoints"""
    
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    uptime_seconds: int = Field(..., ge=0)
    
    # System health
    database_connected: bool = Field(...)
    ai_service_available: bool = Field(...)
    
    # Optional metrics
    metrics: Optional[Dict[str, Any]] = Field(None)
    dependencies: Optional[Dict[str, str]] = Field(None)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "service": "ai-coach",
                "version": "1.0.0",
                "uptime_seconds": 3600,
                "database_connected": True,
                "ai_service_available": True,
                "metrics": {
                    "total_requests": 1250,
                    "avg_response_time_ms": 450,
                    "error_rate": 0.02
                }
            }
        }


class MetricsResponse(BaseResponse):
    """Response model for metrics endpoint"""
    
    total_requests: int = Field(..., ge=0)
    avg_response_time_ms: float = Field(..., ge=0)
    error_rate: float = Field(..., ge=0.0, le=1.0)
    uptime_seconds: int = Field(..., ge=0)
    
    # Performance metrics
    response_time_percentiles: Dict[str, float] = Field(default_factory=dict)
    requests_per_hour: int = Field(..., ge=0)
    mentor_usage_stats: Dict[str, int] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "total_requests": 5000,
                "avg_response_time_ms": 450.5,
                "error_rate": 0.02,
                "uptime_seconds": 86400,
                "response_time_percentiles": {
                    "p50": 400,
                    "p90": 800,
                    "p99": 1200
                },
                "requests_per_hour": 120,
                "mentor_usage_stats": {
                    "tom_merrick": 1500,
                    "dylan_werner": 1200,
                    "ido_portal": 800
                }
            }
        }
