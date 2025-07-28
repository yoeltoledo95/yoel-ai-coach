"""
User repository interface - defines data access contract for users
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..entities.user import User, UserProfile, UserSession


class UserRepository(ABC):
    """Abstract interface for user data access"""
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def add_user(self, user: User, user_id: str = None) -> bool:
        """Add a new user"""
        pass
    
    @abstractmethod
    def save_user(self, user: User, user_id: str = None) -> bool:
        """Save user to storage"""
        pass
    
    @abstractmethod
    def update_user_profile(self, user_id: str, profile: UserProfile) -> bool:
        """Update user profile"""
        pass
    
    @abstractmethod
    def add_user_session(self, user_id: str, session: UserSession) -> bool:
        """Add a new session for user"""
        pass
    
    @abstractmethod
    def get_user_sessions(self, user_id: str, days: int = 7) -> List[UserSession]:
        """Get user sessions from last N days"""
        pass
    
    @abstractmethod
    def get_user_feedback(self, user_id: str, limit: int = 10) -> List[str]:
        """Get recent user feedback"""
        pass
    
    @abstractmethod
    def add_user_feedback(self, user_id: str, feedback: str) -> bool:
        """Add user feedback"""
        pass
    
    @abstractmethod
    def get_weekly_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current weekly plan for user"""
        pass
    
    @abstractmethod
    def save_weekly_plan(self, user_id: str, plan: Dict[str, Any]) -> bool:
        """Save weekly plan for user"""
        pass
    
    @abstractmethod
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user training statistics"""
        pass 