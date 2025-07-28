"""
Prompt Engine for Modular, Mentor-Powered AI Coach
Builds detailed, context-rich prompts for LLMs using mentor context, user data, and exercise KB.
Supports mentor weighting and dynamic mentor selection.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

# TODO: Update imports for new structure
# from coach_core.mentor_brain import get_mentor_context, get_relevant_mentors_for_query, MENTOR_KNOWLEDGE
# Exercise KB functions moved to ai.py - import from there if needed

def get_relevant_exercises(tags: List[str], mentors: List[str], contraindications: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """Get relevant exercises based on tags, mentors, and contraindications"""
    try:
        # Load exercise knowledge base
        exercise_kb_path = Path("data/exercises/exercise_kb.json")
        if not exercise_kb_path.exists():
            exercise_kb_path = Path("../data/exercises/exercise_kb.json")
        
        with open(exercise_kb_path, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        # Filter exercises based on criteria
        relevant_exercises = []
        for exercise in exercises:
            # Check if exercise matches tags
            exercise_tags = [tag.lower() for tag in exercise.get('tags', [])]
            matches_tags = any(tag.lower() in exercise_tags for tag in tags) if tags else True
            
            # Check if exercise is safe for injuries
            exercise_contraindications = exercise.get('contraindications', [])
            if isinstance(exercise_contraindications, str):
                exercise_contraindications = [exercise_contraindications]
            safe_for_injuries = not any(injury.lower() in ' '.join(exercise_contraindications).lower() 
                                      for injury in contraindications) if contraindications else True
            
            # Check if exercise matches mentor style (handle multiple mentors)
            exercise_mentors = exercise.get('mentor', '').lower()
            if exercise_mentors:
                # Split by comma and check if any mentor matches
                exercise_mentor_list = [m.strip() for m in exercise_mentors.split(',')]
                matches_mentors = any(mentor.lower() in exercise_mentor_list for mentor in mentors) if mentors else True
            else:
                matches_mentors = True
            
            if matches_tags and safe_for_injuries and matches_mentors:
                relevant_exercises.append(exercise)
        
        return relevant_exercises[:limit]
        
    except Exception as e:
        print(f"Error loading exercises: {e}")
        return []

def get_next_progression(exercise_name: str, logs: List[Dict[str, Any]]) -> Optional[str]:
    """Get next progression for an exercise based on user logs"""
    try:
        # Simple logic: if user has been doing this exercise consistently, suggest next progression
        exercise_logs = [log for log in logs if exercise_name.lower() in str(log).lower()]
        
        if len(exercise_logs) >= 3:  # User has done this exercise at least 3 times
            # Load exercise to get progressions
            exercise_kb_path = Path("data/exercises/exercise_kb.json")
            if not exercise_kb_path.exists():
                exercise_kb_path = Path("../data/exercises/exercise_kb.json")
            
            with open(exercise_kb_path, 'r', encoding='utf-8') as f:
                exercises = json.load(f)
            
            for exercise in exercises:
                if exercise['name'].lower() == exercise_name.lower():
                    progressions = exercise.get('progressions', [])
                    if progressions:
                        return progressions[0]  # Return first progression
        
        return None
        
    except Exception as e:
        print(f"Error getting progression: {e}")
        return None

def get_previous_regression(exercise_name: str, logs: List[Dict[str, Any]]) -> Optional[str]:
    """Get previous regression for an exercise based on user logs"""
    try:
        # Simple logic: if user is struggling, suggest regression
        exercise_logs = [log for log in logs if exercise_name.lower() in str(log).lower()]
        
        # Check if user has reported difficulty
        difficulty_indicators = ['hard', 'difficult', 'struggle', 'pain', 'sore']
        has_difficulty = any(indicator in str(log).lower() for log in exercise_logs 
                           for indicator in difficulty_indicators)
        
        if has_difficulty:
            # Load exercise to get regressions
            exercise_kb_path = Path("data/exercises/exercise_kb.json")
            if not exercise_kb_path.exists():
                exercise_kb_path = Path("../data/exercises/exercise_kb.json")
            
            with open(exercise_kb_path, 'r', encoding='utf-8') as f:
                exercises = json.load(f)
            
            for exercise in exercises:
                if exercise['name'].lower() == exercise_name.lower():
                    regressions = exercise.get('regressions', [])
                    if regressions:
                        return regressions[0]  # Return first regression
        
        return None
        
    except Exception as e:
        print(f"Error getting regression: {e}")
        return None

def get_mentor_context(query: str, mentor_ids: List[str]) -> str:
    """Get mentor context for specific mentors"""
    # Placeholder - this should integrate with your RAG system
    mentor_contexts = {
        "dylan_werner": "Focus on movement control and isometric strength. Emphasize precision and body awareness.",
        "ido_portal": "Train movement complexity and adaptability. Focus on natural patterns and flow.",
        "patrick_beach": "Emphasize fluid mobility and natural movement patterns. Connect breath with movement.",
        "tom_merrick": "Focus on clean calisthenics and flexibility. Emphasize proper form and progression.",
        "everydamnandre": "Simple, tough conditioning. Focus on mental toughness and consistency.",
        "kneesovertoesguy": "Joint health and bulletproofing. Focus on knee and ankle strength.",
        "emmet_louis": "End-range mobility strength. Focus on active flexibility and joint control."
    }
    
    contexts = []
    for mentor_id in mentor_ids:
        if mentor_id in mentor_contexts:
            contexts.append(f"{mentor_id}: {mentor_contexts[mentor_id]}")
    
    return "\n".join(contexts) if contexts else "Focus on proper form and progressive overload."

def get_relevant_mentors_for_query(query: str) -> List[str]:
    """Get relevant mentors for a query"""
    query_lower = query.lower()
    relevant_mentors = []
    
    # Simple keyword matching
    if any(word in query_lower for word in ['yoga', 'control', 'balance']):
        relevant_mentors.append('dylan_werner')
    if any(word in query_lower for word in ['movement', 'complex', 'flow']):
        relevant_mentors.append('ido_portal')
    if any(word in query_lower for word in ['mobility', 'natural', 'fluid']):
        relevant_mentors.append('patrick_beach')
    if any(word in query_lower for word in ['calisthenics', 'flexibility']):
        relevant_mentors.append('tom_merrick')
    if any(word in query_lower for word in ['kettlebell', 'conditioning']):
        relevant_mentors.append('everydamnandre')
    if any(word in query_lower for word in ['joint', 'knee', 'injury']):
        relevant_mentors.append('kneesovertoesguy')
    if any(word in query_lower for word in ['mobility', 'flexibility', 'range']):
        relevant_mentors.append('emmet_louis')
    
    return relevant_mentors if relevant_mentors else ['dylan_werner', 'tom_merrick']

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
        preferred_mentors.extend(["kneesovertoesguy"])
    # 2. Use query keyword match
    query_mentors = get_relevant_mentors_for_query(user_input)
    # 3. Merge and deduplicate, preserving order
    mentor_ids = []
    for m in preferred_mentors + query_mentors:
        if m not in mentor_ids:
            mentor_ids.append(m)
    # 4. Fallback to all mentors if none found
    if not mentor_ids:
        mentor_ids = ["dylan_werner", "tom_merrick", "patrick_beach"]
    # 5. Limit to top N
    return mentor_ids[:max_mentors]

def summarize_mentor_context(mentor_ids: List[str]) -> str:
    """
    Return a 1-2 line summary for each mentor (for prompt brevity).
    """
    mentor_summaries = {
        "dylan_werner": "Movement control and isometric strength",
        "ido_portal": "Movement complexity and natural patterns", 
        "patrick_beach": "Fluid mobility and natural movement",
        "tom_merrick": "Clean calisthenics and flexibility",
        "everydamnandre": "Simple, tough conditioning",
        "kneesovertoesguy": "Joint health and bulletproofing",
        "emmet_louis": "End-range mobility strength"
    }
    
    summaries = []
    for mentor_id in mentor_ids:
        if mentor_id in mentor_summaries:
            summaries.append(f"{mentor_id}: {mentor_summaries[mentor_id]}")
    
    return "\n".join(summaries)

def get_workout_programming_rules() -> Dict[str, Any]:
    """Get workout programming rules from knowledge base"""
    try:
        rules_path = Path("data/knowledge_base/workout_programming_rules.json")
        if not rules_path.exists():
            rules_path = Path("../data/knowledge_base/workout_programming_rules.json")
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading programming rules: {e}")
        return {}

def get_programming_guidelines_for_goals(user_goals: List[str]) -> Dict[str, Any]:
    """Get programming guidelines based on user goals"""
    rules = get_workout_programming_rules()
    programming_rules = rules.get("workout_programming_rules", {})
    
    guidelines = {}
    for goal in user_goals:
        goal_lower = goal.lower()
        if "strength" in goal_lower or "muscle" in goal_lower:
            guidelines["muscle_hypertrophy"] = programming_rules.get("muscle_hypertrophy", {})
        elif "flexibility" in goal_lower or "mobility" in goal_lower:
            guidelines["flexibility_range_of_motion"] = programming_rules.get("flexibility_range_of_motion", {})
        elif "movement" in goal_lower or "complex" in goal_lower:
            guidelines["movement_quality_complexity"] = programming_rules.get("movement_quality_complexity", {})
        elif "joint" in goal_lower or "health" in goal_lower:
            guidelines["joint_health_prehab_rehab"] = programming_rules.get("joint_health_prehab_rehab", {})
        elif "vitality" in goal_lower or "longevity" in goal_lower:
            guidelines["vitality_longevity_balance"] = programming_rules.get("vitality_longevity_balance", {})
    
    return guidelines

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
    ) -> Dict[str, str]:
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
        
        mentor_context = get_mentor_context(user_input, mentor_ids)
        if len(mentor_ids) > max_mentors:
            mentor_context += "\n\nOTHER MENTORS (summary):\n" + summarize_mentor_context(mentor_ids[max_mentors:])

        # 2. Exercise suggestions (based on mentors, tags, injuries, etc.)
        injuries = self.profile.get("injury_history", {})
        contraindications = [k for k, v in injuries.items() if v and "issue" in v or "pain" in v or "injury" in v]
        tags = [w.lower() for w in user_input.split() if len(w) > 2]
        exercises = get_relevant_exercises(tags=tags, mentors=mentor_ids, contraindications=contraindications, limit=5)

        # 3. Build exercise blocks with progression tracking
        exercise_blocks = []
        for ex in exercises:
            next_prog = get_next_progression(ex["name"], self.logs)
            prev_reg = get_previous_regression(ex["name"], self.logs)
            prog_line = f"Next progression: {next_prog}" if next_prog else ""
            reg_line = f"Suggested regression: {prev_reg}" if prev_reg else ""
            exercise_blocks.append(
                f"- {ex['name']}: {ex['description']} (Mentors: {', '.join(ex.get('mentor', '').split(','))})\n  Cues: {', '.join(ex.get('cues', []))}\n  Progressions: {', '.join(ex.get('progressions', []))}\n  Contraindications: {', '.join(ex.get('contraindications', []))}\n  {prog_line}\n  {reg_line}"
            )

        # 4. Build comprehensive context (merged into single user message as per feedback)
        context_parts = []
        
        # User profile and logs
        context_parts.append(f"USER PROFILE:\n{json.dumps(self.profile, indent=2)}")
        if self.logs:
            context_parts.append(f"RECENT LOGS (last 3 days):\n{json.dumps(self.logs[-3:], indent=2)}")
        
        # Patterns and feedback
        if patterns:
            context_parts.append(f"PATTERNS ANALYSIS:\n{json.dumps(patterns, indent=2)}")
        if feedback:
            context_parts.append(f"FEEDBACK ON PREVIOUS SESSIONS:\n{feedback}")
        
        # Mentor context
        context_parts.append(f"MENTOR CONTEXT:\n{mentor_context}")
        
        # Exercise knowledge base (injected as per feedback)
        if exercise_blocks:
            context_parts.append(f"RELEVANT EXERCISES:\n" + "\n".join(exercise_blocks))
        
        # Workout programming rules (NEW - for better workout structure)
        user_goals = self.profile.get("goals", [])
        programming_guidelines = get_programming_guidelines_for_goals(user_goals)
        if programming_guidelines:
            context_parts.append(f"WORKOUT PROGRAMMING RULES:\n{json.dumps(programming_guidelines, indent=2)}")
        
        # Few-shot examples
        if few_shot_examples is not None:
            examples = few_shot_examples
        else:
            examples = DEFAULT_FEW_SHOT_EXAMPLES
        if examples:
            context_parts.append("EXAMPLES:\n" + "\n---\n".join(examples))

        # User request
        context_parts.append(f"USER REQUEST:\n{user_input}")

        # 5. Build instruction based on prompt type
        if prompt_type == "daily_workout":
            instruction = (
                "You are Yoel's personal AI fitness coach. Using the context above, build a highly detailed, mentor-referenced workout for today. "
                "For each phase (warm-up, activation, main, flexibility, cooldown), list every exercise, sets, reps, cues, and progressions/regressions. "
                "Attribute each exercise to a mentor and explain why it's included and sequenced that way. End with a reflection prompt for Yoel."
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

        # 6. Build final prompt (merged context as single user message per feedback)
        system_prompt = "You are an AI fitness coach with expertise from world-class movement and strength mentors."
        user_message = "\n\n".join([part for part in context_parts if part.strip()]) + "\n\nINSTRUCTION:\n" + instruction
        
        return {
            "system": system_prompt,
            "user": user_message
        } 