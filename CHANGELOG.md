# NextMove Changelog

## 0.5.0

- Status: Release preparation complete
- Added the initial public release scope for the standalone AI Career
  Intelligence Skill:
  - Resume Analysis
  - Resume Improvement
  - Job Matching
  - Career Advice
- Added the provider-neutral Agent Tool Schema and Tool Registry.
- Added `AgentRuntime` for registered Agent Tool invocation.
- Added GitHub-facing documentation for the Skill API, architecture,
  contribution model, and release workflow.
- Added runnable examples, including the full career analysis workflow.

## Epic-004.3 - Package Polish & Release Preparation

- Status: Completed
- Completed:
  - Added `skill/__version__.py` as the single source of truth for Skill package version.
  - Updated `skill/metadata.py` to use the shared package version.
  - Expanded `skill/__init__.py` public exports to include `NextMoveSkill`, `SkillResponse`, `SkillError`, and `__version__`.
  - Added a minimal `pyproject.toml` for future editable installs and packaging readiness.
  - Added package import tests for public API exports and metadata version consistency.
  - Added README installation guidance with `pip install -e .`.

## Epic-004.2 - Skill Packaging Readiness

- Status: Completed
- Completed:
  - Added `skill.utils.to_dict()` for JSON-serializable Skill result, `SkillResponse`, and `SkillError` conversion.
  - Added `skill/metadata.py` with Skill name, version, capabilities, and Agent discovery description.
  - Added Skill usage documentation to `README.md`, including initialization, `run()` calls, capabilities, and input/output examples.
  - Added runnable examples for resume analysis and job matching.
  - Added serialization and metadata tests.

## Epic-004.1 - Skill API Stabilization

- Status: Completed
- Completed:
  - Added provider-neutral `SkillError` and `SkillResponse` schemas for Agent-friendly calls.
  - Added `NextMoveSkill.run(capability, payload)` as a unified compatible API entrypoint.
  - Preserved direct methods and their original business result return types.
  - Renamed `match_job()` parameter from `job` to `job_description`.
  - Added structured success and error responses for supported capabilities, unknown capabilities, and invalid input.
  - Added tests covering all four capabilities through the unified Skill API.

## Epic-003.3 - Career Advice Skill

- Status: Completed
- Completed:
  - Added `skill/career/` with structured schema exports and a rule-based `CareerAdvisor`.
  - Added `CareerAdviceResult` with `current_level`, `possible_paths`, `skill_gaps`, and `recommended_actions`.
  - Connected `NextMoveSkill.career_advice()` to parse resumes when needed and reuse resume analysis when not provided.
  - Implemented first-pass career level inference, data/technical/management path detection, skill gap advice, and recommended actions.
  - Added unit tests for no-experience resumes, technical backgrounds, management backgrounds, and public Skill interface behavior.

## Epic-003.2 - Job Matching Skill

- Status: Completed
- Completed:
  - Added `skill/matching/` with structured schema exports and a rule-based `JobMatcher`.
  - Added `JobMatchResult` with `match_score`, `matched_skills`, `missing_skills`, `strengths`, `gaps`, and `recommendations`.
  - Connected `NextMoveSkill.match_job()` to parse resumes when needed and match against a job description string.
  - Implemented first-pass keyword matching, skill gap detection, and 0-100 scoring based on skill overlap plus work experience.
  - Added unit tests for high match, skill gaps, empty resume, and public Skill interface behavior.

## Epic-003.1 - Resume Improvement Skill

- Status: Completed
- Completed:
  - Added `skill/improvement/` with structured schema exports and a rule-based `ResumeImprover`.
  - Added `ResumeImprovementResult` with `issues`, `suggestions`, and `improved_sections`.
  - Connected `NextMoveSkill.improve_resume()` to parse, analyze, and improve resumes without AI provider dependencies.
  - Generated first-pass suggestions from analysis weaknesses for missing summaries, limited skills, missing skills, missing experience, missing projects, and unquantified outcomes.
  - Added unit tests for direct `ResumeImprover` use and the public Skill interface.

## Epic-002.4 - Skill Interface Integration

- Status: Completed
- Completed:
  - Connected `NextMoveSkill.analyze_resume()` to the Skill Core parser and analyzer.
  - Supported `str` input through `RuleBasedResumeParser.parse()`.
  - Supported `ResumeProfile` input through direct `ResumeAnalyzer.analyze()` execution.
  - Kept `improve_resume()`, `match_job()`, and `career_advice()` as explicit placeholders.
  - Added interface-level unit tests for text input, profile input, and placeholder responses.

## Epic-002.2 - Skill Core Bootstrap

- Status: Completed
- Completed:
  - Initialized standalone `skill/` core package.
  - Added first version of provider-neutral resume and analysis schemas.
  - Added `NextMoveSkill` interface with explicit placeholder responses.
  - Preserved existing FastAPI demo, backend structure, and frontend structure.

项目：

NextMove

Slogan：

Know Your Value.
Find Your Next Career Move.

Development Method：

Sprint + Task

----------------------------

# Sprint 0

## Task-001

- Status: Completed
- Objective: 初始化项目基础目录。
- Completed: 创建基础项目结构、README.md、PROJECT.md。

## Task-002

- Status: Completed
- Objective: 规范项目开发目录。
- Completed: 将项目迁移到 D 盘长期开发目录。

## Task-003

- Status: Completed
- Objective: 初始化 Frontend 项目。
- Completed: 创建 Next.js、TypeScript、Tailwind CSS、App Router、ESLint 前端基础项目。

----------------------------

# Sprint 1

## Task-004

- Status: Completed
- Objective: 初始化 Backend 项目。
- Completed: 创建 FastAPI 最小后端服务。

## Task-005

- Status: Completed
- Objective: 连接 Frontend 与 Backend。
- Completed: 前端读取 Backend API 并显示连接状态。

----------------------------

# Sprint 2

## Task-006

- Status: Completed
- Objective: 实现 Resume 本地文件选择与校验。
- Completed:
  - 本地文件选择
  - PDF/DOC/DOCX 支持
  - 文件大小校验（10MB）
  - 显示文件信息
  - 错误提示
- Knowledge:
  学习了：
  - HTML File Input
  - React State
  - 文件校验
