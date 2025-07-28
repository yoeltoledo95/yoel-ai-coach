#!/usr/bin/env python3
"""
Extract feedback from WhatsApp messages and log it for each user.
"""
import json
import re
from pathlib import Path

def is_feedback_message(text):
    """Determine if a message is likely feedback."""
    text = text.lower()
    feedback_patterns = [
        r"\bfeedback[:\-]?",  # e.g. 'feedback:', 'feedback-'
        r"i felt",             # e.g. 'I felt tired', 'I felt great'
        r"i liked",            # e.g. 'I liked the workout'
        r"session was",        # e.g. 'Session was hard'
        r"workout was",        # e.g. 'Workout was fun'
        r"enjoyed",            # e.g. 'I enjoyed'
        r"struggled",          # e.g. 'I struggled with'
        r"next time",          # e.g. 'Next time I want to...'
        r"improvement",        # e.g. 'Improvement:'
        r"could be better",    # e.g. 'Could be better'
        r"was difficult",      # e.g. 'That was difficult'
        r"was easy",           # e.g. 'That was easy'
        r"energy level",       # e.g. 'Energy level was low'
        r"motivation",         # e.g. 'Motivation was high'
    ]
    return any(re.search(pat, text) for pat in feedback_patterns)

def extract_feedback_from_whatsapp(filepath):
    """Extract feedback messages from WhatsApp interactions JSON."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    feedbacks = []
    for msg in messages:
        if msg.get("from") == "user" and is_feedback_message(msg.get("text", "")):
            feedbacks.append({
                "user_id": msg.get("user_id", "unknown"),
                "timestamp": msg.get("timestamp"),
                "text": msg.get("text")
            })
    return feedbacks

def main():
    whatsapp_json = "data/users/whatsapp_interactions.json"
    feedbacks = extract_feedback_from_whatsapp(whatsapp_json)
    print(f"Found {len(feedbacks)} feedback messages:")
    for fb in feedbacks:
        print(f"[{fb['timestamp']}] User {fb['user_id']}: {fb['text']}")
    # Here you could call your AI coach's log_feedback method for each feedback

if __name__ == "__main__":
    main() 