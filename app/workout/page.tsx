'use client'

import { useState } from 'react'

interface Exercise {
  exercise: string
  sets_reps?: string
  duration?: string
  key_cues: string[]
  purpose?: string
  progression?: string
}

interface WorkoutPlan {
  routine: {
    name: string
    goal: string
    duration_minutes: number
    target_areas: string[]
    equipment: string[]
    exercise_sequence: Exercise[]
    frequency: string
    best_for: string[]
  }
  coaching_message: string
  adaptations?: string[]
  estimated_duration: number
  generated_at: string
}

export default function WorkoutPage() {
  const [message, setMessage] = useState('')
  const [workout, setWorkout] = useState<WorkoutPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateWorkout = async () => {
    if (!message.trim()) return

    setLoading(true)
    setError(null)
    setWorkout(null)
    
    try {
      const response = await fetch('/api/workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })

      if (response.ok) {
        const data = await response.json()
        setWorkout(data)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to generate workout')
      }
    } catch (error) {
      setError('Network error: Unable to connect to server')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Workout Generator
          </h1>
          <p className="text-gray-600">
            Tell me what kind of workout you want and I'll create it for you
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="e.g., 'I want to work on pancake flexibility' or 'Give me a quick morning routine'"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && generateWorkout()}
            />
            <button
              onClick={generateWorkout}
              disabled={loading || !message.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating...' : 'Generate Workout'}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-400">⚠️</span>
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-red-800">Error</h4>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {workout && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {workout.routine.name}
              </h2>
              <p className="text-gray-600 mb-4">{workout.routine.goal}</p>
              
              <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-4">
                <span>⏱️ {workout.estimated_duration} minutes</span>
                <span>🎯 {workout.routine.target_areas.join(', ')}</span>
                <span>📅 {workout.routine.frequency}</span>
              </div>

              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p className="text-blue-800">{workout.coaching_message}</p>
              </div>

              {workout.adaptations && workout.adaptations.length > 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                  <h4 className="font-semibold text-yellow-800 mb-2">Adaptations Made:</h4>
                  <ul className="list-disc list-inside text-yellow-700">
                    {workout.adaptations.map((adaptation, index) => (
                      <li key={index}>{adaptation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-gray-900">Exercise Sequence</h3>
              
              {workout.routine.exercise_sequence.map((exercise, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="text-lg font-semibold text-gray-900">
                      {index + 1}. {exercise.exercise}
                    </h4>
                    <span className="text-sm text-gray-500">
                      {exercise.sets_reps || exercise.duration}
                    </span>
                  </div>
                  
                  <div className="mb-3">
                    <h5 className="font-medium text-gray-700 mb-2">Key Cues:</h5>
                    <ul className="list-disc list-inside text-gray-600 space-y-1">
                      {exercise.key_cues.map((cue, cueIndex) => (
                        <li key={cueIndex}>{cue}</li>
                      ))}
                    </ul>
                  </div>

                  {exercise.purpose && (
                    <div className="text-sm text-gray-500">
                      <strong>Purpose:</strong> {exercise.purpose}
                    </div>
                  )}

                  {exercise.progression && (
                    <div className="text-sm text-blue-600 mt-2">
                      <strong>Progression:</strong> {exercise.progression}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}