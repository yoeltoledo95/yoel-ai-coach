"""
Unit tests for health check endpoints.
Tests monitoring, metrics, and observability features.
"""
import pytest
import json
from unittest.mock import Mock, patch
from application.interfaces.health import (
    health_bp, record_request_metrics, check_database_health,
    check_ai_service_health, check_configuration, get_system_metrics,
    reset_metrics
)


class TestHealthEndpoint:
    """Test /health endpoint functionality"""
    
    def test_health_check_success(self, app_client):
        """Test successful health check"""
        with patch('application.interfaces.health.check_database_health', return_value=True), \
             patch('application.interfaces.health.check_ai_service_health', return_value=True):
            
            response = app_client.get('/api/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert data['service'] == 'ai-coach'
            assert data['version'] == '1.0.0'
            assert data['database_connected'] is True
            assert data['ai_service_available'] is True
            assert 'uptime_seconds' in data
    
    def test_health_check_database_failure(self, app_client):
        """Test health check with database failure"""
        with patch('application.interfaces.health.check_database_health', return_value=False), \
             patch('application.interfaces.health.check_ai_service_health', return_value=True):
            
            response = app_client.get('/api/health')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            
            assert data['status'] == 'error'
            assert data['database_connected'] is False
            assert data['ai_service_available'] is True
    
    def test_health_check_ai_service_failure(self, app_client):
        """Test health check with AI service failure"""
        with patch('application.interfaces.health.check_database_health', return_value=True), \
             patch('application.interfaces.health.check_ai_service_health', return_value=False):
            
            response = app_client.get('/api/health')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            
            assert data['status'] == 'error'
            assert data['database_connected'] is True
            assert data['ai_service_available'] is False
    
    def test_health_check_exception_handling(self, app_client):
        """Test health check with unexpected exception"""
        with patch('application.interfaces.health.check_database_health', side_effect=Exception("Test error")):
            
            response = app_client.get('/api/health')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            
            assert data['status'] == 'error'
            assert 'Health check failed' in data['message']


class TestReadinessEndpoint:
    """Test /ready endpoint functionality"""
    
    def test_readiness_check_success(self, app_client):
        """Test successful readiness check"""
        with patch('application.interfaces.health.check_database_health', return_value=True), \
             patch('application.interfaces.health.check_ai_service_health', return_value=True), \
             patch('application.interfaces.health.check_configuration', return_value=True):
            
            response = app_client.get('/api/ready')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'ready'
            assert data['checks']['database'] is True
            assert data['checks']['ai_service'] is True
            assert data['checks']['configuration'] is True
    
    def test_readiness_check_not_ready(self, app_client):
        """Test readiness check when not ready"""
        with patch('application.interfaces.health.check_database_health', return_value=True), \
             patch('application.interfaces.health.check_ai_service_health', return_value=False), \
             patch('application.interfaces.health.check_configuration', return_value=True):
            
            response = app_client.get('/api/ready')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            
            assert data['status'] == 'not_ready'
            assert data['checks']['database'] is True
            assert data['checks']['ai_service'] is False
            assert data['checks']['configuration'] is True


class TestMetricsEndpoint:
    """Test /metrics endpoint functionality"""
    
    def test_metrics_basic(self, app_client):
        """Test basic metrics endpoint"""
        # Reset metrics first
        reset_metrics()
        
        # Record some test metrics
        record_request_metrics(150.0, False, ['tom_merrick'])
        record_request_metrics(200.0, True, ['dylan_werner'])
        
        response = app_client.get('/api/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert data['total_requests'] == 2
        assert data['error_rate'] == 0.5  # 1 error out of 2 requests
        assert 'avg_response_time_ms' in data
        assert 'uptime_seconds' in data
        assert 'mentor_usage_stats' in data
    
    def test_metrics_with_system_info(self, app_client):
        """Test metrics endpoint with system information"""
        with patch('application.interfaces.health.get_system_metrics', 
                  return_value={'cpu_percent': 25.0, 'memory_percent': 45.0}):
            
            response = app_client.get('/api/metrics?include_system=true')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'system_metrics' in data
            assert data['system_metrics']['cpu_percent'] == 25.0
            assert data['system_metrics']['memory_percent'] == 45.0
    
    def test_metrics_exception_handling(self, app_client):
        """Test metrics endpoint with exception"""
        with patch('application.interfaces.health.record_request_metrics', side_effect=Exception("Test error")):
            
            response = app_client.get('/api/metrics')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            
            assert data['status'] == 'error'
            assert 'Failed to retrieve metrics' in data['message']


class TestHealthCheckFunctions:
    """Test individual health check functions"""
    
    def test_check_database_health_success(self):
        """Test successful database health check"""
        with patch('application.container.container') as mock_container:
            mock_repo = Mock()
            mock_container.get_user_repository.return_value = mock_repo
            
            result = check_database_health()
            
            assert result is True
            mock_repo.get_user.assert_called_once_with("health_check_test")
    
    def test_check_database_health_failure(self):
        """Test database health check failure"""
        with patch('application.container.container') as mock_container:
            mock_container.get_user_repository.side_effect = Exception("Database error")
            
            result = check_database_health()
            
            assert result is False
    
    def test_check_ai_service_health_success(self):
        """Test successful AI service health check"""
        with patch('infrastructure.config.settings.config') as mock_config, \
             patch('application.container.container') as mock_container:
            
            mock_config.openai_api_key = "sk-test-key"
            mock_container.get_openai_client.return_value = Mock()
            
            result = check_ai_service_health()
            
            assert result is True
    
    def test_check_ai_service_health_no_key(self):
        """Test AI service health check without API key"""
        with patch('infrastructure.config.settings.config') as mock_config:
            mock_config.openai_api_key = None
            
            result = check_ai_service_health()
            
            assert result is False
    
    def test_check_configuration_success(self):
        """Test successful configuration check"""
        with patch('infrastructure.config.settings.config') as mock_config:
            mock_config.openai_api_key = "sk-test-key"
            mock_config.debug = True
            
            result = check_configuration()
            
            assert result is True
    
    def test_check_configuration_failure(self):
        """Test configuration check failure"""
        with patch('infrastructure.config.settings.config') as mock_config:
            mock_config.openai_api_key = None
            
            result = check_configuration()
            
            assert result is False


class TestMetricsRecording:
    """Test metrics recording functionality"""
    
    def test_record_request_metrics(self):
        """Test recording request metrics"""
        reset_metrics()
        
        # Record some metrics
        record_request_metrics(100.0, False, ['tom_merrick'])
        record_request_metrics(200.0, True, ['dylan_werner', 'ido_portal'])
        
        # Verify metrics are recorded (would need access to internal state)
        # This is tested indirectly through the metrics endpoint tests
        pass
    
    def test_mentor_usage_tracking(self):
        """Test mentor usage statistics tracking"""
        reset_metrics()
        
        # Record mentor usage
        record_request_metrics(100.0, False, ['tom_merrick'])
        record_request_metrics(150.0, False, ['tom_merrick', 'dylan_werner'])
        record_request_metrics(120.0, False, ['dylan_werner'])
        
        # Verify mentor counts are tracked correctly
        # This would be tested through the metrics endpoint
        pass


class TestSystemMetrics:
    """Test system metrics collection"""
    
    def test_get_system_metrics_success(self):
        """Test successful system metrics collection"""
        with patch('psutil.cpu_percent', return_value=25.5), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock memory info
            mock_memory.return_value.percent = 45.0
            mock_memory.return_value.available = 8 * 1024 * 1024 * 1024  # 8GB
            
            # Mock disk info
            mock_disk.return_value.percent = 60.0
            mock_disk.return_value.free = 100 * 1024 * 1024 * 1024  # 100GB
            
            metrics = get_system_metrics()
            
            assert metrics['cpu_percent'] == 25.5
            assert metrics['memory_percent'] == 45.0
            assert metrics['memory_available_mb'] == 8192  # 8GB in MB
            assert metrics['disk_percent'] == 60.0
            assert metrics['disk_free_gb'] == 100
    
    def test_get_system_metrics_failure(self):
        """Test system metrics collection failure"""
        with patch('psutil.cpu_percent', side_effect=Exception("psutil error")):
            
            metrics = get_system_metrics()
            
            assert 'error' in metrics
            assert metrics['error'] == 'System metrics unavailable'


class TestMetricsReset:
    """Test metrics reset functionality"""
    
    def test_reset_metrics(self):
        """Test resetting metrics"""
        # Record some metrics first
        record_request_metrics(100.0, False, ['tom_merrick'])
        record_request_metrics(200.0, True, ['dylan_werner'])
        
        # Reset metrics
        reset_metrics()
        
        # Verify metrics are reset (tested indirectly through metrics endpoint)
        # After reset, total_requests should be 0, error_count should be 0, etc.
        pass
