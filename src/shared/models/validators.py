"""
Custom validators for AI Coach application.
"""
import re
import html
from typing import Any, Optional


def validate_user_message(message: str) -> str:
    """
    Validate and sanitize user message.
    
    Args:
        message: Raw user message
        
    Returns:
        Sanitized message
        
    Raises:
        ValueError: If message is invalid
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    # Sanitize HTML
    sanitized = html.escape(message.strip())
    
    # Check length
    if len(sanitized) > 1000:
        raise ValueError("Message too long (max 1000 characters)")
    
    # Check for excessive special characters
    special_char_count = len(re.findall(r'[^a-zA-Z0-9\s\.\?\!\,\'\-]', sanitized))
    if special_char_count / len(sanitized) > 0.3:
        raise ValueError("Message contains too many special characters")
    
    # Check for potential injection patterns
    dangerous_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValueError("Message contains potentially dangerous content")
    
    return sanitized


def validate_user_id(user_id: str) -> str:
    """
    Validate user ID format.
    
    Args:
        user_id: User identifier
        
    Returns:
        Validated user ID
        
    Raises:
        ValueError: If user ID is invalid
    """
    if not user_id or not user_id.strip():
        raise ValueError("User ID cannot be empty")
    
    user_id = user_id.strip()
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValueError("User ID can only contain letters, numbers, underscores, and hyphens")
    
    if len(user_id) > 50:
        raise ValueError("User ID too long (max 50 characters)")
    
    return user_id


def sanitize_input(value: Any) -> Any:
    """
    General purpose input sanitization.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        return html.escape(value.strip())
    elif isinstance(value, list):
        return [sanitize_input(item) for item in value]
    elif isinstance(value, dict):
        return {key: sanitize_input(val) for key, val in value.items()}
    else:
        return value


def validate_workout_duration(duration: Optional[int]) -> Optional[int]:
    """
    Validate workout duration.
    
    Args:
        duration: Duration in minutes
        
    Returns:
        Validated duration
        
    Raises:
        ValueError: If duration is invalid
    """
    if duration is None:
        return None
    
    if not isinstance(duration, int):
        raise ValueError("Duration must be an integer")
    
    if duration < 5:
        raise ValueError("Workout duration must be at least 5 minutes")
    
    if duration > 180:
        raise ValueError("Workout duration cannot exceed 3 hours")
    
    return duration


def validate_intensity_level(intensity: Optional[str]) -> Optional[str]:
    """
    Validate workout intensity level.
    
    Args:
        intensity: Intensity level
        
    Returns:
        Validated intensity
        
    Raises:
        ValueError: If intensity is invalid
    """
    if intensity is None:
        return None
    
    valid_levels = {'low', 'moderate', 'high'}
    
    if intensity.lower() not in valid_levels:
        raise ValueError(f"Intensity must be one of: {', '.join(valid_levels)}")
    
    return intensity.lower()


def validate_equipment_list(equipment: Optional[list]) -> Optional[list]:
    """
    Validate equipment list.
    
    Args:
        equipment: List of equipment
        
    Returns:
        Validated equipment list
        
    Raises:
        ValueError: If equipment list is invalid
    """
    if equipment is None:
        return None
    
    if not isinstance(equipment, list):
        raise ValueError("Equipment must be a list")
    
    if len(equipment) > 50:
        raise ValueError("Too many equipment items (max 50)")
    
    valid_equipment = {
        'bodyweight', 'dumbbells', 'barbell', 'kettlebells', 'resistance_bands',
        'pull_up_bar', 'rings', 'medicine_ball', 'foam_roller', 'yoga_mat',
        'bench', 'squat_rack', 'treadmill', 'bike', 'rowing_machine'
    }
    
    validated = []
    for item in equipment:
        if not isinstance(item, str):
            raise ValueError("Equipment items must be strings")
        
        item = item.lower().strip().replace(' ', '_')
        
        if item in valid_equipment:
            validated.append(item)
        else:
            raise ValueError(f"Unknown equipment: {item}")
    
    return list(set(validated))  # Remove duplicates
