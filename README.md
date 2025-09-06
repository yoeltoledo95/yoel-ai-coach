# AI Fitness Coach - Phase 1 Foundation

## Overview
Personal AI fitness coaching system built with Next.js 14, TypeScript, and Tom Merrick's flexibility expertise.

## Current Status
✅ **Phase 1 Foundation Complete**
- Next.js 14 project with TypeScript
- Tom Merrick knowledge base converted to TypeScript
- Workout generation engine implemented
- Basic UI for workout generation

## Architecture
- **Frontend**: Next.js 14 with App Router, TypeScript, Tailwind CSS
- **Data**: TypeScript interfaces for mentor knowledge and routines
- **Engine**: Local workout generation using mentor expertise
- **API**: Next.js API routes for workout generation

## Key Files
- `app/page.tsx` - Main landing page
- `app/workout/page.tsx` - Workout generator interface
- `app/api/workout/route.ts` - Workout generation API endpoint
- `lib/workout-engine.ts` - Core workout generation logic
- `lib/data/tom-merrick.ts` - Tom Merrick's knowledge base and routines

## Available Features
1. **Workout Generation**: Generate workouts based on natural language requests
2. **Mentor Knowledge**: Tom Merrick's flexibility routines and philosophy
3. **Smart Adaptation**: Automatic routine modification based on time/energy constraints
4. **Coaching Messages**: Contextual coaching advice for each workout

## Example Requests
- "I want to work on pancake flexibility"
- "Give me a quick 15 minute morning routine" 
- "I need some hip mobility work"
- "Something gentle, I'm tired today"

## Development
Since we have npm permission issues, the dependencies aren't installed yet. To run locally:

```bash
# Fix npm permissions first, then:
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

## Next Steps (Future Phases)
- Phase 2: User profiles and progress tracking (Supabase integration)
- Phase 3: AI learning and adaptation (OpenAI integration) 
- Phase 4: Full coach experience with planning and analysis

## Technology Stack
- **Next.js 14** - Full-stack React framework
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **No dependencies** - Local knowledge base, no external APIs needed for Phase 1