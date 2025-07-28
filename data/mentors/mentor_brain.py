"""
Mentor Brain - Dynamic RAG-powered mentor knowledge system
Provides access to mentor knowledge through vector search and retrieval
"""

import logging
from typing import List, Dict, Any, Optional
# from coach_core.rag_system import rag_system  # Commented out to avoid import issues

logger = logging.getLogger(__name__)

# Static mentor information (fallback)
MENTOR_KNOWLEDGE = {
    "dylan_werner": {
        "name": "Dylan Werner",
        "focus": "Integrated approach to movement education, synthesizing traditional yoga asana with functional strength, advanced mobility, and precise body control. Mastery of advanced yoga asana (inversions, arm balances), core strength, intelligent breathwork, and holistic well-being.",
        "core_philosophy": (
            "Dylan Werner views yoga as a holistic physical discipline cultivating strength, balance, flexibility, and overall health, translating physical attributes into tangible benefits in everyday life. "
            "He demystifies advanced movements by breaking them down into digestible, progressive steps, building foundational strength, flexibility, mobility, proprioception, and balance. "
            "His unique background (US Marine, paramedic, anatomy studies, wrestling) prioritizes **safety and proper alignment** for injury prevention and rehabilitation. "
            "Breath (Pranayama) is fundamental for nervous system regulation, stress reduction, and deepening movement. "
            "Ultimate goals are to inspire individuals to transcend limitations, overcome fear, cultivate deep body awareness, and achieve lifelong pain-free movement and advanced bodyweight skills. "
            "Key mantras: 'Movement is medicine,' 'Strength and flexibility should go hand in hand,' 'Don't just do the pose, understand it.'"
        ),
        "key_principles": [
            "Myofascial Integrated Alignment (MIA): A holistic, evidence-based system focusing on restoring natural alignment by balancing myofascial meridians. Emphasizes fascial health, holistic alignment, sensation-based movement, sequencing by myofascial lines, 'tuning' poses, and 'fascial glide' movements.",
            "Myofascial Integrated Stretching (MIS): An evidence-based stretching system emphasizing a pre-stretch warm-up, optimal stretch duration (30-60 seconds), minimal discomfort (never painful), mindful and controlled stretching, holistic sequencing (e.g., backbends, hip openers, forward folds), and repetitive postures to promote fascial plasticity.",
            "Progressive Overload in Yoga/Bodyweight: Systematically increases demand through increased repetitions/duration, reduced support (e.g., wall handstand to freestanding), adding complexity (e.g., Crow to Handstand transitions), and building foundational strength (wrist health, SASS, deep core).",
            "Core Integration: Differentiates deep core stability from superficial strength. Cues include 'tuck the tailbone,' 'engage the core,' 'draw ribs and navel in,' 'constant body tension,' and 'posterior chain activation.'",
            "Active Flexibility: Emphasizes muscular engagement to control and sustain stretches, linking strength and flexibility for functional range of motion, integrating dynamic movements with static holds.",
            "Breath-Movement Synchronization (Vinyasa): Links breath and movement for fluid transitions, mental focus, and nervous system regulation. Teaches specific pranayama (Sama Vritti, Breath of Fire, 4-7-8, 10:10:2 – 2:10:10) for various mental/physical goals.",
            "Scapular Strength & Stability: Crucial for arm balances and inversions, emphasizing proper scapular mechanics (e.g., protraction in Plank, not 'shoulders away from ears' in Downward Dog). Develops 'straight arm scapular strength (SASS).'",
            "Targeted Drills for Complex Poses: Breaks down advanced postures into simpler, preparatory drills (e.g., specific handstand hops, Crow Pose progressions, Plank variations for core) to incrementally build foundational strength and awareness."
        ],
        "motivational_style": "Empathetic, analytical, and inspiring. Guides practitioners to understand their body's mechanics, overcome perceived limitations, and foster a deep mind-body connection. Encourages patience, consistency, and internal awareness over external perfection.",
        "typical_session_flow": (
            "Dylan Werner's sessions often start with dynamic warm-ups (like Sun Salutations with specific cues), move into foundational strength and mobility drills (e.g., core activation, scapular work, specific stretches from MIS), progress to targeted preparatory drills for advanced poses, and then integrate these skills into more complex sequences. "
            "Breathwork (Pranayama) is woven throughout the practice for nervous system regulation and focus. "
            "Sessions emphasize mindful, sensation-based movement over rigid alignment, with opportunities for test-retest through progressive challenges."
        ),
        "exercise_library": [
            {
                "name": "Sun Salutation A (Surya Namaskar A)",
                "type": "foundational_flow",
                "description": "A foundational flow comprising Mountain Pose, Raised Hands Pose, Forward Fold, Flat Back, Plank, Chaturanga Dandasana, Upward Facing Dog, and Downward Facing Dog.",
                "benefits": [
                    "Warms up the entire body.",
                    "Builds foundational strength.",
                    "Stretches key muscle groups.",
                    "Links breath and movement.",
                    "Cultivates body awareness.",
                    "Energizes the body and prepares for more complex postures."
                ],
                "key_cues": {
                    "Mountain Pose": "Align body, drop awareness.",
                    "Raised Hands Pose": "Lift arms overhead, palms touch or shoulder-distance apart.",
                    "Forward Fold": "Shift weight slightly into balls of feet, hips over ankles, relax neck.",
                    "Flat Back": "Lift head for natural spine extension, gaze few feet forward.",
                    "Plank": "Hands shoulder-distance, shoulders over wrists, wrap triceps back (elbows face back), squeeze hands slightly for chest engagement, press inner hands, scapular protraction (separate shoulder blades, lift heart), squeeze inner thighs, tuck tailbone, engage core, gaze down/slightly forward.",
                    "Chaturanga Dandasana": "Shift forward onto tippy-toes (shoulders past wrists), bend elbows straight back (hug ribs), lower until shoulders/upper arms parallel to elbows (not below), gaze down, neck long.",
                    "Upward Facing Dog": "Hands under elbows, squeeze elbows, draw shoulders back, press tops of feet, curl chest up, straighten arms, lift thighs off ground, activate legs, engage glutes, squeeze inner thighs, pull shoulder blades together, elevate through crown of head (lengthen neck), gaze forward.",
                    "Downward Facing Dog": "Lift hips, return to balls of feet, press back."
                },
                "target_area_movement_pattern": "Full body warm-up, spinal flexion/extension, hip opening, shoulder stability, core strength, leg strength.",
                "purpose_in_system": "Foundational sequence for vinyasa practice, linking breath and movement, building core strength and body awareness. Prepares the body for more advanced postures.",
                "progressions_regressions": {
                    "progressions": ["Jumping back from Forward Fold to Plank or directly into Chaturanga."],
                    "regressions": ["Stepping back instead of jumping.", "For Chaturanga, use knees-down modification or practice against a wall."]
                }
            },
            {
                "name": "Sun Salutation B (Surya Namaskar B)",
                "type": "foundational_flow",
                "description": "Builds upon Sun Salutation A by incorporating Chair Pose and Warrior I, adding more intensity and leg work.",
                "benefits": [
                    "Increased leg strength and endurance.",
                    "Deeper hip opening (Warrior I).",
                    "Enhanced cardiovascular challenge.",
                    "Further links breath with dynamic movement."
                ],
                "key_cues": {
                    "Chair Pose (Utkatasana)": "Feet hip-width apart, sink hips low (as if sitting in a chair), arms overhead, engage core, 'tuck tailbone' slightly, draw ribs down.",
                    "Warrior I (Virabhadrasana I)": "Front knee stacked over ankle, back foot angled about 45 degrees, hips squared forward, arms overhead, engage core, lift through chest.",
                    "All other poses": "Apply same precise cues as in Sun Salutation A."
                },
                "target_area_movement_pattern": "Legs (quads, hamstrings, glutes), hips (flexion, external rotation), core, full body.",
                "purpose_in_system": "Adds intensity and specific strength building (legs, hips) to the foundational warm-up.",
                "progressions_regressions": {
                    "progressions": ["Hold Chair Pose/Warrior I for longer durations.", "Add arm variations in Chair Pose."],
                    "regressions": ["Reduce depth of Chair Pose.", "Narrow stance in Warrior I."]
                }
            },
            {
                "name": "Supine Lat Stretch Screen",
                "type": "diagnostic_assessment",
                "description": "Lying on your back with knees to chest (to flatten lumbar spine), arms extended overhead with palms up. Assess ability to bring arms to floor.",
                "benefits": ["Assesses lat flexibility.", "Identifies restrictions in shoulder flexion and thoracic extension.", "Helps diagnose contributors to overhead mobility issues."],
                "progressions_regressions": {
                    "regressions": ["Perform with straighter legs if knees to chest is too restrictive.", "Focus on gentle breathing to encourage relaxation."],
                    "progressions": ["Actively press arms down to floor if possible (active stretch)."]
                },
                "key_cues": [
                    "Lie flat on your back, press lower back into floor (knees to chest helps).",
                    "Arms straight overhead, palms facing up.",
                    "Gently try to bring arms to the floor.",
                    "Observe if arms 'dangle' or touch the floor."
                ],
                "target_area_movement_pattern": "Lats, Shoulder Flexion, Thoracic Extension. Shoulder Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for lat tightness that can limit overhead mobility in lifts like snatch or overhead squat."
            },
            {
                "name": "Wall Angel Screen",
                "type": "diagnostic_assessment",
                "description": "Stand with back, head, and entire back against a wall. Arms in an 'L' shape (football goal post), elbows bent, forearms against wall. Slide arms up while maintaining contact.",
                "benefits": ["Assesses gross overhead mobility.", "Identifies restrictions in thoracic spine mobility and pectoral/shoulder tightness.", "Activates scapular stabilizers."],
                "progressions_regressions": {
                    "regressions": ["Feet further from wall to reduce lumbar arch compensation.", "Focus on lower back contact first, then arms."],
                    "progressions": ["Increase duration of hold at top.", "Add light resistance band around wrists to maintain elbow width."]
                },
                "key_cues": [
                    "Back, head, and entire back flat against the wall.",
                    "Feet 4-5 inches from wall.",
                    "Arms in an 'L' shape (90-degree bend at elbows).",
                    "Attempt to flatten back of arms and hands against the wall.",
                    "Slide arms up, maintaining contact, without moving head or lower back."
                ],
                "target_area_movement_pattern": "Thoracic Spine, Shoulders, Pecs, Scapular Stability. Overhead Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for limitations in overhead mobility relevant for pressing, snatching, and overhead squatting."
            },
            {
                "name": "Wall Ankle Mobility Test (Ankle Dorsiflexion Test)",
                "type": "diagnostic_assessment",
                "description": "Kneel with one foot 5 inches from a wall. Push knee directly over middle toe towards the wall while keeping the heel on the floor.",
                "benefits": ["Assesses ankle dorsiflexion flexibility.", "Identifies restrictions that can impact squat depth and knee health.", "Differentiates between joint and soft-tissue restrictions."],
                "progressions_regressions": {
                    "regressions": ["Start with foot closer to the wall (e.g., 3 inches).", "Gentle rocking motion."],
                    "progressions": ["Increase distance from wall (e.g., 6+ inches).", "Add light weight to knee."]
                },
                "key_cues": [
                    "One foot 5 inches (handprint + thumb) from the wall.",
                    "Keep heel firmly on the floor.",
                    "Push knee directly over the middle toe towards the wall.",
                    "Observe if knee touches wall without heel lifting."
                ],
                "target_area_movement_pattern": "Ankle Dorsiflexion, Calves (Gastrocnemius, Soleus). Ankle Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for ankle mobility crucial for achieving proper squat depth and preventing compensatory movements (e.g., foot 'spinning out')."
            },
            {
                "name": "Thomas Test (Hip Internal/External Rotation Test)",
                "type": "diagnostic_assessment",
                "description": "Sit on the edge of a bed/bench with hips at the edge. Pull one knee to chest while allowing the other leg to relax. Assess position of relaxed leg.",
                "benefits": ["Identifies tightness in hip flexors (Iliopsoas, Rectus Femoris) and/or IT band.", "Assesses hip flexion mobility.", "Reveals asymmetry between hip sides."],
                "progressions_regressions": {
                    "regressions": ["Don't pull knee quite as close to chest.", "Use support for stability."],
                    "progressions": ["Focus on actively relaxing the tested leg.", "Compare results rigorously side-to-side."]
                },
                "key_cues": [
                    "Sit on edge of bed/bench, hips at edge.",
                    "Grab one knee, pull it to chest.",
                    "Gently fall backward onto your back.",
                    "Allow the opposite leg to relax completely.",
                    "Observe if relaxed leg lifts off bed or bends."
                ],
                "target_area_movement_pattern": "Hip Flexors, Iliotibial Band, Hip Mobility (Flexion, Internal/External Rotation). Hip Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for hip mobility restrictions that can contribute to low back pain or compensation in lower body movements."
            },
            {
                "name": "Flexion Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is exacerbated by actions such as sitting slouched, pulling up on the underside of a chair, bending movements like picking up objects from the ground, or deadlifting.",
                "benefits": ["Helps diagnose flexion intolerance, often associated with disc bulge/herniation.", "Guides selection of spine-sparing movements."],
                "progressions_regressions": {
                    "regressions": ["Avoid all known aggravating positions.", "Perform activities with maximal bracing."],
                    "progressions": ["Gradually introduce light loads with perfect hip hinge mechanics."]
                },
                "key_cues": [
                    "Consciously adopt positions that typically cause pain.",
                    "Note the exact trigger and pain intensity.",
                    "Compare pain levels with spine-neutral positions."
                ],
                "target_area_movement_pattern": "Lumbar Spine Flexion. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses sensitivity to spinal flexion, guiding corrective strategies focused on neutral spine and hip hinging."
            },
            {
                "name": "Extension Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is provoked by positions such as lying on the stomach, arching backward, or adopting an anterior pelvic tilt.",
                "benefits": ["Helps diagnose extension intolerance, potentially due to facet joint irritation or spondylolisthesis.", "Guides selection of spine-neutral movements."],
                "progressions_regressions": {
                    "regressions": ["Avoid all known aggravating positions.", "Focus on 'ribs down' cue in daily activities."],
                    "progressions": ["Gradually introduce gentle extension movements with controlled core bracing."]
                },
                "key_cues": [
                    "Consciously adopt positions that typically cause pain.",
                    "Note the exact trigger and pain intensity.",
                    "Compare pain levels with spine-neutral positions."
                ],
                "target_area_movement_pattern": "Lumbar Spine Extension. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses sensitivity to spinal extension, guiding corrective strategies focused on maintaining a braced neutral spine."
            },
            {
                "name": "Dynamic Loading/Instability Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain occurs with dynamic loading (running, jumping, Olympic lifts), or subtle micro-movements like sneezing/rolling over. A diagnostic test involves rising onto the toes and quickly dropping onto the heels.",
                "benefits": ["Helps diagnose spinal instability and uneven vertebral sliding.", "Guides emphasis on robust core bracing."],
                "progressions_regressions": {
                    "regressions": ["Avoid dynamic loading; focus on static core bracing.", "Temporary cessation of high-impact activities."],
                    "progressions": ["Gradually reintroduce dynamic movements with strong core bracing.", "Increase intensity of movement."]
                },
                "key_cues": [
                    "Perform dynamic movements or controlled drop test.",
                    "Observe if pain is triggered by shockwave of load or micro-movements.",
                    "Note the exact trigger and pain intensity."
                ],
                "target_area_movement_pattern": "Spinal Stability, Dynamic Core Control. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses spinal instability, emphasizing the need for comprehensive core bracing strategies."
            },
            {
                "name": "Load Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is triggered by holding a light weight at arm's length while taking deep breaths.",
                "benefits": ["Helps diagnose high sensitivity to load, potentially indicative of compressive injury.", "Guides decisions on lifting cessation or modification."],
                "progressions_regressions": {
                    "regressions": ["Avoid any loading.", "Seek assistance for daily lifting tasks."],
                    "progressions": ["Gradually introduce light loads with strong abdominal bracing."]
                },
                "key_cues": [
                    "Hold a light weight at arm's length.",
                    "Take deep breaths while holding.",
                    "Observe if pain is triggered."
                ],
                "target_area_movement_pattern": "Spinal Compression Tolerance. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses extreme load sensitivity, dictating immediate lifting modifications or temporary cessation."
            },
            {
                "name": "Proper Hip Hinging (Corrective Strategy)",
                "type": "corrective_strategy",
                "description": "Learning and consistently applying the movement pattern where the hips initiate the bend, keeping the spine neutral, as seen in movements like the 'short-stop squat' or 'golfer's lift.'",
                "benefits": ["Protects the lumbar spine from excessive flexion.", "Loads the glutes and hamstrings effectively.", "Essential for deadlifts and picking objects safely."],
                "progressions_regressions": {
                    "regressions": ["Wall hinge drill (touching butt to wall)", "Downgrade with PVC pipe along spine.", "Kneeling for light objects."],
                    "progressions": ["Adding light load (e.g., kettlebell RDL)", "Increasing speed of hinge.", "Integrating into more complex lifts."]
                },
                "key_cues": [
                    "Push hips back first.",
                    "Maintain a long, neutral spine (avoid rounding or excessive arching).",
                    "Keep chest up.",
                    "Slight bend in knees, but focus on hip movement."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Erector Spinae. Hip Hinge, Spinal Stability.",
                "purpose_in_system": "Fundamental corrective for flexion intolerance; re-educates the movement pattern for safe lifting and daily activities."
            },
            {
                "name": "Ribs Down (Corrective Cue/Strategy)",
                "type": "corrective_strategy",
                "description": "A fundamental cue to prevent excessive spinal extension by engaging the core and drawing the lower ribs down towards the pelvis, maintaining a braced neutral spine.",
                "benefits": ["Prevents spinal extension intolerance.", "Promotes a neutral lumbar spine.", "Enhances core bracing and intra-abdominal pressure."],
                "progressions_regressions": {
                    "regressions": ["Practice in supine (lying on back) with knees bent, pressing lower back into floor.", "Gentle diaphragmatic breathing."],
                    "progressions": ["Apply cue during all lifts (squats, presses).", "Combine with Valsalva maneuver for maximal bracing."]
                },
                "key_cues": [
                    "Imagine pulling your lower ribs towards your belt line.",
                    "Avoid arching your lower back excessively.",
                    "Engage your abdominals gently."
                ],
                "target_area_movement_pattern": "Core (Rectus Abdominis, Obliques), Diaphragm. Spinal Extension Control, Core Bracing.",
                "purpose_in_system": "Core corrective strategy for extension intolerance; critical for maintaining spinal neutrality during lifting."
            },
            {
                "name": "Abdominal Bracing (Corrective Strategy)",
                "type": "corrective_strategy",
                "description": "A technique to increase intra-abdominal pressure by engaging the entire core musculature, providing stability to the spine for lifting and injury prevention.",
                "benefits": ["Minimizes spinal instability.", "Protects the spine from injury under load.", "Increases power transfer during lifts."],
                "progressions_regressions": {
                    "regressions": ["Practice 'bracing for a punch' while lying on back.", "Focus on 360-degree bracing, not just 'sucking in'."],
                    "progressions": ["Apply bracing to progressively heavier lifts.", "Combine with Valsalva maneuver (holding breath with braced core)."]
                },
                "key_cues": [
                    "Imagine bracing for a punch to the stomach (tighten all around).",
                    "Breathe into your belly and sides, not just chest.",
                    "Create 360-degree tension in your core.",
                    "Maintain bracing throughout the lift."
                ],
                "target_area_movement_pattern": "Core (Transverse Abdominis, Obliques, Rectus Abdominis, Diaphragm, Pelvic Floor). Spinal Stability, Intra-abdominal Pressure.",
                "purpose_in_system": "Fundamental corrective for dynamic loading/instability and load intolerance; provides a stable base for all complex movements."
            },
            {
                "name": "Handstand Preparation Drills (various)",
                "type": "targeted_drill",
                "description": "A series of progressive drills to build strength, alignment, and body awareness for handstands. Includes Downward Dog hops, hollow body holds, Plank variations, and wall walks.",
                "benefits": ["Builds straight arm scapular strength (SASS).", "Develops core stability essential for inversion.", "Improves shoulder and wrist conditioning.", "Enhances proprioception and body awareness while inverted."],
                "progressions_regressions": {
                    "regressions": ["Start with shorter holds for hollow body and planks.", "Practice wall walks with feet lower on the wall.", "Focus on smaller hops in Downward Dog."],
                    "progressions": ["Increase hold durations and repetitions.", "Progress from wall-assisted handstands to freestanding attempts.", "Introduce leg variations (e.g., tuck, straddle)."]
                },
                "key_cues": [
                    "Shoulders directly over wrists.",
                    "Protracted scapulae ('broaden your back').",
                    "Engage core ('tuck tailbone,' 'ribs down').",
                    "Squeeze inner thighs together.",
                    "Look between hands or slightly forward (not directly up or down)."
                ],
                "target_area_movement_pattern": "Shoulders, Wrists, Core, Scapular Stability, Proprioception. Handstand, Inversion.",
                "purpose_in_system": "Systematic progression for safely acquiring handstand skill by building foundational strength and body control."
            },
            {
                "name": "Crow Pose (Bakasana) Drills",
                "type": "targeted_drill",
                "description": "Preparatory drills for Crow Pose, starting from a squat, placing knees on triceps, and gradually shifting weight forward into fingertips before lifting heels.",
                "benefits": ["Builds arm and wrist strength.", "Develops core engagement for arm balances.", "Enhances body control and balance.", "Helps overcome fear of falling."],
                "progressions_regressions": {
                    "regressions": ["Practice with blocks under feet or head for support.", "Focus on weight shift without lifting feet initially.", "Use a bolster or pillow in front for safety."],
                    "progressions": ["Hold for longer durations.", "Transition from Crow Pose to other arm balances (e.g., tripod headstand).", "Explore variations like side crow."]
                },
                "key_cues": [
                    "Start in a squat, hands shoulder-width apart, fingers spread.",
                    "Place knees high on triceps (as close to armpits as possible).",
                    "Look forward, shift weight forward into fingertips.",
                    "Engage core, lift one heel, then the other, towards glutes.",
                    "Squeeze knees into arms."
                ],
                "target_area_movement_pattern": "Arms (triceps, biceps), Wrists, Core, Hip Flexors, Balance. Arm Balance.",
                "purpose_in_system": "Breaks down Crow Pose into manageable steps, building the necessary strength, balance, and confidence."
            },
            {
                "name": "Hollow Body Hold",
                "type": "core_strength",
                "description": "Lying on your back, lift head, shoulders, and legs slightly off the ground, maintaining a neutral lumbar spine and engaged core.",
                "benefits": ["Fundamental for core stability and strength.", "Builds the 'hollow body' shape crucial for handstands and other bodyweight skills.", "Improves overall body tension and control."],
                "progressions_regressions": {
                    "regressions": ["Keep knees bent.", "Lift legs higher.", "Place hands by your sides or under your lower back."],
                    "progressions": ["Extend arms overhead (most challenging).", "Lower legs closer to the ground (without arching back).", "Increase hold duration."]
                },
                "key_cues": [
                    "Press lower back into the floor (no arch).",
                    "Draw navel to spine.",
                    "Keep legs straight and together, pointed toes.",
                    "Arms extended overhead or by sides.",
                    "Gaze towards toes, shoulders off ground."
                ],
                "target_area_movement_pattern": "Deep Core (Transverse Abdominis, Rectus Abdominis, Obliques), Hip Flexors. Core Stability.",
                "purpose_in_system": "Develops foundational core strength and body tension necessary for advanced bodyweight movements."
            },
            {
                "name": "Plank Variations (with Scapular Protraction)",
                "type": "core_strength_and_scapular_stability",
                "description": "Various plank positions (forearm plank, high plank) emphasizing active scapular protraction and core engagement.",
                "benefits": ["Strengthens core and shoulders.", "Improves scapular stability, crucial for overhead movements and arm balances.", "Builds overall body stiffness and endurance."],
                "progressions_regressions": {
                    "regressions": ["Knees down plank.", "Shorter hold durations.", "Wall plank."],
                    "progressions": ["One-arm/one-leg plank.", "Plank shoulder taps.", "Plank rocks."]
                },
                "key_cues": [
                    "Shoulders directly over wrists (high plank) or elbows (forearm plank).",
                    "Push the floor away, protracting shoulder blades ('separate them,' 'lift heart').",
                    "Tuck tailbone, engage glutes.",
                    "Draw ribs and navel in, maintaining a straight line from head to heels."
                ],
                "target_area_movement_pattern": "Core, Shoulders, Scapular Stabilizers, Triceps, Quads. Core Stability, Scapular Control.",
                "purpose_in_system": "Builds fundamental core and shoulder girdle strength and stability, critical for all bodyweight movements."
            },
            {
                "name": "Chaturanga Dandasana Modifications",
                "type": "strength_building_and_alignment",
                "description": "Progressive modifications for Chaturanga, focusing on proper alignment and muscle engagement.",
                "benefits": ["Builds strength in triceps, shoulders, and core.", "Establishes proper elbow and shoulder alignment.", "Prevents shoulder injuries common in incorrect Chaturanga."],
                "progressions_regressions": {
                    "regressions": ["Knees-down Chaturanga.", "Practice against a wall (standing push-ups at an angle).", "Reduce depth of descent."],
                    "progressions": ["Full Chaturanga (off knees).", "Slower descent.", "Hold at the bottom parallel position for longer."]
                },
                "key_cues": [
                    "Start in Plank, shift forward onto tippy-toes (shoulders past wrists).",
                    "Hug elbows tightly to sides (like 'robot arms').",
                    "Lower until shoulders and upper arms are parallel to elbows (no deeper).",
                    "Maintain engaged core and long neck, gaze slightly forward."
                ],
                "target_area_movement_pattern": "Triceps, Shoulders (Deltoids, Rotator Cuff), Core. Push Strength, Shoulder Stability.",
                "purpose_in_system": "Develops the specific strength and alignment needed for safe and effective Chaturanga, preventing common yoga injuries."
            },
            {
                "name": "Sama Vritti (Equal Ratio Breathing)",
                "type": "pranayama",
                "description": "Breathing technique where inhalation and exhalation are equal in duration and intensity (e.g., 4-count inhale, 4-count exhale).",
                "benefits": ["Calms the nervous system.", "Reduces stress and anxiety.", "Increases Heart Rate Variability (HRV), indicating a healthy autonomic nervous system.", "Promotes mental equanimity and focus."],
                "progressions_regressions": {
                    "regressions": ["Start with shorter counts (e.g., 3 seconds).", "Focus on gentle, unforced breath."],
                    "progressions": ["Increase breath count (e.g., 6, 8 seconds).", "Practice in challenging poses to maintain calm."]
                },
                "key_cues": [
                    "Inhale slowly through the nose for a count.",
                    "Exhale slowly through the nose for the same count.",
                    "Keep breath smooth and even, without strain.",
                    "Focus on the sensation of the breath."
                ],
                "target_area_movement_pattern": "Respiratory System, Nervous System Regulation. Breathwork, Mental Focus.",
                "purpose_in_system": "Foundation for nervous system regulation, bringing balance and calm, applicable in both passive and active practices."
            },
            {
                "name": "The 4-7-8 Breath",
                "type": "pranayama",
                "description": "A calming breath technique: Inhale for 4 counts, hold for 7 counts, exhale for 8 counts.",
                "benefits": ["Activates the parasympathetic nervous system.", "Promotes deep relaxation and sleep.", "Reduces stress and anxiety.", "Increases carbon dioxide levels, slowing heart rate and lowering blood pressure."],
                "progressions_regressions": {
                    "regressions": ["Start with shorter counts, maintaining the 1:2 exhale ratio.", "Practice in a relaxed, seated position."],
                    "progressions": ["Perform multiple cycles.", "Integrate before sleep for improved rest."]
                },
                "key_cues": [
                    "Inhale quietly through the nose for a count of 4.",
                    "Hold the breath for a count of 7.",
                    "Exhale completely through the mouth, making a 'whoosh' sound, for a count of 8.",
                    "Repeat for several cycles."
                ],
                "target_area_movement_pattern": "Respiratory System, Parasympathetic Nervous System. Relaxation, Stress Reduction.",
                "purpose_in_system": "Powerful tool for cultivating tamasic (calming) energy and promoting deep relaxation and recovery."
            }
        ]
    },
    "ido_portal": {
        "name": "Ido Portal",
        "focus": "Movement complexity, natural patterns, holistic physical development",
        "core_philosophy": "Movement Culture: An integrated approach beyond traditional fitness, encompassing health, aesthetics, performance, and art. Emphasizes cross-disciplinary exchange and the 'Mover' concept.",
        "key_principles": [
            "Movement Culture: Integrated perspective on physicality.",
            "The 'Mover' Concept: Self-identification and continuous development beyond singular disciplines.",
            "Generalist vs. Specialist: Ability to dynamically switch focus based on context.",
            "Holistic Approach: Integration of nutrition, sleep, and mental well-being.",
            "Play as a Tool: Fundamental for learning, exploration, and enjoyment.",
            "I-I-I Principle (Isolation, Integration, Improvisation): Hierarchical progression for skill acquisition, rooted in neuroplasticity.",
            "Dogma: Defining your ultimate 'Why' as the foundation for goals and methods.",
            "Repetition is the Mother of Skill: Consistent, high-quality practice for mastery.",
            "Progressive Overload (Expanded): Continuous increase of various parameters (ROM, TUT, reps, density, complexity, etc.) to drive adaptation.",
            "Loaded Progressive Stretching & 'Improper Alignment' Training: Building resilience and strength in end-ranges/challenging positions.",
            "Quality Over Quantity: 100% correct execution for every repetition.",
            "Movement as Nutrition / Movement Snacks: Frequent, varied movement throughout the day for continuous adaptation.",
            "Kinesthetic Intelligence: Understanding and controlling body movements, learning through physical expression."
        ],
        "motivational_style": "Philosophical, challenging, emphasizes curiosity and intrinsic motivation, often uses analogies.",
        "typical_session_flow": [
            "1. Comprehensive Warm-up: Spinal Waves, joint rotations, specific body part preparation.",
            "2. Skill Work: Focused practice on specific movement skills (e.g., Handstand, Rings) emphasizing Isolation, Integration, then Improvisation.",
            "3. Integration & Strength: Ground-based movement (e.g., QM), loaded stretching, bodyweight strength exercises in various patterns.",
            "4. Cool-down / Decompression: Hanging protocols, gentle mobility work, somatics.",
            "5. Movement Snacks: Short, varied movement bursts performed throughout the day, separate from main training sessions."
        ],
        "exercise_library": [
            {
                "name": "Spinal Waves",
                "description": "A method for mobilizing, integrating, and articulating each individual section of the spine one at a time. Can be sagittal (forward/backward) or lateral (side-to-side).",
                "benefits": [
                    "Increases spinal fluidity, nutrition, and blood flow.",
                    "Enhances body awareness and control for precise movements.",
                    "Reduces back injury risk by increasing spinal awareness.",
                    "Prepares body for unchoreographed life and expands usable range of motion."
                ],
                "progressions_regressions": {
                    "regressions": [
                        "Smaller, more segmented movements.",
                        "Potentially with external support or visual cues to isolate segments.",
                        "Focus on quality over speed initially."
                    ],
                    "progressions": [
                        "Increasing fluidity, speed, and control through full range.",
                        "More complex variations or combining with other movements."
                    ]
                },
                "key_cues": [
                    "Take it slow and ENJOY.",
                    "Move at each section individually one at a time.",
                    "Pretend that there's a wall in front... and behind you (for lateral waves).",
                    "Smooth, continuous motion."
                ],
                "target_area_movement_pattern": "Entire spine (cervical, thoracic, lumbar), promoting articulation and integration of spinal movement. Overall body awareness and control.",
                "purpose_in_system": "Foundational practice for spinal articulation in non-linear patterns. Key mobility technique often used in warm-ups and general movement preparation ('Movement Terminology')."
            },
            {
                "name": "Quadrupedal Movement (QM) / Locomotion (e.g., Lizard Crawl)",
                "description": "Ground-based bodyweight exercises using four points of contact (hands and feet), including crawling, sprawling, twisting/turning, reaching, and flowing. Lizard Crawl is a low-to-ground pattern with shoulders, torso, and hips hovering 1-2 inches above the floor, involving coordinated limb movement.",
                "benefits": [
                    "Develops strength, agility, flexibility.",
                    "Improves physical competence, balance, coordination, spatial awareness, and overall athleticism.",
                    "Enhances movement IQ and transitions.",
                    "Builds strength at more angles, aids injury mitigation, improves mind-body connection, and bodyweight control.",
                    "Provides unique upper extremity loading, connects the core, and restores lost primal movement patterns."
                ],
                "progressions_regressions": {
                    "regressions": [
                        "Practice individual patterns when fresh (warm-up).",
                        "For Lizard Crawl: two hands in contact while practicing hip ROM/foot placement; stationary reaching with lead arm.",
                        "Easier variations of specific QM patterns (e.g., simpler crawls, shorter distances)."
                    ],
                    "progressions": [
                        "Increase distance/time (15-20ft, 30-40s continuous, up to 5 min for advanced).",
                        "Slow tempo, other variations.",
                        "Fuse isolated work into sequences.",
                        "Add resistance (e.g., weighted lizard crawl).",
                        "Increase complexity/volume and speed."
                    ]
                },
                "key_cues": [
                    "Keep the spine parallel to the floor.",
                    "Avoid excessive movement through the torso.",
                    "Quiet hand/foot contacts.",
                    "Imagine balancing a glass of water on your back. Don't spill a drop.",
                    "Move slow for greater benefit.",
                    "For Lizard Crawl, bend knee and internally rotate hip to stay lower."
                ],
                "target_area_movement_pattern": "Full body, significant demands on scapular mobility/stabilization, core control, hip mobility. Unique upper extremity loading. Torso musculature for spine protection.",
                "purpose_in_system": "Foundational component of Isolation and Integration phases. Builds foundational strength, stability, mobility, and conditioning. Expands movement capacity, integrated into warm-ups, circuits, and flow sessions. Helps develop ground movement proficiency."
            },
            {
                "name": "Handstand Basics (Wall Handstand, Free Handstand)",
                "description": "Mastering the fundamental skill of balancing inverted on one's hands. Progresses from wall-supported variations to freestanding holds.",
                "benefits": [
                    "Develops significant shoulder strength and stability.",
                    "Improves balance and proprioception.",
                    "Strengthens wrist and forearm stabilizers.",
                    "Enhances body awareness and control.",
                    "Builds confidence and mental fortitude."
                ],
                "progressions_regressions": {
                    "regressions": [
                        "Crow Pose/Frog Stand (forearm support, foundational balance).",
                        "Pike Handstand against wall (feet on wall, hips stacked).",
                        "Back to wall handstand (facing wall, hands close).",
                        "Stomach to wall handstand (facing away from wall, controlled entry/exit)."
                    ],
                    "progressions": [
                        "Freestanding Handstand (short holds, then longer).",
                        "Handstand walks.",
                        "One-arm handstand progressions.",
                        "Press to handstand variations."
                    ]
                },
                "key_cues": [
                    "Scapular protraction (pushing floor away).",
                    "Straight arms, locked elbows.",
                    "Ribs tucked (no arching back).",
                    "Engage glutes and quads (straight legs).",
                    "Head neutral or slight gaze forward.",
                    "Use fingers/wrists to control balance (like grabbing a ball)."
                ],
                "target_area_movement_pattern": "Shoulders (deltoids, rotator cuff), triceps, lats, core (all abdominal muscles), wrists, forearms. Inverted static hold, balance.",
                "purpose_in_system": "Key skill in Movement Culture for developing upper body strength, balance, and advanced body control. Integrates straight arm strength and core stability, crucial for many other advanced skills."
            },
            {
                "name": "Copenhagen Plank (Adductor/Groin Strength)",
                "description": "A challenging side plank variation specifically designed to strengthen the adductor muscles (inner thigh) and improve groin stability. Performed by supporting the body on one forearm and the top leg, with the bottom leg hanging or placed on a bench/elevated surface.",
                "benefits": [
                    "Significantly reduces risk of groin strains/injuries, especially in sports.",
                    "Strengthens hip adductors and core stabilizers.",
                    "Improves hip health and stability.",
                    "Addresses muscular imbalances between adductors and abductors."
                ],
                "progressions_regressions": {
                    "regressions": [
                        "Both knees bent, supporting body with top knee on bench.",
                        "Bottom knee bent, top leg extended on bench.",
                        "Regular side plank with leg lift."
                    ],
                    "progressions": [
                        "Top foot only on bench, bottom leg hanging freely.",
                        "Weighted Copenhagen plank.",
                        "Longer hold durations.",
                        "Dynamic variations (e.g., lifting bottom leg to meet top leg)."
                    ]
                },
                "key_cues": [
                    "Maintain a straight line from head to heels.",
                    "Engage your core to prevent hip sag.",
                    "Actively squeeze the inner thigh of the top leg into the bench/support.",
                    "Control the movement, don't just hang."
                ],
                "target_area_movement_pattern": "Hip adductors (inner thigh), obliques, glutes, core. Isometric hold for hip/groin stability.",
                "purpose_in_system": "Injury prevention, particularly for athletes, and building resilience in vulnerable areas. Part of developing 'Loaded Progressive Stretching' and improving overall joint integrity."
            },
            {
                "name": "Hanging Protocols (Passive & Active Hanging)",
                "description": "Series of exercises involving hanging from a bar to decompress the spine, strengthen grip, and improve shoulder health. Includes passive (relaxed) and active (shoulders engaged, scapular retraction/depression) variations.",
                "benefits": [
                    "Decompresses the spine, improving spinal health.",
                    "Strengthens grip endurance and strength.",
                    "Improves shoulder mobility and rotator cuff health.",
                    "Enhances lat and upper back activation.",
                    "Builds foundational pulling strength.",
                    "Releases tension in the shoulders and upper back."
                ],
                "progressions_regressions": {
                    "regressions": [
                        "Feet supported on a box (less bodyweight).",
                        "One-arm assisted hang (using other hand for support).",
                        "Shorter durations or more frequent breaks."
                    ],
                    "progressions": [
                        "Longer passive hangs (up to several minutes).",
                        "Active hangs (pulling shoulders down/away from ears).",
                        "Scapular pull-ups (only shoulder blade movement).",
                        "One-arm active hang.",
                        "Weighted hangs."
                    ]
                },
                "key_cues": [
                    "For passive: fully relax shoulders, let gravity stretch.",
                    "For active: pull shoulder blades down and back, engage lats.",
                    "Maintain a strong, even grip.",
                    "Breathe deeply and relax the rest of the body."
                ],
                "target_area_movement_pattern": "Lats, grip muscles (forearms), scapular stabilizers (rhomboids, traps), shoulders. Spinal decompression, upper body pulling foundation.",
                "purpose_in_system": "Fundamental for shoulder health, grip strength, and preparing the body for advanced pulling movements. A daily 'movement snack' to improve posture and general upper body function."
            }
        ]
    },
    "patrick_beach": {
        "name": "Patrick Beach",
        "focus": "Natural Movement and Mobility",
        "core_philosophy": "Movement should feel natural and fluid. Focus on natural movement patterns and mobility.",
        "key_principles": ["Natural Movement", "Fluid Motion", "Mobility Focus"],
        "training_methods": ["Movement Flow", "Mobility Work", "Natural Patterns"],
        "motivational_style": "Encouraging, patient, emphasizes natural movement"
    },
    "squatu": {
        "name": "SquatU",
        "focus": "Joint Safety and Injury Prevention",
        "core_philosophy": "Train smart, not hard. Focus on joint safety and proper movement patterns.",
        "key_principles": ["Joint Safety", "Injury Prevention", "Proper Form"],
        "training_methods": ["Joint Mobility", "Movement Correction", "Safety-First Training"],
        "motivational_style": "Educational, safety-focused, emphasizes proper form"
    },
    "kneesovertoesguy": {
        "name": "Ben Patrick (KneesOverToesGuy)",
        "focus": "Knee health, joint bulletproofing, athletic longevity, foundational strength, pain-free movement, full range of motion strength",
        "core_philosophy": "Challenges conventional wisdom by advocating 'Knees Over Toes' movement for joint health and performance. Focuses on 'bulletproofing' joints (knees, ankles, hips, spine) by systematically strengthening them through their full, pain-free range of motion. Prioritizes proactive physical investment and integrating rehabilitation with performance training.",
        "key_principles": [
            "Knees over toes is safe and beneficial when trained progressively.",
            "Bulletproofing joints means enhancing mobility, strength, and resilience to reduce injury risk.",
            "Pain-Free Sets the Gains Free!: Train at a level that does not induce pain; modify and regress as needed.",
            "Build From The Ground Up: Develop strength sequentially from ankles, to knees, to hips, to shoulders.",
            "Build From Side-to-Side: Address unilateral imbalances with unilateral exercises.",
            "Build From Front-to-Back: Strengthen opposing muscle groups for balanced development.",
            "Build BOTH Short-Range and Long-Range: Develop strength across the entire joint ROM.",
            "Build From Light-to-Heavy: Gradual load increase with mastery of form; includes bodyweight periods.",
            "Build From Long-to-Short (Duration): Progress from slow, controlled movements to explosive ones.",
            "Build From Slow-to-Fast: Systematic transition from controlled strength to dynamic drills.",
            "Build and Keep a Bulletproofing Reserve: Prioritize deceleration and eccentric strength before acceleration.",
            "Truth in Numbers: Utilize measurable metrics for objective assessment and progress tracking."
        ],
        "motivational_style": "Empathetic (born from personal struggle), empowering, data-driven, practical, challenging traditional dogmas, emphasizes long-term benefits and self-responsibility.",
        "typical_session_flow": [
            "1. Foundational Warm-up: Often includes backward walking/sledding for blood flow and low-impact joint prep.",
            "2. Targeted Joint Preparation: Specific drills for ankles, knees (e.g., tibialis raises, calf stretches).",
            "3. Main Strength Work: Focus on ATG exercises with full ROM and controlled eccentrics (e.g., ATG Split Squats, Reverse Nordics).",
            "4. Complementary Strength/Flexibility: Addressing other key areas (e.g., hip flexors, spinal mobility).",
            "5. Cool-down: Gentle movements, sometimes including more passive stretching or tissue work."
        ],
        "exercise_library": [
            {
                "name": "ATG Split Squat",
                "description": "A deep lunge variation where the front knee tracks significantly over the toes, often with the back heel elevated, to build full knee flexion strength and hip flexor flexibility.",
                "benefits": [
                    "Strengthens VMO (Vastus Medialis Oblique) and vastus lateralis through full knee flexion.",
                    "Improves ankle dorsiflexion and hip flexor flexibility.",
                    "Enhances unilateral leg strength and balance.",
                    "Considered the #1 knee bulletproofer."
                ],
                "progressions_regressions": {
                    "regressions": ["Bodyweight only", "Reduced depth", "Using support (e.g., holding onto a post)", "Smaller front knee range (less KOT)", "Higher back heel elevation"],
                    "progressions": ["Adding external weight (e.g., dumbbells, barbell)", "Increasing depth (ass to grass)", "Elevating front foot (for greater stretch)", "Slowing tempo (e.g., 3-second eccentric)", "Reducing back heel elevation"]
                },
                "key_cues": [
                    "Keep the back leg straight and actively engaged (quads locked).",
                    "Front heel stays down.",
                    "Allow front knee to track far over toes.",
                    "Maintain an upright torso.",
                    "Control the descent.",
                    "Aim for 'ass to grass' depth if possible."
                ],
                "target_area_movement_pattern": "Quadriceps (especially VMO), Hip Flexors, Glutes, Hamstrings (secondary). Unilateral knee flexion, hip extension.",
                "purpose_in_system": "Core exercise for knee bulletproofing; develops strength, mobility, and resilience through full knee flexion and hip extension. Foundational for athletic movements."
            },
            {
                "name": "Tibialis Raise",
                "description": "An exercise targeting the tibialis anterior muscle on the front of the shin, crucial for ankle dorsiflexion and knee deceleration.",
                "benefits": [
                    "Strengthens tibialis anterior, improving ankle dorsiflexion.",
                    "Reduces shin splints and knee pain.",
                    "Enhances deceleration capacity and jumping ability.",
                    "Improves ankle stability and foot health."
                ],
                "progressions_regressions": {
                    "regressions": ["Bodyweight seated", "Using a band for assistance", "Reduced range"],
                    "progressions": ["Standing (back against wall)", "Using a KOTG Tib Bar or dumbbell on toes", "Increased reps/sets", "Slower tempo (eccentric emphasis)"]
                },
                "key_cues": [
                    "Keep heels on the ground.",
                    "Lift toes and ball of foot as high as possible.",
                    "Control the lowering phase.",
                    "Focus on the contraction of the shin muscle."
                ],
                "target_area_movement_pattern": "Tibialis Anterior. Ankle dorsiflexion.",
                "purpose_in_system": "Foundational exercise for ankle and knee health; addresses a commonly weak and neglected muscle essential for impact absorption and deceleration."
            },
            {
                "name": "KOTG Calf Stretch / Elephant Walk",
                "description": "A dynamic stretch for the calves and hamstrings, emphasizing full ankle dorsiflexion and plantarflexion.",
                "benefits": [
                    "Improves ankle dorsiflexion and plantarflexion.",
                    "Increases calf flexibility and Achilles tendon mobility.",
                    "Enhances hamstring flexibility (especially in Elephant Walk).",
                    "Improves overall lower leg health."
                ],
                "progressions_regressions": {
                    "regressions": ["Less depth in stretch", "Holding onto support", "Shorter duration"],
                    "progressions": ["Deeper stretch (e.g., elevated surface for KOTG Calf Stretch)", "Longer duration/reps", "Increased speed of movement in Elephant Walk"]
                },
                "key_cues": [
                    "Keep legs straight (or slightly bent for less hamstring pull).",
                    "Push heels towards the ground (in KOTG Calf Stretch).",
                    "Alternate driving heels down and lifting high (in Elephant Walk).",
                    "Feel the stretch in the calves and Achilles."
                ],
                "target_area_movement_pattern": "Calves (Gastrocnemius, Soleus), Achilles Tendon, Hamstrings. Ankle dorsiflexion/plantarflexion, hamstring extensibility.",
                "purpose_in_system": "Addresses ankle mobility, a key component for knee health and proper squat mechanics. Elephant Walk provides dynamic hamstring and calf lengthening."
            },
            {
                "name": "Reverse Nordic",
                "description": "An eccentric-focused exercise for the quadriceps, where the body leans back from the knees with the torso and hips in a straight line.",
                "benefits": [
                    "Develops significant eccentric quadriceps strength.",
                    "Improves knee flexion flexibility and strength at end range.",
                    "Enhances knee tendon resilience.",
                    "Beneficial for patellar tendonitis and general knee health."
                ],
                "progressions_regressions": {
                    "regressions": ["Assisted (e.g., using a band, holding a pole)", "Reduced range of motion (less lean back)", "Shorter hold duration at bottom"],
                    "progressions": ["Unassisted", "Holding a weight (e.g., medicine ball to chest)", "Slower eccentric tempo (e.g., 5-10 seconds)", "Holding the bottom position (isometric)"]
                },
                "key_cues": [
                    "Keep a straight line from knees to shoulders (avoid breaking at the hips).",
                    "Control the eccentric (lowering) phase slowly.",
                    "Squeeze glutes to maintain hip extension.",
                    "Engage quadriceps to control the movement."
                ],
                "target_area_movement_pattern": "Quadriceps, Hip Flexors (stretch). Knee flexion, eccentric control.",
                "purpose_in_system": "Crucial for building eccentric strength and resilience in the quadriceps and patellar tendon, directly addressing knee pain and preparing for powerful athletic movements."
            },
            {
                "name": "Sissy Squat",
                "description": "A quadriceps-dominant exercise where the body leans back from the knees, emphasizing extreme knee flexion and quad contraction.",
                "benefits": [
                    "Targets quadriceps, particularly VMO, through extreme knee flexion.",
                    "Enhances knee joint resilience and strength at end range.",
                    "Improves balance and core stability.",
                    "Develops strong quadriceps for jumping and sprinting."
                ],
                "progressions_regressions": {
                    "regressions": ["Holding onto support", "Reduced depth", "Less lean back"],
                    "progressions": ["Freestanding", "Adding external weight (e.g., holding a plate)", "Increased depth (butt to calves)", "Slower tempo"]
                },
                "key_cues": [
                    "Keep a straight line from knees to shoulders.",
                    "Allow knees to track far over toes.",
                    "Lift heels high off the ground (on toes).",
                    "Control the descent and ascent.",
                    "Squeeze quads at the top."
                ],
                "target_area_movement_pattern": "Quadriceps (especially VMO). Extreme knee flexion, balance.",
                "purpose_in_system": "Advanced quadriceps isolation and knee bulletproofing exercise, building strength and mobility in a highly challenging knee flexion pattern."
            },
            {
                "name": "Patrick Step",
                "description": "An exercise where one steps down from an elevated surface, maintaining an upright torso, to load the VMO and inner quad through terminal knee extension.",
                "benefits": [
                    "Strengthens the Vastus Medialis Oblique (VMO) at terminal knee extension.",
                    "Improves knee stability and tracking.",
                    "Addresses medial knee pain and tracking issues.",
                    "Enhances control during stepping and landing."
                ],
                "progressions_regressions": {
                    "regressions": ["Lower step height", "Reduced depth of step down", "Holding onto support"],
                    "progressions": ["Higher step height", "Adding external weight (e.g., holding dumbbells)", "Slower tempo", "Increased number of repetitions"]
                },
                "key_cues": [
                    "Keep the heel of the standing leg on the step.",
                    "Knee tracks forward over the toes as you step down.",
                    "Maintain an upright torso.",
                    "Control the movement, don't just drop.",
                    "Feel the engagement in the inner quad just above the knee."
                ],
                "target_area_movement_pattern": "Quadriceps (VMO), Glutes (stabilization). Terminal knee extension strength, knee control.",
                "purpose_in_system": "Key exercise for strengthening the VMO and ensuring full, pain-free knee extension, crucial for knee health and athletic performance."
            },
            {
                "name": "Seated Goodmornings",
                "description": "A hip hinge exercise performed seated with legs straight, focusing on hamstring length and spinal flexion/extension.",
                "benefits": [
                    "Improves hamstring flexibility.",
                    "Strengthens spinal erectors and lower back through a full range of motion.",
                    "Enhances hip hinge mechanics.",
                    "Can be loaded for progressive hamstring and back strength."
                ],
                "progressions_regressions": {
                    "regressions": ["Unweighted", "Bent knees", "Reduced range of motion"],
                    "progressions": ["Adding external weight (e.g., barbell on back, dumbbell held to chest)", "Increasing depth while maintaining straight legs", "Slower tempo for more control"]
                },
                "key_cues": [
                    "Keep legs straight (or mostly straight).",
                    "Hinge from the hips, not the lower back (initially focus on keeping back flat, then allow controlled rounding as per KOTG's methods for spinal health).",
                    "Feel the stretch in the hamstrings.",
                    "Control the movement both down and up."
                ],
                "target_area_movement_pattern": "Hamstrings, Glutes, Spinal Erectors. Hip hinge, spinal flexion/extension, hamstring extensibility.",
                "purpose_in_system": "Develops hamstring flexibility and strengthens the posterior chain through a loaded hip hinge, contributing to overall lower body power and spinal health."
            },
            {
                "name": "Hip Flexor Swimmers",
                "description": "A dynamic movement to improve hip flexor mobility and control, involving controlled leg swings or rotations.",
                "benefits": [
                    "Increases hip flexor flexibility and strength.",
                    "Improves hip joint mobility and range of motion.",
                    "Enhances hip control and stability."
                ],
                "progressions_regressions": {
                    "regressions": ["Smaller range of motion", "Slower tempo", "Using hands for support"],
                    "progressions": ["Larger range of motion", "Faster tempo (controlled)", "Adding light ankle weights", "Integrating into more complex movement flows"]
                },
                "key_cues": [
                    "Control the movement throughout the entire range.",
                    "Keep the rest of the body stable.",
                    "Focus on isolating the movement to the hip joint."
                ],
                "target_area_movement_pattern": "Hip Flexors (Psoas, Iliacus, Rectus Femoris), Hip capsule. Hip flexion, extension, rotation.",
                "purpose_in_system": "Enhances hip mobility and active control, crucial for sprinting, jumping, and overall lower body athleticism. Addresses tightness that can contribute to lower back pain."
            },
            {
                "name": "Friction Training (e.g., Backward Sled Pull)",
                "description": "Resistance training involving backward movement, often using a sled or similar friction device, for low-impact strengthening.",
                "benefits": [
                    "Strengthens quadriceps and feet with minimal impact on joints.",
                    "Increases blood flow to the knees, aiding recovery and health.",
                    "Builds powerful deceleration capacity.",
                    "Excellent for individuals with knee pain or for active recovery."
                ],
                "progressions_regressions": {
                    "regressions": ["Lighter load", "Shorter distance", "Slower pace"],
                    "progressions": ["Heavier load", "Longer distance", "Faster pace", "Incorporating hills"]
                },
                "key_cues": [
                    "Maintain an upright posture.",
                    "Drive through the balls of the feet.",
                    "Focus on pushing the ground away.",
                    "Keep knees relatively high (stepping action).",
                    "Breathe consistently."
                ],
                "target_area_movement_pattern": "Quadriceps, Calves, Tibialis Anterior, Feet, Glutes (secondary). Backward locomotion, low-impact strength.",
                "purpose_in_system": "Foundational 'bulletproofing' exercise, especially for knee health. Builds strength and resilience in a pain-free manner, serving as a crucial entry point for many with knee issues and a staple for ongoing joint health."
            }
        ]
    },
    "everydamnandre": {
        "name": "Andre Crews (Everydamnandré)",
        "focus": "Kettlebell mastery, metabolic conditioning, mental toughness, functional strength, efficient training",
        "core_philosophy": "Fitness is about 'getting it done' consistently, regardless of circumstances. The kettlebell is the most versatile tool for building comprehensive physical and mental resilience. Training should be efficient, high-impact, and cultivate grit to translate to all aspects of life.",
        "key_principles": [
            "Just get it done: Emphasizes consistent effort over perfect conditions.",
            "No excuses: Cultivate mental fortitude to overcome internal and external barriers.",
            "Kettlebell mastery: Prioritize proficiency in fundamental kettlebell movements for safety and efficacy.",
            "Metabolic conditioning: Maximize cardiovascular and muscular endurance through high-density workouts (e.g., EMOMs, AMRAPs, Circuits).",
            "Simplicity & Efficiency: Achieve significant results with minimal equipment and time investment.",
            "Progressive Overload: Systematically increase training stress (weight, reps, sets, density, complexity) for continuous adaptation.",
            "Functional Strength: Focus on strength that directly translates to real-world activities.",
            "Mental Fortitude: Deliberately push through discomfort to build psychological resilience.",
            "Train for life: Develop unshakeable physical and mental resilience for lifelong capacity."
        ],
        "motivational_style": "Direct, demanding, empowering, pragmatic, inspiring grit and a 'no-excuses' mindset. Focuses on the mental side of training as much as the physical.",
        "typical_session_flow": [
            "1. Dynamic Warm-up: Prepare the body for high-intensity work.",
            "2. Main Conditioning Block: Often an EMOM, AMRAP, or circuit focusing on compound kettlebell movements.",
            "3. Brief Cool-down: Basic stretching or light movement for recovery."
        ],
        "exercise_library": [
            {
                "name": "Kettlebell Swing (Russian)",
                "description": "A powerful, ballistic hip-hinge movement where the kettlebell swings to chest height. Focuses on hip drive.",
                "benefits": [
                    "Develops explosive power in the glutes and hamstrings (posterior chain).",
                    "Enhances cardiovascular endurance.",
                    "Improves grip strength and core stability."
                ],
                "progressions_regressions": {
                    "regressions": ["Two-hand swing with lighter bell", "Reduced range of motion", "Focus on hinge mechanics without explosion"],
                    "progressions": ["One-hand swing", "Heavier kettlebell", "Higher repetitions/sets", "Reduced rest intervals"]
                },
                "key_cues": [
                    "Hinge, not squat (push hips back, slight knee bend).",
                    "Snap the hips (explosive hip extension).",
                    "Pack the shoulders (keep shoulders down and back).",
                    "Bell floats to chest height, not pulled with arms."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Erector Spinae, Core, Lats. Hip Hinge, Ballistic Power.",
                "purpose_in_system": "Foundational power exercise for posterior chain development and metabolic conditioning."
            },
            {
                "name": "Kettlebell Swing (American)",
                "description": "A ballistic hip-hinge movement similar to the Russian swing, but the kettlebell travels overhead.",
                "benefits": [
                    "Develops power endurance and full-body conditioning.",
                    "Enhances shoulder stability and overhead mobility.",
                    "Builds mental toughness through sustained effort."
                ],
                "progressions_regressions": {
                    "regressions": ["Russian swing", "Lighter kettlebell", "Reduced overhead height"],
                    "progressions": ["Heavier kettlebell", "Increased reps/sets", "One-hand American swing", "Incorporating into AMRAPs/EMOMs"]
                },
                "key_cues": [
                    "Hinge, snap, punch overhead (controlled overhead extension).",
                    "Keep arms long (don't pull with shoulders).",
                    "Full lockout at the top (hips, knees, shoulders in line)."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Core, Shoulders, Traps. Hip Hinge, Overhead Extension, Ballistic Power.",
                "purpose_in_system": "High-intensity conditioning, full-body power endurance, and shoulder stability development."
            },
            {
                "name": "Goblet Squat",
                "description": "A fundamental squat variation holding a kettlebell against the chest, emphasizing proper squat mechanics and core stability.",
                "benefits": [
                    "Develops foundational lower body strength (quads, glutes).",
                    "Improves core stability and upper back engagement.",
                    "Enhances squat depth and mobility."
                ],
                "progressions_regressions": {
                    "regressions": ["Bodyweight squat", "Squatting to a box/bench", "Lighter kettlebell"],
                    "progressions": ["Heavier kettlebell", "Increased depth", "Tempo squats", "Moving to double kettlebell front squat"]
                },
                "key_cues": [
                    "Knees out (drive knees over toes).",
                    "Chest up (maintain upright torso).",
                    "Elbows inside knees (at the bottom of the squat).",
                    "Deep squat (hips below knees)."
                ],
                "target_area_movement_pattern": "Quadriceps, Glutes, Hamstrings, Core, Upper Back. Squat Pattern.",
                "purpose_in_system": "Builds fundamental squat mechanics, lower body strength, and core stability, serving as a base for other movements."
            },
            {
                "name": "Kettlebell Clean & Press",
                "description": "A complex two-part movement: cleaning the kettlebell to the rack position (chest/shoulder) and then pressing it overhead.",
                "benefits": [
                    "Develops full-body power and coordination.",
                    "Builds shoulder and upper body strength (pushing).",
                    "Enhances core stability and grip strength.",
                    "Metabolic conditioning when performed in circuits."
                ],
                "progressions_regressions": {
                    "regressions": ["Separate clean and press", "Lighter kettlebell", "Two-hand clean"],
                    "progressions": ["Heavier kettlebell", "Increased reps/sets", "Longer complexes", "Double kettlebell clean & press"]
                },
                "key_cues": [
                    "Explosive hip drive (for the clean).",
                    "Absorb the bell softly (catch in the rack position).",
                    "Vertical forearm (in rack and overhead).",
                    "Breathe behind the shield (core bracing for the press)."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Core, Lats, Biceps, Shoulders, Triceps. Hinge/Squat, Pull, Rack, Press.",
                "purpose_in_system": "Develops explosive power, integrated strength (pulling and pushing), and shoulder stability."
            },
            {
                "name": "Kettlebell Snatch",
                "description": "A ballistic movement that transitions the kettlebell from the floor or hang to an overhead lockout in one fluid motion.",
                "benefits": [
                    "Develops explosive full-body power and endurance.",
                    "High-intensity conditioning.",
                    "Enhances shoulder endurance and grip strength.",
                    "Improves coordination and timing."
                ],
                "progressions_regressions": {
                    "regressions": ["Clean & Press", "Lighter kettlebell", "Reduced reps", "High pull to overhead press"],
                    "progressions": ["Heavier kettlebell", "Increased reps/sets/duration", "Snatch ladders/complexes"]
                },
                "key_cues": [
                    "Fast hands (quick transition through the handle).",
                    "Punch through the bell (strong lockout overhead).",
                    "Smooth lockout (no slamming bell overhead).",
                    "Don't let the bell flop (control descent)."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Core, Shoulders, Lats, Traps. Hip Hinge, Ballistic, Overhead Lockout.",
                "purpose_in_system": "Peak power development, high-intensity conditioning, and shoulder endurance."
            },
            {
                "name": "Turkish Get-Up",
                "description": "A complex, multi-planar movement that transitions from lying on your back to standing, holding a kettlebell overhead.",
                "benefits": [
                    "Develops full-body stability and core strength (especially obliques).",
                    "Enhances shoulder health and mobility.",
                    "Improves coordination, balance, and proprioception.",
                    "Builds mental focus and discipline."
                ],
                "progressions_regressions": {
                    "regressions": ["No weight/shoe on fist", "Segmented practice of each step", "Lighter kettlebell"],
                    "progressions": ["Heavier kettlebell", "Increased fluidity and speed (while maintaining control)", "Using double kettlebells"]
                },
                "key_cues": [
                    "Eyes on the bell (maintain gaze on kettlebell overhead).",
                    "Slow and controlled (segmental movement).",
                    "Maintain tension (throughout the body).",
                    "Each step is a strong position."
                ],
                "target_area_movement_pattern": "Core (obliques), Shoulders, Hips, Glutes, Quads. Multi-planar Stability, Unilateral Strength, Coordination.",
                "purpose_in_system": "Enhances full-body stability, core strength, shoulder health, and motor control."
            },
            {
                "name": "Farmer's Carry",
                "description": "Walking with heavy kettlebells (or dumbbells) in each hand.",
                "benefits": [
                    "Significantly improves grip strength and forearm endurance.",
                    "Enhances core stability and postural endurance.",
                    "Builds full-body functional strength and resilience."
                ],
                "progressions_regressions": {
                    "regressions": ["Lighter kettlebells", "Shorter distances/durations", "One-arm carry"],
                    "progressions": ["Heavier kettlebells", "Longer distances/durations", "Walk uphill", "Uneven carries (different weights in each hand)"]
                },
                "key_cues": [
                    "Tall posture (stand upright).",
                    "Shoulders packed down (avoid shrugging).",
                    "Brace the core (maintain rigidity).",
                    "Walk with purpose (controlled steps)."
                ],
                "target_area_movement_pattern": "Grip, Forearms, Traps, Core, Glutes, Quads. Static Hold, Locomotion.",
                "purpose_in_system": "Builds foundational grip strength, core stability, and overall physical robustness for daily life and lifting."
            },
            {
                "name": "Kettlebell Thruster",
                "description": "A compound movement combining a Goblet Squat with an overhead press, performed in a fluid motion.",
                "benefits": [
                    "Excellent for metabolic conditioning and cardiovascular endurance.",
                    "Develops full-body power and muscular endurance.",
                    "Engages legs, core, and shoulders in one movement."
                ],
                "progressions_regressions": {
                    "regressions": ["Separate Goblet Squat and Overhead Press", "Lighter kettlebell", "Reduced depth in squat"],
                    "progressions": ["Heavier kettlebell", "Increased reps/sets", "Faster tempo (while maintaining form)", "Double kettlebell thruster"]
                },
                "key_cues": [
                    "Fluid movement (squat to press seamlessly).",
                    "Use the legs to drive the press (generate momentum from the lower body).",
                    "Full squat depth.",
                    "Overhead lockout."
                ],
                "target_area_movement_pattern": "Quadriceps, Glutes, Hamstrings, Shoulders, Triceps, Core. Squat, Overhead Press.",
                "purpose_in_system": "High-intensity full-body conditioning, improving muscular endurance and power output."
            },
            {
                "name": "Kettlebell Renegade Row",
                "description": "Performed from a plank position with hands on kettlebells, alternately rowing one kettlebell up to the side of the chest.",
                "benefits": [
                    "Significantly improves core stability and anti-rotation strength.",
                    "Builds upper body pulling strength (lats, biceps).",
                    "Enhances shoulder stability in a challenging position."
                ],
                "progressions_regressions": {
                    "regressions": ["Perform from knees", "Use lighter kettlebells", "Reduce range of motion"],
                    "progressions": ["Heavier kettlebells", "Increased reps/sets", "Slower tempo for more control", "Holding the top position briefly"]
                },
                "key_cues": [
                    "Maintain plank rigidity (keep body straight).",
                    "Square hips (avoid rotating hips).",
                    "Pull elbow to ceiling (drive with the back muscles).",
                    "Control the descent."
                ],
                "target_area_movement_pattern": "Core, Lats, Biceps, Shoulders, Triceps. Plank, Unilateral Pull.",
                "purpose_in_system": "Develops core stability, upper body pulling strength, and anti-rotational control."
            },
            {
                "name": "Kettlebell Windmill",
                "description": "A complex movement involving a hip hinge and spinal rotation, often with a kettlebell pressed overhead, to improve oblique strength, shoulder stability, and hamstring flexibility.",
                "benefits": [
                    "Develops oblique strength and rotational core stability.",
                    "Enhances shoulder stability and control, especially overhead.",
                    "Improves hip mobility and hamstring flexibility.",
                    "Great for body awareness and coordination."
                ],
                "progressions_regressions": {
                    "regressions": ["No weight", "Shoe on fist overhead", "Lighter kettlebell", "Reduced depth of hinge"],
                    "progressions": ["Heavier kettlebell", "Increased depth (hand to floor)", "Slower tempo for more control", "Holding the bottom position"]
                },
                "key_cues": [
                    "Keep eyes on the bell (overhead hand).",
                    "Straight leg, hinge at hip (rotate and push hips out).",
                    "Control the rotation (avoid collapsing).",
                    "Stack joints (shoulder, wrist)."
                ],
                "target_area_movement_pattern": "Obliques, Hamstrings, Glutes, Shoulders, Core. Hip Hinge, Rotational Stability, Overhead Stability.",
                "purpose_in_system": "Advanced exercise for oblique strength, shoulder stability, and integrated hip/hamstring mobility."
            }
        ],
        "conditioning_templates": [
            {
                "type": "EMOM (Every Minute On the Minute)",
                "description": "Perform a set number of repetitions at the top of each minute, with the remaining time in the minute serving as rest. Builds density and manages work-to-rest ratios effectively.",
                "parameters": "Duration (e.g., 10-20 minutes), Exercises (e.g., 1-2 per minute), Reps per minute (e.g., 5-10)",
                "primary_stimulus": "Work capacity, Metabolic conditioning, Pacing, Density training",
                "example_structure": "Minute 1: 10 Kettlebell Swings; Minute 2: 5 Kettlebell Goblet Squats"
            },
            {
                "type": "AMRAP (As Many Rounds/Reps As Possible)",
                "description": "Complete as many rounds or repetitions of a given circuit as possible within a set time limit. Pushes intensity and mental fortitude.",
                "parameters": "Duration (e.g., 5-15 minutes), Exercises per round (e.g., 2-4), Reps per exercise",
                "primary_stimulus": "Muscular endurance, Cardiovascular endurance, Mental fortitude, Pushing limits",
                "example_structure": "1 Round: 10 Kettlebell Swings, 5 Kettlebell Cleans, 5 Kettlebell Presses (complete as many rounds as possible in 10 minutes)"
            },
            {
                "type": "Fixed Rounds/Reps Circuit",
                "description": "Multiple exercises are performed sequentially with minimal rest between them, followed by a longer rest period before repeating the circuit.",
                "parameters": "Number of Rounds (e.g., 3-5), Exercises per round, Reps per exercise, Rest between rounds (e.g., 60-90 seconds)",
                "primary_stimulus": "Strength endurance, General physical preparedness, Structured progression",
                "example_structure": "3 Rounds: 15 Kettlebell Swings, 10 Goblet Squats, 5 Kettlebell Cleans (rest 60 seconds between rounds)"
            },
            {
                "type": "Ladders (Ascending/Descending Reps)",
                "description": "Progressively increase or decrease repetitions across sets for a given exercise or mini-complex.",
                "parameters": "Number of sets, Rep scheme (e.g., 1-2-3-4-5), Exercises (1 or 2)",
                "primary_stimulus": "Strength, Power, Work capacity, Progressive intensity",
                "example_structure": "Kettlebell Clean & Press Ladder: 1 rep, then 2, then 3, then 4, then 5 (rest as needed between sets)"
            },
            {
                "type": "Simple & Sinister Style",
                "description": "A foundational program by Pavel Tsatsouline often used by Everydamnandré, focusing on mastery of Kettlebell Swings and Turkish Get-Ups.",
                "parameters": "100 Swings, 10 Turkish Get-Ups (5 per side)",
                "primary_stimulus": "Foundational strength, Power, Stability, Skill development, Consistent practice",
                "example_structure": "10 sets of 10 Swings (Russian), 10 sets of 1 Turkish Get-Up (5/side). Focus on quality, ample rest between sets."
            }
        ]
    },
    "emmet_louis": {
        "name": "Emmet Louis",
        "focus": "Mobility, active flexibility, strength at end ranges, neurological control, handbalancing",
        "core_philosophy": "A systematic approach to flexibility and strength that emphasizes neurological control and building strength at end ranges of motion to gain functional and lasting mobility. Distinguishes between passive, active, and dynamic flexibility, prioritizing active control. Aims to demystify complex information and make it actionable.",
        "key_principles": [
            "Think in timeframes of 18 months and you'll never be disappointed: Emphasizes patience and long-term consistency for lasting results.",
            "You can only own what you can control: True mobility is active, neurological command over your range of motion.",
            "Strength at end ranges: Crucial for safety, functionality, and retaining increased flexibility.",
            "Minimal Effective Dose: Efficiency in training; do what's needed, no more.",
            "If flexibility isn't used it won't be maintained: Active engagement is ongoing.",
            "Always be active in our flexibility and it shouldn't be passive: Prioritize muscular engagement during stretching.",
            "Gravity: Understand its influence (assistive, neutral, resistive) on ROM.",
            "Tasking: Developmental work occurs within discipline application; task-based exercises.",
            "Seeds: Progress from foundational movements to advanced skills.",
            "Velocity: Use speed as a stimulus for dynamic flexibility.",
            "Layering: Combine methods for synergistic and efficient results.",
            "Simple: Nervous system hides complexity under simple interfaces; keep instructions clear.",
            "Time: Consistent, long-term training for near-permanent results."
        ],
        "motivational_style": "Pragmatic, scientific, demystifying, focused on long-term results and functional application, emphasizes neurological understanding.",
        "typical_session_flow": [
            "1. Assessment of current range (often includes passive testing to identify potential).",
            "2. Targeted warm-up/joint preparation for specific areas to be worked.",
            "3. Active flexibility drills, often incorporating PAILs/RAILs and PNF for neurological engagement and end-range strength.",
            "4. Loaded stretching or strength work at newly acquired end ranges.",
            "5. Integration of new ranges into functional movements or skill-specific tasks.",
            "6. Cool-down or complementary mobility."
        ],
        "exercise_library": [
            {
                "name": "Pancake Stretch (with PAILs/RAILs)",
                "description": "A seated stretch with legs spread wide, focusing on hip flexion and hamstring/adductor extensibility. Enhanced with isometric contractions.",
                "benefits": [
                    "Significantly improves hip flexion and external rotation flexibility.",
                    "Strengthens hamstrings and adductors at lengthened ranges.",
                    "Prerequisite for skills like press to handstand."
                ],
                "progressions_regressions": {
                    "regressions": ["Passive pancake holds (gravity assisted)", "Elevated hips/seated on block", "Wider leg angle"],
                    "progressions": ["Deeper active pulls (RAILs)", "Increased external load (e.g., holding kettlebell)", "Longer PAILs/RAILs holds", "Reduced reliance on external load (active control)"]
                },
                "key_cues": [
                    "Hinge from the hips, maintaining a flat back.",
                    "Actively engage quads to press knees down (extend legs).",
                    "For PAILs: Push heels/legs into floor (5-10s, 25-50% effort).",
                    "For RAILs: Actively pull torso deeper with hip flexors/core (5-10s).",
                    "Breathe deeply and relax into the stretch after contractions."
                ],
                "target_area_movement_pattern": "Hips (flexion, external rotation), Hamstrings, Adductors. Deep hip flexion flexibility.",
                "purpose_in_system": "Core flexibility exercise for hip opening and hamstring length, building active control and end-range strength crucial for various advanced skills. Often used as a benchmark for lower body mobility."
            },
            {
                "name": "Jefferson Curl",
                "description": "A rounded spine forward fold designed to progressively lengthen the hamstrings and strengthen the spine in flexion.",
                "benefits": [
                    "Increases hamstring flexibility (especially at the mid-range and end-range).",
                    "Improves spinal articulation and controlled spinal flexion mobility.",
                    "Builds strength in the back muscles at lengthened positions."
                ],
                "progressions_regressions": {
                    "regressions": ["Unweighted/Bodyweight Jefferson Curl", "Reduced range of motion", "Bent knees"],
                    "progressions": ["Gradually increasing external weight (e.g., dumbbell)", "Increasing height of platform (to go deeper)", "Slower tempo, longer holds at bottom (PNF)"]
                },
                "key_cues": [
                    "Start by tucking the chin to the chest.",
                    "Slowly roll down, one vertebra at a time, allowing the spine to round.",
                    "Keep legs relatively straight but allow a micro-bend in knees if needed.",
                    "Focus on reaching towards the floor, not just hinging.",
                    "Control the eccentric phase and the return."
                ],
                "target_area_movement_pattern": "Hamstrings, Spinal Erectors, Glutes. Spinal flexion and hamstring extensibility.",
                "purpose_in_system": "A key exercise for developing posterior chain flexibility and spinal mobility, particularly emphasizing controlled, loaded spinal flexion."
            },
            {
                "name": "Cossack Squat",
                "description": "A deep side-lunge movement that challenges hip adductor and hamstring flexibility and strength at end range.",
                "benefits": [
                    "Improves adductor and hamstring flexibility.",
                    "Develops strength and control in the inner thigh and groin at lengthened positions.",
                    "Enhances hip mobility and unilateral leg strength."
                ],
                "progressions_regressions": {
                    "regressions": ["Holding onto support", "Reduced depth", "Elevating heel of squatting leg"],
                    "progressions": ["Increased depth (hip to heel)", "Adding external weight (e.g., kettlebell goblet style)", "Slowing tempo", "Controlling the straight leg actively", "Moving to floor for a full middle split progression"]
                },
                "key_cues": [
                    "Keep the heel of the squatting leg on the ground.",
                    "Straight leg remains straight, foot ideally flexed.",
                    "Squat down as deep as possible with control.",
                    "Actively push the knee out on the bent leg.",
                    "Maintain a relatively upright torso."
                ],
                "target_area_movement_pattern": "Adductors, Hamstrings, Glutes, Quadriceps. Hip abduction/adduction, unilateral squat.",
                "purpose_in_system": "Functional mobility exercise that builds active end-range strength and flexibility in the adductors and hamstrings, crucial for lower body movement fluidity."
            },
            {
                "name": "Shoulder External Rotation (Loaded/Active)",
                "description": "Drills focused on improving the range of motion and strength in external rotation of the shoulder joint.",
                "benefits": [
                    "Increases active shoulder external rotation range.",
                    "Strengthens rotator cuff muscles and scapular stabilizers.",
                    "Improves overhead mobility and pressing stability.",
                    "Reduces risk of shoulder impingement."
                ],
                "progressions_regressions": {
                    "regressions": ["Bodyweight-only external rotations", "Reduced range of motion", "Assisted movements"],
                    "progressions": ["Adding light external load (e.g., small dumbbell, band)", "PAILs/RAILs application", "Increasing time under tension at end range", "Integrating into overhead pressing or handbalancing warm-ups"]
                },
                "key_cues": [
                    "Isolate movement to the shoulder joint, avoid compensation from torso.",
                    "Maintain a stable scapula.",
                    "Actively pull into the external rotation.",
                    "Control the eccentric phase."
                ],
                "target_area_movement_pattern": "Rotator Cuff (infraspinatus, teres minor), Deltoids, Scapular Stabilizers. Shoulder external rotation flexibility and strength.",
                "purpose_in_system": "Crucial for healthy shoulder mechanics, especially for overhead movements, pressing, and handbalancing. Builds active control at end range to protect the joint."
            },
            {
                "name": "Spinal Segmentation Drills (e.g., Cat-Cow variations)",
                "description": "Exercises focusing on articulating individual vertebrae of the spine, promoting isolated movement and control.",
                "benefits": [
                    "Improves spinal mobility and flexibility (flexion and extension).",
                    "Enhances body awareness and neuromuscular control of the spine.",
                    "Can alleviate stiffness and improve posture."
                ],
                "progressions_regressions": {
                    "regressions": ["Smaller range of motion", "Focusing on only one segment (e.g., thoracic)", "Performed lying down"],
                    "progressions": ["Increased range of motion and isolation", "Slower tempo for more control", "Integrating into more complex movements (e.g., wave movements, flowing sequences)"]
                },
                "key_cues": [
                    "Initiate movement from the tailbone/pelvis.",
                    "Move one vertebra at a time, like a ripple.",
                    "Avoid global movement; focus on isolation.",
                    "Breathe with the movement, exhaling on flexion, inhaling on extension."
                ],
                "target_area_movement_pattern": "Spine (thoracic, lumbar, cervical), Core. Spinal articulation, flexion, and extension.",
                "purpose_in_system": "Develops precise control and mobility throughout the entire spine, supporting overall movement quality, injury resilience, and preparation for complex skills like handstands and bridging."
            }
        ]
    },
    "dr_andy_galpin": {
        "name": "Dr. Andy Galpin",
        "focus": "Science-Based Performance Optimization",
        "core_philosophy": "Use science to optimize performance, recovery, and nutrition.",
        "key_principles": ["Science-Based", "Performance Optimization", "Recovery Focus"],
        "training_methods": ["Evidence-Based Training", "Recovery Protocols", "Nutrition Science"],
        "motivational_style": "Educational, science-focused, emphasizes evidence-based approach"
    },
    "tom_merrick": {
        "name": "Tom Merrick",
        "focus": "Calisthenics, flexibility, functional strength, movement longevity, bodyweight mastery",
        "core_philosophy": "A holistic approach to physical development, emphasizing the symbiotic relationship between strength and skill through bodyweight training. Prioritizes 'physical freedom' and 'movement longevity' over aesthetics, achieved through mastering basics, consistency, clean form, and a 'Warrior' mindset.",
        "key_principles": [
            "Knowing Is Nice but Doing Is Better: Prioritize practical application and consistent effort.",
            "You Are What You Do, Not What You Say You'll Do: True progress comes from disciplined, consistent action.",
            "Mastering the Basics: Develop foundational strength and perfect fundamental exercises before advancing.",
            "Consistency over Intensity: Regular engagement and compounding small improvements lead to long-term progress.",
            "Listening to Your Body: Adjust intensity and prioritize recovery based on physical state.",
            "Clean Form First: Non-negotiable for maximizing physiological stimulus, skill acquisition, and injury prevention.",
            "The 'Warrior' Archetype: Cultivate aggression, purpose, mindfulness, and discipline for training success."
        ],
        "motivational_style": "Action-oriented, disciplined, philosophical (uses concepts like 'Warrior' archetype), emphasizes consistent effort and self-mastery.",
        "typical_session_flow": [
            "1. Structured Warm-up: Joint preparation, light movement (e.g., wrist and shoulder warm-ups).",
            "2. Skill Work: Performed at the beginning of the session when fresh (e.g., Handstand, Front Lever progressions).",
            "3. Main Strength Work: Compound bodyweight exercises, often incorporating tempo manipulation and RIR (e.g., Push-up variations, Dips, Pull-up variations).",
            "4. Additional Mobility/Flexibility: Dedicated flexibility routines (e.g., Pancake, Bridge) or targeted joint health work.",
            "5. Cool-down: Gentle movements, stretching.",
            "6. Daily Mobility 'Movement Snacks': Short (10-20 min) very light, recovery-focused sessions throughout the week."
        ],
        "exercise_library": [
            {
                "name": "Push-up Variations",
                "description": "A foundational bodyweight exercise for upper body pushing strength, scaled from beginner to advanced levels. Emphasizes clean form and control.",
                "benefits": [
                    "Develops upper body pushing strength, hypertrophy in chest, triceps, and shoulders.",
                    "Builds foundational pushing strength for more complex movements."
                ],
                "progressions_regressions": {
                    "regressions": ["Incline Push-ups", "Kneeling Push-ups"],
                    "progressions": ["Pseudo Planche Push-ups", "Archer Push-ups", "One-Arm Push-ups", "Handstand Push-ups"]
                },
                "key_cues": [
                    "Twist hands into the ground (for ring push-ups) to enhance stability.",
                    "Maintain clean form through full range of motion."
                ],
                "target_area_movement_pattern": "Chest, Triceps, Shoulders. Horizontal pushing pattern.",
                "purpose_in_system": "Foundational push exercise; builds base strength and prepares for advanced straight-arm pressing skills."
            },
            {
                "name": "Dips",
                "description": "A critical bodyweight exercise for developing pushing strength, lockout strength, and stability, particularly in the triceps and shoulders.",
                "benefits": [
                    "Enhances upper body pushing strength, especially in triceps, shoulders, and chest.",
                    "Improves scapula and shoulder stability.",
                    "Builds lockout strength."
                ],
                "progressions_regressions": {
                    "regressions": ["Band-Assisted Dips", "Eccentric Dips (weighted/unweighted)", "One-Leg Supported Dips"],
                    "progressions": ["Weighted Dips", "Russian Dips"]
                },
                "key_cues": [
                    "Slow, controlled eccentric phase.",
                    "Shoulders remain nicely fixed locked into their joints.",
                    "Go only as deep as comfortable with good form."
                ],
                "target_area_movement_pattern": "Triceps, Shoulders, Chest, Lower Traps. Vertical pushing pattern.",
                "purpose_in_system": "Foundational pushing exercise, vital for overall upper body strength development and pre-requisite for many advanced skills."
            },
            {
                "name": "Pull-up Variations",
                "description": "Fundamental vertical pulling patterns to build strength and mass in the back and biceps, with variations for different skill levels.",
                "benefits": [
                    "Develops upper body pulling strength, back and biceps hypertrophy.",
                    "Essential for overall upper body strength and skill progression."
                ],
                "progressions_regressions": {
                    "regressions": ["Inverted Rows (horizontal pull)", "Band-Assisted Pull-ups", "Pull-up Negatives"],
                    "progressions": ["Weighted Pull-ups/Chin-ups", "One-Arm Pull-up/Chin-up"]
                },
                "key_cues": [
                    "Clean, controlled movement through the full range of motion.",
                    "(Implicit: focus on back and bicep engagement)."
                ],
                "target_area_movement_pattern": "Back (Lats, Rhomboids), Biceps, Upper Back. Vertical pulling pattern.",
                "purpose_in_system": "Foundational pull exercise; essential for upper body strength and skill progression, leading to advanced skills like the Front Lever."
            },
            {
                "name": "Front Lever",
                "description": "An advanced static hold requiring significant straight-arm strength, upper back strength, and core tension. Demands patience and precise technique.",
                "benefits": [
                    "Develops significant straight arm strength and upper back strength.",
                    "Enhances core tension and full-body rigidity."
                ],
                "progressions_regressions": {
                    "regressions": ["Tuck Front Lever", "Lever Pull Negatives", "Arc Rows", "Straight Arm Band Pull Downs", "Angled Holds (3-5s)", "Tempo Descends (5-10s) from Inverted Hang"],
                    "progressions": ["Straddle Front Lever", "One-Leg Front Lever", "Half Lay Front Lever", "Full Front Lever"]
                },
                "key_cues": [
                    "Squeeze bar tight; arms straight.",
                    "Short, shallow breaths.",
                    "Actively pull down with lats.",
                    "Tense core/thighs; push feet away to maintain horizontal bodyline.",
                    "Develop strong mind-muscle connection with upper back, arms, and core."
                ],
                "target_area_movement_pattern": "Upper Back (rhomboids, traps), Lats, Arms (Biceps, Triceps), Core, Thighs. Static straight arm pulling skill.",
                "purpose_in_system": "Advanced straight arm strength skill; one of the 'big 4' skills in Merrick's advanced programs, demonstrating high levels of body control."
            },
            {
                "name": "L-sit",
                "description": "A foundational exercise for developing core compression and straight arm strength, where the body is held in an 'L' shape off the ground.",
                "benefits": [
                    "Develops core compression and strength.",
                    "Builds straight arm strength in shoulders and triceps.",
                    "Strengthens hip flexors."
                ],
                "progressions_regressions": {
                    "regressions": ["Tuck L-sit (knees to chest)", "Low L-sit (below horizontal)", "Single-Leg L-sit"],
                    "progressions": ["Straddle L-sit", "Full L-sit (legs straight & horizontal)", "Raising Legs Higher"]
                },
                "key_cues": [
                    "Keep arms straight.",
                    "Tuck knees to chest for tuck L-sit.",
                    "Lean back slightly for balance.",
                    "Maintain a tight grip.",
                    "Shrug elbow pits.",
                    "Point toes."
                ],
                "target_area_movement_pattern": "Core (abdominal muscles), Hip Flexors, Shoulders, Triceps. Static compression and straight arm hold.",
                "purpose_in_system": "Foundational core compression & straight arm strength skill, useful for advancing to skills like the planche and handstands."
            },
            {
                "name": "Pancake Stretch",
                "description": "A deep seated hamstring and hip flexibility stretch, vital for improving external hip rotation and hamstring length.",
                "benefits": [
                    "Significantly improves hamstring and hip flexibility.",
                    "Enhances external hip rotation.",
                    "Prerequisite for advanced skills (e.g., press to handstand, planche)."
                ],
                "progressions_regressions": {
                    "regressions": ["Static holds (30-120s) with less depth", "Using support (e.g., blocks under hands)"],
                    "progressions": ["Contract-Relax/PNF technique (5-10s contraction, 5-10s relaxation)", "Weighted Pancake (e.g., 10 reps with 10s hold on last rep)", "Increasing depth/range"]
                },
                "key_cues": [
                    "Breathe deeply.",
                    "Push heels down (for PNF).",
                    "Soften/melt into the floor.",
                    "Keep hips connected to the surface.",
                    "Actively use own strength to get more flexible (engage quadriceps and hip flexors)."
                ],
                "target_area_movement_pattern": "Hips (adductors, external rotators), Hamstrings. Hip flexion and external rotation flexibility.",
                "purpose_in_system": "Key flexibility position; crucial for advanced skills requiring hip mobility and part of Merrick's 'Big 5 Flexibility' routines."
            },
            {
                "name": "Bridge (Wheel Pose)",
                "description": "A movement to develop shoulder and spine flexibility, focusing on a deep backbend.",
                "benefits": [
                    "Improves shoulder and spinal flexibility.",
                    "Strengthens glutes and hamstrings."
                ],
                "progressions_regressions": {
                    "regressions": ["Easier variations with shorter range of motion or less arch", "Supported bridge"],
                    "progressions": ["Full Bridge (Wheel Pose)", "Progressively deeper arch", "Straightening arms/legs"]
                },
                "key_cues": [
                    "Butt tight, belly tight (to protect lower back).",
                    "Exaggerate shoulder positioning.",
                    "Push shoulder into ground.",
                    "Open chest.",
                    "Breathe."
                ],
                "target_area_movement_pattern": "Shoulders, Spine (thoracic extension), Glutes, Hamstrings. Spinal extension and shoulder flexion flexibility.",
                "purpose_in_system": "Key flexibility position; part of Merrick's 'Big 5 Flexibility' routines, essential for overall spinal and shoulder health."
            },
            {
                "name": "Wrist Warm-ups",
                "description": "A series of exercises designed to strengthen wrists, prevent injury, and enhance range of motion, crucial for handstands and other calisthenics.",
                "benefits": [
                    "Increases wrist strength and endurance.",
                    "Reduces risk of wrist injuries.",
                    "Enhances wrist range of motion and overall joint health."
                ],
                "progressions_regressions": {
                    "regressions": ["Fewer repetitions, less aggressive range of motion", "Reduced weight bearing"],
                    "progressions": ["Increased repetitions/sets", "Adding light external load", "More challenging angles/positions"]
                },
                "key_cues": [
                    "Keep a nice firm wrist.",
                    "Roll onto thumb (for wrist roller deviation).",
                    "Emphasize length around the wrist joint."
                ],
                "target_area_movement_pattern": "Wrists, Forearms. Wrist flexion, extension, ulnar/radial deviation, and rotation.",
                "purpose_in_system": "Essential warm-up and strengthening for handstands and any upper body calisthenics involving weight bearing on hands. Proactive injury prevention."
            },
            {
                "name": "Shoulder Warm-ups",
                "description": "Routines designed to improve shoulder mobility, stability, and range of motion, essential for all upper body and hand balancing movements.",
                "benefits": [
                    "Opens shoulders and improves flexibility.",
                    "Enhances shoulder stability and control.",
                    "Increases range of motion for overhead movements and handstands."
                ],
                "progressions_regressions": {
                    "regressions": ["Shorter holds, less active engagement", "Using lighter resistance or bodyweight only"],
                    "progressions": ["Loaded Shoulder Stretches (adjusting hand width, adding contractions)", "Squatting down to increase load", "Progressing to full hang"]
                },
                "key_cues": [
                    "Push shoulder into ground (for wall chest stretches).",
                    "Open chest.",
                    "Breathe deeply and consistently.",
                    "Reach hands backwards (retract shoulder blades) or pull hands down (contract bicep/pec) for loaded stretches."
                ],
                "target_area_movement_pattern": "Shoulders (deltoids, rotator cuff), Chest, Lats, Biceps. Shoulder flexion, extension, internal/external rotation, and scapular control.",
                "purpose_in_system": "Essential warm-up for any upper body work, especially hand balancing and handstand sessions. Crucial for full range of motion and injury prevention."
            },
            {
                "name": "Handstand (Basics & Progressions)",
                "description": "Developing the fundamental skill of balancing inverted on one's hands, progressing from wall-supported to freestanding holds and advanced shapes.",
                "benefits": [
                    "Develops significant shoulder strength and stability.",
                    "Improves balance, proprioception, and body awareness.",
                    "Strengthens wrists and forearms.",
                    "Builds mental focus and discipline."
                ],
                "progressions_regressions": {
                    "regressions": ["Frog Stand (forearm support, foundational balance)", "Elevated Pike Hold", "Wall Plank", "Handstand Kick-ups"],
                    "progressions": ["Solid Holds (30-60s) freestanding", "Exploring Shapes (Straddle, Diamond)", "Line Refinement", "Press to Handstand (Tuck, Straddle, Straight)", "One-Arm Handstand"]
                },
                "key_cues": [
                    "(Implicit: Hollow body, active shoulders, straight arms, stacked joints)",
                    "Maintain a strong, stable line.",
                    "Use fingers/wrists for balance adjustments."
                ],
                "target_area_movement_pattern": "Shoulders, Triceps, Core, Wrists, Forearms. Inverted static balance skill.",
                "purpose_in_system": "A key skill for advanced body control, integrating strength, balance, and precision. Central to many calisthenics progressions and a measure of bodyweight mastery."
            }
        ]
    },
    "squat_university": {
        "name": "Dr. Aaron Horschig (Squat University)",
        "focus": "Optimizing human movement within strength training, injury prevention, performance enhancement, refining squat mechanics, and improving mobility specifically for lifting activities.",
        "core_philosophy": (
            "Dr. Horschig's central thesis is 'Improve Technique. Decrease Pain. Increase Performance.' He bridges physical therapy and high-performance lifting, viewing pain as a signal of underlying biomechanical dysfunction rather than just a symptom. "
            "His approach is diagnostic, focusing on identifying root 'movement faults' and then systematically correcting them. "
            "He advocates for mastering fundamental bodyweight movement patterns before adding external load (the 'Adaptation Model' emphasizing safe load distribution). "
            "A foundational framework is the 'Joint-by-Joint' concept, which identifies alternating patterns of mobility and stability throughout the kinetic chain, explaining how dysfunction in one joint leads to compensatory movement and potential injury in adjacent joints. "
            "His ultimate goal is pain-free lifting, maximized strength potential, long-term athletic health, and proactive injury prevention through a 'Coaching > Training' and 'Proactivity over Reactivity' mindset."
        ),
        "key_principles": [
            "Biomechanical Root Cause Analysis: Identifies fundamental biomechanical dysfunctions causing pain/performance limitations, rather than just treating symptoms. Focus on segmental breakdown and force distribution.",
            "Systematic Movement Assessment & Diagnostic Drills: Employs specific tests (e.g., Overhead Squat Assessment, Ankle Dorsiflexion, Hip Rotation Tests, Load/Intolerance Tests) to pinpoint specific mobility restrictions, stability deficits, or motor control issues. Utilizes immediate 'test-retest' to confirm effectiveness.",
            "Targeted Corrective Exercise Prescription: Selects highly individualized exercises to resolve identified movement dysfunctions, improve mobility, alleviate pain, and correct muscle imbalances. Emphasizes quality of movement over quantity, and appropriate 'load capacity' for healing/strengthening.",
            "Motor Control & Proprioception Re-education: Focuses on retraining the nervous system for efficient, pain-free movement and enhancing the body's spatial awareness. Prioritizes 'training before strengthening' with high-quality repetitions and consistent practice.",
            "Core Stability & Bracing: Emphasizes true core stability (coordinated action of 29 pairs of trunk muscles) over isolated strength to maintain neutral spine and prevent excessive spinal motion."
        ],
        "motivational_style": "Analytical, instructional, and empowering. Guides individuals to understand their own bodies and take ownership of their movement quality. Encourages a 'proactive' and 'coaching' mindset over 'reactive' and 'quick-fix' approaches, aiming for sustainable strength and long-term athletic health.",
        "typical_session_flow": (
            "While not a strict 'workout flow' in the traditional sense, Dr. Horschig's process for intervention follows a diagnostic and prescriptive pathway: "
            "1. Symptom-Driven Assessment: Identify pain triggers and aggravating factors (e.g., flexion/extension intolerance). "
            "2. Diagnostic Drills: Perform specific movement tests (e.g., ankle dorsiflexion, hip rotation, overhead screen) to pinpoint underlying movement faults and 'weak links'. "
            "3. Corrective Exercise Prescription: Implement targeted drills to address identified mobility restrictions, stability deficits, or motor control issues. "
            "4. Test-Re-test: Immediately re-assess movement patterns/symptoms to confirm effectiveness of intervention. "
            "5. Modified Training/Pain-Free Replacement Movements: Integrate corrected mechanics into lifting, often starting with reduced load or alternative movements until original patterns are restored pain-free."
        ),
        "exercise_library": [
            {
                "name": "Supine Lat Stretch Screen",
                "type": "diagnostic_assessment",
                "description": "Lying on your back with knees to chest (to flatten lumbar spine), arms extended overhead with palms up. Assess ability to bring arms to floor.",
                "benefits": ["Assesses lat flexibility.", "Identifies restrictions in shoulder flexion and thoracic extension.", "Helps diagnose contributors to overhead mobility issues."],
                "progressions_regressions": {
                    "regressions": ["Perform with straighter legs if knees to chest is too restrictive.", "Focus on gentle breathing to encourage relaxation."],
                    "progressions": ["Actively press arms down to floor if possible (active stretch)."]
                },
                "key_cues": [
                    "Lie flat on your back, press lower back into floor (knees to chest helps).",
                    "Arms straight overhead, palms facing up.",
                    "Gently try to bring arms to the floor.",
                    "Observe if arms 'dangle' or touch the floor."
                ],
                "target_area_movement_pattern": "Lats, Shoulder Flexion, Thoracic Extension. Shoulder Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for lat tightness that can limit overhead mobility in lifts like snatch or overhead squat."
            },
            {
                "name": "Wall Angel Screen",
                "type": "diagnostic_assessment",
                "description": "Stand with back, head, and entire back against a wall. Arms in an 'L' shape (football goal post), elbows bent, forearms against wall. Slide arms up while maintaining contact.",
                "benefits": ["Assesses gross overhead mobility.", "Identifies restrictions in thoracic spine mobility and pectoral/shoulder tightness.", "Activates scapular stabilizers."],
                "progressions_regressions": {
                    "regressions": ["Feet further from wall to reduce lumbar arch compensation.", "Focus on lower back contact first, then arms."],
                    "progressions": ["Increase duration of hold at top.", "Add light resistance band around wrists to maintain elbow width."]
                },
                "key_cues": [
                    "Back, head, and entire back flat against the wall.",
                    "Feet 4-5 inches from wall.",
                    "Arms in an 'L' shape (90-degree bend at elbows).",
                    "Attempt to flatten back of arms and hands against the wall.",
                    "Slide arms up, maintaining contact, without moving head or lower back."
                ],
                "target_area_movement_pattern": "Thoracic Spine, Shoulders, Pecs, Scapular Stability. Overhead Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for limitations in overhead mobility relevant for pressing, snatching, and overhead squatting."
            },
            {
                "name": "Wall Ankle Mobility Test (Ankle Dorsiflexion Test)",
                "type": "diagnostic_assessment",
                "description": "Kneel with one foot 5 inches from a wall. Push knee directly over middle toe towards the wall while keeping the heel on the floor.",
                "benefits": ["Assesses ankle dorsiflexion flexibility.", "Identifies restrictions that can impact squat depth and knee health.", "Differentiates between joint and soft-tissue restrictions."],
                "progressions_regressions": {
                    "regressions": ["Start with foot closer to the wall (e.g., 3 inches).", "Gentle rocking motion."],
                    "progressions": ["Increase distance from wall (e.g., 6+ inches).", "Add light weight to knee."]
                },
                "key_cues": [
                    "One foot 5 inches (handprint + thumb) from the wall.",
                    "Keep heel firmly on the floor.",
                    "Push knee directly over the middle toe towards the wall.",
                    "Observe if knee touches wall without heel lifting."
                ],
                "target_area_movement_pattern": "Ankle Dorsiflexion, Calves (Gastrocnemius, Soleus). Ankle Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for ankle mobility crucial for achieving proper squat depth and preventing compensatory movements (e.g., foot 'spinning out')."
            },
            {
                "name": "Thomas Test (Hip Internal/External Rotation Test)",
                "type": "diagnostic_assessment",
                "description": "Sit on the edge of a bed/bench with hips at the edge. Pull one knee to chest while allowing the other leg to relax. Assess position of relaxed leg.",
                "benefits": ["Identifies tightness in hip flexors (Iliopsoas, Rectus Femoris) and/or IT band.", "Assesses hip flexion mobility.", "Reveals asymmetry between hip sides."],
                "progressions_regressions": {
                    "regressions": ["Don't pull knee quite as close to chest.", "Use support for stability."],
                    "progressions": ["Focus on actively relaxing the tested leg.", "Compare results rigorously side-to-side."]
                },
                "key_cues": [
                    "Sit on edge of bed/bench, hips at edge.",
                    "Grab one knee, pull it to chest.",
                    "Gently fall backward onto your back.",
                    "Allow the opposite leg to relax completely.",
                    "Observe if relaxed leg lifts off bed or bends."
                ],
                "target_area_movement_pattern": "Hip Flexors, Iliotibial Band, Hip Mobility (Flexion, Internal/External Rotation). Hip Mobility Assessment.",
                "purpose_in_system": "Diagnostic screen for hip mobility restrictions that can contribute to low back pain or compensation in lower body movements."
            },
            {
                "name": "Flexion Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is exacerbated by actions such as sitting slouched, pulling up on the underside of a chair, bending movements like picking up objects from the ground, or deadlifting.",
                "benefits": ["Helps diagnose flexion intolerance, often associated with disc bulge/herniation.", "Guides selection of spine-sparing movements."],
                "progressions_regressions": {
                    "regressions": ["Avoid all known aggravating positions.", "Perform activities with maximal bracing."],
                    "progressions": ["Gradually introduce light loads with perfect hip hinge mechanics."]
                },
                "key_cues": [
                    "Consciously adopt positions that typically cause pain.",
                    "Note the exact trigger and pain intensity.",
                    "Compare pain levels with spine-neutral positions."
                ],
                "target_area_movement_pattern": "Lumbar Spine Flexion. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses sensitivity to spinal flexion, guiding corrective strategies focused on neutral spine and hip hinging."
            },
            {
                "name": "Extension Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is provoked by positions such as lying on the stomach, arching backward, or adopting an anterior pelvic tilt.",
                "benefits": ["Helps diagnose extension intolerance, potentially due to facet joint irritation or spondylolisthesis.", "Guides selection of spine-neutral movements."],
                "progressions_regressions": {
                    "regressions": ["Avoid all known aggravating positions.", "Focus on 'ribs down' cue in daily activities."],
                    "progressions": ["Gradually introduce gentle extension movements with controlled core bracing."]
                },
                "key_cues": [
                    "Consciously adopt positions that typically cause pain.",
                    "Note the exact trigger and pain intensity.",
                    "Compare pain levels with spine-neutral positions."
                ],
                "target_area_movement_pattern": "Lumbar Spine Extension. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses sensitivity to spinal extension, guiding corrective strategies focused on maintaining a braced neutral spine."
            },
            {
                "name": "Dynamic Loading/Instability Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain occurs with dynamic loading (running, jumping, Olympic lifts), or subtle micro-movements like sneezing/rolling over. A diagnostic test involves rising onto the toes and quickly dropping onto the heels.",
                "benefits": ["Helps diagnose spinal instability and uneven vertebral sliding.", "Guides emphasis on robust core bracing."],
                "progressions_regressions": {
                    "regressions": ["Avoid dynamic loading; focus on static core bracing.", "Temporary cessation of high-impact activities."],
                    "progressions": ["Gradually reintroduce dynamic movements with strong core bracing.", "Increase intensity of movement."]
                },
                "key_cues": [
                    "Perform dynamic movements or controlled drop test.",
                    "Observe if pain is triggered by shockwave of load or micro-movements.",
                    "Note the exact trigger and pain intensity."
                ],
                "target_area_movement_pattern": "Spinal Stability, Dynamic Core Control. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses spinal instability, emphasizing the need for comprehensive core bracing strategies."
            },
            {
                "name": "Load Intolerance Test",
                "type": "diagnostic_assessment",
                "description": "Observe if pain is triggered by holding a light weight at arm's length while taking deep breaths.",
                "benefits": ["Helps diagnose high sensitivity to load, potentially indicative of compressive injury.", "Guides decisions on lifting cessation or modification."],
                "progressions_regressions": {
                    "regressions": ["Avoid any loading.", "Seek assistance for daily lifting tasks."],
                    "progressions": ["Gradually introduce light loads with strong abdominal bracing."]
                },
                "key_cues": [
                    "Hold a light weight at arm's length.",
                    "Take deep breaths while holding.",
                    "Observe if pain is triggered."
                ],
                "target_area_movement_pattern": "Spinal Compression Tolerance. Low Back Pain Diagnosis.",
                "purpose_in_system": "Diagnoses extreme load sensitivity, dictating immediate lifting modifications or temporary cessation."
            },
            {
                "name": "Proper Hip Hinging (Corrective Strategy)",
                "type": "corrective_strategy",
                "description": "Learning and consistently applying the movement pattern where the hips initiate the bend, keeping the spine neutral, as seen in movements like the 'short-stop squat' or 'golfer's lift.'",
                "benefits": ["Protects the lumbar spine from excessive flexion.", "Loads the glutes and hamstrings effectively.", "Essential for deadlifts and picking objects safely."],
                "progressions_regressions": {
                    "regressions": ["Wall hinge drill (touching butt to wall)", "Downgrade with PVC pipe along spine.", "Kneeling for light objects."],
                    "progressions": ["Adding light load (e.g., kettlebell RDL)", "Increasing speed of hinge.", "Integrating into more complex lifts."]
                },
                "key_cues": [
                    "Push hips back first.",
                    "Maintain a long, neutral spine (avoid rounding or excessive arching).",
                    "Keep chest up.",
                    "Slight bend in knees, but focus on hip movement."
                ],
                "target_area_movement_pattern": "Glutes, Hamstrings, Erector Spinae. Hip Hinge, Spinal Stability.",
                "purpose_in_system": "Fundamental corrective for flexion intolerance; re-educates the movement pattern for safe lifting and daily activities."
            },
            {
                "name": "Ribs Down (Corrective Cue/Strategy)",
                "type": "corrective_strategy",
                "description": "A fundamental cue to prevent excessive spinal extension by engaging the core and drawing the lower ribs down towards the pelvis, maintaining a braced neutral spine.",
                "benefits": ["Prevents spinal extension intolerance.", "Promotes a neutral lumbar spine.", "Enhances core bracing and intra-abdominal pressure."],
                "progressions_regressions": {
                    "regressions": ["Practice in supine (lying on back) with knees bent, pressing lower back into floor.", "Gentle diaphragmatic breathing."],
                    "progressions": ["Apply cue during all lifts (squats, presses).", "Combine with Valsalva maneuver for maximal bracing."]
                },
                "key_cues": [
                    "Imagine pulling your lower ribs towards your belt line.",
                    "Avoid arching your lower back excessively.",
                    "Engage your abdominals gently."
                ],
                "target_area_movement_pattern": "Core (Rectus Abdominis, Obliques), Diaphragm. Spinal Extension Control, Core Bracing.",
                "purpose_in_system": "Core corrective strategy for extension intolerance; critical for maintaining spinal neutrality during lifting."
            },
            {
                "name": "Abdominal Bracing (Corrective Strategy)",
                "type": "corrective_strategy",
                "description": "A technique to increase intra-abdominal pressure by engaging the entire core musculature, providing stability to the spine for lifting and injury prevention.",
                "benefits": ["Minimizes spinal instability.", "Protects the spine from injury under load.", "Increases power transfer during lifts."],
                "progressions_regressions": {
                    "regressions": ["Practice 'bracing for a punch' while lying on back.", "Focus on 360-degree bracing, not just 'sucking in'."],
                    "progressions": ["Apply bracing to progressively heavier lifts.", "Combine with Valsalva maneuver (holding breath with braced core)."]
                },
                "key_cues": [
                    "Imagine bracing for a punch to the stomach (tighten all around).",
                    "Breathe into your belly and sides, not just chest.",
                    "Create 360-degree tension in your core.",
                    "Maintain bracing throughout the lift."
                ],
                "target_area_movement_pattern": "Core (Transverse Abdominis, Obliques, Rectus Abdominis, Diaphragm, Pelvic Floor). Spinal Stability, Intra-abdominal Pressure.",
                "purpose_in_system": "Fundamental corrective for dynamic loading/instability and load intolerance; provides a stable base for all complex movements."
            }
        ]
    }
}

def get_all_mentors_context() -> Dict[str, Dict[str, Any]]:
    """Get all mentor information (static fallback)"""
    return MENTOR_KNOWLEDGE

def get_mentor_specialization(mentor_name: str) -> Optional[str]:
    """Get mentor's specialization"""
    mentor = MENTOR_KNOWLEDGE.get(mentor_name.lower().replace(' ', '_'))
    return mentor.get('focus') if mentor else None

def get_mentor_context(query: str, mentor_names: Optional[List[str]] = None) -> str:
    """Get mentor context using RAG system"""
    try:
        return rag_system.get_mentor_context(query, mentor_names)
    except Exception as e:
        logger.error(f"❌ Error getting mentor context via RAG: {e}")
        # Fallback to static knowledge
        return get_static_mentor_context(query, mentor_names)

def get_static_mentor_context(query: str, mentor_names: Optional[List[str]] = None) -> str:
    """Get mentor context from static knowledge (fallback)"""
    context_parts = []
    
    # Filter mentors if specific ones requested
    mentors_to_use = mentor_names if mentor_names else MENTOR_KNOWLEDGE.keys()
    
    for mentor_id in mentors_to_use:
        if mentor_id in MENTOR_KNOWLEDGE:
            mentor = MENTOR_KNOWLEDGE[mentor_id]
            context_parts.append(f"""
{mentor['name']} - {mentor['focus']}:
Philosophy: {mentor['core_philosophy']}
Key Principles: {', '.join(mentor['key_principles'][:3])}
Training Methods: {', '.join(mentor['training_methods'][:3])}
Motivational Style: {mentor['motivational_style']}
""")
    
    return "\n".join(context_parts) if context_parts else "No mentor information available."

def create_mentor_prompt(user_input: str, mentor_names: Optional[List[str]] = None) -> str:
    """Create a prompt incorporating mentor knowledge"""
    try:
        # Use RAG system to get relevant mentor context
        mentor_context = rag_system.get_mentor_context(user_input, mentor_names)
        
        prompt = f"""You are an AI fitness coach with access to knowledge from world-class movement and strength mentors.

MENTOR KNOWLEDGE:
{mentor_context}

USER INPUT: {user_input}

Provide advice that synthesizes the best insights from these mentors, considering the user's specific needs and context."""
        
        return prompt
        
    except Exception as e:
        logger.error(f"❌ Error creating mentor prompt: {e}")
        # Fallback to static prompt
        return f"Based on mentor knowledge, respond to: {user_input}"

def search_mentor_knowledge(query: str, mentor_names: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search mentor knowledge using RAG system"""
    try:
        return rag_system.search_mentor_knowledge(query, mentor_names, top_k)
    except Exception as e:
        logger.error(f"❌ Error searching mentor knowledge: {e}")
        return []

def get_weekly_planning_context() -> str:
    """Get comprehensive context for weekly planning"""
    try:
        return rag_system.get_weekly_planning_context()
    except Exception as e:
        logger.error(f"❌ Error getting weekly planning context: {e}")
        return "Error retrieving planning knowledge."

def get_mentor_statistics() -> Dict[str, Any]:
    """Get statistics about the knowledge base"""
    try:
        return rag_system.get_mentor_statistics()
    except Exception as e:
        logger.error(f"❌ Error getting mentor statistics: {e}")
        return {'error': str(e)}

def get_relevant_mentors_for_query(query: str) -> List[str]:
    """Get relevant mentors for a specific query"""
    query_lower = query.lower()
    relevant_mentors = []
    
    # Map keywords to mentors
    keyword_mapping = {
        "dylan_werner": ["yoga", "control", "isometric", "balance", "flow"],
        "ido_portal": ["movement", "complex", "adaptability", "culture", "flow"],
        "patrick_beach": ["natural", "fluid", "mobility", "gentle", "recovery"],
        "squatu": ["injury", "pain", "shoulder", "joint", "safety"],
        "kneesovertoesguy": ["knee", "bulletproof", "longevity", "joint health"],
        "everydamnandré": ["simple", "tough", "mental", "consistency"],
        "dr_andy_galpin": ["science", "nutrition", "performance", "recovery"],
        "tom_merrick": ["calisthenics", "flexibility", "strength", "longevity", "bodyweight"]
    }
    
    for mentor_id, keywords in keyword_mapping.items():
        if any(keyword in query_lower for keyword in keywords):
            relevant_mentors.append(mentor_id)
    
    return relevant_mentors if relevant_mentors else ["dylan_werner", "patrick_beach"]

def get_mentor_knowledge_summary(mentor_name: str) -> Optional[Dict[str, Any]]:
    """Get a summary of a specific mentor's knowledge"""
    mentor_id = mentor_name.lower().replace(' ', '_')
    return MENTOR_KNOWLEDGE.get(mentor_id) 