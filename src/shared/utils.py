from typing import Dict, Any

def detect_split(training_done: str) -> str:
    """Detect training split from training_done string."""
    if not training_done or training_done.lower() == "none/rest day":
        return "Rest"
    elif "push" in training_done.lower():
        return "Push"
    elif "pull" in training_done.lower():
        return "Pull"
    elif "legs" in training_done.lower():
        return "Legs"
    elif "yoga" in training_done.lower():
        return "Yoga"
    elif "mobility" in training_done.lower() or "recovery" in training_done.lower():
        return "Recovery"
    else:
        return "Other"

def calculate_recovery_score(entry: Dict[str, Any]) -> float:
    """Calculate recovery score based on entry fields."""
    score = 5.0  # Base score
    # Energy level (0-10)
    if 'energy' in entry:
        try:
            energy = float(entry['energy'])
            score += (energy - 5) * 0.3
        except:
            pass
    # Sleep hours
    if 'sleep_hours' in entry:
        try:
            sleep = float(entry['sleep_hours'])
            if 7 <= sleep <= 9:
                score += 1.0
            elif 6 <= sleep < 7 or 9 < sleep <= 10:
                score += 0.5
            elif sleep < 6:
                score -= 1.0
        except:
            pass
    # Sleep quality
    if 'sleep_quality' in entry:
        try:
            quality = float(entry['sleep_quality'])
            score += (quality - 5) * 0.2
        except:
            pass
    # Stress level (inverse)
    if 'stress_level' in entry:
        try:
            stress = float(entry['stress_level'])
            score -= (stress - 5) * 0.2
        except:
            pass
    # Training quality
    if 'training_quality' in entry:
        try:
            training_quality = float(entry['training_quality'])
            score += (training_quality - 5) * 0.1
        except:
            pass
    # Hydration
    if 'hydration' in entry:
        try:
            hydration = float(entry['hydration'])
            score += (hydration - 5) * 0.1
        except:
            pass
    return max(0, min(10, score))

def estimate_training_volume(training_done: str) -> str:
    """Estimate training volume from training_done string."""
    if not training_done or training_done.lower() == "none/rest day":
        return "none"
    elif "heavy" in training_done.lower():
        return "high"
    elif "moderate" in training_done.lower():
        return "medium"
    elif "light" in training_done.lower() or "mobility" in training_done.lower() or "recovery" in training_done.lower():
        return "low"
    else:
        return "medium" 