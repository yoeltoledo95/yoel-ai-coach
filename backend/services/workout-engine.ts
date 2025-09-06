import { tomMerrickData, type Routine, type Exercise } from '../data/mentors/tom-merrick'

export interface WorkoutConstraints {
  time?: number
  equipment?: string
  energy?: 'low' | 'medium' | 'high'
}

export interface WorkoutRequest {
  message: string
  constraints?: WorkoutConstraints
}

export interface AnalyzedIntent {
  goal: string | null
  timePreference: number | null
  equipment: string | null
  bodyParts: string[]
  energyLevel: string | null
}

export interface WorkoutPlan {
  routine: Routine
  coaching_message: string
  adaptations?: string[]
  estimated_duration: number
  generated_at: string
}

export class WorkoutEngine {
  private mentorData = tomMerrickData

  generateWorkout(request: WorkoutRequest): WorkoutPlan {
    // Step 1: Analyze user intent
    const intent = this.analyzeIntent(request.message)
    
    // Step 2: Find best matching routine
    const routine = this.findBestRoutine(intent, request.constraints)
    
    // Step 3: Apply constraints and adaptations
    const adaptedRoutine = this.adaptRoutine(routine, request.constraints)
    
    // Step 4: Generate coaching message
    const coachingMessage = this.generateCoachingMessage(adaptedRoutine, request)
    
    return {
      routine: adaptedRoutine,
      coaching_message: coachingMessage,
      adaptations: this.getAdaptations(routine, adaptedRoutine, request.constraints),
      estimated_duration: adaptedRoutine.duration_minutes,
      generated_at: new Date().toISOString()
    }
  }

  private analyzeIntent(message: string): AnalyzedIntent {
    const messageLower = message.toLowerCase()
    
    let goal = null
    let timePreference = null
    let equipment = null
    let bodyParts: string[] = []
    let energyLevel = null

    // Goal detection
    if (messageLower.includes('pancake') || messageLower.includes('forward fold') || messageLower.includes('hip flexibility')) {
      goal = 'pancake_progression'
    } else if (messageLower.includes('morning') || messageLower.includes('wake up') || messageLower.includes('start day')) {
      goal = 'daily_morning_mobility'
    } else if (messageLower.includes('flexibility') || messageLower.includes('mobility')) {
      goal = 'daily_morning_mobility' // Default flexibility goal
    }

    // Time detection
    if (messageLower.includes('15 min') || messageLower.includes('quick') || messageLower.includes('short')) {
      timePreference = 15
    } else if (messageLower.includes('20 min')) {
      timePreference = 20
    }

    // Body parts detection
    if (messageLower.includes('hip') || messageLower.includes('hips')) {
      bodyParts.push('hips')
    }
    if (messageLower.includes('shoulder') || messageLower.includes('shoulders')) {
      bodyParts.push('shoulders')
    }
    if (messageLower.includes('back')) {
      bodyParts.push('spine')
    }

    // Energy level detection
    if (messageLower.includes('tired') || messageLower.includes('low energy') || messageLower.includes('gentle')) {
      energyLevel = 'low'
    }

    return { goal, timePreference, equipment, bodyParts, energyLevel }
  }

  private findBestRoutine(intent: AnalyzedIntent, constraints?: WorkoutConstraints): Routine {
    const routines = this.mentorData.routines.by_goal

    // First try to match by goal
    if (intent.goal && routines[intent.goal]) {
      return routines[intent.goal]
    }

    // Then try to match by time
    const timeAvailable = constraints?.time || intent.timePreference
    if (timeAvailable) {
      const timeKey = `${timeAvailable}_min`
      const timeRoutines = this.mentorData.routines.by_time[timeKey]
      if (timeRoutines && timeRoutines.length > 0) {
        return routines[timeRoutines[0]]
      }
    }

    // Default to morning mobility
    return routines.daily_morning_mobility
  }

  private adaptRoutine(routine: Routine, constraints?: WorkoutConstraints): Routine {
    let adapted = { ...routine, exercise_sequence: [...routine.exercise_sequence] }
    
    if (!constraints) return adapted

    // Time constraints
    if (constraints.time && constraints.time < routine.duration_minutes) {
      // Shorten the routine
      const maxExercises = constraints.time >= 15 ? 4 : 3
      adapted.exercise_sequence = adapted.exercise_sequence.slice(0, maxExercises)
      adapted.duration_minutes = constraints.time
    }

    // Energy constraints
    if (constraints.energy === 'low') {
      // Reduce intensity by shortening hold times
      adapted.exercise_sequence = adapted.exercise_sequence.map(exercise => {
        if (exercise.duration && exercise.duration.includes('seconds')) {
          // Reduce by 25%
          const newDuration = exercise.duration.replace(/(\d+)(?=.*seconds)/, (match, p1) => {
            return Math.max(20, Math.floor(parseInt(p1) * 0.75)).toString()
          })
          return { ...exercise, duration: newDuration }
        }
        return exercise
      })
    }

    return adapted
  }

  private generateCoachingMessage(routine: Routine, request: WorkoutRequest): string {
    const philosophy = this.mentorData.core.philosophy
    
    const messages = {
      pancake_progression: `Great choice working on your pancake flexibility! Remember Tom's approach: patience and consistency over forcing depth. Today we'll work through the pancake progression systematically. Focus on the hip hinge pattern in the good mornings, then gradually work deeper in the seated positions. Listen to your body - flexibility is a skill that develops with daily practice, not force.`,
      
      daily_morning_mobility: `Perfect way to start your day! This morning mobility sequence will wake up your entire system. Tom emphasizes moving through your natural ranges first - no need to push hard this early. Focus on the quality of movement and connecting with your breath. These 15 minutes will set you up for better movement throughout your day.`
    }

    const routineKey = Object.keys(this.mentorData.routines.by_goal).find(
      key => this.mentorData.routines.by_goal[key].name === routine.name
    )

    return messages[routineKey as keyof typeof messages] || 
           `Here's your ${routine.name}. Focus on proper form and listen to your body. ${philosophy.split('.')[0]}.`
  }

  private getAdaptations(original: Routine, adapted: Routine, constraints?: WorkoutConstraints): string[] {
    const adaptations: string[] = []

    if (adapted.exercise_sequence.length < original.exercise_sequence.length) {
      adaptations.push(`Shortened from ${original.exercise_sequence.length} to ${adapted.exercise_sequence.length} exercises due to time constraints`)
    }

    if (constraints?.energy === 'low') {
      adaptations.push('Reduced hold times for low energy levels')
    }

    if (adapted.duration_minutes < original.duration_minutes) {
      adaptations.push(`Duration reduced from ${original.duration_minutes} to ${adapted.duration_minutes} minutes`)
    }

    return adaptations
  }
}