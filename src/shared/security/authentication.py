"""
Authentication and authorization utilities.
"""
import jwt
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from flask import request, jsonify, current_app, g
from shared.exceptions import AuthenticationError, AuthorizationError
try:
    from infrastructure.config.settings import config
except ImportError:
    # Fallback for testing
    class MockConfig:
        jwt_secret = None
    config = MockConfig()

logger = logging.getLogger(__name__)


class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.jwt_secret = getattr(config, 'jwt_secret', None) or secrets.token_urlsafe(32)
        self.token_expiry = 24  # hours
        
        if not getattr(config, 'jwt_secret', None):
            logger.warning("⚠️ No JWT secret configured, using generated secret (will not persist across restarts)")
        
        logger.info("🔐 Authentication manager initialized")
    
    def generate_token(self, user_id: str, user_data: Dict[str, Any] = None) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_id: User identifier
            user_data: Additional user data to include in token
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry),
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        if user_data:
            payload.update(user_data)
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        logger.info(f"🔐 Token generated for user: {user_id}")
        
        return token
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check expiration (jwt library does this automatically, but let's be explicit)
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                raise AuthenticationError("Token has expired")
            
            logger.debug(f"🔐 Token validated for user: {payload.get('user_id')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        # Generate salt
        salt = secrets.token_bytes(32)
        
        # Hash password with salt
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        # Return salt + hash as hex
        return salt.hex() + password_hash.hex()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            # Extract salt and hash
            salt = bytes.fromhex(hashed[:64])  # First 32 bytes as hex
            password_hash = bytes.fromhex(hashed[64:])  # Rest as hex
            
            # Hash provided password with same salt
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            # Secure comparison
            return secrets.compare_digest(password_hash, computed_hash)
            
        except (ValueError, IndexError):
            return False
    
    def generate_api_key(self, prefix: str = "ak") -> str:
        """Generate secure API key"""
        api_key = f"{prefix}_{secrets.token_urlsafe(32)}"
        logger.info(f"🔑 API key generated with prefix: {prefix}")
        return api_key


# Global auth manager
auth_manager = AuthManager()


def require_auth(optional: bool = False):
    """
    Authentication decorator for Flask routes
    
    Args:
        optional: If True, authentication is optional
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Check Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Check query parameter (fallback, less secure)
            if not token:
                token = request.args.get('token')
            
            if not token:
                if optional:
                    g.current_user = None
                    return f(*args, **kwargs)
                else:
                    return jsonify({
                        'status': 'error',
                        'error_code': 'AUTHENTICATION_REQUIRED',
                        'message': 'Authentication token required'
                    }), 401
            
            try:
                payload = auth_manager.validate_token(token)
                g.current_user = payload
                g.user_id = payload.get('user_id')
                
            except AuthenticationError as e:
                return jsonify({
                    'status': 'error',
                    'error_code': 'AUTHENTICATION_FAILED',
                    'message': str(e)
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(permission: str):
    """
    Authorization decorator for Flask routes
    
    Args:
        permission: Required permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'status': 'error',
                    'error_code': 'AUTHENTICATION_REQUIRED',
                    'message': 'Authentication required'
                }), 401
            
            user_permissions = g.current_user.get('permissions', [])
            
            if permission not in user_permissions and 'admin' not in user_permissions:
                logger.warning(f"🚨 Authorization failed: {g.current_user.get('user_id')} lacks permission: {permission}")
                return jsonify({
                    'status': 'error',
                    'error_code': 'AUTHORIZATION_FAILED',
                    'message': f'Permission required: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def rate_limit_by_user():
    """Rate limiting identifier function using authenticated user"""
    if hasattr(g, 'user_id') and g.user_id:
        return f"user:{g.user_id}"
    else:
        return f"ip:{request.remote_addr}"
