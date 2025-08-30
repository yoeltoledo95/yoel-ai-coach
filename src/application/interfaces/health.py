"""
Health check endpoints for monitoring and observability.
Provides system health, readiness, and metrics endpoints.
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from shared.models.responses import HealthCheckResponse, MetricsResponse, ResponseStatus
from shared.exceptions import DatabaseError, ConfigurationError
from infrastructure.config.settings import config

logger = logging.getLogger(__name__)

# Global metrics storage (in production, use Redis or proper metrics store)
_start_time = time.time()
_request_count = 0
_total_response_time = 0.0
_error_count = 0
_mentor_usage = {}

health_bp = Blueprint('health', __name__)


def record_request_metrics(response_time_ms: float, error: bool = False, mentors_used: Optional[list] = None):
    """Record metrics for a request"""
    global _request_count, _total_response_time, _error_count, _mentor_usage
    
    _request_count += 1
    _total_response_time += response_time_ms
    
    if error:
        _error_count += 1
    
    if mentors_used:
        for mentor in mentors_used:
            _mentor_usage[mentor] = _mentor_usage.get(mentor, 0) + 1


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    Returns: 200 if service is healthy, 503 if unhealthy
    """
    try:
        # Check database connection
        database_healthy = check_database_health()
        
        # Check AI service availability  
        ai_service_healthy = check_ai_service_health()
        
        # Calculate uptime
        uptime_seconds = int(time.time() - _start_time)
        
        # Determine overall health
        is_healthy = database_healthy and ai_service_healthy
        
        response = HealthCheckResponse(
            status=ResponseStatus.SUCCESS if is_healthy else ResponseStatus.ERROR,
            service="ai-coach",
            version="1.0.0",
            uptime_seconds=uptime_seconds,
            database_connected=database_healthy,
            ai_service_available=ai_service_healthy
        )
        
        status_code = 200 if is_healthy else 503
        return jsonify(response.dict()), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Health check failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint for Kubernetes.
    Returns: 200 if service is ready to accept traffic
    """
    try:
        # More thorough checks for readiness
        database_ready = check_database_health()
        ai_service_ready = check_ai_service_health()
        config_valid = check_configuration()
        
        is_ready = database_ready and ai_service_ready and config_valid
        
        checks = {
            "database": database_ready,
            "ai_service": ai_service_ready,
            "configuration": config_valid
        }
        
        response = {
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        status_code = 200 if is_ready else 503
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Readiness check failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Metrics endpoint for monitoring.
    Returns: Application metrics and performance data
    """
    try:
        include_system = request.args.get('include_system', 'false').lower() == 'true'
        
        # Calculate metrics
        uptime_seconds = int(time.time() - _start_time)
        avg_response_time = _total_response_time / max(_request_count, 1)
        error_rate = _error_count / max(_request_count, 1)
        requests_per_hour = _request_count / max(uptime_seconds / 3600, 1/3600)
        
        response = MetricsResponse(
            status=ResponseStatus.SUCCESS,
            total_requests=_request_count,
            avg_response_time_ms=avg_response_time,
            error_rate=error_rate,
            uptime_seconds=uptime_seconds,
            requests_per_hour=int(requests_per_hour),
            mentor_usage_stats=dict(_mentor_usage)
        )
        
        result = response.dict()
        
        # Add system metrics if requested
        if include_system:
            result["system_metrics"] = get_system_metrics()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve metrics",
            "timestamp": datetime.utcnow().isoformat()
        }), 500


def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        # Import here to avoid circular imports
        from application.container import container
        
        user_repo = container.get_user_repository()
        # Try a simple operation
        user_repo.get_user("health_check_test")  # This should not crash
        return True
        
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


def check_ai_service_health() -> bool:
    """Check if AI service (OpenAI) is accessible"""
    try:
        # Check if API key is configured
        if not config.openai_api_key:
            return False
        
        # Import here to avoid circular imports  
        from application.container import container
        
        openai_client = container.get_openai_client()
        # For now, just check if client is configured
        # In production, you might make a lightweight API call
        return openai_client is not None
        
    except Exception as e:
        logger.warning(f"AI service health check failed: {e}")
        return False


def check_configuration() -> bool:
    """Check if required configuration is present"""
    try:
        required_configs = [
            config.openai_api_key,
            config.debug is not None,
        ]
        
        return all(conf is not None for conf in required_configs)
        
    except Exception as e:
        logger.warning(f"Configuration check failed: {e}")
        return False


def get_system_metrics() -> Dict[str, Any]:
    """Get system-level metrics"""
    try:
        # CPU and memory info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available // (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free // (1024 * 1024 * 1024)
        }
        
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        return {"error": "System metrics unavailable"}


def reset_metrics():
    """Reset metrics (for testing)"""
    global _request_count, _total_response_time, _error_count, _mentor_usage, _start_time
    
    _request_count = 0
    _total_response_time = 0.0
    _error_count = 0
    _mentor_usage = {}
    _start_time = time.time()
