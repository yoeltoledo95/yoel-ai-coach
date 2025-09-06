export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-bold mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          AI Fitness Coach
        </h1>
        
        <p className="text-xl text-gray-600 mb-8">
          Your personal AI trainer powered by world-class mentor knowledge
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="text-2xl mb-3">🏋️</div>
            <h3 className="text-lg font-semibold mb-2">Smart Workouts</h3>
            <p className="text-gray-600 text-sm">AI-generated workouts from Tom Merrick's expertise</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="text-2xl mb-3">📈</div>
            <h3 className="text-lg font-semibold mb-2">Track Progress</h3>
            <p className="text-gray-600 text-sm">Intelligent analysis of your fitness journey</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="text-2xl mb-3">🧠</div>
            <h3 className="text-lg font-semibold mb-2">Learns & Adapts</h3>
            <p className="text-gray-600 text-sm">AI coach that understands your patterns</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="text-2xl mb-3">👨‍🏫</div>
            <h3 className="text-lg font-semibold mb-2">Expert Mentors</h3>
            <p className="text-gray-600 text-sm">Knowledge from world-class coaches</p>
          </div>
        </div>
        
        <div className="bg-gray-50 p-6 rounded-lg border">
          <h2 className="text-xl font-semibold mb-4">Phase 1: Foundation</h2>
          <p className="text-gray-700 mb-4">
            Building the core workout generation system with Tom Merrick's flexibility expertise
          </p>
          <div className="text-sm text-gray-500 mb-4">
            Status: Workout generation engine complete ✅
          </div>
          <a 
            href="/workout" 
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Workout Generator →
          </a>
        </div>
      </div>
    </main>
  )
}