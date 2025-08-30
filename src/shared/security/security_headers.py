"""
Security headers middleware for Flask applications.
"""
import logging
from functools import wraps
from flask import Flask, request, g
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SecurityHeaders:
    """Security headers configuration and middleware"""
    
    # Default security headers
    DEFAULT_HEADERS = {
        # Prevent MIME sniffing
        'X-Content-Type-Options': 'nosniff',
        
        # XSS Protection
        'X-XSS-Protection': '1; mode=block',
        
        # Frame options (prevent clickjacking)
        'X-Frame-Options': 'DENY',
        
        # Referrer policy
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        
        # Content Security Policy
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
        
        # Strict Transport Security (HTTPS only)
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        
        # Feature Policy / Permissions Policy
        'Permissions-Policy': (
            "camera=(), "
            "microphone=(), "
            "location=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "accelerometer=(), "
            "gyroscope=()"
        ),
        
        # Cache Control for sensitive endpoints
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    def __init__(self, app: Flask = None, custom_headers: Dict[str, str] = None):
        """
        Initialize security headers middleware
        
        Args:
            app: Flask application instance
            custom_headers: Additional custom headers
        """
        self.headers = self.DEFAULT_HEADERS.copy()
        if custom_headers:
            self.headers.update(custom_headers)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        @app.after_request
        def add_security_headers(response):
            """Add security headers to all responses"""
            
            # Skip security headers for static files (optional)
            if request.endpoint and request.endpoint.startswith('static'):
                return response
            
            # Add all security headers
            for header, value in self.headers.items():
                # Don't override existing headers
                if header not in response.headers:
                    response.headers[header] = value
            
            # Add CORS headers if needed (controlled)
            origin = request.headers.get('Origin')
            if origin:
                # Only allow configured origins
                allowed_origins = getattr(app.config, 'CORS_ORIGINS', [])
                if origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            
            return response
        
        logger.info("🛡️ Security headers middleware initialized")
    
    def update_csp(self, directive: str, value: str):
        """Update Content Security Policy directive"""
        current_csp = self.headers.get('Content-Security-Policy', '')
        
        # Simple CSP update (could be more sophisticated)
        if directive in current_csp:
            # Replace existing directive
            import re
            pattern = f"{directive}[^;]*;"
            replacement = f"{directive} {value};"
            self.headers['Content-Security-Policy'] = re.sub(pattern, replacement, current_csp)
        else:
            # Add new directive
            self.headers['Content-Security-Policy'] += f" {directive} {value};"
        
        logger.info(f"🛡️ CSP updated: {directive} = {value}")


def security_audit_middleware(app: Flask):
    """Security auditing middleware"""
    
    @app.before_request
    def security_audit():
        """Audit security aspects of incoming requests"""
        
        # Initialize security context
        g.security_context = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'content_length': request.content_length or 0,
            'suspicious_indicators': []
        }
        
        # Check for suspicious patterns
        suspicious_indicators = []
        
        # Large request body
        if g.security_context['content_length'] > 1024 * 1024:  # 1MB
            suspicious_indicators.append('large_request_body')
        
        # Suspicious User-Agent
        ua = g.security_context['user_agent'].lower()
        if any(pattern in ua for pattern in ['bot', 'crawler', 'scanner', 'exploit']):
            suspicious_indicators.append('suspicious_user_agent')
        
        # Missing User-Agent (automation indicator)
        if not g.security_context['user_agent']:
            suspicious_indicators.append('missing_user_agent')
        
        # Suspicious referer
        referer = g.security_context['referer']
        if referer and any(pattern in referer.lower() for pattern in ['admin', 'config', 'setup']):
            suspicious_indicators.append('suspicious_referer')
        
        # Multiple suspicious indicators
        g.security_context['suspicious_indicators'] = suspicious_indicators
        
        if len(suspicious_indicators) >= 2:
            logger.warning(f"🚨 Multiple suspicious indicators: {suspicious_indicators} from {g.security_context['ip_address']}")
    
    @app.after_request 
    def security_response_audit(response):
        """Audit security aspects of outgoing responses"""
        
        # Log security events
        if hasattr(g, 'security_context'):
            if g.security_context['suspicious_indicators']:
                logger.info(f"🔍 Security audit: {g.security_context['suspicious_indicators']} - Status: {response.status_code}")
        
        return response
    
    logger.info("🛡️ Security audit middleware initialized")
