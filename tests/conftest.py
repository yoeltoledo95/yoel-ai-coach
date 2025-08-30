"""
Test configuration and fixtures for AI Coach tests.
Provides common test setup, mocks, and utilities.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shared.exceptions import *
from shared.models.requests import ChatRequest
from shared.models.responses import ChatResponse, ErrorResponse
from infrastructure.config.testing import TestingConfig


@pytest.fixture
def test_config():
    """Provide test configuration"""
    return TestingConfig()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = Mock()
    mock_client.generate_response.return_value = "Great workout today! Focus on proper form."
    mock_client.generate_from_prompt.return_value = "Excellent question about training!"
    return mock_client


@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing"""
    mock_repo = Mock()
    mock_repo.get_user.return_value = {
        "user_id": "test_user",
        "name": "Test User",
        "goals": ["strength", "mobility"],
        "experience_level": "intermediate"
    }
    mock_repo.save_user.return_value = True
    return mock_repo


@pytest.fixture
def mock_mentor_repository():
    """Mock mentor repository for testing"""
    mock_repo = Mock()
    mock_repo.get_mentor_context.return_value = "Tom Merrick emphasizes controlled movements and proper form."
    return mock_repo


@pytest.fixture
def mock_exercise_repository():
    """Mock exercise repository for testing"""
    mock_repo = Mock()
    mock_repo.get_exercises_by_tags.return_value = [
        {"name": "Push-ups", "difficulty": "intermediate", "tags": ["chest", "arms"]},
        {"name": "Squats", "difficulty": "beginner", "tags": ["legs", "core"]}
    ]
    return mock_repo


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing"""
    return ChatRequest(
        user_id="test_user_123",
        message="What workout should I do today?",
        session_id="session_456"
    )


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    return {
        "user_id": "test_user",
        "name": "Test User",
        "age": 30,
        "goals": ["strength", "flexibility", "weight_loss"],
        "experience_level": "intermediate",
        "injuries": ["shoulder"],
        "equipment": ["bodyweight", "dumbbells"],
        "training_preferences": {
            "frequency": 4,
            "duration": 45,
            "preferred_style": "calisthenics"
        }
    }


@pytest.fixture
def sample_coaching_response():
    """Sample coaching response for testing"""
    return {
        "response": "Great question! Based on your goals, I recommend focusing on compound movements today.",
        "mentors_used": ["tom_merrick", "dylan_werner"],
        "intent": "workout_request",
        "confidence": 0.95
    }


@pytest.fixture
def mock_rag_system():
    """Mock RAG system for testing"""
    mock_rag = Mock()
    mock_rag.get_mentor_context.return_value = "Expert advice from top mentors"
    mock_rag.get_statistics.return_value = {
        "total_mentors": 15,
        "system_type": "simple_keyword_based"
    }
    return mock_rag


@pytest.fixture
def app_client():
    """Test client for Flask application"""
    from application.interfaces.web_chat_interface import WebChatInterface
    
    # Mock dependencies
    with patch('application.container') as mock_container_module:
        mock_container = Mock()
        mock_container.get_get_coaching_response_use_case.return_value = Mock()
        
        interface = WebChatInterface(mock_container)
        interface.app.config['TESTING'] = True
        
        with interface.app.test_client() as client:
            yield client


@pytest.fixture
def mock_container():
    """Mock dependency injection container"""
    mock_container = Mock()
    
    # Mock all container methods
    mock_container.get_openai_client.return_value = Mock()
    mock_container.get_user_repository.return_value = Mock()
    mock_container.get_mentor_repository.return_value = Mock()
    mock_container.get_exercise_repository.return_value = Mock()
    mock_container.get_coaching_service.return_value = Mock()
    mock_container.get_get_coaching_response_use_case.return_value = Mock()
    
    return mock_container


# Test data factories
class UserFactory:
    """Factory for creating test user data"""
    
    @staticmethod
    def create(user_id="test_user", **kwargs):
        """Create test user with defaults"""
        default_user = {
            "user_id": user_id,
            "name": "Test User",
            "age": 25,
            "goals": ["fitness"],
            "experience_level": "beginner",
            "injuries": [],
            "equipment": ["bodyweight"]
        }
        default_user.update(kwargs)
        return default_user


class RequestFactory:
    """Factory for creating test requests"""
    
    @staticmethod
    def chat_request(message="Hello coach", user_id="test_user", **kwargs):
        """Create test chat request"""
        data = {
            "user_id": user_id,
            "message": message,
            **kwargs
        }
        return ChatRequest(**data)


# Test utilities
def assert_valid_response(response_dict: Dict[str, Any]):
    """Assert response has valid structure"""
    assert "status" in response_dict
    assert "timestamp" in response_dict
    assert response_dict["status"] in ["success", "error", "warning"]


def assert_error_response(response_dict: Dict[str, Any], expected_code: str = None):
    """Assert response is a valid error"""
    assert_valid_response(response_dict)
    assert response_dict["status"] == "error"
    assert "error_code" in response_dict
    assert "message" in response_dict
    
    if expected_code:
        assert response_dict["error_code"] == expected_code


def assert_chat_response(response_dict: Dict[str, Any]):
    """Assert response is a valid chat response"""
    assert_valid_response(response_dict)
    assert response_dict["status"] == "success"
    assert "response" in response_dict
    assert len(response_dict["response"]) > 0
