# NextMove AI Project Config

## Mission
Help users make better career decisions with AI, instead of helping them blindly submit more resumes.

## Product
NextMove is an AI Career Intelligence Platform and AI Career Intelligence Skill Framework.

Slogan: Know Your Value. Find Your Next Career Move.

## Current Stage
Epic-025.1 Domain-aware Job Matching, Epic-025.2 Career Stage Model,
Epic-025.3 Evidence-based Match Explanation, and Epic-025.4 Career Intelligence
Quality Benchmark are complete. Epic-025.5A Career Taxonomy Expansion adds
Product job families and bounded Sales-to-Product and Administration-to-HR
transfer evidence. Five fictional offline scenarios now pass Domain, Career
Stage, Evidence, Explanation, and Safety checks without changing public
contracts. Git release work remains paused.

## Current Sprint
Epic-025 Career Intelligence Quality.

## Current Goal
Keep the expanded taxonomy stable and use the benchmark to select any next
domain or capability expansion. Continue to preserve direct-versus-transferable
evidence semantics and public contracts.

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
Design the next benchmark-guided taxonomy increment only after reviewing real
quality gaps. Do not weaken benchmark expectations, resume release work, or
expose internal explanation/transfer data without a separate contract Epic.
