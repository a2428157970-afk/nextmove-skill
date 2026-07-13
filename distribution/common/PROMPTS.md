# NextMove Prompt Templates

以下模板同时适用于 Runtime Package 和 Prompt-only Pilot Kit。请先确认当前模式：

- Runtime 模式只有在离线预检实际输出 `NEXTMOVE_READY` 后，才可以声称结果来自 NextMove Runtime。
- Prompt-only 模式必须标记 `NEXTMOVE_PROMPT_ONLY`，结果只是按照 NextMove 说明进行的体验预览。

请先删除姓名、电话、邮箱、地址、证件号、真实公司机密和其他非必要敏感信息。

## 完整职业分析

```text
请使用当前已确认的 NextMove 模式完成职业分析，并在报告开头标明模式。
如果当前是 Runtime 模式，必须已经通过真实离线预检；如果是 Prompt-only，
请标明 NEXTMOVE_PROMPT_ONLY，不得声称调用了 NextMoveSkill.run()。

只使用我提供的简历和岗位材料，不得编造职位、职责、技能、年限、成果、
教育或证书。区分材料事实、基于证据的判断和建议。不得把可迁移证据写成
目标岗位的直接经验；未知信息必须写成“信息不足”，不能写成能力缺失。

请输出 Human Career Report，依次包含：你的职业画像、你的优势、岗位匹配、
如果转型、下一步行动。每项优势附证据；行动按立即、短期、长期排序并关联
具体差距。最后列出风险、置信度和需要补充的信息。不要保证成功或录用结果。
```

## 岗位匹配

```text
请使用当前已确认的 NextMove 模式比较简历与岗位，并在报告开头标明模式。
Runtime 模式必须已经通过真实离线预检；Prompt-only 模式必须标明
NEXTMOVE_PROMPT_ONLY，不得声称调用了本地 Python Skill。

不得编造任何经历。区分材料事实、证据判断和建议；保留已有匹配结果，不要
自行美化分数。逐项说明为什么匹配、证据在哪里、主要差距是什么。可迁移
证据不能表述成直接经验；未看到的内容写成信息不足。输出 Human Career
Report 的岗位匹配、行动、风险和置信度部分，不保证求职或录用结果。
```

## 职业转型

```text
请使用当前已确认的 NextMove 模式分析职业转型，并在报告开头标明模式。
Runtime 模式必须已经通过真实离线预检；Prompt-only 模式必须标明
NEXTMOVE_PROMPT_ONLY，不得声称结果来自 NextMoveSkill.run()。

只使用提供的材料，不得编造经历。明确展示“当前领域 → 目标领域”、转型类型、
直接能力、可迁移能力、缺失能力和信息不足项。不得把可迁移能力写成目标岗位
直接经验，也不得把未知信息写成已确认缺失。输出 Human Career Report，并将
行动按立即、短期、长期排序且关联差距。区分事实、证据判断和建议，不保证
转型成功、offer 或任何求职结果。
```
