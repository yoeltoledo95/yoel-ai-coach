"""
Mentor repository interface - defines data access contract for mentors
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.mentor import Mentor, MentorSpecialization


class MentorRepository(ABC):
    """Abstract interface for mentor data access"""
    
    @abstractmethod
    def get_mentor(self, mentor_id: str) -> Optional[Mentor]:
        """Get mentor by ID"""
        pass
    
    @abstractmethod
    def get_mentor_by_name(self, name: str) -> Optional[Mentor]:
        """Get mentor by name"""
        pass
    
    @abstractmethod
    def get_all_mentors(self) -> List[Mentor]:
        """Get all mentors"""
        pass
    
    @abstractmethod
    def get_mentors_by_specialization(self, specialization: MentorSpecialization) -> List[Mentor]:
        """Get mentors by specialization"""
        pass
    
    @abstractmethod
    def search_mentors(self, query: str) -> List[Mentor]:
        """Search mentors by query"""
        pass
    
    @abstractmethod
    def get_relevant_mentors_for_query(self, query: str) -> List[Mentor]:
        """Get mentors relevant to a specific query"""
        pass
    
    @abstractmethod
    def get_mentor_context(self, query: str, mentor_names: Optional[List[str]] = None) -> str:
        """Get mentor context for a query"""
        pass
    
    @abstractmethod
    def get_weekly_planning_context(self) -> str:
        """Get context for weekly planning"""
        pass
    
    @abstractmethod
    def get_mentor_statistics(self) -> Dict[str, Any]:
        """Get mentor knowledge base statistics"""
        pass 