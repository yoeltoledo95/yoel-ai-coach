import { NextRequest, NextResponse } from 'next/server'
import { WorkoutEngine } from '../../../backend/services/workout-engine'

const workoutEngine = new WorkoutEngine()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, constraints } = body

    // Input validation
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'Message is required and must be a non-empty string' },
        { status: 400 }
      )
    }

    if (message.length > 1000) {
      return NextResponse.json(
        { error: 'Message too long (max 1000 characters)' },
        { status: 400 }
      )
    }

    // Validate constraints if provided
    if (constraints && typeof constraints === 'object') {
      const { time, equipment, energy } = constraints
      
      if (time !== undefined && (typeof time !== 'number' || time < 5 || time > 180)) {
        return NextResponse.json(
          { error: 'Time constraint must be a number between 5 and 180 minutes' },
          { status: 400 }
        )
      }

      if (equipment !== undefined && typeof equipment !== 'string') {
        return NextResponse.json(
          { error: 'Equipment constraint must be a string' },
          { status: 400 }
        )
      }

      if (energy !== undefined && !['low', 'medium', 'high'].includes(energy)) {
        return NextResponse.json(
          { error: 'Energy constraint must be "low", "medium", or "high"' },
          { status: 400 }
        )
      }
    }

    const workout = workoutEngine.generateWorkout({
      message,
      constraints
    })

    return NextResponse.json(workout)
  } catch (error) {
    console.error('Workout generation error:', error)
    
    // Provide more specific error information
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      { 
        error: 'Failed to generate workout',
        details: (error as Error).message
      },
      { status: 500 }
    )
  }
}