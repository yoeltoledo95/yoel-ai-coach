# AI Fitness Coach Project - Claude Configuration

## Project Architecture
**Type:** Next.js 14+ web app (App Router) with TypeScript  
**Package Manager:** npm (can switch to pnpm for faster installs)  
**Database:** PostgreSQL via Supabase (auth + database + vector search)  
**AI:** OpenAI API (GPT-4 for generation, GPT-3.5 for simple tasks)

## Essential Commands
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run test suite
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler
- `npm run db:migrate` - Run database migrations
- `npm run validate:mentors` - Validate mentor JSON structure

## File Structure
```
frontend/app/           # Next.js App Router pages
frontend/components/    # React components
frontend/lib/          # Utilities, hooks, API clients
backend/services/      # Business logic classes
backend/data/mentors/  # JSON knowledge base (8 files, ~50KB each)
database/migrations/   # SQL migration files
```

## Code Standards
**TypeScript Requirements:**
- Strict mode enabled - zero any types allowed
- All API responses must be properly typed
- Create interfaces from JSON structures systematically
- Use Zod for runtime validation schemas

**React Patterns:**
- Server components where possible
- Functional components only
- API routes handle OpenAI calls
- Use react-hook-form for forms
- Destructure imports: `import { foo } from 'bar'`

**Architecture:**
- Service classes for business logic
- Hybrid workout generation: 70% template-based, 20% AI creative, 10% hybrid
- Mentor knowledge in JSON files (not database) for easier updates

## Git Workflow
**Branch naming:** `phase-1-workout-engine`, `phase-2-planning`, etc.  
**Commits:** Conventional commits (`feat:`, `fix:`, `refactor:`)  
**Deployment:** Direct to main → Vercel auto-deploy  
**Always run typecheck before committing**

## Critical Performance Rules
**Token Optimization:**
- Use minimal prompts needed for GPT-4 calls
- Cache aggressively to reduce API costs
- Use GPT-3.5 for simple tasks, GPT-4 only for complex generation
- Calculate and monitor token usage in custom scripts

**Cost Management:**
- Cache workout generation results
- Batch API calls when possible
- Monitor OpenAI usage dashboard
- Set usage alerts

## Workout Safety Constraints
**CRITICAL:** Never exceed 30% week-to-week volume increases  
**Validation:** Always validate workout structure against safety rules  
**Mentor Authenticity:** Maintain each mentor's specific approach and philosophy

## Key Dependencies
```json
{
  "@supabase/supabase-js": "latest",
  "openai": "latest", 
  "zod": "latest",
  "recharts": "latest",
  "react-hook-form": "latest"
}
```

## Testing Strategy
**Framework:** Jest + React Testing Library  
**Coverage:** Target 80%+ for new features  
**Test Cases Needed:**
- Different user energy states (1-10 scale)
- Soreness map variations
- Available time constraints (15min to 2+ hours)
- Equipment availability scenarios

## Development Phases
**Phase 1 (Current):** Basic workout generation working  
**Phase 2:** Planning system (4-12 week mesocycles)  
**Phase 3:** Learning/pattern recognition from feedback  
**Phase 4:** Full coaching experience

## AI Generation Strategy
**User State Inputs:**
- Daily energy level (1-10)
- Soreness map (body regions)
- Available time
- Equipment access

**Planning System:**
- 4-12 week mesocycles
- Weekly check-ins and adjustments
- Pattern recognition from workout feedback

## Common Issues
**Build Problems:** Clear node_modules, reinstall dependencies  
**Type Errors:** Run full typecheck for complete context  
**Supabase Issues:** Check environment variables and connection  
**OpenAI API:** Monitor rate limits and token usage

## Custom Scripts
- Import mentor JSONs to database
- Validate workout structure against safety rules
- Calculate token usage across different prompt strategies
- Analyze workout generation patterns

---

## Claude Code Instructions

### Communication Style
**IMPORTANT:** Be direct and logical. No sugar coating or politeness.
- State problems clearly without softening language
- Provide solutions immediately after identifying issues
- Focus on what works, what doesn't, and how to fix it
- Zero fluff or unnecessary explanations

### Research Requirements
**YOU MUST follow this sequence:**
1. Read relevant files - explicitly state "not writing code yet"
2. Understand the complete problem scope
3. Use "ultrathink" for complex workout generation logic
4. Make detailed implementation plan
5. Get explicit approval before coding

### Implementation Standards
**Critical for this project:**
- Optimize every OpenAI API call for tokens and cost
- Validate all mentor data consistency
- Test workout safety rules rigorously
- Maintain type safety across all API boundaries
- Cache everything possible

### Workout Generation Specifics
**When working on workout logic:**
- Always validate against 30% volume increase rule
- Check mentor authenticity for generated content
- Test with multiple user state combinations
- Calculate token costs for different prompt strategies
- Verify exercise form instructions are complete

### Database Operations
**Supabase patterns:**
- Use TypeScript client with proper typing
- Handle auth state properly
- Implement row-level security where needed
- Use vector search for exercise similarity

### Error Handling Requirements
- Implement graceful OpenAI API failures
- Handle Supabase connection issues
- Validate all user inputs with Zod
- Log errors with sufficient context for debugging

### Performance Monitoring
**Track these metrics:**
- OpenAI token usage per workout generation
- API response times
- Database query performance
- Cache hit rates