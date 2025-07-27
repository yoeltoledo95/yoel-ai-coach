"""
Mentor Brain - Dynamic RAG-powered mentor knowledge system
Provides access to mentor knowledge through vector search and retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from coach_core.rag_system import rag_system

logger = logging.getLogger(__name__)

# Static mentor information (fallback)
MENTOR_KNOWLEDGE = {
    "dylan_werner": {
        "name": "Dylan Werner",
        "focus": "Yoga and Movement Control",
        "core_philosophy": "Control your body, control your mind. Focus on precise movement control and isometric strength.",
        "key_principles": ["Movement Control", "Isometric Strength", "Mind-Body Integration"],
        "training_methods": ["Isometric Training", "Movement Flow", "Strength Through Control"],
        "motivational_style": "Calm, focused, emphasizes precision and control"
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
        "name": "KneesOverToesGuy",
        "focus": "Bulletproofing and Longevity",
        "core_philosophy": "Build bulletproof joints for long-term health and performance.",
        "key_principles": ["Joint Health", "Longevity", "Bulletproofing"],
        "training_methods": ["Joint Strengthening", "Mobility Work", "Longevity Training"],
        "motivational_style": "Educational, longevity-focused, emphasizes joint health"
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