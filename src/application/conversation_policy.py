"""
Conversation policy for chatbot: intent detection and slot-filling.

This module stays minimal: we detect if the user wants a workout plan and
ask only the missing information we need to compose it. All constraints and
variation are user-driven (asked in-chat), not hardcoded defaults.
"""
from typing import Dict, Any, Optional, Tuple


class ConversationPolicy:
    """Tiny policy engine for detecting intent and collecting slots.

    Intents handled here are minimal for P0:
    - build_today_plan: user is asking for a workout plan today
    - explain_exercise: user asks to explain an exercise
    - replace_exercise: user asks to replace an exercise
    - make_image: user asks to render an image of the plan
    - feedback_log: user provides done/modified/pain notes
    Otherwise fall back to general coaching.
    """

    PLAN_KEYWORDS = (
        "create a workout", "give me a workout", "plan my workout", "design a workout",
        "what should i train today", "need a training plan", "workout plan",
        "build me a workout", "build a workout", "workout for", "training plan",
        "build me a plan", "create a plan", "give me a plan"
    )

    IMAGE_KEYWORDS = ("make image", "image", "png", "picture", "visual")

    EXPLAIN_KEYWORDS = ("what is", "how to", "explain", "difference between")

    REPLACE_KEYWORDS = ("replace", "swap", "alternative", "substitute")

    FEEDBACK_KEYWORDS = ("done", "completed", "modified", "pain", "notes")

    REQUIRED_SLOTS = (
        "time_available",          # e.g., 30, 45, 60 (minutes)
        "equipment_available",     # free text list, e.g., "rings, bands, kettlebells"
        "shoulder_pain_today",     # yes/no + brief text allowed
        "knee_pain_today",         # yes/no + brief text allowed
        "method_preference",       # rounds | emom | flow | ladder (optional, can be none)
        "different_or_similar"     # different | similar (vs last session)
    )

    def detect_intent(self, message: str) -> str:
        text = (message or "").strip().lower()
        if any(k in text for k in self.IMAGE_KEYWORDS):
            return "make_image"
        if any(k in text for k in self.REPLACE_KEYWORDS):
            return "replace_exercise"
        if any(k in text for k in self.EXPLAIN_KEYWORDS):
            return "explain_exercise"
        if any(k in text for k in self.FEEDBACK_KEYWORDS):
            return "feedback_log"
        if any(k in text for k in self.PLAN_KEYWORDS):
            return "build_today_plan"
        return "general"

    def next_missing_slot(self, slots: Dict[str, Any]) -> Optional[str]:
        for key in self.REQUIRED_SLOTS:
            if not slots.get(key):
                return key
        return None

    def question_for_slot(self, slot: str) -> str:
        questions = {
            "time_available": "How many minutes do you have today? (e.g., 30, 45, 60)",
            "equipment_available": "What equipment do you have right now? (e.g., rings, bands, kettlebells, step)",
            "shoulder_pain_today": "Any shoulder pain today? If yes, where/when does it appear?",
            "knee_pain_today": "Any knee pain today? If yes, where/when does it appear?",
            "method_preference": "Do you prefer Rounds, EMOM, Flow, or Ladder today? If no preference, say 'no'.",
            "different_or_similar": "Do you want something different from yesterday, or similar?",
        }
        return questions.get(slot, f"Please provide: {slot}")


