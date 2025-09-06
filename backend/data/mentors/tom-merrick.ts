export interface Exercise {
  exercise: string
  sets_reps?: string
  duration?: string
  key_cues: string[]
  purpose?: string
  progression?: string
}

export interface Routine {
  name: string
  goal: string
  duration_minutes: number
  target_areas: string[]
  equipment: string[]
  exercise_sequence: Exercise[]
  frequency: string
  progression_timeline?: string
  best_for: string[]
  pairs_well_with?: string
}

export interface DecisionRule {
  if: string
  then: string
  routine: string
  modification?: string
  next_step?: string
}

export interface MentorData {
  core: {
    specialty: string[]
    philosophy: string
    signature_methods: string[]
    target_audience: string[]
    training_style: string
  }
  routines: {
    by_goal: Record<string, Routine>
    by_time: Record<string, string[]>
    by_equipment: Record<string, string[]>
  }
  decision_trees: {
    rules: DecisionRule[]
  }
}

export const tomMerrickData: MentorData = {
  core: {
    specialty: ["flexibility", "mobility", "calisthenics_basics", "body_control"],
    philosophy: "Tom believes in patient, progressive flexibility training with a focus on active mobility and strength through range of motion. He emphasizes consistency over intensity, teaching that flexibility is a skill that requires daily practice. His approach combines passive stretching with active strengthening work, ensuring joints are both mobile and stable. He advocates for understanding your body's signals and working with, not against, your current limitations.",
    signature_methods: [
      "Follow along flexibility routines",
      "Active flexibility development", 
      "Loaded progressive stretching",
      "Daily mobility practice",
      "Contract-relax PNF stretching"
    ],
    target_audience: ["beginners", "intermediate", "desk_workers", "calisthenics_athletes"],
    training_style: "Calm, educational, emphasizes proper form over depth"
  },
  
  routines: {
    by_goal: {
      pancake_progression: {
        name: "Pancake Good Morning Routine",
        goal: "Develop pancake flexibility systematically",
        duration_minutes: 20,
        target_areas: ["hamstrings", "adductors", "hip_flexors", "lower_back"],
        equipment: ["yoga_block_optional", "resistance_band_optional"],
        exercise_sequence: [
          {
            exercise: "Standing Good Mornings",
            sets_reps: "2x10",
            key_cues: [
              "Hinge at hips, not lower back",
              "Keep slight knee bend",
              "Feel stretch in hamstrings"
            ],
            purpose: "Warm up posterior chain"
          },
          {
            exercise: "Standing Straddle Good Mornings",
            sets_reps: "2x8 each direction",
            key_cues: [
              "Wide stance, toes slightly out",
              "Fold toward left, center, right",
              "Keep back straight"
            ],
            purpose: "Pattern the pancake movement"
          },
          {
            exercise: "Seated Pancake Reach",
            duration: "3x45 seconds",
            key_cues: [
              "Sit tall first, then hinge forward",
              "Reach arms forward, not down",
              "Breathe into the stretch"
            ],
            progression: "Add 5 seconds each week"
          },
          {
            exercise: "Pancake Pulses",
            sets_reps: "3x10",
            key_cues: [
              "Small bouncing movements",
              "Stay in comfortable range",
              "Use momentum gently"
            ],
            purpose: "Active flexibility"
          },
          {
            exercise: "Single Leg Seated Forward Fold",
            duration: "2x30 seconds each leg",
            key_cues: [
              "One leg straight, one bent",
              "Square hips to extended leg",
              "Flex foot strongly"
            ],
            purpose: "Address imbalances"
          },
          {
            exercise: "Pancake Hold with Contract-Relax",
            duration: "3 rounds",
            key_cues: [
              "Push hands into floor for 5 seconds",
              "Relax and sink deeper for 10 seconds",
              "Repeat 3 times"
            ],
            purpose: "PNF stretching for deeper range"
          }
        ],
        frequency: "3-4x per week",
        progression_timeline: "Expect 1-2 inches improvement per month",
        best_for: ["pancake_goal", "hip_mobility", "hamstring_flexibility"],
        pairs_well_with: "Hip flexor work and core training"
      },
      
      daily_morning_mobility: {
        name: "15 Minute Morning Routine",
        goal: "General mobility and movement prep",
        duration_minutes: 15,
        target_areas: ["full_body", "spine", "hips", "shoulders"],
        equipment: ["none"],
        exercise_sequence: [
          {
            exercise: "Cat-Cow Stretches",
            duration: "1 minute",
            key_cues: [
              "Move through entire spine",
              "Sync with breathing",
              "Include neck movement"
            ]
          },
          {
            exercise: "Thoracic Spine Rotations",
            sets_reps: "10 each side",
            key_cues: [
              "Keep hips facing forward",
              "Reach arm across body",
              "Look over shoulder"
            ]
          },
          {
            exercise: "Hip CARs (Controlled Articular Rotations)",
            sets_reps: "5 each leg",
            key_cues: [
              "Slow, controlled circles",
              "Maximum range without compensation",
              "Keep core engaged"
            ]
          },
          {
            exercise: "Shoulder Dislocates (imaginary band)",
            sets_reps: "10 reps",
            key_cues: [
              "Wide grip with imaginary band",
              "Keep arms straight",
              "Only go as far as comfortable"
            ]
          },
          {
            exercise: "Deep Squat Hold",
            duration: "1 minute",
            key_cues: [
              "Heels down if possible",
              "Knees tracking over toes",
              "Use hands for balance if needed"
            ]
          },
          {
            exercise: "Standing Forward Fold",
            duration: "1 minute",
            key_cues: [
              "Bend knees as needed",
              "Let head hang",
              "Sway side to side"
            ]
          }
        ],
        frequency: "Daily",
        best_for: ["morning_routine", "desk_workers", "general_maintenance"]
      }
    },
    
    by_time: {
      "15_min": ["daily_morning_mobility"],
      "20_min": ["pancake_progression"]
    },
    
    by_equipment: {
      "bodyweight_only": ["daily_morning_mobility", "pancake_progression"]
    }
  },
  
  decision_trees: {
    rules: [
      {
        if: "user wants pancake AND has tight hamstrings",
        then: "Start with single leg work and standing good mornings",
        routine: "pancake_progression",
        modification: "Spend extra time on hamstring specific work"
      },
      {
        if: "user has only 15 minutes AND wants flexibility",
        then: "Quick morning mobility sequence",
        routine: "daily_morning_mobility"
      },
      {
        if: "user is very stiff beginner",
        then: "Start with daily morning routine for 2 weeks",
        routine: "daily_morning_mobility",
        next_step: "Add specific flexibility work after base is built"
      }
    ]
  }
}