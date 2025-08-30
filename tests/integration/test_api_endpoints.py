"""
Integration tests for API endpoints.
Tests complete request/response flow with real components.
"""
import pytest
import json
from unittest.mock import Mock, patch
from shared.models.requests import ChatRequest
from shared.models.responses import ChatResponse, ErrorResponse


class TestChatAPIIntegration:
    """Integration tests for chat API endpoint"""
    
    def test_chat_endpoint_success_flow(self, app_client):
        """Test successful chat request flow"""
        # Mock the coaching service response
        mock_response = Mock()
        mock_response.response = "Great question! Here's a personalized workout for you..."
        mock_response.mentors_used = ["tom_merrick", "dylan_werner"]
        mock_response.intent = "workout_request"
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Make request
            response = app_client.post('/api/chat', 
                json={
                    'user_id': 'test_user_123',
                    'message': 'What workout should I do today?',
                    'user_name': 'Test User'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify response structure
            assert data['status'] == 'success'
            assert 'response' in data
            assert 'mentors_used' in data
            assert 'response_time_ms' in data
            assert data['mentors_used'] == ["tom_merrick", "dylan_werner"]
    
    def test_chat_endpoint_yoel_user_mapping(self, app_client):
        """Test special handling for Yoel user"""
        mock_response = Mock()
        mock_response.response = "Hey Yoel! Based on your profile..."
        mock_response.mentors_used = ["ido_portal"]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Test with Yoel's name
            response = app_client.post('/api/chat',
                json={
                    'user_id': 'some_id',
                    'message': 'Hello coach',
                    'user_name': 'Yoel'
                })
            
            assert response.status_code == 200
            
            # Verify the use case was called with yoel_user
            mock_use_case.execute.assert_called_once()
            call_args = mock_use_case.execute.call_args[0]
            assert call_args[0] == 'yoel_user'  # user_id should be mapped to yoel_user
    
    def test_chat_endpoint_validation_error(self, app_client):
        """Test chat endpoint with validation errors"""
        # Test with invalid user_id format
        response = app_client.post('/api/chat',
            json={
                'user_id': 'invalid user@id!',
                'message': 'Hello'
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['status'] == 'error'
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert 'message' in data
    
    def test_chat_endpoint_empty_message(self, app_client):
        """Test chat endpoint with empty message"""
        response = app_client.post('/api/chat',
            json={
                'user_id': 'test_user',
                'message': ''
            })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['status'] == 'error'
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert 'empty' in data['message'].lower()
    
    def test_chat_endpoint_missing_body(self, app_client):
        """Test chat endpoint with missing request body"""
        response = app_client.post('/api/chat')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['status'] == 'error'
        assert data['error_code'] == 'VALIDATION_ERROR'
    
    def test_chat_endpoint_coaching_service_error(self, app_client):
        """Test chat endpoint with coaching service error"""
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = Exception("Coaching service unavailable")
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            response = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'Hello coach'
                })
            
            assert response.status_code == 500
            data = json.loads(response.data)
            
            assert data['status'] == 'error'
            assert data['error_code'] == 'INTERNAL_ERROR'
            assert 'unexpected error' in data['message'].lower()
    
    def test_chat_endpoint_session_management(self, app_client):
        """Test chat endpoint session management"""
        mock_response = Mock()
        mock_response.response = "Test response"
        mock_response.mentors_used = []
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Make multiple requests to test session handling
            with app_client.session_transaction() as sess:
                sess['conversation_history'] = []
            
            response1 = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'First message'
                })
            
            response2 = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'Second message'
                })
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Session should track conversation history
            # (Testing would require access to session state)


class TestClearSessionEndpoint:
    """Integration tests for clear session endpoint"""
    
    def test_clear_session_endpoint(self, app_client):
        """Test clear session endpoint"""
        # Set up session with some data
        with app_client.session_transaction() as sess:
            sess['conversation_history'] = [('user', 'Hello'), ('bot', 'Hi there')]
            sess['user_data'] = {'name': 'Test User'}
        
        response = app_client.post('/api/clear-session')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert 'cleared' in data['message'].lower()


class TestHealthEndpointsIntegration:
    """Integration tests for health endpoints"""
    
    def test_health_endpoint_with_real_checks(self, app_client):
        """Test health endpoint with real health checks"""
        # This test uses real health check functions
        response = app_client.get('/api/health')
        
        # Should succeed or fail gracefully
        assert response.status_code in [200, 503]
        data = json.loads(response.data)
        
        assert 'status' in data
        assert 'service' in data
        assert 'database_connected' in data
        assert 'ai_service_available' in data
    
    def test_readiness_endpoint_integration(self, app_client):
        """Test readiness endpoint integration"""
        response = app_client.get('/api/ready')
        
        assert response.status_code in [200, 503]
        data = json.loads(response.data)
        
        assert 'status' in data
        assert 'checks' in data
        assert 'database' in data['checks']
        assert 'ai_service' in data['checks']
        assert 'configuration' in data['checks']
    
    def test_metrics_endpoint_integration(self, app_client):
        """Test metrics endpoint integration"""
        response = app_client.get('/api/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert 'total_requests' in data
        assert 'avg_response_time_ms' in data
        assert 'error_rate' in data
        assert 'uptime_seconds' in data


class TestRequestResponseFlow:
    """Test complete request/response flow"""
    
    def test_pydantic_model_integration(self, app_client):
        """Test Pydantic model integration in API flow"""
        # Test that request goes through Pydantic validation
        valid_request_data = {
            'user_id': 'test_user_123',
            'message': 'What exercises should I do?',
            'session_id': 'session_456'
        }
        
        mock_response = Mock()
        mock_response.response = "Here are some exercises..."
        mock_response.mentors_used = ["tom_merrick"]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            response = app_client.post('/api/chat', json=valid_request_data)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Response should follow ChatResponse model structure
            assert 'status' in data
            assert 'response' in data
            assert 'mentors_used' in data
            assert 'timestamp' in data
    
    def test_error_response_model_integration(self, app_client):
        """Test error response model integration"""
        # Make invalid request
        invalid_request = {
            'user_id': '',  # Invalid empty user_id
            'message': 'Hello'
        }
        
        response = app_client.post('/api/chat', json=invalid_request)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        # Should follow ErrorResponse model structure
        assert data['status'] == 'error'
        assert 'error_code' in data
        assert 'message' in data
        assert 'timestamp' in data
    
    def test_metrics_recording_integration(self, app_client):
        """Test that metrics are recorded during API calls"""
        mock_response = Mock()
        mock_response.response = "Test response"
        mock_response.mentors_used = ["tom_merrick"]
        
        with patch('application.container.container') as mock_container, \
             patch('application.interfaces.health.record_request_metrics') as mock_record:
            
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            response = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'Hello'
                })
            
            assert response.status_code == 200
            
            # Verify metrics recording was called
            mock_record.assert_called_once()
            call_args = mock_record.call_args[0]
            assert call_args[0] > 0  # response_time_ms
            assert call_args[1] is False  # error flag
            assert call_args[2] == ["tom_merrick"]  # mentors_used


class TestEndToEndScenarios:
    """End-to-end integration test scenarios"""
    
    def test_complete_user_interaction_flow(self, app_client):
        """Test complete user interaction from start to finish"""
        mock_responses = [
            Mock(response="Hello! I'm your AI coach. What are your fitness goals?", mentors_used=[]),
            Mock(response="Great! Here's a strength workout for you...", mentors_used=["tom_merrick"]),
            Mock(response="For push-ups, focus on form...", mentors_used=["tom_merrick"])
        ]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = mock_responses
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Initial greeting
            response1 = app_client.post('/api/chat',
                json={
                    'user_id': 'new_user',
                    'message': 'Hello'
                })
            
            assert response1.status_code == 200
            data1 = json.loads(response1.data)
            assert 'AI coach' in data1['response']
            
            # Step 2: Request workout
            response2 = app_client.post('/api/chat',
                json={
                    'user_id': 'new_user',
                    'message': 'I want to build strength'
                })
            
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            assert 'workout' in data2['response'].lower()
            assert 'tom_merrick' in data2['mentors_used']
            
            # Step 3: Ask for exercise details
            response3 = app_client.post('/api/chat',
                json={
                    'user_id': 'new_user',
                    'message': 'How do I do push-ups properly?'
                })
            
            assert response3.status_code == 200
            data3 = json.loads(response3.data)
            assert 'push-ups' in data3['response'].lower()
            assert 'form' in data3['response'].lower()
    
    def test_error_recovery_flow(self, app_client):
        """Test error recovery in user interaction flow"""
        with patch('application.container.container') as mock_container:
            # First request fails
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = [
                Exception("Temporary service error"),
                Mock(response="Sorry about that! I'm back online. How can I help?", mentors_used=[])
            ]
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Request that fails
            response1 = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'Hello'
                })
            
            assert response1.status_code == 500
            data1 = json.loads(response1.data)
            assert data1['status'] == 'error'
            
            # Step 2: Recovery request
            response2 = app_client.post('/api/chat',
                json={
                    'user_id': 'test_user',
                    'message': 'Hello again'
                })
            
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            assert data2['status'] == 'success'
            assert 'back online' in data2['response']
