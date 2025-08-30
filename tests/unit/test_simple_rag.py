"""
Unit tests for SimpleMentorRAG system.
Tests mentor selection, context generation, and performance.
"""
import pytest
from unittest.mock import Mock, patch
from infrastructure.database.vector_store.simple_rag import SimpleMentorRAG


class TestSimpleMentorRAG:
    """Test SimpleMentorRAG functionality"""
    
    @pytest.fixture
    def rag_system(self):
        """Create SimpleMentorRAG instance for testing"""
        with patch('infrastructure.database.vector_store.simple_rag.MENTOR_KNOWLEDGE') as mock_mentors:
            mock_mentors = {
                'tom_merrick': {
                    'name': 'Tom Merrick',
                    'focus': 'Calisthenics and flexibility',
                    'philosophy': 'Clean movement patterns and progressive overload',
                    'key_principles': ['Form first', 'Progressive overload', 'Consistency'],
                    'exercise_library': [
                        {'name': 'Push-ups', 'description': 'Basic upper body exercise'},
                        {'name': 'Handstand', 'description': 'Advanced balance and strength'}
                    ]
                },
                'dylan_werner': {
                    'name': 'Dylan Werner',
                    'focus': 'Yoga and isometric strength',
                    'philosophy': 'Mind-body connection through movement',
                    'key_principles': ['Breath awareness', 'Isometric holds', 'Body control'],
                    'exercise_library': [
                        {'name': 'Warrior III', 'description': 'Balance and stability pose'},
                        {'name': 'Plank variations', 'description': 'Core strength exercises'}
                    ]
                },
                'everydamnandre': {
                    'name': 'Everydamnandré',
                    'focus': 'Kettlebell training',
                    'philosophy': 'Functional strength through kettlebell movements',
                    'key_principles': ['Hip hinge mastery', 'Power generation', 'Mental toughness'],
                    'exercise_library': [
                        {'name': 'Kettlebell swing', 'description': 'Fundamental kettlebell movement'},
                        {'name': 'Turkish get-up', 'description': 'Full body coordination exercise'}
                    ]
                }
            }
            
            rag = SimpleMentorRAG()
            rag.mentors = mock_mentors
            return rag
    
    def test_initialization(self, rag_system):
        """Test SimpleMentorRAG initialization"""
        assert rag_system is not None
        assert hasattr(rag_system, 'mentors')
        assert len(rag_system.mentors) == 3
        assert 'tom_merrick' in rag_system.mentors
        assert 'dylan_werner' in rag_system.mentors
        assert 'everydamnandre' in rag_system.mentors
    
    def test_keyword_based_mentor_selection(self, rag_system):
        """Test mentor selection based on keywords"""
        # Test calisthenics keyword
        mentors = rag_system._select_mentors_by_keywords("I want to learn calisthenics")
        assert 'tom_merrick' in mentors
        
        # Test yoga keyword
        mentors = rag_system._select_mentors_by_keywords("I'm interested in yoga")
        assert 'dylan_werner' in mentors
        
        # Test kettlebell keyword
        mentors = rag_system._select_mentors_by_keywords("Show me kettlebell workouts")
        assert 'everydamnandre' in mentors
        
        # Test flexibility keyword
        mentors = rag_system._select_mentors_by_keywords("I need help with flexibility")
        assert any(mentor in ['tom_merrick', 'dylan_werner'] for mentor in mentors)
    
    def test_mentor_selection_fallback(self, rag_system):
        """Test fallback mentor selection for general queries"""
        mentors = rag_system._select_mentors_by_keywords("general fitness question")
        
        # Should return default mentors
        assert len(mentors) > 0
        assert len(mentors) <= 4  # Max 4 mentors
        assert 'dylan_werner' in mentors  # Should include default mentors
        assert 'tom_merrick' in mentors
    
    def test_mentor_selection_deduplication(self, rag_system):
        """Test mentor selection removes duplicates"""
        # Query that might match multiple keywords for same mentor
        mentors = rag_system._select_mentors_by_keywords("calisthenics strength flexibility")
        
        # Should not have duplicates
        assert len(mentors) == len(set(mentors))
        assert 'tom_merrick' in mentors
    
    def test_mentor_context_generation(self, rag_system):
        """Test mentor context generation"""
        context = rag_system.get_mentor_context("What's the best way to do push-ups?")
        
        assert context is not None
        assert len(context) > 0
        assert isinstance(context, str)
        
        # Should contain mentor information
        assert any(mentor in context.lower() for mentor in ['tom merrick', 'dylan werner'])
        
        # Should contain relevant content
        assert any(keyword in context.lower() for keyword in ['form', 'movement', 'strength'])
    
    def test_mentor_context_with_specific_mentors(self, rag_system):
        """Test mentor context generation with specific mentors"""
        specified_mentors = ['tom_merrick', 'dylan_werner']
        context = rag_system.get_mentor_context(
            "How do I improve my push-ups?", 
            mentor_names=specified_mentors
        )
        
        assert context is not None
        assert 'Tom Merrick' in context
        assert 'Dylan Werner' in context
        assert 'Everydamnandré' not in context  # Should not include unspecified mentor
    
    def test_mentor_context_limits_mentors(self, rag_system):
        """Test mentor context limits to max 4 mentors"""
        # This test would be more relevant with more than 4 mentors
        # For now, test that it handles the limit correctly
        all_mentors = list(rag_system.mentors.keys())
        context = rag_system.get_mentor_context("general question", mentor_names=all_mentors)
        
        assert context is not None
        # Should handle all available mentors gracefully
        assert len(context) > 0
    
    def test_relevant_exercises_extraction(self, rag_system):
        """Test relevant exercise extraction from mentor libraries"""
        mentor_data = rag_system.mentors['tom_merrick']
        exercises = rag_system._get_relevant_exercises(mentor_data, "push-ups handstand")
        
        assert isinstance(exercises, list)
        assert len(exercises) <= 3  # Max 3 exercises
        
        # Should include relevant exercises
        exercise_names = [ex.lower() for ex in exercises]
        assert any('push' in name for name in exercise_names)
    
    def test_relevant_exercises_with_dict_format(self, rag_system):
        """Test exercise extraction with dictionary format"""
        mentor_data = rag_system.mentors['tom_merrick']
        exercises = rag_system._get_relevant_exercises(mentor_data, "push")
        
        # Should extract exercise names from dict format
        assert isinstance(exercises, list)
        if exercises:
            assert all(isinstance(ex, str) for ex in exercises)
    
    def test_relevant_exercises_no_matches(self, rag_system):
        """Test exercise extraction with no matches"""
        mentor_data = rag_system.mentors['tom_merrick']
        exercises = rag_system._get_relevant_exercises(mentor_data, "completely unrelated query")
        
        assert isinstance(exercises, list)
        # May be empty or have default exercises
    
    def test_get_statistics(self, rag_system):
        """Test statistics generation"""
        stats = rag_system.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_mentors' in stats
        assert 'system_type' in stats
        assert 'avg_response_time' in stats
        
        assert stats['total_mentors'] == 3
        assert stats['system_type'] == 'simple_keyword_based'
        assert stats['avg_response_time'] == '<0.1s'
    
    def test_performance_characteristics(self, rag_system):
        """Test performance characteristics of simple RAG"""
        import time
        
        start_time = time.time()
        context = rag_system.get_mentor_context("What's the best workout for strength?")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should be very fast (under 0.1 seconds)
        assert response_time < 0.1
        assert context is not None
        assert len(context) > 0
    
    def test_error_handling_missing_mentor(self, rag_system):
        """Test error handling when mentor is missing"""
        # Request specific mentor that doesn't exist
        context = rag_system.get_mentor_context(
            "Test query", 
            mentor_names=['nonexistent_mentor']
        )
        
        # Should handle gracefully without crashing
        assert context is not None
        # May be empty or contain fallback content
    
    def test_error_handling_malformed_mentor_data(self, rag_system):
        """Test error handling with malformed mentor data"""
        # Add malformed mentor data
        rag_system.mentors['malformed_mentor'] = {
            'name': 'Malformed Mentor',
            # Missing required fields
        }
        
        context = rag_system.get_mentor_context(
            "Test query", 
            mentor_names=['malformed_mentor']
        )
        
        # Should handle gracefully
        assert context is not None
    
    def test_context_content_structure(self, rag_system):
        """Test mentor context content structure"""
        context = rag_system.get_mentor_context("Help me with flexibility")
        
        # Should contain structured mentor information
        assert '**' in context  # Bold formatting for names
        assert 'Philosophy:' in context
        assert 'Key Principles:' in context
        
        # Should be well-formatted
        lines = context.split('\n')
        assert len(lines) > 1  # Multi-line content
    
    def test_context_truncation_and_limits(self, rag_system):
        """Test context respects limits and truncation"""
        # Test with query that matches many mentors
        context = rag_system.get_mentor_context("strength flexibility movement")
        
        # Should not be excessively long
        assert len(context) < 5000  # Reasonable limit
        
        # Should contain multiple mentors but be manageable
        mentor_count = context.count('**')  # Count mentor name markers
        assert mentor_count <= 4  # Respects max mentor limit
