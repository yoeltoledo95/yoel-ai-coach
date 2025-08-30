"""
Unit tests for Pydantic request/response models.
Tests validation, serialization, and error handling.
"""
import pytest
from pydantic import ValidationError
from shared.models.requests import ChatRequest, UserProfileRequest, WorkoutRequest
from shared.models.responses import ChatResponse, ErrorResponse, HealthCheckResponse
from shared.models.validators import validate_user_message, validate_user_id


class TestChatRequest:
    """Test ChatRequest model validation"""
    
    def test_valid_chat_request(self):
        """Test valid chat request creation"""
        request = ChatRequest(
            user_id="test_user_123",
            message="What workout should I do today?",
            session_id="session_456"
        )
        
        assert request.user_id == "test_user_123"
        assert request.message == "What workout should I do today?"
        assert request.session_id == "session_456"
        assert request.context is None
    
    def test_chat_request_minimal(self):
        """Test chat request with minimal required fields"""
        request = ChatRequest(
            user_id="user123",
            message="Hello"
        )
        
        assert request.user_id == "user123"
        assert request.message == "Hello"
        assert request.session_id is None
        assert request.context is None
    
    def test_invalid_user_id_format(self):
        """Test invalid user ID format validation"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(
                user_id="invalid user@id!",
                message="Hello"
            )
        
        error = exc_info.value
        assert "pattern" in str(error).lower() or "invalid" in str(error).lower()
    
    def test_empty_message_validation(self):
        """Test empty message validation"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(
                user_id="test_user",
                message=""
            )
        
        error = exc_info.value
        assert "1 character" in str(error) or "empty" in str(error).lower()
    
    def test_message_too_long(self):
        """Test message length validation"""
        long_message = "x" * 1001  # Exceeds 1000 char limit
        
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(
                user_id="test_user",
                message=long_message
            )
        
        error = exc_info.value
        assert "1000" in str(error) or "long" in str(error).lower()
    
    def test_message_sanitization(self):
        """Test HTML sanitization in message"""
        request = ChatRequest(
            user_id="test_user",
            message="Hello <script>alert('xss')</script> coach!"
        )
        
        # Message should be sanitized (HTML escaped)
        assert "<script>" not in request.message
        # Note: alert may be HTML-escaped as &lt;script&gt;alert(...)&lt;/script&gt;
        assert "Hello" in request.message
        assert "coach" in request.message
    
    def test_user_id_validation(self):
        """Test user ID validation"""
        # Valid user ID
        request = ChatRequest(
            user_id="test_user_123",
            message="Hello"
        )
        
        assert request.user_id == "test_user_123"


class TestUserProfileRequest:
    """Test UserProfileRequest model validation"""
    
    def test_valid_user_profile_request(self):
        """Test valid user profile creation"""
        request = UserProfileRequest(
            user_id="test_user",
            name="John Doe",
            age=30,
            goals=["strength", "flexibility"],
            experience_level="intermediate",
            injuries=["shoulder"],
            equipment=["dumbbells", "bodyweight"]
        )
        
        assert request.user_id == "test_user"
        assert request.name == "John Doe"
        assert request.age == 30
        assert "strength" in request.goals
        assert request.experience_level == "intermediate"
    
    def test_age_validation_bounds(self):
        """Test age validation boundaries"""
        # Too young
        with pytest.raises(ValidationError):
            UserProfileRequest(user_id="test", age=12)
        
        # Too old
        with pytest.raises(ValidationError):
            UserProfileRequest(user_id="test", age=121)
        
        # Valid boundaries
        young_user = UserProfileRequest(user_id="test", age=13)
        old_user = UserProfileRequest(user_id="test", age=120)
        
        assert young_user.age == 13
        assert old_user.age == 120
    
    def test_experience_level_validation(self):
        """Test experience level validation"""
        # Valid levels
        for level in ["beginner", "intermediate", "advanced"]:
            request = UserProfileRequest(user_id="test", experience_level=level)
            assert request.experience_level == level
        
        # Invalid level
        with pytest.raises(ValidationError):
            UserProfileRequest(user_id="test", experience_level="expert")
    
    def test_goals_validation(self):
        """Test goals list validation"""
        # Valid goals
        request = UserProfileRequest(
            user_id="test",
            goals=["strength", "flexibility", "weight_loss"]
        )
        assert len(request.goals) == 3
        
        # Too many goals
        with pytest.raises(ValidationError):
            UserProfileRequest(
                user_id="test",
                goals=["goal" + str(i) for i in range(11)]  # 11 goals > 10 limit
            )
        
        # Empty goal in list
        with pytest.raises(ValidationError):
            UserProfileRequest(
                user_id="test",
                goals=["strength", "", "flexibility"]
            )
    
    def test_name_sanitization(self):
        """Test name sanitization and validation"""
        # Valid name (letters, spaces, hyphens)
        request = UserProfileRequest(
            user_id="test",
            name="John Smith"
        )
        assert request.name == "John Smith"
        
        # Name with invalid characters
        with pytest.raises(ValidationError):
            UserProfileRequest(
                user_id="test",
                name="John<script>alert('xss')</script>"
            )


class TestWorkoutRequest:
    """Test WorkoutRequest model validation"""
    
    def test_valid_workout_request(self):
        """Test valid workout request creation"""
        request = WorkoutRequest(
            user_id="test_user",
            workout_type="strength",
            duration=45,
            intensity="moderate",
            focus_areas=["chest", "arms"],
            equipment=["dumbbells"]
        )
        
        assert request.user_id == "test_user"
        assert request.workout_type == "strength"
        assert request.duration == 45
        assert request.intensity == "moderate"
        assert "chest" in request.focus_areas
    
    def test_workout_type_validation(self):
        """Test workout type validation"""
        valid_types = ["strength", "cardio", "flexibility", "mixed", "recovery"]
        
        for workout_type in valid_types:
            request = WorkoutRequest(user_id="test", workout_type=workout_type)
            assert request.workout_type == workout_type
        
        # Invalid type
        with pytest.raises(ValidationError):
            WorkoutRequest(user_id="test", workout_type="invalid_type")
    
    def test_duration_validation(self):
        """Test duration validation boundaries"""
        # Too short
        with pytest.raises(ValidationError):
            WorkoutRequest(user_id="test", duration=4)
        
        # Too long
        with pytest.raises(ValidationError):
            WorkoutRequest(user_id="test", duration=181)
        
        # Valid boundaries
        short_workout = WorkoutRequest(user_id="test", duration=5)
        long_workout = WorkoutRequest(user_id="test", duration=180)
        
        assert short_workout.duration == 5
        assert long_workout.duration == 180
    
    def test_intensity_validation(self):
        """Test intensity validation"""
        valid_intensities = ["low", "moderate", "high"]
        
        for intensity in valid_intensities:
            request = WorkoutRequest(user_id="test", intensity=intensity)
            assert request.intensity == intensity
        
        # Invalid intensity
        with pytest.raises(ValidationError):
            WorkoutRequest(user_id="test", intensity="extreme")
    
    def test_focus_areas_validation(self):
        """Test focus areas validation"""
        # Valid focus areas
        request = WorkoutRequest(
            user_id="test",
            focus_areas=["chest", "back", "legs"]
        )
        assert len(request.focus_areas) == 3
        
        # Too many focus areas
        with pytest.raises(ValidationError):
            WorkoutRequest(
                user_id="test",
                focus_areas=["area" + str(i) for i in range(6)]  # 6 > 5 limit
            )
        
        # Invalid focus area
        with pytest.raises(ValidationError):
            WorkoutRequest(
                user_id="test",
                focus_areas=["invalid_area"]
            )


class TestChatResponse:
    """Test ChatResponse model"""
    
    def test_valid_chat_response(self):
        """Test valid chat response creation"""
        response = ChatResponse(
            status="success",
            response="Here's your workout plan...",
            mentors_used=["tom_merrick", "dylan_werner"],
            intent="workout_request",
            confidence=0.95,
            response_time_ms=850
        )
        
        assert response.status == "success"
        assert "workout plan" in response.response
        assert len(response.mentors_used) == 2
        assert response.confidence == 0.95
    
    def test_confidence_validation(self):
        """Test confidence score validation"""
        # Valid confidence scores
        for confidence in [0.0, 0.5, 1.0]:
            response = ChatResponse(
                status="success",
                response="Test response",
                confidence=confidence
            )
            assert response.confidence == confidence
        
        # Invalid confidence scores
        for invalid_confidence in [-0.1, 1.1]:
            with pytest.raises(ValidationError):
                ChatResponse(
                    status="success",
                    response="Test response",
                    confidence=invalid_confidence
                )


class TestErrorResponse:
    """Test ErrorResponse model"""
    
    def test_valid_error_response(self):
        """Test valid error response creation"""
        response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid input provided",
            details={"field": "message", "issue": "too_long"}
        )
        
        assert response.status == "error"
        assert response.error_code == "VALIDATION_ERROR"
        assert response.message == "Invalid input provided"
        assert response.details["field"] == "message"
    
    def test_error_response_minimal(self):
        """Test error response with minimal fields"""
        response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Something went wrong"
        )
        
        assert response.status == "error"
        assert response.error_code == "INTERNAL_ERROR"
        assert response.message == "Something went wrong"
        assert response.details is None


class TestHealthCheckResponse:
    """Test HealthCheckResponse model"""
    
    def test_valid_health_response(self):
        """Test valid health check response"""
        response = HealthCheckResponse(
            status="success",
            service="ai-coach",
            version="1.0.0",
            uptime_seconds=3600,
            database_connected=True,
            ai_service_available=True
        )
        
        assert response.status == "success"
        assert response.service == "ai-coach"
        assert response.uptime_seconds == 3600
        assert response.database_connected is True
        assert response.ai_service_available is True


class TestValidators:
    """Test custom validator functions"""
    
    def test_validate_user_message(self):
        """Test user message validation function"""
        # Valid message
        message = validate_user_message("Hello, how are you?")
        assert message == "Hello, how are you?"
        
        # Message with HTML
        message = validate_user_message("Hello <b>coach</b>!")
        assert "<b>" not in message  # Should be escaped
        assert "coach" in message
        
        # Empty message
        with pytest.raises(ValueError, match="empty"):
            validate_user_message("")
        
        # Too long message
        with pytest.raises(ValueError, match="too long"):
            validate_user_message("x" * 1001)
        
        # Too many special characters
        with pytest.raises(ValueError, match="special characters"):
            validate_user_message("!@#$%^&*()!@#$%^&*()")
    
    def test_validate_user_id(self):
        """Test user ID validation function"""
        # Valid user IDs
        for user_id in ["user123", "test_user", "user-123"]:
            validated = validate_user_id(user_id)
            assert validated == user_id
        
        # Invalid user IDs
        invalid_ids = ["", "  ", "user@domain.com", "user with spaces"]
        
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError):
                validate_user_id(invalid_id)
        
        # User ID with whitespace (should be trimmed)
        validated = validate_user_id("  test_user  ")
        assert validated == "test_user"
