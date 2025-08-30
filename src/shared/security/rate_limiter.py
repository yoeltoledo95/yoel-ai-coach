"""
Rate limiting implementation for API endpoints.
"""
import time
import logging
from typing import Dict, Tuple, Optional
from threading import Lock
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify, g

from shared.exceptions import RateLimitError
try:
    from infrastructure.config.settings import config
except ImportError:
    # Fallback for testing
    class MockConfig:
        rate_limit_enabled = True
        rate_limit_per_minute = 60
        rate_limit_per_hour = 1000
    config = MockConfig()

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe rate limiter with sliding window"""
    
    def __init__(self):
        self._windows = defaultdict(lambda: {
            'minute': deque(),
            'hour': deque()
        })
        self._lock = Lock()
        self._enabled = getattr(config, 'rate_limit_enabled', True)
        self._per_minute = getattr(config, 'rate_limit_per_minute', 60)
        self._per_hour = getattr(config, 'rate_limit_per_hour', 1000)
        
        logger.info(f"🛡️ Rate limiter initialized: {self._per_minute}/min, {self._per_hour}/hour")
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed and return current usage stats
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            
        Returns:
            Tuple of (allowed: bool, stats: dict)
        """
        if not self._enabled:
            return True, {'requests_this_minute': 0, 'requests_this_hour': 0}
        
        current_time = time.time()
        
        with self._lock:
            windows = self._windows[identifier]
            minute_window = windows['minute']
            hour_window = windows['hour']
            
            # Clean old entries (older than 60 seconds for minute, 3600 for hour)
            minute_cutoff = current_time - 60
            hour_cutoff = current_time - 3600
            
            while minute_window and minute_window[0] < minute_cutoff:
                minute_window.popleft()
            
            while hour_window and hour_window[0] < hour_cutoff:
                hour_window.popleft()
            
            # Check limits
            minute_count = len(minute_window)
            hour_count = len(hour_window)
            
            stats = {
                'requests_this_minute': minute_count,
                'requests_this_hour': hour_count,
                'limit_per_minute': self._per_minute,
                'limit_per_hour': self._per_hour
            }
            
            if minute_count >= self._per_minute:
                logger.warning(f"🚨 Rate limit exceeded (minute): {identifier} - {minute_count}/{self._per_minute}")
                return False, stats
            
            if hour_count >= self._per_hour:
                logger.warning(f"🚨 Rate limit exceeded (hour): {identifier} - {hour_count}/{self._per_hour}")
                return False, stats
            
            # Add current request
            minute_window.append(current_time)
            hour_window.append(current_time)
            
            stats['requests_this_minute'] = len(minute_window)
            stats['requests_this_hour'] = len(hour_window)
            
            return True, stats
    
    def get_stats(self, identifier: str) -> Dict[str, int]:
        """Get current rate limit stats for identifier"""
        if not self._enabled:
            return {'requests_this_minute': 0, 'requests_this_hour': 0}
        
        _, stats = self.is_allowed(identifier)
        return stats
    
    def reset(self, identifier: Optional[str] = None):
        """Reset rate limits (for testing)"""
        with self._lock:
            if identifier:
                if identifier in self._windows:
                    del self._windows[identifier]
            else:
                self._windows.clear()
        logger.info(f"🧹 Rate limits reset for: {identifier or 'ALL'}")


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(rate_spec=None):
    """
    Rate limiting decorator for Flask routes
    
    Args:
        rate_spec: Rate specification (string like "5 per minute") or function to extract identifier
                  Defaults to IP address based limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not getattr(config, 'rate_limit_enabled', True):
                return f(*args, **kwargs)
            
            # Determine identifier
            if callable(rate_spec):
                # rate_spec is a function to get identifier
                identifier = rate_spec()
            else:
                # Default to IP address
                identifier = request.remote_addr or 'unknown'
            
            # Check rate limit
            allowed, stats = rate_limiter.is_allowed(identifier)
            
            if not allowed:
                error_response = {
                    'status': 'error',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded. Please try again later.',
                    'rate_limit_stats': stats,
                    'retry_after': 60  # seconds
                }
                
                response = jsonify(error_response)
                response.status_code = 429
                response.headers['Retry-After'] = '60'
                response.headers['X-RateLimit-Limit-Minute'] = str(stats['limit_per_minute'])
                response.headers['X-RateLimit-Limit-Hour'] = str(stats['limit_per_hour'])
                response.headers['X-RateLimit-Remaining-Minute'] = str(max(0, stats['limit_per_minute'] - stats['requests_this_minute']))
                response.headers['X-RateLimit-Remaining-Hour'] = str(max(0, stats['limit_per_hour'] - stats['requests_this_hour']))
                
                return response
            
            # Store stats in Flask's g for access in the request
            g.rate_limit_stats = stats
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
