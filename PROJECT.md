# NextMove AI Project Config

## Mission
Help users make better career decisions with AI, instead of helping them blindly submit more resumes.

## Product
NextMove is an AI Career Intelligence Platform and AI Career Intelligence Skill Framework.

Slogan: Know Your Value. Find Your Next Career Move.

## Current Stage
Epic-020.1 Product Application Layer Boundary completed on the released v0.7.0
baseline. The deterministic Skill Core, optional AI boundary, and a
transport-neutral application workflow remain independently owned.

## Current Sprint
Product Application Layer Boundary completed.

## Current Goal
Prepare a bounded Epic-020.2 to validate application-owned request inputs and
response contracts without changing the Skill Core or adding a transport,
frontend, provider, persistence, or dependency.

## Tech Stack
- Frontend: Next.js
- Backend: FastAPI
- Database: Not selected yet
- AI: Optional provider-neutral enhancement with an injected-transport
  OpenAI-compatible adapter; no SDK, environment loading, or live default call

## Out Of Scope
- No business features
- No login system
- No AI features
- No database
- No resume submission automation

## Next Task
Epic-020.2: Application Request Boundary Validation.
