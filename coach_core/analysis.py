from typing import List, Dict, Any

def analyze_patterns(logs: List[Dict[str, Any]]) -> str:
    """Analyze patterns in user's logs for AI context and UI display."""
    if not logs:
        return "No training history available yet."
    
    recent_logs = logs[-7:]  # Last 7 days
    energy_trend = []
    training_frequency = 0
    common_soreness = []
    
    for log in recent_logs:
        if 'energy' in log and str(log['energy']).isdigit():
            energy_trend.append(int(log['energy']))
        if log.get('training_done') and log['training_done'].strip():
            training_frequency += 1
        if log.get('soreness') and log['soreness'] and log['soreness'].lower() != 'none':
            common_soreness.extend([s.strip() for s in log['soreness'].split(",")])
    
    analysis = f"Recent Analysis:\n"
    if energy_trend:
        avg_energy = sum(energy_trend) / len(energy_trend)
        analysis += f"- Average energy: {avg_energy:.1f}/10\n"
    analysis += f"- Training frequency: {training_frequency} days in last week\n"
    if common_soreness:
        analysis += f"- Common soreness: {', '.join(set(common_soreness))}\n"
    return analysis 