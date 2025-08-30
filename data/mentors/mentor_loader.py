"""
Mentor Loader - Loads mentor knowledge from individual files
Replaces the monolithic mentor_brain.py with modular mentor files
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MentorLoader:
    """Loads and manages mentor knowledge from individual mentor files"""
    
    def __init__(self):
        self.mentors: Dict[str, Dict[str, Any]] = {}
        self._load_all_mentors()
    
    def _load_all_mentors(self) -> None:
        """Load all mentor files from the mentors directory"""
        mentors_dir = Path(__file__).parent
        
        # Import each mentor file
        try:
            from .dylan_werner import DYLAN_WERNER
            self.mentors["dylan_werner"] = DYLAN_WERNER
            
            from .ido_portal import IDO_PORTAL  
            self.mentors["ido_portal"] = IDO_PORTAL
            
            from .ben_patrick import BEN_PATRICK
            self.mentors["kneesovertoesguy"] = BEN_PATRICK
            
            from .tom_merrick import TOM_MERRICK
            self.mentors["tom_merrick"] = TOM_MERRICK
            
            from .emmet_louis import EMMET_LOUIS
            self.mentors["emmet_louis"] = EMMET_LOUIS
            
            from .adriell_mayes import ADRIELL_MAYES
            self.mentors["everydamnandre"] = ADRIELL_MAYES
            
            from .aaron_horschig import AARON_HORSCHIG
            self.mentors["squat_university"] = AARON_HORSCHIG
            
            from .andy_galpin import ANDY_GALPIN
            self.mentors["dr_andy_galpin"] = ANDY_GALPIN
            
            from .patrick_beach import PATRICK_BEACH
            self.mentors["patrick_beach"] = PATRICK_BEACH
            
            logger.info(f"Loaded {len(self.mentors)} mentors: {list(self.mentors.keys())}")
            
        except ImportError as e:
            logger.error(f"Error importing mentor files: {e}")
            raise
    
    def get_mentor(self, mentor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific mentor by ID"""
        return self.mentors.get(mentor_id)
    
    def get_all_mentors(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded mentors"""
        return self.mentors
    
    def get_mentors_by_tags(self, tags: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get mentors that have any of the specified tags"""
        matching_mentors = {}
        
        for mentor_id, mentor_data in self.mentors.items():
            mentor_tags = mentor_data.get("tags", [])
            if any(tag.lower() in [t.lower() for t in mentor_tags] for tag in tags):
                matching_mentors[mentor_id] = mentor_data
                
        return matching_mentors
    
    def get_mentors_by_specialization(self, specializations: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get mentors that specialize in any of the specified areas"""
        matching_mentors = {}
        
        for mentor_id, mentor_data in self.mentors.items():
            mentor_specs = mentor_data.get("specializations", [])
            if any(spec.lower() in [s.lower() for s in mentor_specs] for spec in specializations):
                matching_mentors[mentor_id] = mentor_data
                
        return matching_mentors
    
    def get_mentors_by_experience_level(self, level: str) -> Dict[str, Dict[str, Any]]:
        """Get mentors appropriate for a specific experience level"""
        matching_mentors = {}
        
        for mentor_id, mentor_data in self.mentors.items():
            mentor_levels = mentor_data.get("experience_level", [])
            if level.lower() in [l.lower() for l in mentor_levels]:
                matching_mentors[mentor_id] = mentor_data
                
        return matching_mentors
    
    def get_mentors_by_injury_focus(self, injury_areas: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get mentors that can help with specific injury areas"""
        matching_mentors = {}
        
        for mentor_id, mentor_data in self.mentors.items():
            mentor_injuries = mentor_data.get("injury_focus", [])
            if any(injury.lower() in [i.lower() for i in mentor_injuries] for injury in injury_areas):
                matching_mentors[mentor_id] = mentor_data
                
        return matching_mentors

# Global instance for easy import
mentor_loader = MentorLoader()

# Backward compatibility - expose the old format
MENTOR_KNOWLEDGE = mentor_loader.get_all_mentors()
