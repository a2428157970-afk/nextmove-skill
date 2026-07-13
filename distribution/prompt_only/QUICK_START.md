# Prompt-only Quick Start

**NEXTMOVE_PROMPT_ONLY**

1. Upload this Prompt-only Pilot Kit as reference material.
2. Tell the Agent that the current mode is Prompt-only and that it will not
   execute local Python Skill code.
3. Copy one template from [PROMPTS.md](PROMPTS.md).
4. Use the fictional resume and job description under `examples/` first.
5. Require the result to remain labelled `NEXTMOVE_PROMPT_ONLY`.

ChatGPT file upload provides reference context only; it will not execute the
local Python Skill. Do not claim that a preview came from the real NextMove
Runtime. For real execution, obtain the Runtime Skill Package, use a host with
Python 3.11+, and pass its offline readiness preflight.
