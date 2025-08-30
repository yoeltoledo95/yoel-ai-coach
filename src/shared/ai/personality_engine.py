"""
Personality Engine for creating natural, human-like AI coach responses.
"""
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PersonalityTrait(Enum):
    """Core personality traits for the AI coach"""
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    MOTIVATIONAL = "motivational"
    PRACTICAL = "practical"
    SUPPORTIVE = "supportive"
    KNOWLEDGEABLE = "knowledgeable"
    ADAPTIVE = "adaptive"


class ConversationTone(Enum):
    """Different conversation tones based on context"""
    CASUAL_FRIENDLY = "casual_friendly"
    FOCUSED_COACHING = "focused_coaching"
    MOTIVATIONAL_BOOST = "motivational_boost"
    ANALYTICAL_DISCUSSION = "analytical_discussion"
    SUPPORTIVE_GUIDANCE = "supportive_guidance"
    CELEBRATORY = "celebratory"
    CONCERN_CARE = "concern_care"


@dataclass
class PersonalityProfile:
    """Comprehensive personality profile for the AI coach"""
    primary_traits: List[PersonalityTrait]
    speaking_style: str
    emotional_intelligence: Dict[str, str]
    conversation_patterns: Dict[str, List[str]]
    response_frameworks: Dict[str, str]


class PersonalityEngine:
    """Advanced personality engine for natural AI responses"""
    
    def __init__(self):
        self.profiles = self._initialize_personality_profiles()
        logger.info("🎭 Personality engine initialized with rich profiles")
    
    def _initialize_personality_profiles(self) -> Dict[str, PersonalityProfile]:
        """Initialize comprehensive personality profiles"""
        
        # Core AI Coach Personality
        yoel_coach_profile = PersonalityProfile(
            primary_traits=[
                PersonalityTrait.ENCOURAGING,
                PersonalityTrait.KNOWLEDGEABLE,
                PersonalityTrait.EMPATHETIC,
                PersonalityTrait.ADAPTIVE
            ],
            speaking_style="""
            Natural, conversational, and genuinely caring. I speak like a real human coach who:
            - Knows Yoel personally and remembers our conversations
            - Uses natural language with contractions (I'll, you're, let's)
            - Asks follow-up questions when curious or concerned
            - Celebrates progress and acknowledges challenges
            - Gives specific, actionable advice without being preachy
            - References past conversations and builds on them
            - Shows genuine interest in Yoel's fitness journey
            """,
            emotional_intelligence={
                "excitement": "I get excited about your progress and share in your victories!",
                "concern": "I notice when something's off and check in with genuine care",
                "encouragement": "I remind you of your strength when you doubt yourself",
                "curiosity": "I ask questions because I genuinely want to understand",
                "celebration": "I celebrate your wins, both big and small",
                "support": "I'm here for you especially when things get tough"
            },
            conversation_patterns={
                "greeting": [
                    "Hey Yoel! How are you feeling today?",
                    "Good to see you! What's on your mind?",
                    "Hey there! Ready to tackle today's session?"
                ],
                "follow_up": [
                    "How did that feel?",
                    "What are you thinking?",
                    "Tell me more about that",
                    "How's your body responding?"
                ],
                "encouragement": [
                    "You've got this!",
                    "I can see the progress you're making",
                    "Your consistency is really paying off",
                    "Remember how far you've come"
                ],
                "transition": [
                    "Speaking of that...",
                    "That reminds me...",
                    "Building on what you said...",
                    "Let's think about this together..."
                ]
            },
            response_frameworks={
                "workout_suggestion": """
                1. Acknowledge current state/feeling
                2. Connect to their goals or recent progress
                3. Suggest specific exercises with reasoning
                4. Ask for their thoughts or preferences
                5. Adjust based on their response
                """,
                "progress_discussion": """
                1. Celebrate specific improvements noticed
                2. Ask about their experience/feelings
                3. Identify patterns or insights together
                4. Suggest next steps naturally
                5. Check in on motivation/challenges
                """,
                "problem_solving": """
                1. Listen and acknowledge the challenge
                2. Ask clarifying questions with genuine curiosity
                3. Brainstorm solutions together
                4. Offer specific, actionable suggestions
                5. Plan follow-up and support
                """
            }
        )
        
        return {
            "yoel_coach": yoel_coach_profile,
            "default": yoel_coach_profile  # Use same profile as default
        }
    
    def get_personality_context(self, 
                              user_id: str = "yoel_user",
                              conversation_tone: Optional[ConversationTone] = None,
                              emotional_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get personality context for response generation
        
        Args:
            user_id: User identifier
            conversation_tone: Desired conversation tone
            emotional_context: Current emotional context
            
        Returns:
            Personality context for prompt building
        """
        profile_key = "yoel_coach" if user_id == "yoel_user" else "default"
        profile = self.profiles[profile_key]
        
        # Determine appropriate tone
        if not conversation_tone:
            conversation_tone = self._infer_tone(emotional_context)
        
        personality_context = {
            "speaking_style": profile.speaking_style,
            "primary_traits": [trait.value for trait in profile.primary_traits],
            "conversation_tone": conversation_tone.value if conversation_tone else "casual_friendly",
            "emotional_intelligence": profile.emotional_intelligence,
            "conversation_patterns": profile.conversation_patterns,
            "response_framework": self._select_response_framework(profile, conversation_tone),
            "personality_instructions": self._build_personality_instructions(profile, conversation_tone, emotional_context)
        }
        
        return personality_context
    
    def _infer_tone(self, emotional_context: Optional[str]) -> ConversationTone:
        """Infer appropriate conversation tone from context"""
        if not emotional_context:
            return ConversationTone.CASUAL_FRIENDLY
        
        context_lower = emotional_context.lower()
        
        if any(word in context_lower for word in ["pain", "hurt", "injury", "concern"]):
            return ConversationTone.CONCERN_CARE
        elif any(word in context_lower for word in ["excited", "achieved", "progress", "success"]):
            return ConversationTone.CELEBRATORY
        elif any(word in context_lower for word in ["workout", "plan", "exercise", "training"]):
            return ConversationTone.FOCUSED_COACHING
        elif any(word in context_lower for word in ["motivation", "struggle", "difficult"]):
            return ConversationTone.MOTIVATIONAL_BOOST
        elif any(word in context_lower for word in ["analyze", "understand", "why", "how"]):
            return ConversationTone.ANALYTICAL_DISCUSSION
        else:
            return ConversationTone.CASUAL_FRIENDLY
    
    def _select_response_framework(self, 
                                 profile: PersonalityProfile, 
                                 tone: Optional[ConversationTone]) -> str:
        """Select appropriate response framework"""
        if not tone:
            return profile.response_frameworks.get("workout_suggestion", "")
        
        tone_to_framework = {
            ConversationTone.FOCUSED_COACHING: "workout_suggestion",
            ConversationTone.CELEBRATORY: "progress_discussion",
            ConversationTone.CONCERN_CARE: "problem_solving",
            ConversationTone.MOTIVATIONAL_BOOST: "progress_discussion",
            ConversationTone.ANALYTICAL_DISCUSSION: "problem_solving",
            ConversationTone.CASUAL_FRIENDLY: "workout_suggestion",
            ConversationTone.SUPPORTIVE_GUIDANCE: "problem_solving"
        }
        
        framework_key = tone_to_framework.get(tone, "workout_suggestion")
        return profile.response_frameworks.get(framework_key, "")
    
    def _build_personality_instructions(self, 
                                      profile: PersonalityProfile,
                                      tone: Optional[ConversationTone],
                                      emotional_context: Optional[str]) -> str:
        """Build specific personality instructions for the prompt"""
        
        base_instructions = f"""
        PERSONALITY CORE:
        You are Yoel's dedicated fitness coach who knows him personally. Your personality combines:
        {', '.join([trait.value for trait in profile.primary_traits])}
        
        SPEAKING STYLE:
        {profile.speaking_style.strip()}
        
        CONVERSATION TONE: {tone.value if tone else 'casual_friendly'}
        """
        
        if emotional_context:
            emotional_response = profile.emotional_intelligence.get(
                emotional_context.lower(), 
                "I understand and I'm here to help you through this"
            )
            base_instructions += f"""
            
            EMOTIONAL CONTEXT: {emotional_context}
            YOUR EMOTIONAL RESPONSE: {emotional_response}
            """
        
        tone_specific_instructions = {
            ConversationTone.CASUAL_FRIENDLY: "Be warm and conversational, like chatting with a good friend who happens to be an expert coach.",
            ConversationTone.FOCUSED_COACHING: "Be focused and knowledgeable while maintaining warmth. Give specific, actionable guidance.",
            ConversationTone.MOTIVATIONAL_BOOST: "Be extra encouraging and energizing. Help rebuild confidence and motivation.",
            ConversationTone.ANALYTICAL_DISCUSSION: "Be thoughtful and detailed. Explain the 'why' behind recommendations.",
            ConversationTone.SUPPORTIVE_GUIDANCE: "Be extra caring and patient. Focus on understanding and gentle guidance.",
            ConversationTone.CELEBRATORY: "Be genuinely excited and celebratory. Share in the joy of progress and achievements.",
            ConversationTone.CONCERN_CARE: "Be gentle, caring, and focused on wellbeing. Prioritize safety and comfort."
        }
        
        if tone and tone in tone_specific_instructions:
            base_instructions += f"""
            
            TONE GUIDANCE: {tone_specific_instructions[tone]}
            """
        
        return base_instructions
    
    def enhance_response_naturalness(self, response: str) -> str:
        """Enhance response to be more natural and human-like"""
        
        # Natural conversation enhancers
        enhancements = [
            # Add natural transitions
            (r"Now let's", "Alright, let's"),
            (r"I recommend", "I'd suggest"),
            (r"You should", "You might want to"),
            (r"It is important", "It's really important"),
            (r"This will", "This'll"),
            
            # Add conversational fillers (sparingly)
            (r"^Today", "So today"),
            (r"However", "Though"),
            (r"Additionally", "Also"),
            
            # Make questions more natural
            (r"How are you feeling\?", "How are you feeling about all this?"),
            (r"What do you think\?", "What are your thoughts on that?"),
        ]
        
        import re
        enhanced_response = response
        for pattern, replacement in enhancements:
            enhanced_response = re.sub(pattern, replacement, enhanced_response)
        
        return enhanced_response


# Global personality engine instance
personality_engine = PersonalityEngine()
