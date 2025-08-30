# AI Fitness Coach - Claude Code Context

## Project Overview
This is a personal AI fitness coaching system for Yoel, built with Python and Flask. The goal is to create a simple, effective chat-based fitness coach that leverages mentor knowledge and exercise databases.

## Current Architecture Issues
- **Over-engineered**: 11,000+ lines of code for what should be a simple chat bot
- **Complex dependencies**: 65 Python files with enterprise patterns
- **Performance problems**: Response times were 6-20 seconds before optimization
- **Maintenance burden**: Too many abstraction layers and complex dependency injection

## Target Architecture
We want to rebuild this as a simple, direct application:
- Single Flask app (~200 lines)
- Simple JSON data files
- Direct OpenAI integration
- No complex RAG systems
- No enterprise patterns

## Key Files
- `data/users/yoel_profile.json` - User profile with goals, injuries, preferences
- `data/exercises/exercise_kb.json` - Exercise database (132 exercises)
- `data/mentors/` - Mentor knowledge files
- `src/` - Current over-engineered codebase

## User Profile (Yoel)
- **Goals**: handstand, pancake flexibility, fix muscular imbalances
- **Injuries**: shoulder issues (ongoing), knee (recovered)
- **Training**: calisthenics, 4-6 days/week, movement quality focus
- **Mentors**: Ido Portal, Dylan Werner, Tom Merrick, etc.

## Development Goals
1. **Simplify**: Reduce from 11,000 lines to ~500 lines
2. **Performance**: Sub-second response times
3. **Maintainability**: Easy to understand and modify
4. **Functionality**: Same features, simpler implementation

## Commands
```bash
# Start the current app
python src/main.py

# Test the web interface
curl -X POST http://localhost:8001/api/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'
```

## Next Steps
1. Create simple app.py with basic functionality
2. Test with real conversations
3. Add features incrementally
4. Optimize performance
5. Polish UI/UX
