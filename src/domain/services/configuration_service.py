"""
Configuration service interface for domain layer.
Provides abstraction for accessing configuration data without file system dependencies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ConfigurationService(ABC):
    """Abstract configuration service for domain layer data access"""
    
    @abstractmethod
    def get_workout_programming_rules(self) -> Dict[str, Any]:
        """Get workout programming rules and guidelines"""
        pass
    
    @abstractmethod
    def get_exercise_knowledge_base(self) -> Dict[str, Any]:
        """Get exercise knowledge base data"""
        pass
    
    @abstractmethod
    def get_mentor_knowledge(self) -> Dict[str, Any]:
        """Get mentor knowledge and expertise data"""
        pass
    
    @abstractmethod
    def get_programming_guidelines(self, focus_area: str) -> Dict[str, Any]:
        """Get specific programming guidelines for focus area"""
        pass


class InMemoryConfigurationService(ConfigurationService):
    """In-memory implementation for testing"""
    
    def __init__(self):
        self._workout_rules = {}
        self._exercise_kb = {}
        self._mentor_knowledge = {}
    
    def get_workout_programming_rules(self) -> Dict[str, Any]:
        return self._workout_rules
    
    def get_exercise_knowledge_base(self) -> Dict[str, Any]:
        return self._exercise_kb
    
    def get_mentor_knowledge(self) -> Dict[str, Any]:
        return self._mentor_knowledge
    
    def get_programming_guidelines(self, focus_area: str) -> Dict[str, Any]:
        rules = self._workout_rules.get("workout_programming_rules", {})
        return rules.get(focus_area, {})
