"""
File-based configuration service implementation.
Handles loading configuration data from files in the infrastructure layer.
"""
import json
import importlib.util
from typing import Dict, Any
from pathlib import Path

from domain.services.configuration_service import ConfigurationService
from shared.exceptions import ConfigurationError
from shared.logging import get_logger

logger = get_logger(__name__)


class FileConfigurationService(ConfigurationService):
    """File-based configuration service for production use"""
    
    def __init__(self, data_root: Path = None):
        """
        Initialize with data root path
        
        Args:
            data_root: Path to data directory, defaults to project root / data
        """
        if data_root is None:
            # Find project root by going up from this file
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            data_root = project_root / "data"
        
        self.data_root = data_root
        self._workout_rules_cache = None
        self._exercise_kb_cache = None
        self._mentor_knowledge_cache = None
        
        logger.info(f"📁 Configuration service initialized with data root: {data_root}")
    
    def get_workout_programming_rules(self) -> Dict[str, Any]:
        """Load workout programming rules from JSON file"""
        if self._workout_rules_cache is not None:
            return self._workout_rules_cache
        
        try:
            rules_path = self.data_root / "knowledge_base" / "workout_programming_rules.json"
            with open(rules_path, 'r', encoding='utf-8') as f:
                self._workout_rules_cache = json.load(f)
                logger.debug(f"✅ Loaded workout programming rules from {rules_path}")
                return self._workout_rules_cache
        except Exception as e:
            logger.warning(f"⚠️ Could not load workout programming rules: {e}")
            return {}
    
    def get_exercise_knowledge_base(self) -> Dict[str, Any]:
        """Load exercise knowledge base from JSON file"""
        if self._exercise_kb_cache is not None:
            return self._exercise_kb_cache
        
        try:
            kb_path = self.data_root / "exercises" / "exercise_kb.json"
            with open(kb_path, 'r', encoding='utf-8') as f:
                self._exercise_kb_cache = json.load(f)
                logger.debug(f"✅ Loaded exercise knowledge base from {kb_path}")
                return self._exercise_kb_cache
        except Exception as e:
            logger.warning(f"⚠️ Could not load exercise knowledge base: {e}")
            return {}
    
    def get_mentor_knowledge(self) -> Dict[str, Any]:
        """Load mentor knowledge from Python module"""
        if self._mentor_knowledge_cache is not None:
            return self._mentor_knowledge_cache
        
        try:
            mentor_brain_path = self.data_root / "mentors" / "mentor_brain.py"
            
            # Dynamically import mentor brain module
            spec = importlib.util.spec_from_file_location("mentor_brain", mentor_brain_path)
            mentor_brain = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mentor_brain)
            
            self._mentor_knowledge_cache = mentor_brain.MENTOR_KNOWLEDGE
            logger.debug(f"✅ Loaded mentor knowledge from {mentor_brain_path}")
            return self._mentor_knowledge_cache
        except Exception as e:
            logger.warning(f"⚠️ Could not load mentor knowledge: {e}")
            return {}
    
    def get_programming_guidelines(self, focus_area: str) -> Dict[str, Any]:
        """Get specific programming guidelines for focus area"""
        rules = self.get_workout_programming_rules()
        programming_rules = rules.get("workout_programming_rules", {})
        return programming_rules.get(focus_area, {})
    
    def clear_cache(self):
        """Clear all cached data (useful for testing)"""
        self._workout_rules_cache = None
        self._exercise_kb_cache = None
        self._mentor_knowledge_cache = None
        logger.debug("🧹 Configuration cache cleared")
