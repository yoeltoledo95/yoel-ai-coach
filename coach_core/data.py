import json
from typing import List, Dict, Any, Optional, Tuple
from .database import CoachDatabase
from functools import lru_cache
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Legacy JSON paths for backward compatibility
PROFILE_PATH = "yoel_profile.json"
LOGS_PATH = "daily_logs.json"

def get_default_profile() -> Dict[str, Any]:
    """Get Yoel's default profile with his specific preferences and context."""
    return {
        "name": "Yoel",
        "age": 30,
        "goals": ["strength", "endurance", "mobility"],
        "training_preferences": {
            "split": "Push/Pull/Legs",
            "training_days": 4,
            "preferred_style": "calisthenics",
            "secondary_activities": ["yoga", "mobility"]
        },
        "injury_history": {
            "shoulder": "ongoing issues, needs careful management",
            "knee": "recovered, can do more work now"
        },
        "nutrition_preferences": {
            "diet": "flexible, focuses on protein and clean carbs",
            "favorites": ["eggs with tahini", "chicken with rice", "vegetables"]
        },
        "recovery_needs": {
            "sleep_target": 7.5,
            "stress_management": "important",
            "mobility_work": "daily"
        }
    }

def validate_log_entry(log: Dict[str, Any]) -> bool:
    """Validate a log entry has required fields."""
    required_fields = ["date", "timestamp"]
    return all(field in log for field in required_fields)

def validate_profile_entry(profile: Dict[str, Any]) -> bool:
    """Validate profile data structure."""
    return isinstance(profile, dict)

def load_profile(db=None) -> Dict[str, Any]:
    """Load profile from database (single source of truth)."""
    db = db or CoachDatabase()
    try:
        profile = db.load_profile()
        if profile and validate_profile_entry(profile):
            # Check if this is Yoel's profile (not test data)
            if profile.get("name") == "Yoel":
                return profile
            else:
                logger.info("Found test profile, creating Yoel's default profile")
                default_profile = get_default_profile()
                save_profile(default_profile, db)
                return default_profile
        else:
            logger.info("No profile in database, creating default")
            default_profile = get_default_profile()
            save_profile(default_profile, db)
            return default_profile
    except Exception as e:
        logger.error(f"Error loading profile from database: {e}")
        # Only fall back to JSON if database is corrupted/missing
        try:
            with open(PROFILE_PATH, "r") as f:
                profile = json.load(f)
                if validate_profile_entry(profile):
                    logger.warning("Falling back to JSON profile due to database error")
                    return profile
        except Exception as json_error:
            logger.error(f"JSON fallback also failed: {json_error}")
        
        # Create default profile as last resort
        default_profile = get_default_profile()
        save_profile(default_profile, db)
        return default_profile

def save_profile(profile: Dict[str, Any], db=None) -> bool:
    """Save profile to database (single source of truth)."""
    db = db or CoachDatabase()
    try:
        if not validate_profile_entry(profile):
            logger.error("Invalid profile data structure")
            return False
        
        # Save to database only
        db.save_profile(profile)
        
        # Clear cache since profile changed
        clear_cache()
        return True
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        return False

def load_logs(db=None) -> List[Dict[str, Any]]:
    """Load logs from database (single source of truth)."""
    db = db or CoachDatabase()
    try:
        logs = db.load_logs()
        if logs:
            # Validate all log entries
            valid_logs = [log for log in logs if validate_log_entry(log)]
            if len(valid_logs) != len(logs):
                logger.warning(f"Filtered out {len(logs) - len(valid_logs)} invalid log entries")
            return valid_logs
        else:
            logger.info("No logs in database")
            return []
    except Exception as e:
        logger.error(f"Error loading logs from database: {e}")
        # Only fall back to JSON if database is corrupted/missing
        try:
            with open(LOGS_PATH, "r") as f:
                logs = json.load(f)
                # Validate all log entries
                valid_logs = [log for log in logs if validate_log_entry(log)]
                if len(valid_logs) != len(logs):
                    logger.warning(f"Filtered out {len(logs) - len(valid_logs)} invalid log entries from JSON")
                logger.warning("Falling back to JSON logs due to database error")
                return valid_logs
        except Exception as json_error:
            logger.error(f"JSON fallback also failed: {json_error}")
        
        return []

def save_logs(logs: List[Dict[str, Any]], db=None) -> bool:
    """Save logs to database (single source of truth)."""
    db = db or CoachDatabase()
    try:
        # Validate all log entries
        valid_logs = [log for log in logs if validate_log_entry(log)]
        if len(valid_logs) != len(logs):
            logger.warning(f"Filtered out {len(logs) - len(valid_logs)} invalid log entries")
        
        # Save to database only
        db.save_logs(valid_logs)
        
        # Clear cache since logs changed
        clear_cache()
        return True
    except Exception as e:
        logger.error(f"Error saving logs: {e}")
        return False

def add_log(log: Dict[str, Any], db=None) -> bool:
    """Add a single log to database."""
    db = db or CoachDatabase()
    try:
        if not validate_log_entry(log):
            logger.error("Invalid log entry structure")
            return False
        
        db.add_log(log)
        # Clear cache since logs changed
        clear_cache()
        return True
    except Exception as e:
        logger.error(f"Error adding log: {e}")
        return False

def get_log_by_date(date: str, db=None) -> Optional[Dict[str, Any]]:
    """Get log by date from database."""
    db = db or CoachDatabase()
    try:
        result = db.get_log_by_date(date)
        return result if result and validate_log_entry(result) else None
    except Exception as e:
        logger.error(f"Error getting log by date {date}: {e}")
        return None

@lru_cache(maxsize=128)
def get_recent_logs(days: int = 7, db=None) -> List[Dict[str, Any]]:
    """Get recent logs from database."""
    db = db or CoachDatabase()
    try:
        logs = db.get_recent_logs(days)
        # Validate all log entries
        valid_logs = [log for log in logs if validate_log_entry(log)]
        if len(valid_logs) != len(logs):
            logger.warning(f"Filtered out {len(logs) - len(valid_logs)} invalid log entries")
        return valid_logs
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        return []

@lru_cache(maxsize=64)
def get_stats(db=None) -> Dict[str, Any]:
    """Get stats from database."""
    db = db or CoachDatabase()
    try:
        return db.get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}

# Backup/Export/Import functions
def export_to_json(profile_path: str = PROFILE_PATH, logs_path: str = LOGS_PATH, db=None) -> bool:
    """Export database data to JSON files for backup."""
    db = db or CoachDatabase()
    try:
        # Export profile
        profile = load_profile(db)
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)
        
        # Export logs
        logs = load_logs(db)
        with open(logs_path, "w") as f:
            json.dump(logs, f, indent=2)
        
        logger.info(f"Successfully exported {len(logs)} logs and profile to JSON")
        return True
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return False

def import_from_json(profile_path: str = PROFILE_PATH, logs_path: str = LOGS_PATH, db=None) -> bool:
    """Import JSON data to database."""
    db = db or CoachDatabase()
    try:
        # Import profile
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile = json.load(f)
            if validate_profile_entry(profile):
                save_profile(profile, db)
                logger.info("Successfully imported profile from JSON")
        
        # Import logs
        if os.path.exists(logs_path):
            with open(logs_path, "r") as f:
                logs = json.load(f)
            valid_logs = [log for log in logs if validate_log_entry(log)]
            if valid_logs:
                save_logs(valid_logs, db)
                logger.info(f"Successfully imported {len(valid_logs)} logs from JSON")
        
        return True
    except Exception as e:
        logger.error(f"Error importing from JSON: {e}")
        return False

def check_sync_status(db=None) -> Tuple[bool, Dict[str, Any]]:
    """Check if database and JSON files are in sync."""
    db = db or CoachDatabase()
    try:
        # Get database data
        db_profile = load_profile(db)
        db_logs = load_logs(db)
        
        # Get JSON data
        json_profile = {}
        json_logs = []
        
        try:
            with open(PROFILE_PATH, "r") as f:
                json_profile = json.load(f)
        except:
            pass
        
        try:
            with open(LOGS_PATH, "r") as f:
                json_logs = json.load(f)
        except:
            pass
        
        # Compare
        profile_sync = db_profile == json_profile
        logs_sync = len(db_logs) == len(json_logs)
        
        # More detailed comparison for logs (check dates)
        if logs_sync and db_logs and json_logs:
            db_dates = set(log.get("date") for log in db_logs)
            json_dates = set(log.get("date") for log in json_logs)
            logs_sync = db_dates == json_dates
        
        is_synced = profile_sync and logs_sync
        
        status = {
            "is_synced": is_synced,
            "profile_sync": profile_sync,
            "logs_sync": logs_sync,
            "db_logs_count": len(db_logs),
            "json_logs_count": len(json_logs),
            "db_profile_keys": list(db_profile.keys()),
            "json_profile_keys": list(json_profile.keys())
        }
        
        return is_synced, status
    except Exception as e:
        logger.error(f"Error checking sync status: {e}")
        return False, {"error": str(e)}

def migrate_from_json(db=None):
    """Migrate existing JSON data to database (one-time operation)."""
    db = db or CoachDatabase()
    try:
        db.migrate_from_json()
    except Exception as e:
        logger.error(f"Error migrating from JSON: {e}")

# Cache invalidation function
def clear_cache():
    """Clear all caches when data is updated."""
    get_recent_logs.cache_clear()
    get_stats.cache_clear() 