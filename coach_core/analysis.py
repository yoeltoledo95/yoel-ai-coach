"""
Analysis module for AI coaching system
Provides pattern analysis, recovery scoring, and training volume calculations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from statistics import mean, median

logger = logging.getLogger(__name__)

def analyze_patterns(logs: List[Dict[str, Any]], days: int = 7) -> Dict[str, Any]:
    """
    Analyze user patterns from recent logs
    Returns insights for AI coaching decisions
    """
    try:
        if not logs:
            return {"error": "No logs available for analysis"}
        
        # Get recent logs (last N days)
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = [
            log for log in logs 
            if datetime.fromisoformat(log.get('date', '2020-01-01')) >= cutoff_date
        ]
        
        if not recent_logs:
            return {"error": f"No logs in the last {days} days"}
        
        analysis = {
            "total_days": len(recent_logs),
            "training_frequency": _calculate_training_frequency(recent_logs),
            "recovery_trends": _analyze_recovery_trends(recent_logs),
            "mood_patterns": _analyze_mood_patterns(recent_logs),
            "sleep_quality": _analyze_sleep_quality(recent_logs),
            "energy_levels": _analyze_energy_levels(recent_logs),
            "soreness_patterns": _analyze_soreness_patterns(recent_logs),
            "nutrition_consistency": _analyze_nutrition_consistency(recent_logs),
            "hydration_consistency": _analyze_hydration_consistency(recent_logs),
            "recommendations": _generate_recommendations(recent_logs)
        }
        
        logger.info(f"✅ Pattern analysis completed for {len(recent_logs)} days")
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Error analyzing patterns: {e}")
        return {"error": f"Analysis failed: {str(e)}"}

def _calculate_training_frequency(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate training frequency and consistency"""
    training_days = [log for log in logs if log.get('training_done')]
    total_days = len(logs)
    
    if total_days == 0:
        return {"frequency": 0, "consistency": "unknown", "last_training": None}
    
    frequency = len(training_days) / total_days
    
    # Determine consistency level
    if frequency >= 0.8:
        consistency = "excellent"
    elif frequency >= 0.6:
        consistency = "good"
    elif frequency >= 0.4:
        consistency = "moderate"
    else:
        consistency = "needs_improvement"
    
    # Find last training day
    last_training = None
    for log in reversed(logs):
        if log.get('training_done'):
            last_training = log.get('date')
            break
    
    return {
        "frequency": round(frequency, 2),
        "consistency": consistency,
        "training_days": len(training_days),
        "total_days": total_days,
        "last_training": last_training
    }

def _analyze_recovery_trends(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze recovery patterns and trends"""
    recovery_scores = []
    for log in logs:
        score = log.get('recovery_score')
        if score is not None and isinstance(score, (int, float)):
            recovery_scores.append(float(score))
    
    if not recovery_scores:
        return {"trend": "unknown", "average": None, "recommendation": "Need more recovery data"}
    
    avg_recovery = mean(recovery_scores)
    recent_avg = mean(recovery_scores[-3:]) if len(recovery_scores) >= 3 else avg_recovery
    
    # Determine trend
    if recent_avg > avg_recovery + 0.5:
        trend = "improving"
    elif recent_avg < avg_recovery - 0.5:
        trend = "declining"
    else:
        trend = "stable"
    
    # Generate recommendation
    if avg_recovery < 5:
        recommendation = "Focus on recovery - consider rest days and mobility work"
    elif avg_recovery < 7:
        recommendation = "Moderate recovery - balance training intensity"
    else:
        recommendation = "Good recovery - can push training intensity"
    
    return {
        "trend": trend,
        "average": round(avg_recovery, 1),
        "recent_average": round(recent_avg, 1),
        "recommendation": recommendation
    }

def _analyze_mood_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze mood patterns and trends"""
    moods = [log.get('mood') for log in logs if log.get('mood')]
    
    if not moods:
        return {"pattern": "unknown", "recommendation": "Track mood more consistently"}
    
    # Count mood frequencies
    mood_counts = {}
    for mood in moods:
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    dominant_mood = max(mood_counts.keys(), key=lambda k: mood_counts[k])
    mood_variety = len(mood_counts)
    
    # Generate recommendation based on mood patterns
    if dominant_mood in ['great', 'good', 'excellent']:
        recommendation = "Positive mood trend - good time for challenging training"
    elif dominant_mood in ['tired', 'low', 'stressed']:
        recommendation = "Consider lighter training focus and recovery work"
    else:
        recommendation = "Mixed mood - adapt training to daily energy"
    
    return {
        "dominant_mood": dominant_mood,
        "mood_variety": mood_variety,
        "total_mood_entries": len(moods),
        "recommendation": recommendation
    }

def _analyze_sleep_quality(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze sleep patterns and quality"""
    sleep_hours = []
    for log in logs:
        hours = log.get('sleep_hours')
        if hours is not None and isinstance(hours, (int, float)):
            sleep_hours.append(float(hours))
    
    if not sleep_hours:
        return {"quality": "unknown", "recommendation": "Track sleep hours consistently"}
    
    avg_sleep = mean(sleep_hours)
    
    if avg_sleep >= 8:
        quality = "excellent"
        recommendation = "Great sleep - optimal for training performance"
    elif avg_sleep >= 7:
        quality = "good"
        recommendation = "Good sleep - maintain current routine"
    elif avg_sleep >= 6:
        quality = "moderate"
        recommendation = "Moderate sleep - consider earlier bedtime"
    else:
        quality = "needs_improvement"
        recommendation = "Insufficient sleep - prioritize sleep hygiene"
    
    return {
        "average_hours": round(avg_sleep, 1),
        "quality": quality,
        "recommendation": recommendation
    }

def _analyze_energy_levels(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze energy level patterns"""
    energy_levels = []
    for log in logs:
        energy = log.get('energy')
        if energy is not None and isinstance(energy, (int, float)):
            energy_levels.append(float(energy))
    
    if not energy_levels:
        return {"trend": "unknown", "recommendation": "Track energy levels consistently"}
    
    avg_energy = mean(energy_levels)
    recent_energy = mean(energy_levels[-3:]) if len(energy_levels) >= 3 else avg_energy
    
    if recent_energy > avg_energy + 1:
        trend = "increasing"
        recommendation = "High energy - good time for intense training"
    elif recent_energy < avg_energy - 1:
        trend = "decreasing"
        recommendation = "Lower energy - focus on recovery and mobility"
    else:
        trend = "stable"
        recommendation = "Stable energy - maintain current training approach"
    
    return {
        "average": round(avg_energy, 1),
        "recent_average": round(recent_energy, 1),
        "trend": trend,
        "recommendation": recommendation
    }

def _analyze_soreness_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze soreness patterns and recovery needs"""
    soreness_levels = []
    for log in logs:
        soreness = log.get('soreness')
        if soreness is not None and isinstance(soreness, (int, float)):
            soreness_levels.append(float(soreness))
    
    if not soreness_levels:
        return {"pattern": "unknown", "recommendation": "Track soreness levels consistently"}
    
    avg_soreness = mean(soreness_levels)
    high_soreness_days = len([s for s in soreness_levels if s >= 7])
    
    if avg_soreness >= 7:
        pattern = "high_soreness"
        recommendation = "High soreness - prioritize recovery and mobility work"
    elif avg_soreness >= 5:
        pattern = "moderate_soreness"
        recommendation = "Moderate soreness - balance training intensity"
    else:
        pattern = "low_soreness"
        recommendation = "Low soreness - can increase training intensity"
    
    return {
        "average": round(avg_soreness, 1),
        "high_soreness_days": high_soreness_days,
        "pattern": pattern,
        "recommendation": recommendation
    }

def _analyze_nutrition_consistency(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze nutrition tracking consistency"""
    nutrition_entries = [log.get('nutrition') for log in logs if log.get('nutrition')]
    consistency = len(nutrition_entries) / len(logs) if logs else 0
    
    if consistency >= 0.8:
        status = "excellent"
        recommendation = "Great nutrition tracking - maintain consistency"
    elif consistency >= 0.6:
        status = "good"
        recommendation = "Good nutrition tracking - aim for daily consistency"
    else:
        status = "needs_improvement"
        recommendation = "Inconsistent nutrition tracking - try daily logging"
    
    return {
        "consistency": round(consistency, 2),
        "status": status,
        "recommendation": recommendation
    }

def _analyze_hydration_consistency(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze hydration tracking consistency"""
    hydration_entries = [log.get('hydration') for log in logs if log.get('hydration')]
    consistency = len(hydration_entries) / len(logs) if logs else 0
    
    if consistency >= 0.8:
        status = "excellent"
        recommendation = "Great hydration tracking - maintain consistency"
    elif consistency >= 0.6:
        status = "good"
        recommendation = "Good hydration tracking - aim for daily consistency"
    else:
        status = "needs_improvement"
        recommendation = "Inconsistent hydration tracking - try daily logging"
    
    return {
        "consistency": round(consistency, 2),
        "status": status,
        "recommendation": recommendation
    }

def _generate_recommendations(logs: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    # Training frequency recommendations
    training_freq = _calculate_training_frequency(logs)
    if training_freq['consistency'] == 'needs_improvement':
        recommendations.append("Increase training frequency - aim for 3-4 sessions per week")
    elif training_freq['consistency'] == 'excellent':
        recommendations.append("Excellent training consistency - consider adding variety")
    
    # Recovery recommendations
    recovery = _analyze_recovery_trends(logs)
    if recovery.get('trend') == 'declining':
        recommendations.append("Recovery declining - prioritize rest days and mobility work")
    
    # Sleep recommendations
    sleep = _analyze_sleep_quality(logs)
    if sleep.get('quality') == 'needs_improvement':
        recommendations.append("Improve sleep quality - aim for 7-9 hours per night")
    
    # Energy recommendations
    energy = _analyze_energy_levels(logs)
    if energy.get('trend') == 'decreasing':
        recommendations.append("Energy decreasing - consider lighter training focus")
    
    return recommendations

def calculate_recovery_score(log: Dict[str, Any]) -> Optional[int]:
    """
    Calculate recovery score based on sleep, energy, soreness, and mood
    Returns score 1-10 where 10 is fully recovered
    """
    try:
        sleep_hours = log.get('sleep_hours')
        energy = log.get('energy')
        soreness = log.get('soreness')
        mood = log.get('mood')
        
        score = 5  # Base score
        
        # Sleep contribution (0-3 points)
        if sleep_hours:
            try:
                sleep_val = float(sleep_hours)
                if sleep_val >= 8:
                    score += 3
                elif sleep_val >= 7:
                    score += 2
                elif sleep_val >= 6:
                    score += 1
            except (ValueError, TypeError):
                pass  # Skip if sleep_hours is not a number
        
        # Energy contribution (0-2 points)
        if energy:
            try:
                energy_val = float(energy)
                if energy_val >= 8:
                    score += 2
                elif energy_val >= 6:
                    score += 1
            except (ValueError, TypeError):
                pass  # Skip if energy is not a number
        
        # Soreness contribution (0-2 points)
        if soreness is not None:
            try:
                soreness_val = float(soreness)
                if soreness_val <= 3:
                    score += 2
                elif soreness_val <= 5:
                    score += 1
            except (ValueError, TypeError):
                pass  # Skip if soreness is not a number
        
        # Mood contribution (0-1 point)
        if mood in ['great', 'excellent', 'good']:
            score += 1
        
        return min(max(score, 1), 10)  # Clamp between 1-10
        
    except Exception as e:
        logger.error(f"Error calculating recovery score: {e}")
        return None

def calculate_training_volume(log: Dict[str, Any]) -> Optional[int]:
    """
    Calculate training volume based on session details
    Returns volume score 1-10 where 10 is high volume
    """
    try:
        training_done = log.get('training_done')
        if not training_done:
            return 0
        
        # Simple volume calculation based on training description
        training_desc = str(training_done).lower()
        
        volume = 5  # Base volume
        
        # Intensity indicators
        if any(word in training_desc for word in ['intense', 'heavy', 'max', 'hard']):
            volume += 3
        elif any(word in training_desc for word in ['moderate', 'medium', 'balanced']):
            volume += 1
        elif any(word in training_desc for word in ['light', 'easy', 'recovery']):
            volume -= 2
        
        # Duration indicators
        if any(word in training_desc for word in ['long', 'extended', 'marathon']):
            volume += 2
        elif any(word in training_desc for word in ['short', 'quick', 'brief']):
            volume -= 1
        
        return min(max(volume, 1), 10)  # Clamp between 1-10
        
    except Exception as e:
        logger.error(f"Error calculating training volume: {e}")
        return None 