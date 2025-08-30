"""
End-to-end tests for complete user journeys.
Tests realistic user scenarios from start to finish.
"""
import pytest
import json
from unittest.mock import Mock, patch


class TestNewUserOnboarding:
    """Test complete new user onboarding journey"""
    
    def test_new_user_complete_journey(self, app_client):
        """Test complete new user journey from greeting to workout"""
        # Mock realistic coaching responses
        mock_responses = [
            # Greeting response
            Mock(
                response="Hello! I'm your AI fitness coach. I'm here to help you achieve your fitness goals. What brings you here today?",
                mentors_used=[],
                intent="greeting"
            ),
            # Goal setting response
            Mock(
                response="Excellent goals! Building strength and improving flexibility is a great combination. Based on your interests, I'd recommend starting with bodyweight exercises. Are you completely new to fitness, or do you have some experience?",
                mentors_used=["tom_merrick"],
                intent="goal_setting"
            ),
            # Experience assessment response
            Mock(
                response="Perfect! As a beginner, we'll focus on building a solid foundation with proper form. I'll create a beginner-friendly routine that combines strength and flexibility. Would you like me to design your first workout?",
                mentors_used=["tom_merrick", "dylan_werner"],
                intent="experience_assessment"
            ),
            # Workout generation response
            Mock(
                response="""Great! Here's your personalized beginner workout:

**Warm-up (5 minutes):**
- Arm circles: 30 seconds each direction
- Leg swings: 30 seconds each leg
- Gentle stretching: 3 minutes

**Main Workout (20 minutes):**
1. **Wall Push-ups** - 2 sets of 8-12 reps
   Focus on controlled movement and proper form
   
2. **Bodyweight Squats** - 2 sets of 10-15 reps
   Keep your chest up and weight in your heels
   
3. **Modified Plank** - 2 sets of 15-30 seconds
   Start on knees if needed, build up gradually
   
4. **Standing Forward Fold** - Hold for 30 seconds
   Gentle stretch for hamstrings and back

**Cool-down (5 minutes):**
- Deep breathing and gentle stretching

Start with this 2-3 times per week. How does this look for your first week?""",
                mentors_used=["tom_merrick", "dylan_werner"],
                intent="workout_request"
            ),
            # Follow-up response
            Mock(
                response="Wonderful! Remember, consistency is key. Start slowly and focus on proper form rather than speed or intensity. If any exercise feels uncomfortable, stop and ask me for modifications. I'm here to support you every step of the way. Good luck with your first workout!",
                mentors_used=["tom_merrick"],
                intent="encouragement"
            )
        ]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = mock_responses
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Initial greeting
            response1 = app_client.post('/api/chat', json={
                'user_id': 'new_user_001',
                'message': 'Hello! I\'m new here.'
            })
            
            assert response1.status_code == 200
            data1 = json.loads(response1.data)
            assert data1['status'] == 'success'
            assert 'fitness coach' in data1['response'].lower()
            assert 'goals' in data1['response'].lower()
            
            # Step 2: User shares goals
            response2 = app_client.post('/api/chat', json={
                'user_id': 'new_user_001', 
                'message': 'I want to build strength and improve my flexibility.'
            })
            
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            assert 'strength' in data2['response'].lower()
            assert 'flexibility' in data2['response'].lower()
            assert 'tom_merrick' in data2['mentors_used']
            
            # Step 3: User indicates experience level
            response3 = app_client.post('/api/chat', json={
                'user_id': 'new_user_001',
                'message': 'I\'m a complete beginner to fitness.'
            })
            
            assert response3.status_code == 200
            data3 = json.loads(response3.data)
            assert 'beginner' in data3['response'].lower()
            assert 'foundation' in data3['response'].lower()
            assert len(data3['mentors_used']) >= 1
            
            # Step 4: User requests workout
            response4 = app_client.post('/api/chat', json={
                'user_id': 'new_user_001',
                'message': 'Yes, please create my first workout!'
            })
            
            assert response4.status_code == 200
            data4 = json.loads(response4.data)
            assert 'workout' in data4['response'].lower()
            assert 'push-ups' in data4['response'].lower()
            assert 'squats' in data4['response'].lower()
            assert 'plank' in data4['response'].lower()
            assert len(data4['mentors_used']) >= 2
            
            # Step 5: User confirms understanding
            response5 = app_client.post('/api/chat', json={
                'user_id': 'new_user_001',
                'message': 'This looks perfect! Thank you!'
            })
            
            assert response5.status_code == 200
            data5 = json.loads(response5.data)
            assert 'consistency' in data5['response'].lower() or 'form' in data5['response'].lower()
            
            # Verify all interactions were successful
            assert all(response.status_code == 200 for response in [response1, response2, response3, response4, response5])


class TestExperiencedUserJourney:
    """Test journey for experienced user seeking advanced guidance"""
    
    def test_experienced_user_advanced_workout(self, app_client):
        """Test experienced user requesting advanced workout"""
        mock_responses = [
            Mock(
                response="Hey there! I can see you're experienced with training. What specific goals are you working towards right now?",
                mentors_used=[],
                intent="greeting"
            ),
            Mock(
                response="Handstand training is incredibly rewarding! Based on your calisthenics background, I'll design a progression-focused session. Do you have any current limitations or areas you'd like to emphasize?",
                mentors_used=["emmet_louis", "tom_merrick"],
                intent="goal_assessment"
            ),
            Mock(
                response="""Perfect! Here's an advanced handstand progression workout:

**Handstand-Focused Session (45 minutes):**

**Warm-up (10 minutes):**
- Wrist preparation sequence
- Shoulder mobility complex
- Hollow body progression

**Skill Work (25 minutes):**
1. **Wall Handstand Holds** - 5 sets of 30-60 seconds
   Focus on perfect line and shoulder engagement
   
2. **Freestanding Attempts** - 10 minutes practice
   Short, quality holds with proper entry
   
3. **Handstand Push-up Progression** - 4 sets
   Current level with 1-2 challenge reps
   
4. **L-sit to Handstand Transitions** - 3 sets of 3-5
   Advanced coordination work

**Strength Supplement (10 minutes):**
- Pseudo planche push-ups: 3x8
- Pike push-ups: 3x10
- Hollow body rocks: 3x15

The key is consistent daily practice with perfect form. How does this align with your current training?""",
                mentors_used=["emmet_louis", "tom_merrick", "ido_portal"],
                intent="advanced_workout"
            )
        ]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = mock_responses
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Experienced user greeting
            response1 = app_client.post('/api/chat', json={
                'user_id': 'experienced_user_001',
                'message': 'Hi! I\'ve been training calisthenics for 3 years.'
            })
            
            assert response1.status_code == 200
            data1 = json.loads(response1.data)
            assert 'experienced' in data1['response'].lower()
            
            # Step 2: Specific goal
            response2 = app_client.post('/api/chat', json={
                'user_id': 'experienced_user_001',
                'message': 'I want to improve my handstand. I can hold it for about 10 seconds consistently.'
            })
            
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            assert 'handstand' in data2['response'].lower()
            assert len(data2['mentors_used']) >= 2
            
            # Step 3: Request specific workout
            response3 = app_client.post('/api/chat', json={
                'user_id': 'experienced_user_001',
                'message': 'I have good shoulder mobility but want to work on my handstand push-ups too.'
            })
            
            assert response3.status_code == 200
            data3 = json.loads(response3.data)
            assert 'handstand' in data3['response']
            assert 'push-up' in data3['response']
            assert 'progression' in data3['response'].lower()
            assert len(data3['mentors_used']) >= 2


class TestYoelSpecificJourney:
    """Test journey specific to Yoel's profile and goals"""
    
    def test_yoel_personalized_session(self, app_client):
        """Test Yoel's personalized coaching experience"""
        mock_responses = [
            Mock(
                response="Hey Yoel! Good to see you. How are you feeling today? Any shoulder issues or areas you want to focus on?",
                mentors_used=["dylan_werner"],
                intent="check_in"
            ),
            Mock(
                response="""Perfect! Here's a shoulder-friendly session focusing on your handstand and pancake goals:

**Today's Session - Shoulder Health + Skills (50 minutes):**

**Shoulder Prep (10 minutes):**
- Gentle rotations and band work
- Wall angels progression
- Scapular stability drills

**Handstand Work (20 minutes):**
- Wall-supported holds with perfect alignment
- Slow, controlled entries (Emmet Louis style)
- Core integration work (Dylan Werner approach)

**Pancake Flexibility (15 minutes):**
- Active stretching with strength components
- Isometric holds in end ranges
- Hip flexor integration work

**Recovery Focus (5 minutes):**
- Breath work and gentle movement
- Shoulder decompression

This balances your goals while respecting your shoulder. The Ido Portal movement principles are woven throughout for natural patterns. Sound good?""",
                mentors_used=["emmet_louis", "dylan_werner", "ido_portal", "tom_merrick"],
                intent="personalized_workout"
            )
        ]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = mock_responses
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Yoel check-in (should trigger special user handling)
            response1 = app_client.post('/api/chat', json={
                'user_name': 'Yoel',  # This should map to yoel_user
                'message': 'Hey coach, ready for today\'s session.'
            })
            
            assert response1.status_code == 200
            data1 = json.loads(response1.data)
            assert 'yoel' in data1['response'].lower()
            assert 'shoulder' in data1['response'].lower()
            
            # Step 2: Yoel's specific request
            response2 = app_client.post('/api/chat', json={
                'user_name': 'Yoel',
                'message': 'Feeling good today! Want to work on handstand progression and pancake flexibility. Shoulder is feeling stable.'
            })
            
            assert response2.status_code == 200
            data2 = json.loads(response2.data)
            assert 'handstand' in data2['response']
            assert 'pancake' in data2['response']
            assert 'shoulder' in data2['response']
            assert len(data2['mentors_used']) >= 3  # Should reference multiple mentors
            
            # Verify Yoel's mentors are included
            expected_mentors = ['emmet_louis', 'dylan_werner', 'ido_portal']
            assert any(mentor in data2['mentors_used'] for mentor in expected_mentors)


class TestErrorScenarios:
    """Test user journeys with error scenarios"""
    
    def test_user_journey_with_service_interruption(self, app_client):
        """Test user journey resilience to service interruptions"""
        mock_responses = [
            Mock(response="Hello! How can I help?", mentors_used=[]),
            Exception("Service temporarily unavailable"),  # Simulated error
            Mock(response="I'm back! Sorry about that interruption. How can I assist you?", mentors_used=[])
        ]
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = mock_responses
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            # Step 1: Successful interaction
            response1 = app_client.post('/api/chat', json={
                'user_id': 'resilient_user',
                'message': 'Hello coach'
            })
            
            assert response1.status_code == 200
            
            # Step 2: Service error
            response2 = app_client.post('/api/chat', json={
                'user_id': 'resilient_user', 
                'message': 'What workout should I do?'
            })
            
            assert response2.status_code == 500
            data2 = json.loads(response2.data)
            assert data2['status'] == 'error'
            
            # Step 3: Recovery
            response3 = app_client.post('/api/chat', json={
                'user_id': 'resilient_user',
                'message': 'Are you working now?'
            })
            
            assert response3.status_code == 200
            data3 = json.loads(response3.data)
            assert 'back' in data3['response'].lower() or 'sorry' in data3['response'].lower()


class TestPerformanceJourney:
    """Test user journey with performance validation"""
    
    def test_response_time_during_user_journey(self, app_client):
        """Test that response times remain acceptable during user journey"""
        import time
        
        mock_response = Mock(
            response="Here's your workout...",
            mentors_used=["tom_merrick"]
        )
        
        with patch('application.container.container') as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_response
            mock_container.get_get_coaching_response_use_case.return_value = mock_use_case
            
            response_times = []
            
            # Make several requests and measure response times
            for i in range(5):
                start_time = time.time()
                
                response = app_client.post('/api/chat', json={
                    'user_id': 'performance_user',
                    'message': f'Request number {i+1}'
                })
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert response.status_code == 200
                
                # Each response should be under 2 seconds (reasonable for test environment)
                assert response_time < 2.0
            
            # Average response time should be reasonable
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 1.0  # Average under 1 second
