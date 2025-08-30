"""
WorkoutComposer: builds a workout plan using the project's knowledge base
JSON + mentors RAG context, strictly following user-driven constraints.

Inputs:
- slots: time_available, equipment_available, shoulder_pain_today,
  knee_pain_today, method_preference (optional), different_or_similar
- last_7_days: recent plans summary to vary on request
- mentor_context: text from RAG to bias selection and cues

Output:
- plan dict with sections: Warm-up, Main (method-specific blocks), Cooldown
"""
from typing import Dict, Any, List, Optional

from ..repositories.exercise_repository import ExerciseRepository


class WorkoutComposer:
    def __init__(self, exercise_repo: ExerciseRepository):
        self.exercise_repo = exercise_repo

    def compose(self,
                slots: Dict[str, Any],
                last_7_days: List[Dict[str, Any]],
                mentor_context: str) -> Dict[str, Any]:
        method = self._choose_method(slots)
        time_min = self._parse_time(slots.get("time_available"))
        equip = self._parse_equipment(slots.get("equipment_available"))
        shoulder_pain = str(slots.get("shoulder_pain_today", "no")).lower()
        knee_pain = str(slots.get("knee_pain_today", "no")).lower()
        variation = (slots.get("different_or_similar") or "different").lower()

        # Section: Warm-up per KB guidance (1–3 mobility moves)
        warmup = self._build_warmup(equip, shoulder_pain, knee_pain)

        # Section: Main per chosen method
        main = self._build_main_blocks(method, equip, time_min, shoulder_pain, knee_pain, variation, last_7_days, mentor_context)

        # Section: Cooldown per KB
        cooldown = self._build_cooldown(shoulder_pain, knee_pain)

        return {
            "method": method,
            "duration_min": time_min,
            "sections": [
                {"title": "Warm-Up", "items": warmup},
                {"title": "Main", "blocks": main},
                {"title": "Cooldown", "items": cooldown},
            ]
        }

    def _choose_method(self, slots: Dict[str, Any]) -> str:
        pref = (slots.get("method_preference") or "").strip().lower()
        if pref in ("rounds", "emom", "flow", "ladder"):
            return pref
        # Fallback simple heuristic based on time/energy
        t = self._parse_time(slots.get("time_available"))
        if t <= 30:
            return "emom"
        return "rounds"

    def _parse_time(self, val: Any) -> int:
        try:
            return max(20, min(90, int(str(val).strip())))
        except Exception:
            return 45

    def _parse_equipment(self, val: Any) -> List[str]:
        if not val:
            return []
        return [x.strip().lower() for x in str(val).split(',') if x.strip()]

    def _build_warmup(self, equip: List[str], shoulder_pain: str, knee_pain: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        items.append({"name": "Scapular Wall Slides", "reps": "2x8", "cues": ["slow", "keep contact"]})
        if knee_pain.startswith("y"):
            items.append({"name": "Spanish Squat Hold", "time": "30s", "cues": ["upright", "knees track"]})
        else:
            items.append({"name": "Cossack Squats", "reps": "2x5/side", "cues": ["controlled depth"]})
        items.append({"name": "Cat-Cow → Thoracic Rotations", "reps": "2x5/side"})
        return items[:3]

    def _build_main_blocks(self, method: str, equip: List[str], time_min: int, shoulder_pain: str, knee_pain: str,
                           variation: str, last_7_days: List[Dict[str, Any]], mentor_context: str) -> List[Dict[str, Any]]:
        # P0: simple three-block structure for rounds/emom; flow/ladder will be similar
        blocks: List[Dict[str, Any]] = []
        shoulder_safe = shoulder_pain.startswith("y")
        knee_safe = not knee_pain.startswith("y")

        if method in ("rounds", "emom"):
            block_a = {"label": "A", "items": []}
            block_b = {"label": "B", "items": []}
            block_c = {"label": "C", "items": []}

            # A: knee + scapular
            if knee_safe:
                block_a["items"].append({"name": "Patrick Step", "reps": "8/leg"})
            else:
                block_a["items"].append({"name": "Spanish Squat", "time": "30-45s"})
            block_a["items"].append({"name": "Wall Scapular Slides", "reps": "8-10"})

            # B: posterior + cuff
            block_b["items"].append({"name": "Glute Bridge March", "reps": "8/leg"})
            block_b["items"].append({"name": "Side-Lying External Rotation", "reps": "10/side"})

            # C: core + carry/conditioning
            block_c["items"].append({"name": "Step-Up to Knee Drive", "reps": "8/leg"})
            block_c["items"].append({"name": "KB Front Rack March" if "kettlebell" in equip or "kb" in equip else "Plank Shoulder Taps",
                                      "time": "20-30s"})

            blocks.extend([block_a, block_b, block_c])
        elif method == "flow":
            blocks.append({
                "label": "Flow",
                "items": [
                    {"name": "Lizard Crawl", "time": "30-45s" if not shoulder_safe else None, "subs": "Bear Plank Protraction" if shoulder_safe else None},
                    {"name": "90/90 Sit → Shin Box Switch", "reps": "5/side"},
                    {"name": "Spinal Waves", "reps": "6 slow"}
                ]
            })
        else:  # ladder
            blocks.append({
                "label": "Ladder",
                "items": [
                    {"name": "Pseudo Planche Push-Up", "reps": "10-8-6-4-2" if not shoulder_safe else "5x6 slow"},
                    {"name": "Single-Leg Elevated Glute Bridge", "reps": "alt legs 10-8-6-4-2"}
                ]
            })

        return blocks

    def _build_cooldown(self, shoulder_pain: str, knee_pain: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        items.append({"name": "Doorway Pec Stretch", "time": "30s/side"})
        if knee_pain.startswith("y"):
            items.append({"name": "Half-Kneeling Hip Flexor Stretch", "time": "30s/side"})
        items.append({"name": "90/90 Hip Switch", "reps": "10"})
        return items


