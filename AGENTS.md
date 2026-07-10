# NextMove Development Guidelines

## 项目定位

NextMove 是：

AI Career Intelligence Skill Framework

目标：

构建一个可被 AI Agent 调用的职业智能 Skill。

核心能力：

- Resume Analysis
- Resume Profile Extraction
- Job Matching
- Career Advice

## 当前开发原则

1. Skill Core 优先

未来核心能力应该独立于 Web。

2. Web Demo 保留

Frontend / Backend 作为展示和测试入口。

3. 模块化设计

避免大规模耦合。

优先：

- packages/
- skill/
- knowledge/
- schemas/

4. AI Provider 独立

不要绑定单一模型。

支持未来：

- OpenAI
- Claude
- Gemini
- Local Model

5. 数据结构优先

核心输出必须结构化。

例如：

- Resume Profile
- Career Profile
- Job Match Result

6. 开发规范

修改前：

- 阅读已有代码
- 理解当前架构
- 避免无必要重构

每个 Epic 完成后：

更新：

- CHANGELOG.md
- NEXT_TASK.md
- PROJECT.md（必要时）

7. 禁止事项

未经确认不要：

- 删除已有功能
- 大规模重写 frontend
- 大规模修改 backend
- 引入新的复杂依赖
- 接入收费 AI API
