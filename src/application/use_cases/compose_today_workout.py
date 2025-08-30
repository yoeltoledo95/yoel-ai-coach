"""
Use case: Compose today's workout via chat, with slot-filling and RAG bias.

Flow:
- Detect plan intent and ask only missing slots
- Retrieve mentor context (RAG)
- Compose workout per knowledge base via WorkoutComposer
- Return clean text plan; image only on explicit request (handled elsewhere)
"""
from typing import Dict, Any

from shared.logging import get_logger
from application.conversation_policy import ConversationPolicy
from domain.services.workout_composer import WorkoutComposer


logger = get_logger(__name__)


class ComposeTodayWorkoutUseCase:
    def __init__(self,
                 composer: WorkoutComposer,
                 mentor_repository,
                 user_memory_store,
                 conversation_policy: ConversationPolicy | None = None):
        self.composer = composer
        self.mentor_repository = mentor_repository
        self.user_memory_store = user_memory_store
        self.policy = conversation_policy or ConversationPolicy()

    def execute(self, user_id: str, user_message: str, slots: Dict[str, Any]) -> Dict[str, Any]:
        intent = self.policy.detect_intent(user_message)
        if intent != "build_today_plan":
            # Not our intent; signal caller to route elsewhere
            return {"handoff": True}

        # Attempt to fill a waiting slot from caller (handled in web layer). If no slot is pending,
        # proceed to check if anything is missing and ask the first missing.
        next_slot = self.policy.next_missing_slot(slots)
        if next_slot:
            question = self.policy.question_for_slot(next_slot)
            return {"ask": next_slot, "question": question, "slots": slots}

        # All slots present → build plan
        try:
            # Mentor context from RAG
            mentor_context = self.mentor_repository.get_mentor_context(user_message)

            # Last 7 days (best-effort from memory store)
            memory_summary = self.user_memory_store.get_user_memory_summary(user_id) or {}
            last_7_days = memory_summary.get("recent_conversations", [])

            plan = self.composer.compose(slots=slots, last_7_days=last_7_days, mentor_context=mentor_context or "")

            text = self._format_plan_text(plan)
            return {"plan": plan, "text": text}
        except Exception as e:
            logger.error(f"Error composing workout: {e}")
            return {"error": "Could not compose workout today. Please try again."}

    def _format_plan_text(self, plan: Dict[str, Any]) -> str:
        parts: list[str] = []
        method = plan.get("method", "rounds").upper()
        duration = plan.get("duration_min")
        parts.append(f"Method: {method} | Duration: ~{duration} min")
        for section in plan.get("sections", []):
            title = section.get("title")
            parts.append(f"\n{title}:")
            if title == "Main":
                for block in section.get("blocks", []):
                    label = block.get("label", "Block")
                    parts.append(f"  {label}:")
                    for item in block.get("items", []):
                        line = self._format_item(item)
                        parts.append(f"    - {line}")
            else:
                for item in section.get("items", []):
                    parts.append(f"  - {self._format_item(item)}")
        return "\n".join(parts)

    def _format_item(self, item: Dict[str, Any]) -> str:
        name = item.get("name")
        reps = item.get("reps")
        timev = item.get("time")
        if reps:
            return f"{name} — {reps}"
        if timev:
            return f"{name} — {timev}"
        return name


