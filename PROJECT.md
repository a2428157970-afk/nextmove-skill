# NextMove AI Project Config

## Mission
Help users make better career decisions with AI, instead of helping them blindly submit more resumes.

## Product
NextMove is an AI Career Intelligence Platform and AI Career Intelligence Skill Framework.

Slogan: Know Your Value. Find Your Next Career Move.

## Current Stage
Epic-025.1 Domain-aware Job Matching and Epic-025.2 Career Stage Model are
merged. NextMove now classifies a focused v1 career taxonomy, scores Domain,
Skill, and Qualification evidence, and derives an internal evidence-based stage
assessment for analysis and advice without changing public contracts. Git
release work remains paused.

## Current Sprint
Epic-025 Career Intelligence Quality.

## Current Goal
Continue Epic-025.3 Evidence-based Match Explanation using the merged
domain-aware matching baseline, then validate HR, technical, career-transition,
and insufficient-information fixtures without exposing new public result fields.

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
Execute Epic-025.3 implementation only through its approved TDD plan. Keep
explanation data internal until a separately approved Agent-contract versioning
Epic; do not resume release work as part of that step.
