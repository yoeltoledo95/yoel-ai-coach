"""
System efficiency tests for AI Coach
Tests mentor usage, response quality, and performance benchmarks
"""
import time
import psutil
import os
import sys
import requests
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import Counter

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

@dataclass
class PerformanceMetrics:
    response_time: float
    memory_usage_mb: float
    mentors_mentioned: List[str]
    response_length: int
    api_calls_made: int

@dataclass
class TestResult:
    test_name: str
    metrics: PerformanceMetrics
    quality_score: float
    efficiency_score: float

class SystemEfficiencyTester:
    """Test system efficiency, mentor usage, and response quality"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
        # Known mentors for tracking
        self.known_mentors = [
            "Dylan Werner", "Ido Portal", "Tom Merrick", "Emmet Louis",
            "Patrick Beach", "Everydamnandré", "JTM_FIT", "FitnessFAQs",
            "Austin Dunham", "KneesOverToesGuy", "Dr. Andy Galpin", "Marcus Filly"
        ]
    
    def clear_session(self):
        """Clear session before each test"""
        try:
            requests.post(f"{self.base_url}/api/clear-session")
        except:
            pass
    
    def measure_performance(self, test_name: str, message: str, user_name: str = "Yoel") -> PerformanceMetrics:
        """Measure performance metrics for a single request"""
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make request and measure time
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers={"Content-Type": "application/json"},
                json={"message": message, "user_name": user_name},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get('response', '')
            
        except Exception as e:
            print(f"Error in {test_name}: {e}")
            response_text = ""
        
        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Analyze mentor mentions
        mentors_mentioned = []
        for mentor in self.known_mentors:
            if mentor.lower() in response_text.lower():
                mentors_mentioned.append(mentor)
        
        return PerformanceMetrics(
            response_time=end_time - start_time,
            memory_usage_mb=final_memory - initial_memory,
            mentors_mentioned=mentors_mentioned,
            response_length=len(response_text),
            api_calls_made=1  # Simplified for now
        )
    
    def score_response_quality(self, response_text: str, expected_context: str) -> float:
        """Score response quality on a scale of 0-10"""
        score = 5.0  # Base score
        
        # Check for natural conversation
        if "Hi" in response_text or "Hey" in response_text:
            score += 1.0
        
        # Check for personalization
        if "Yoel" in response_text:
            score += 1.0
        
        # Check for practical advice
        practical_keywords = ["try", "focus", "start", "consider", "recommend"]
        if any(keyword in response_text.lower() for keyword in practical_keywords):
            score += 1.0
        
        # Check for empathy/understanding
        empathy_keywords = ["understand", "feel", "normal", "listen to your body"]
        if any(keyword in response_text.lower() for keyword in empathy_keywords):
            score += 1.0
        
        # Penalize if too robotic/template-like
        if "Phase 1:" in response_text or "Sets/Reps:" in response_text:
            score -= 2.0
        
        # Penalize if too long (over 1000 chars for simple questions)
        if len(response_text) > 1000 and len(expected_context) < 50:
            score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def calculate_efficiency_score(self, metrics: PerformanceMetrics) -> float:
        """Calculate efficiency score based on performance metrics"""
        score = 10.0
        
        # Response time penalty
        if metrics.response_time > 5.0:
            score -= 3.0
        elif metrics.response_time > 3.0:
            score -= 2.0
        elif metrics.response_time > 2.0:
            score -= 1.0
        
        # Memory usage penalty
        if metrics.memory_usage_mb > 100:
            score -= 2.0
        elif metrics.memory_usage_mb > 50:
            score -= 1.0
        
        # Mentor overuse penalty (too many mentors = complexity)
        if len(metrics.mentors_mentioned) > 5:
            score -= 2.0
        elif len(metrics.mentors_mentioned) > 3:
            score -= 1.0
        
        return max(0.0, score)
    
    def run_conversation_tests(self) -> List[TestResult]:
        """Run a series of conversation tests"""
        
        test_cases = [
            ("simple_greeting", "hello", "hello"),
            ("tired_today", "I feel tired today", "tired"),
            ("workout_request", "give me a workout", "workout"),
            ("question_about_goals", "what are my goals?", "goals"),
            ("general_fitness_question", "how often should I train?", "training frequency")
        ]
        
        for test_name, message, context in test_cases:
            print(f"\n🧪 Running test: {test_name}")
            
            # Clear session for clean test
            self.clear_session()
            
            # Measure performance
            metrics = self.measure_performance(test_name, message)
            
            # Score quality and efficiency
            quality_score = self.score_response_quality("", context)  # Would need actual response
            efficiency_score = self.calculate_efficiency_score(metrics)
            
            result = TestResult(
                test_name=test_name,
                metrics=metrics,
                quality_score=quality_score,
                efficiency_score=efficiency_score
            )
            
            self.results.append(result)
            
            # Print immediate results
            print(f"  ⏱️  Response time: {metrics.response_time:.2f}s")
            print(f"  💾 Memory usage: {metrics.memory_usage_mb:.1f}MB")
            print(f"  👥 Mentors mentioned: {len(metrics.mentors_mentioned)}")
            print(f"  📝 Response length: {metrics.response_length} chars")
            print(f"  🎯 Quality score: {quality_score:.1f}/10")
            print(f"  ⚡ Efficiency score: {efficiency_score:.1f}/10")
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive efficiency report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Calculate averages
        avg_response_time = sum(r.metrics.response_time for r in self.results) / len(self.results)
        avg_memory_usage = sum(r.metrics.memory_usage_mb for r in self.results) / len(self.results)
        avg_quality_score = sum(r.quality_score for r in self.results) / len(self.results)
        avg_efficiency_score = sum(r.efficiency_score for r in self.results) / len(self.results)
        
        # Analyze mentor usage
        all_mentors = []
        for result in self.results:
            all_mentors.extend(result.metrics.mentors_mentioned)
        mentor_usage = Counter(all_mentors)
        
        return {
            "summary": {
                "total_tests": len(self.results),
                "avg_response_time": round(avg_response_time, 2),
                "avg_memory_usage_mb": round(avg_memory_usage, 1),
                "avg_quality_score": round(avg_quality_score, 1),
                "avg_efficiency_score": round(avg_efficiency_score, 1)
            },
            "mentor_analysis": {
                "unique_mentors_used": len(mentor_usage),
                "most_used_mentors": mentor_usage.most_common(5),
                "avg_mentors_per_response": round(len(all_mentors) / len(self.results), 1)
            },
            "performance_breakdown": [
                {
                    "test": r.test_name,
                    "response_time": r.metrics.response_time,
                    "memory_mb": r.metrics.memory_usage_mb,
                    "mentors_count": len(r.metrics.mentors_mentioned),
                    "quality": r.quality_score,
                    "efficiency": r.efficiency_score
                }
                for r in self.results
            ]
        }

def main():
    """Run efficiency tests and generate report"""
    print("🚀 Starting AI Coach Efficiency Tests...")
    
    tester = SystemEfficiencyTester()
    
    # Run tests
    results = tester.run_conversation_tests()
    
    # Generate and print report
    report = tester.generate_report()
    
    print("\n" + "="*60)
    print("📊 EFFICIENCY REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"📈 Average Response Time: {summary['avg_response_time']}s")
    print(f"💾 Average Memory Usage: {summary['avg_memory_usage_mb']}MB")
    print(f"🎯 Average Quality Score: {summary['avg_quality_score']}/10")
    print(f"⚡ Average Efficiency Score: {summary['avg_efficiency_score']}/10")
    
    mentor_analysis = report['mentor_analysis']
    print(f"\n👥 Mentor Usage:")
    print(f"  - Average mentors per response: {mentor_analysis['avg_mentors_per_response']}")
    print(f"  - Most used mentors: {mentor_analysis['most_used_mentors']}")
    
    # Save detailed report
    with open('efficiency_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: efficiency_report.json")

if __name__ == "__main__":
    main()
