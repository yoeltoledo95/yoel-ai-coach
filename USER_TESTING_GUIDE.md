# 🤖 AI Coach User Testing Guide

## 🎯 **Testing Options Available**

### **1. Web Interface Testing (Recommended for Development)**
- **URL**: http://localhost:5001
- **Status**: ✅ Running
- **Features**: 
  - Interactive chat interface
  - Pre-built test scenarios
  - Real-time AI responses
  - No WhatsApp setup required

### **2. WhatsApp Integration Testing**
- **Status**: ✅ Ready (requires API key setup)
- **Endpoint**: http://localhost:8000/webhook
- **Features**: Real WhatsApp messaging

### **3. Automated Testing**
- **Script**: `python scripts/mock_testing.py`
- **Status**: ✅ Available
- **Features**: Component testing without API keys

## 🧪 **Test Scenarios to Try**

### **Beginner User Scenarios**
1. **New User**: "Hi! I'm new to fitness and want to get stronger. Can you help me create a workout plan?"
2. **Weight Loss**: "I want to lose weight and tone up. I have 30 minutes a day to work out."
3. **Equipment Limited**: "I only have dumbbells at home. What workouts can I do?"

### **Intermediate User Scenarios**
4. **Specific Exercise**: "I want to learn how to do a handstand. What's the best progression?"
5. **Injury Recovery**: "I have a knee injury from running. What exercises should I avoid?"
6. **Mobility Focus**: "My hips are really tight and I can't squat properly. Help me improve my mobility."

### **Advanced User Scenarios**
7. **Mentor-Specific**: "I want to train like Ido Portal. What exercises should I focus on?"
8. **Weekly Planning**: "Can you create a weekly workout plan for me? I want to build muscle and improve my cardio."
9. **Nutrition**: "What should I eat before and after my workouts?"

### **Motivation & Support Scenarios**
10. **Motivation**: "I'm feeling unmotivated to work out today. Can you help me get motivated?"
11. **Progress Tracking**: "How can I track my progress effectively?"
12. **Recovery**: "I'm feeling sore after yesterday's workout. What should I do?"

## 📊 **What to Test**

### **AI Response Quality**
- ✅ **Relevance**: Does the response address the user's question?
- ✅ **Specificity**: Does it provide specific exercises/advice?
- ✅ **Safety**: Does it consider injuries and limitations?
- ✅ **Progression**: Does it suggest appropriate progressions/regressions?

### **Mentor Integration**
- ✅ **Dylan Werner**: Yoga, breathing, mindfulness focus
- ✅ **Ido Portal**: Movement culture, complexity, flow
- ✅ **Tom Merrick**: Calisthenics, bodyweight strength
- ✅ **KneesOverToesGuy**: Joint health, knee safety
- ✅ **Emmet Louis**: Mobility, flexibility, end-range strength

### **Exercise Recommendations**
- ✅ **Equipment Matching**: Suggests exercises for available equipment
- ✅ **Injury Awareness**: Avoids exercises that could aggravate injuries
- ✅ **Progressive Overload**: Suggests appropriate progressions
- ✅ **Multi-Mentor Support**: Combines expertise from multiple mentors

### **System Features**
- ✅ **Context Awareness**: Remembers user goals and limitations
- ✅ **Personalization**: Adapts to user experience level
- ✅ **Safety First**: Prioritizes injury prevention
- ✅ **Motivational Support**: Provides encouragement and guidance

## 🚀 **How to Start Testing**

### **Option 1: Web Interface (Easiest)**
1. Open browser to: http://localhost:5001
2. Try the pre-built test scenarios
3. Type custom messages in the input field
4. Evaluate AI responses

### **Option 2: WhatsApp Testing**
1. Set up WhatsApp Business API
2. Configure webhook to: http://localhost:8000/webhook
3. Send messages through WhatsApp
4. Check responses in real-time

### **Option 3: Direct API Testing**
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi! I need help with my workout plan"}'
```

## 📝 **Testing Checklist**

### **Functionality Tests**
- [ ] AI responds to basic fitness questions
- [ ] Exercise recommendations are appropriate
- [ ] Mentor-specific advice is provided
- [ ] Safety considerations are mentioned
- [ ] Progressions/regressions are suggested

### **Quality Tests**
- [ ] Responses are helpful and actionable
- [ ] Language is clear and motivating
- [ ] Exercises are properly described
- [ ] Safety warnings are included when needed
- [ ] Multiple mentor perspectives are integrated

### **User Experience Tests**
- [ ] Response time is reasonable (< 5 seconds)
- [ ] Messages are well-formatted
- [ ] Advice is personalized to user context
- [ ] Follow-up questions are appropriate
- [ ] Encouragement and motivation are provided

## 🐛 **Bug Reporting**

If you encounter issues:

1. **Note the exact message sent**
2. **Record the AI response received**
3. **Describe what you expected**
4. **Include any error messages**
5. **Report via**: Create an issue in the repository

## 📈 **Performance Metrics**

Track these metrics during testing:

- **Response Quality**: 1-5 scale
- **Relevance**: Does it answer the question?
- **Safety**: Are safety considerations included?
- **Specificity**: Are specific exercises mentioned?
- **Motivation**: Does it encourage the user?

## 🎯 **Success Criteria**

The AI Coach should:

✅ **Provide helpful, actionable advice**
✅ **Consider user safety and limitations**
✅ **Integrate multiple mentor perspectives**
✅ **Suggest appropriate exercises and progressions**
✅ **Maintain a motivating and supportive tone**
✅ **Remember user context and preferences**
✅ **Respond quickly and consistently**

## 🔧 **Technical Setup**

### **Current Status**
- ✅ **Main App**: Running on port 8000
- ✅ **Test Interface**: Running on port 5001
- ✅ **Database**: SQLite with 132 exercises
- ✅ **Mentor Knowledge**: 10 mentors with detailed expertise
- ✅ **RAG System**: Vector-based knowledge retrieval
- ✅ **Multi-Mentor Support**: Exercises can have multiple mentors

### **System Components**
- **Exercise Library**: 132 exercises with mentor assignments
- **Mentor Knowledge**: 10 comprehensive mentor profiles
- **RAG System**: Retrieves relevant mentor context
- **Prompt Engine**: Builds contextual prompts
- **Database**: Stores user data and feedback

## 🎉 **Ready to Test!**

Your AI Coach is ready for comprehensive user testing. Start with the web interface at http://localhost:5001 and explore the various test scenarios to evaluate the system's performance and user experience. 