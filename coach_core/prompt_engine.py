"""
Prompt Engine for Modular, Mentor-Powered AI Coach
Builds detailed, context-rich prompts for LLMs using mentor context, user data, and exercise KB.
Supports mentor weighting and dynamic mentor selection.
"""

from typing import List, Dict, Any, Optional
from coach_core.mentor_brain import get_mentor_context, get_relevant_mentors_for_query, MENTOR_KNOWLEDGE
# Exercise KB functions moved to ai.py - import from there if needed
import json

def select_top_mentors(user_profile: Dict[str, Any], user_input: str, max_mentors: int = 3) -> List[str]:
    """
    Select top mentors based on user profile (preferences/goals) and query keywords.
    Returns a list of mentor IDs.
    """
    # 1. Use explicit preferences/goals if present
    preferences = user_profile.get("training_preferences", {})
    goals = user_profile.get("goals", [])
    preferred_mentors = []
    # Example: if user likes yoga, prioritize Dylan Werner, Patrick Beach
    if any("yoga" in str(g).lower() for g in goals) or "yoga" in str(preferences).lower():
        preferred_mentors.extend(["dylan_werner", "patrick_beach"])
    if any("calisthenics" in str(g).lower() for g in goals) or "calisthenics" in str(preferences).lower():
        preferred_mentors.append("tom_merrick")
    if any("kettlebell" in str(g).lower() for g in goals) or "kettlebell" in str(preferences).lower():
        preferred_mentors.append("everydamnandre")
    if any("joint" in str(g).lower() or "injury" in str(g).lower() for g in goals):
        preferred_mentors.extend(["squatu", "kneesovertoesguy"])
    # 2. Use query keyword match
    query_mentors = get_relevant_mentors_for_query(user_input)
    # 3. Merge and deduplicate, preserving order
    mentor_ids = []
    for m in preferred_mentors + query_mentors:
        if m not in mentor_ids:
            mentor_ids.append(m)
    # 4. Fallback to all mentors if none found
    if not mentor_ids:
        mentor_ids = list(MENTOR_KNOWLEDGE.keys())
    # 5. Limit to top N
    return mentor_ids[:max_mentors]

def summarize_mentor_context(mentor_ids: List[str]) -> str:
    """
    Return a 1-2 line summary for each mentor (for prompt brevity).
    """
    summaries = []
    for m in mentor_ids:
        mentor = MENTOR_KNOWLEDGE.get(m)
        if mentor:
            summary = f"{mentor['name']} ({mentor['focus']}): {mentor['core_philosophy'][:120]}..."
            summaries.append(summary)
    return "\n".join(summaries)

# Example few-shot gold standard for a detailed, mentor-referenced workout
DEFAULT_FEW_SHOT_EXAMPLES = [
    """
Yoel — this is an exciting challenge – combining the best of all four mentors into one comprehensive workout for today. We'll focus on your specific requests: knee health, shoulder health, kettlebell movement, pancake flexibility, and forward fold flexibility (including good mornings).

This workout will embody the common denominators we identified: full range of motion, progressive and systematic approach, consistency, listening to your body, and a holistic view for movement longevity.

---

### Your Integrated Mentor-Powered Workout: Knee & Shoulder Health, Kettlebells, and Deep Flexibility

**Goal:** Enhance knee and shoulder joint health, improve mobility, build resilience, develop kettlebell proficiency, and increase pancake/forward fold flexibility.
**Duration:** Approximately 60-80 minutes (adjust based on your pace and rest needs).
**Frequency:** This is a full-body, comprehensive session. Consider 2-3 times a week, with other days for active recovery or lighter mobility.

---

#### **Phase 1: Dynamic Warm-up & Joint Preparation (10-12 minutes)**
*Purpose:* Prepare the entire kinetic chain, focusing on spinal articulation, wrists, and ankles, and initiating blood flow to the knees.
*Mentors:* Ido Portal (Spinal Waves), Tom Merrick (Wrist & Shoulder Warm-ups), Ben Patrick (Backward Movement), Dylan Werner (Ankle Mobility).

1. **Spinal Waves (Ido Portal):**
   - *Description:* Start on all fours (cat-cow position). Gently articulate each segment of your spine, moving from tailbone to head (flexion and extension). Focus on isolating movement to one vertebra at a time.
   - *Sets/Reps:* 2 sets of 8-10 slow, controlled repetitions in each direction.
   - *Cues:* "Take it slow and ENJOY.", "Move at each section individually.", "Smooth, continuous motion."

2. **Wrist Warm-ups (Tom Merrick):**
   - *Description:* Perform Wrist Clock Walks, First Knuckle Push-ups, and Reverse Wrist Curls.
   - *Sets/Reps:* 1 set of 10-15 repetitions for each exercise.
   - *Cues:* "Keep a nice firm wrist.", "Emphasize length around the wrist joint."

3. **Shoulder Warm-ups (Tom Merrick / Emmet Louis):**
   - *Description:* Arm Circles, Controlled Shoulder Rotations, Wall Angels.
   - *Sets/Reps:* 1-2 sets for each.
   - *Cues:* "Control the movement, don't just swing.", "Isolate movement to the shoulder joint."

4. **Backward Walk / Sled Pull (Ben Patrick):**
   - *Description:* Walk backward, pulling a sled or walking backward on a treadmill/outdoors.
   - *Sets/Duration:* 2 sets of 1-2 minutes or 50-100 feet.
   - *Cues:* "Maintain an upright posture.", "Drive through the balls of the feet."

5. **Wall Ankle Mobility Test/Drill (Ben Patrick / Dylan Werner):**
   - *Description:* Kneel facing a wall. Place one foot 4-5 inches from the wall. Keeping heel down, push knee directly over middle toe towards the wall.
   - *Sets/Reps:* 1 set of 8-10 repetitions per side.
   - *Cues:* "Keep heel firmly on the floor.", "Push knee directly over the middle toe."

#### **Phase 2: Foundational Joint Health & Mobility (20-25 minutes)**
*Purpose:* Directly address knee and shoulder resilience, building strength and control through their full ranges.
*Mentors:* Ben Patrick (Knees), Emmet Louis (Shoulders, active mobility).

1. **Tibialis Raise (Ben Patrick):**
   - *Description:* Stand with your back against a wall, feet 6-12 inches away. Lift your toes and the balls of your feet off the ground, only your heels remain. Control the lowering.
   - *Sets/Reps:* 3 sets of 15-20 repetitions.
   - *Cues:* "Keep heels on the ground.", "Lift toes as high as possible."

2. **Reverse Nordic (Ben Patrick):**
   - *Description:* Kneel on the floor, keeping your torso and hips in a straight line. Slowly lean back, controlling the movement with your quads. Go only as far as you can pain-free.
   - *Sets/Reps:* 3 sets of 5-8 repetitions. Focus on a slow, controlled eccentric (lowering) phase (3-5 seconds).
   - *Cues:* "Keep a straight line from knees to shoulders.", "Control the eccentric (lowering) phase slowly."

3. **Hanging Protocols (Ido Portal / Tom Merrick):**
   - *Description:* Find a pull-up bar. Alternate between passive and active hangs.
   - *Sets/Duration:* Accumulate 2-3 minutes of hanging. Sets of 30-60 seconds.
   - *Cues:* "For passive: fully relax shoulders, let gravity stretch.", "For active: pull shoulder blades down and back."

4. **Shoulder External Rotation (Emmet Louis - Active/Loaded):**
   - *Description:* Lying on your side, elbow bent 90 degrees, upper arm tucked to side. With a light dumbbell or resistance band, actively rotate your forearm upwards.
   - *Sets/Reps:* 3 sets of 10-15 repetitions per arm.
   - *Cues:* "Isolate movement to the shoulder joint, avoid compensation from torso."

#### **Phase 3: Kettlebell Strength & Conditioning (15-20 minutes)**
*Purpose:* Build full-body functional strength, power, and conditioning using versatile kettlebell movements.
*Mentor:* Everydamnandré.

**Option A: Foundational Strength Focus**
- *Structure:* Fixed Rounds/Reps Circuit (Everydamnandré)
- *Rounds:* 3-4 Rounds
- *Rest:* 60-90 seconds between rounds.

    1. **Kettlebell Goblet Squat:** 8-12 reps
    2. **Kettlebell Russian Swing:** 10-15 reps
    3. **Kettlebell Clean & Press:** 5-8 reps per side

**Option B: Conditioning & Mental Toughness Focus**
- *Structure:* EMOM (Every Minute On the Minute) (Everydamnandré)
- *Duration:* 10-15 minutes

    - *Minute 1:* 8-12 Kettlebell Swings
    - *Minute 2:* 5-8 Kettlebell Clean & Press

#### **Phase 4: Deep Flexibility & Spinal Health (15-20 minutes)**
*Purpose:* Actively improve pancake and forward fold flexibility, and enhance spinal mobility.
*Mentors:* Emmet Louis (Pancake, Jefferson Curl), Tom Merrick (Pancake, Good Mornings).

1. **Pancake Stretch (Emmet Louis & Tom Merrick):**
   - *Description:* Sit with legs spread wide. Hinge from hips, keeping back flat.
   - *Sets/Duration:* 3 sets. Hold for 30 seconds, then PNF.
   - *Cues:* "Keep hips connected to surface.", "Actively use your own strength to get more flexible."

2. **Seated Good Mornings (Tom Merrick):**
   - *Description:* Sit on floor with legs straight and together. Hinge from hips, keeping back flat, reaching forward.
   - *Sets/Reps:* 3 sets of 10-12 controlled repetitions.
   - *Cues:* "Keep your back flat, hinge from the hips."

3. **Jefferson Curl (Emmet Louis):**
   - *Description:* Stand tall, optionally on a slight elevation. Tuck chin, round down one vertebra at a time.
   - *Sets/Reps:* 3 sets of 5-8 very slow, controlled repetitions.
   - *Cues:* "Start with the chin tuck.", "Roll down one vertebra at a time."

#### **Phase 5: Cool-down & Integration (5-7 minutes)**
*Purpose:* Promote recovery, integrate new ranges, and calm the nervous system.
*Mentors:* Dylan Werner (Pranayama), Ido Portal (Spinal Waves).

1. **4-7-8 Breath (Dylan Werner):**
   - *Description:* Inhale for 4, hold for 7, exhale for 8.
   - *Sets/Reps:* 5-8 cycles.
   - *Cues:* "Focus on the counts.", "Exhale completely."

2. **Gentle Spinal Waves / Cat-Cow (Ido Portal):**
   - *Description:* Gentle, fluid cat-cow movements.
   - *Sets/Reps:* 2-3 minutes of continuous, gentle movement.
   - *Cues:* "Move with your breath.", "Find ease in your spine."

---

**Post-Workout Reflection (Yoel's AI Coach):**
- How did your knees and shoulders feel throughout the workout?
- Which kettlebell movements felt most challenging or rewarding?
- Did you notice any improvements in your pancake or forward fold depth?
- How did this integrated approach feel compared to more specialized sessions?

Remember, Yoel, this is a powerful blend. Listen to your body, adjust as needed, and enjoy the journey of becoming a more resilient, mobile, and functionally strong mover!
    """
]

class PromptEngine:
    """
    Modular prompt builder for the AI coach.
    - Merges mentor context, user profile/logs, relevant exercises, and few-shot examples.
    - Supports mentor weighting and dynamic mentor selection.
    - Use mentor_focus or mentor_weights to override auto-selection.
    - Optionally injects few-shot gold standard examples for more structured LLM output.
    """
    def __init__(self, profile: Dict[str, Any], logs: List[Dict[str, Any]]):
        self.profile = profile
        self.logs = logs

    def build_prompt(
        self,
        user_input: str,
        prompt_type: str = "daily_workout",
        patterns: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        few_shot_examples: Optional[List[str]] = None,
        detail_level: str = "high",
        mentor_focus: Optional[List[str]] = None,
        mentor_weights: Optional[Dict[str, float]] = None,
        max_mentors: int = 3
    ) -> str:
        """
        Build a single user message for the LLM, merging all context.
        prompt_type: 'daily_workout', 'check_in', 'reflection', etc.
        detail_level: 'high' (default), 'medium', 'low'
        mentor_focus: explicit list of mentor IDs to prioritize
        mentor_weights: dict of mentor_id: weight (future use)
        max_mentors: how many mentors to inject in detail (rest as summary)
        few_shot_examples: list of gold standard examples (if None, uses default)
        """
        # 1. Mentor selection and context
        if mentor_focus:
            mentor_ids = mentor_focus
        else:
            mentor_ids = select_top_mentors(self.profile, user_input, max_mentors=max_mentors)
        # If more than max_mentors, summarize the rest
        mentor_context = get_mentor_context(user_input, mentor_ids)
        if len(mentor_ids) > max_mentors:
            mentor_context += "\n\nOTHER MENTORS (summary):\n" + summarize_mentor_context(mentor_ids[max_mentors:])

        # 2. Exercise suggestions (based on mentors, tags, injuries, etc.)
        injuries = self.profile.get("injury_history", {})
        contraindications = [k for k, v in injuries.items() if v and "issue" in v or "pain" in v or "injury" in v]
        tags = [w.lower() for w in user_input.split() if len(w) > 2]
        exercises = get_relevant_exercises(tags=tags, mentors=mentor_ids, contraindications=contraindications, limit=5)

        # 3. User context
        exercise_blocks = []
        for ex in exercises:
            next_prog = get_next_progression(ex["name"], self.logs)
            prev_reg = get_previous_regression(ex["name"], self.logs)
            prog_line = f"Next progression: {next_prog}" if next_prog else ""
            reg_line = f"Suggested regression: {prev_reg}" if prev_reg else ""
            exercise_blocks.append(
                f"- {ex['name']}: {ex['description']} (Mentors: {', '.join(ex['mentors'])})\n  Cues: {', '.join(ex['cues'])}\n  Progressions: {', '.join(ex['progressions'])}\n  Contraindications: {', '.join(ex['contraindications'])}\n  {prog_line}\n  {reg_line}"
            )
        context_blocks = [
            f"PROFILE:\n{json.dumps(self.profile, indent=2)}",
            f"RECENT LOGS (last 3 days):\n{json.dumps(self.logs[-3:], indent=2)}" if self.logs else "",
            f"PATTERNS ANALYSIS:\n{json.dumps(patterns, indent=2)}" if patterns else "",
            f"FEEDBACK ON PREVIOUS SESSIONS:\n{feedback}" if feedback else "",
            f"MENTOR CONTEXT:\n{mentor_context}",
            f"RELEVANT EXERCISES:\n" + "\n".join(exercise_blocks) if exercise_blocks else ""
        ]

        # 4. Few-shot examples (optional)
        if few_shot_examples is not None:
            examples = few_shot_examples
        else:
            examples = DEFAULT_FEW_SHOT_EXAMPLES
        if examples:
            context_blocks.append("EXAMPLES:\n" + "\n---\n".join(examples))

        # 5. User request
        context_blocks.append(f"USER REQUEST:\n{user_input}")

        # 6. Instruction
        if prompt_type == "daily_workout":
            instruction = (
                "You are Yoel's personal AI fitness coach. Using the context above, build a highly detailed, mentor-referenced workout for today. "
                "For each phase (warm-up, activation, main, flexibility, cooldown), list every exercise, sets, reps, cues, and progressions/regressions. "
                "Attribute each exercise to a mentor and explain why it’s included and sequenced that way. End with a reflection prompt for Yoel."
            )
        elif prompt_type == "check_in":
            instruction = (
                "You are Yoel's AI coach. Using the context above, ask Yoel a smart, open-ended check-in question about his recovery, mood, or readiness."
            )
        elif prompt_type == "reflection":
            instruction = (
                "You are Yoel's AI coach. Using the context above, prompt Yoel to reflect on his training, progress, and learning."
            )
        else:
            instruction = (
                "You are Yoel's AI coach. Using the context above, answer the user's request in detail, referencing mentors and exercises as appropriate."
            )

        # 7. Merge all into a single user message
        prompt = "\n\n".join([b for b in context_blocks if b.strip()]) + "\n\nINSTRUCTION:\n" + instruction
        return prompt 