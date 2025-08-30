"""
Comprehensive workout quality testing with mentor-specific benchmarks.
"""
import pytest
from typing import Dict, Any

from shared.ai.workout_quality_scorer import workout_quality_scorer, QualityDimension


class TestWorkoutQualityScorer:
    """Test suite for workout quality scoring system"""
    
    def setup_method(self):
        """Setup test data"""
        self.yoel_profile = {
            "name": "Yoel",
            "injuries": ["meniscus_tear", "shoulder_impingement"],
            "goals": ["mobility", "joint_health", "strength"],
            "experience_level": "intermediate"
        }
        
        self.healthy_profile = {
            "name": "Test User",
            "injuries": [],
            "goals": ["strength", "hypertrophy"],
            "experience_level": "beginner"
        }
    
    def test_ben_patrick_joint_health_workout(self):
        """Test 1: Ben Patrick focused knee-safe workout"""
        
        workout_text = """
        Hey Yoel! Since your meniscus is feeling tender today, let's focus on Ben Patrick's knee-friendly approach.
        
        **Warm-up (8 minutes)**
        - Backward walking (3 minutes) - Ben Patrick's favorite for knee health
        - Tibialis raises (2 sets of 15) - these are game-changers for knee stability
        
        **Main Session (25 minutes)**
        - Backward sled pull (3 sets of 50 feet) - builds resilience without stress
        - Shoulder shrugs (3 sets of 12) - safe upper body work
        - 4-7-8 breathing (5 minutes) - Dylan Werner style recovery
        
        **Cool-down (7 minutes)**
        - Gentle spinal waves
        - More breathing work
        
        How does this feel? We're avoiding any deep knee flexion and focusing on backward movement patterns that Ben Patrick recommends for meniscus health.
        """
        
        context = {
            "equipment_available": ["sled", "space for walking"],
            "time_available": 40
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for Ben Patrick workout
        assert score.overall_score >= 85, f"Expected high score for Ben Patrick workout, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.SAFETY] >= 90, "Should be very safe for knee issues"
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 80, "Should align well with Ben Patrick"
        assert "ben_patrick" in score.mentor_coverage, "Should recognize Ben Patrick principles"
        assert score.mentor_coverage["ben_patrick"] >= 0.7, "Should have strong Ben Patrick coverage"
        assert len(score.safety_flags) == 0, "Should have no safety flags for knee-safe workout"
        assert score.grade in ["A+", "A"], f"Expected A grade, got {score.grade}"
    
    def test_ido_portal_mobility_flow(self):
        """Test 2: Ido Portal focused mobility workout"""
        
        workout_text = """
        Yoel, let's explore movement quality today with Ido Portal's approach to spinal mobility!
        
        **Movement Exploration (45 minutes)**
        - Spinal waves (10 minutes) - Ido's signature movement, focus on articulation
        - Hanging protocols (3 sets of 30-60 seconds) - passive and active variations
        - Locomotion patterns (15 minutes) - bear crawl, crab walk, lizard walk
        - Pancake stretch progression (10 minutes) - Tom Merrick style with Ido's flow
        - Integration flow (5 minutes) - connect all movements smoothly
        
        Remember Ido's principle: movement quality over quantity. Listen to your body and explore what feels good today. How does your spine feel as you move through these patterns?
        """
        
        context = {
            "equipment_available": ["pull-up bar", "open floor space"],
            "time_available": 45
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for Ido Portal workout
        assert score.overall_score >= 80, f"Expected good score for Ido Portal workout, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 75, "Should align with Ido Portal principles"
        assert score.dimension_scores[QualityDimension.STRUCTURE] >= 70, "Should have good flow structure"
        assert "ido_portal" in score.mentor_coverage, "Should recognize Ido Portal principles"
        assert score.mentor_coverage["ido_portal"] >= 0.6, "Should have decent Ido Portal coverage"
    
    def test_everydamnandre_kettlebell_power(self):
        """Test 3: Everydamnandré kettlebell strength workout"""
        
        workout_text = """
        Time for some Everydamnandré style kettlebell power, Yoel!
        
        **Warm-up (8 minutes)**
        - Joint mobility and activation
        - Light kettlebell swings (2 sets of 10)
        
        **Main Session (25 minutes)**
        - Kettlebell swings (5 sets of 15) - focus on hip drive and power
        - Kettlebell clean and press (4 sets of 6 each side) - technical mastery
        - Turkish get-ups (3 sets of 2 each side) - total body integration
        
        **Cool-down (7 minutes)**
        - Light stretching and breathing
        
        Channel that Everydamnandré mental toughness - every rep with intention and power! How are your shoulders feeling with the overhead work?
        """
        
        context = {
            "equipment_available": ["kettlebells"],
            "time_available": 40
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for Everydamnandré workout
        # Note: This should score lower on safety due to Turkish get-ups with shoulder issues
        assert score.dimension_scores[QualityDimension.SAFETY] < 70, "Should flag safety concerns with shoulder impingement"
        assert len(score.safety_flags) > 0, "Should have safety flags for Turkish get-ups"
        assert "turkish_getup" in score.safety_flags[0].lower() or "get-up" in score.safety_flags[0].lower(), "Should specifically flag Turkish get-ups"
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 70, "Should align with Everydamnandré"
    
    def test_tom_merrick_flexibility_focus(self):
        """Test 4: Tom Merrick flexibility deep work"""
        
        workout_text = """
        Deep flexibility work today, Yoel, using Tom Merrick's approach to progressive stretching!
        
        **Warm-up (5 minutes)**
        - Joint circles and light movement
        
        **Deep Stretch Session (30 minutes)**
        - Pancake stretch progression (3 sets of 30 seconds + PNF) - Tom's specialty
        - Jefferson curls (3 sets of 5, very controlled) - spinal mobility
        - Pike progression (3 sets of 30 seconds) - hamstring and back flexibility
        - Hip flexor stretches (2 sets of 45 seconds each side)
        
        **Integration (5 minutes)**
        - Gentle movement to integrate new ranges
        
        Remember Tom's principle: active flexibility is stronger than passive. Use your strength to get more flexible! How does your back feel through these ranges?
        """
        
        context = {
            "equipment_available": ["yoga mat", "wall"],
            "time_available": 40
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for Tom Merrick workout
        assert score.overall_score >= 85, f"Expected high score for flexibility work, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.SAFETY] >= 85, "Flexibility work should be very safe"
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 80, "Should align well with Tom Merrick"
        assert "tom_merrick" in score.mentor_coverage, "Should recognize Tom Merrick principles"
    
    def test_yoel_knee_sensitive_day(self):
        """Test 7: Yoel's knee-sensitive day scenario"""
        
        workout_text = """
        I can see your meniscus is feeling tender today, Yoel. Let's stick to Ben Patrick's safest protocols.
        
        **Gentle Session (35 minutes)**
        - Backward walking (5 minutes) - zero knee stress
        - Tibialis raises (3 sets of 12) - strengthen without strain
        - Upper body focus with shoulder shrugs (3 sets of 10)
        - Breathing work (10 minutes) - Dylan Werner's 4-7-8 technique
        - Gentle spinal movement (5 minutes)
        
        No deep squats, no forward lunges, no pivoting movements today. How does this feel? We can always adjust based on how your knee responds.
        """
        
        context = {
            "pain_level": "moderate knee discomfort",
            "time_available": 35
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for knee-sensitive workout
        assert score.overall_score >= 90, f"Expected very high score for injury-appropriate workout, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.SAFETY] >= 95, "Should be extremely safe for knee issues"
        assert score.dimension_scores[QualityDimension.PERSONALIZATION] >= 85, "Should be highly personalized"
        assert len(score.safety_flags) == 0, "Should have no safety flags"
        assert score.grade == "A+", f"Expected A+ grade for perfect injury accommodation, got {score.grade}"
    
    def test_yoel_shoulder_limitation(self):
        """Test 8: Yoel's shoulder impingement scenario"""
        
        workout_text = """
        Since your shoulder is bothering you today, Yoel, let's work around it with Emmet Louis and Tom Merrick principles.
        
        **Shoulder-Safe Session (40 minutes)**
        - Gentle shoulder circles and mobility (5 minutes)
        - Pancake stretch work (15 minutes) - no shoulder involvement
        - Lower body strength with bodyweight squats (3 sets of 10)
        - Core work without overhead (10 minutes)
        - Breathing and relaxation (5 minutes)
        
        No overhead work, no handstand progressions, keeping everything below shoulder height until the impingement settles. How does your shoulder feel with these movements?
        """
        
        context = {
            "pain_location": "shoulder impingement",
            "time_available": 40
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for shoulder-safe workout
        assert score.dimension_scores[QualityDimension.SAFETY] >= 85, "Should be safe for shoulder issues"
        assert score.dimension_scores[QualityDimension.PERSONALIZATION] >= 80, "Should acknowledge shoulder limitation"
        # Note: Bodyweight squats might be flagged for meniscus, so overall safety might be lower
    
    def test_yoel_perfect_day(self):
        """Test 9: Yoel's feeling-great multi-mentor workout"""
        
        workout_text = """
        Yoel, you're feeling fantastic today! Let's integrate multiple mentors for a comprehensive session.
        
        **Dynamic Warm-up (10 minutes)**
        - Spinal waves (Ido Portal) - movement preparation
        - Backward walking (Ben Patrick) - knee activation
        - Shoulder mobility (Emmet Louis) - joint preparation
        
        **Main Session (40 minutes)**
        - Kettlebell swings (Everydamnandré) - 4 sets of 12, power focus
        - Pancake stretch progression (Tom Merrick) - 3 sets with PNF
        - Tibialis raises (Ben Patrick) - 3 sets of 15, knee health
        - Hanging protocols (Ido Portal) - 3 sets of 45 seconds
        - Shoulder shrugs (Emmet Louis) - 3 sets of 12, controlled
        
        **Cool-down (10 minutes)**
        - 4-7-8 breathing (Dylan Werner) - nervous system reset
        - Gentle spinal waves integration
        
        This integrates all your mentors while respecting your injury history. We're using power from Everydamnandré, mobility from Tom and Ido, joint health from Ben Patrick, shoulder care from Emmet, and recovery from Dylan. How does this comprehensive approach feel?
        """
        
        context = {
            "energy_level": "high",
            "equipment_available": ["kettlebells", "pull-up bar"],
            "time_available": 60
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for multi-mentor integration
        assert score.overall_score >= 85, f"Expected high score for comprehensive workout, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 85, "Should have excellent mentor integration"
        assert len([m for m in score.mentor_coverage.values() if m > 0.3]) >= 4, "Should integrate multiple mentors"
        assert score.dimension_scores[QualityDimension.PERSONALIZATION] >= 85, "Should be highly personalized"
    
    def test_poor_workout_example(self):
        """Test with a poorly structured, unsafe workout"""
        
        workout_text = """
        Do some squats and push-ups. Maybe 3 sets. Add some weight if you want.
        """
        
        context = {}
        
        score = workout_quality_scorer.score_workout(workout_text, self.yoel_profile, context)
        
        # Assertions for poor workout
        assert score.overall_score < 60, f"Expected low score for poor workout, got {score.overall_score}"
        assert score.dimension_scores[QualityDimension.COMMUNICATION] < 50, "Should score poorly on communication"
        assert score.dimension_scores[QualityDimension.STRUCTURE] < 50, "Should score poorly on structure"
        assert score.dimension_scores[QualityDimension.PERSONALIZATION] < 40, "Should score poorly on personalization"
        assert score.grade in ["C+", "C"], f"Expected C grade, got {score.grade}"
        assert len(score.recommendations) >= 3, "Should have multiple improvement recommendations"
    
    def test_healthy_user_advanced_workout(self):
        """Test advanced workout for healthy user"""
        
        workout_text = """
        Ready for an advanced challenge! 
        
        **Power Session (45 minutes)**
        - Turkish get-ups (4 sets of 3 each side) - total body integration
        - Handstand progressions (15 minutes) - Emmet Louis style
        - Reverse nordics (3 sets of 5) - advanced Ben Patrick
        - Advanced kettlebell flows (15 minutes)
        
        This is high-intensity, high-skill work. Perfect for building serious strength and coordination!
        """
        
        context = {
            "equipment_available": ["kettlebells", "wall space"],
            "time_available": 45
        }
        
        score = workout_quality_scorer.score_workout(workout_text, self.healthy_profile, context)
        
        # Assertions for healthy user advanced workout
        assert score.dimension_scores[QualityDimension.SAFETY] >= 70, "Should be safe for healthy user"
        # Should not penalize for advanced exercises when user is healthy
        assert len([flag for flag in score.safety_flags if "not be suitable" in flag]) == 0, "Should not flag exercises for healthy user"


class TestMentorSpecificValidation:
    """Test mentor-specific exercise and principle validation"""
    
    def test_ben_patrick_exercise_recognition(self):
        """Test recognition of Ben Patrick exercises"""
        
        workout_text = "Let's do some tibialis raises and backward sled pulls, following Ben Patrick's approach."
        
        score = workout_quality_scorer.score_workout(workout_text, {}, {})
        
        assert "ben_patrick" in score.mentor_coverage
        assert score.mentor_coverage["ben_patrick"] > 0.5
    
    def test_mentor_principle_detection(self):
        """Test detection of mentor principles in text"""
        
        workout_text = """
        Following Ido Portal's philosophy of movement quality over quantity, 
        let's explore these patterns with Ben Patrick's full range of motion approach.
        """
        
        score = workout_quality_scorer.score_workout(workout_text, {}, {})
        
        assert score.dimension_scores[QualityDimension.MENTOR_ALIGNMENT] >= 60
        assert "ido_portal" in score.mentor_coverage
    
    def test_exercise_database_coverage(self):
        """Test that exercise database covers key mentor exercises"""
        
        exercises = workout_quality_scorer.exercise_db
        
        # Check Ben Patrick exercises
        assert "tibialis_raise" in exercises
        assert "reverse_nordic" in exercises
        assert exercises["tibialis_raise"].mentor_relevance == 1.0
        
        # Check Tom Merrick exercises  
        assert "pancake_stretch" in exercises
        assert exercises["pancake_stretch"].mentor_relevance == 1.0
        
        # Check safety classifications
        assert exercises["tibialis_raise"].injury_safe == True
        assert exercises["tibialis_raise"].joint_load <= 2


@pytest.fixture
def sample_workout_text():
    """Sample workout text for testing"""
    return """
    Hey Yoel! Based on your goals and current state, here's today's session:
    
    **Warm-up (8 minutes)**
    - Spinal waves (3 minutes) - Ido Portal style
    - Tibialis raises (2 sets of 15) - Ben Patrick for knee health
    
    **Main Session (30 minutes)**
    - Pancake stretch progression (Tom Merrick approach)
    - Kettlebell swings (Everydamnandré power focus)
    - Shoulder shrugs (Emmet Louis technique)
    
    **Cool-down (7 minutes)**
    - 4-7-8 breathing (Dylan Werner method)
    
    How does this feel for your current energy level?
    """


def test_comprehensive_scoring_pipeline(sample_workout_text):
    """Test the complete scoring pipeline"""
    
    user_profile = {
        "name": "Yoel",
        "injuries": ["meniscus_tear"],
        "goals": ["mobility", "strength"]
    }
    
    context = {
        "time_available": 45,
        "equipment_available": ["kettlebells"]
    }
    
    score = workout_quality_scorer.score_workout(sample_workout_text, user_profile, context)
    
    # Validate complete score object
    assert isinstance(score.overall_score, float)
    assert 0 <= score.overall_score <= 100
    assert len(score.dimension_scores) == 5
    assert isinstance(score.recommendations, list)
    assert isinstance(score.safety_flags, list)
    assert isinstance(score.mentor_coverage, dict)
    assert score.grade in ["A+", "A", "B+", "B", "C+", "C"]
