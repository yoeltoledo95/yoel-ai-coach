"""
Advanced input validation and sanitization utilities.
"""
import re
import html
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from shared.exceptions import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """Advanced input validation and sanitization"""
    
    # Dangerous patterns that should be rejected
    DANGEROUS_PATTERNS = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'data:text/html',          # Data URLs with HTML
        r'vbscript:',               # VBScript
        r'on\w+\s*=',               # Event handlers
        r'<iframe.*?>',             # IFrames
        r'<object.*?>',             # Object tags
        r'<embed.*?>',              # Embed tags
        r'<form.*?>',               # Forms
        r'<input.*?>',              # Input fields
        r'<link.*?>',               # Link tags
        r'<meta.*?>',               # Meta tags
        r'<base.*?>',               # Base tags
        r'eval\s*\(',               # eval() calls
        r'Function\s*\(',           # Function constructor
        r'setTimeout\s*\(',         # setTimeout calls
        r'setInterval\s*\(',        # setInterval calls
        r'document\.',              # Document access
        r'window\.',                # Window access
        r'location\.',              # Location access
        r'\.innerHTML',             # innerHTML manipulation
        r'\.outerHTML',             # outerHTML manipulation
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',          # Union select
        r'drop\s+table',            # Drop table
        r'delete\s+from',           # Delete from
        r'insert\s+into',           # Insert into
        r'update\s+set',            # Update set
        r'create\s+table',          # Create table
        r'alter\s+table',           # Alter table
        r'exec\s*\(',               # Exec calls
        r'sp_\w+',                  # Stored procedures
        r'xp_\w+',                  # Extended procedures
        r'--\s*$',                  # SQL comments
        r'/\*.*?\*/',               # SQL block comments
        r';\s*$',                   # Statement terminators
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$]',                 # Command separators
        r'\$\(',                    # Command substitution
        r'`.*?`',                   # Backtick execution
        r'>\s*/dev/',               # Device redirection
        r'<\s*/dev/',               # Device input
        r'nc\s+',                   # Netcat
        r'wget\s+',                 # Wget
        r'curl\s+',                 # Curl
        r'chmod\s+',                # Chmod
        r'rm\s+-',                  # Remove with flags
        r'sudo\s+',                 # Sudo
        r'su\s+',                   # Su
    ]
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content"""
        if not text:
            return ""
        
        # HTML escape
        sanitized = html.escape(text)
        
        # URL decode to catch encoded attacks
        try:
            decoded = unquote(sanitized)
            # Re-escape after decoding
            sanitized = html.escape(decoded)
        except Exception:
            # If decoding fails, stick with escaped version
            pass
        
        return sanitized
    
    @classmethod
    def validate_message(cls, message: str, max_length: int = 1000) -> str:
        """
        Comprehensive message validation
        
        Args:
            message: Raw message
            max_length: Maximum allowed length
            
        Returns:
            Sanitized message
            
        Raises:
            ValidationError: If message is invalid or dangerous
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        original_length = len(message)
        message = message.strip()
        
        # Length check
        if len(message) > max_length:
            raise ValidationError(f"Message too long (max {max_length} characters)")
        
        # Check for suspicious length reduction after stripping
        if original_length > len(message) * 2:
            raise ValidationError("Message contains excessive whitespace")
        
        # Check for dangerous patterns
        message_lower = message.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE | re.DOTALL):
                logger.warning(f"🚨 Dangerous pattern detected: {pattern}")
                raise ValidationError("Message contains potentially dangerous content")
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.warning(f"🚨 SQL injection pattern detected: {pattern}")
                raise ValidationError("Message contains potentially dangerous SQL content")
        
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"🚨 Command injection pattern detected: {pattern}")
                raise ValidationError("Message contains potentially dangerous command content")
        
        # Check character composition
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s\.\?\!\,\'\-\:\;\(\)]', message))
        if special_chars / len(message) > 0.4:
            raise ValidationError("Message contains too many special characters")
        
        # Check for excessive repetition
        if re.search(r'(.)\1{50,}', message):  # 50+ repeated characters
            raise ValidationError("Message contains excessive character repetition")
        
        # Check for binary-like content
        non_printable = len(re.findall(r'[^\x20-\x7E]', message))
        if non_printable > 0:
            raise ValidationError("Message contains non-printable characters")
        
        # Sanitize and return
        return cls.sanitize_html(message)
    
    @classmethod
    def validate_user_id(cls, user_id: str) -> str:
        """
        Validate user ID format
        
        Args:
            user_id: Raw user ID
            
        Returns:
            Sanitized user ID
            
        Raises:
            ValidationError: If user ID is invalid
        """
        if not user_id or not user_id.strip():
            raise ValidationError("User ID cannot be empty")
        
        user_id = user_id.strip()
        
        # Length check
        if len(user_id) > 50:
            raise ValidationError("User ID too long (max 50 characters)")
        
        # Format check - only alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            raise ValidationError("User ID contains invalid characters")
        
        # Check for suspicious patterns
        if re.search(r'[_-]{3,}', user_id):  # Multiple consecutive special chars
            raise ValidationError("User ID format invalid")
        
        return user_id
    
    @classmethod
    def validate_session_id(cls, session_id: Optional[str]) -> Optional[str]:
        """Validate session ID format"""
        if not session_id:
            return None
        
        session_id = session_id.strip()
        
        if len(session_id) > 100:
            raise ValidationError("Session ID too long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            raise ValidationError("Session ID contains invalid characters")
        
        return session_id
    
    @classmethod
    def validate_json_payload(cls, payload: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """
        Validate JSON payload structure and content
        
        Args:
            payload: JSON payload
            max_depth: Maximum nesting depth
            
        Returns:
            Validated payload
            
        Raises:
            ValidationError: If payload is invalid
        """
        if not isinstance(payload, dict):
            raise ValidationError("Payload must be a JSON object")
        
        # Check depth
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValidationError(f"JSON too deeply nested (max {max_depth} levels)")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(payload)
        
        # Check for excessively large strings
        def check_strings(obj):
            if isinstance(obj, str) and len(obj) > 10000:
                raise ValidationError("JSON contains excessively large string")
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_strings(item)
        
        check_strings(payload)
        
        return payload
    
    @classmethod
    def validate_auth(cls, data: dict) -> dict:
        """Validate authentication data"""
        if not isinstance(data, dict):
            raise ValidationError("Invalid data format")
        
        # Email validation
        email = data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email is required")
        
        # Basic email format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        # Password validation
        password = data.get('password', '')
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters")
        
        # Name validation (for signup)
        result = {
            'email': email,
            'password': password
        }
        
        if 'name' in data:
            name = data.get('name', '').strip()
            if name:
                result['name'] = cls.sanitize_html(name)
        
        return result
