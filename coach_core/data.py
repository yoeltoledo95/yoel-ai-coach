import json
from typing import List, Dict, Any

PROFILE_PATH = "yoel_profile.json"
LOGS_PATH = "daily_logs.json"

def load_profile(path: str = PROFILE_PATH) -> Dict[str, Any]:
    """Load user profile from JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_profile(profile: Dict[str, Any], path: str = PROFILE_PATH) -> None:
    """Save user profile to JSON file."""
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)

def load_logs(path: str = LOGS_PATH) -> List[Dict[str, Any]]:
    """Load daily logs from JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_logs(logs: List[Dict[str, Any]], path: str = LOGS_PATH) -> None:
    """Save daily logs to JSON file."""
    with open(path, "w") as f:
        json.dump(logs, f, indent=2) 