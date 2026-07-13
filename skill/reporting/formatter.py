"""JSON and Markdown formatters for internal Human Career Reports."""

from __future__ import annotations

import json

from skill.reporting.schemas import HumanCareerReport, ReportAction


class HumanCareerReportFormatter:
    """Render an internal report without changing any public Skill output."""

    def to_json(self, report: HumanCareerReport, *, indent: int | None = 2) -> str:
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=indent)

    def to_markdown(self, report: HumanCareerReport) -> str:
        lines = [
            "# 职业分析报告",
            "",
            self._line(report.career_summary),
            "",
            "## 你的职业画像",
            "",
            f"- 当前领域：{self._line(report.current_profile.current_domain)}",
            f"- 当前阶段：{self._line(report.career_stage.stage)}",
            f"- 阶段解释：{self._line(report.career_stage.explanation)}",
            f"- 职业概述：{self._line(report.current_profile.profile_summary)}",
            "- 核心能力："
            + ("、".join(report.current_profile.core_capabilities) or "当前暂无充分证据。"),
            "",
            "## 你的优势",
            "",
        ]
        if report.strengths:
            for strength in report.strengths:
                lines.extend(
                    [
                        f"### {self._line(strength.capability)}",
                        "",
                        self._line(strength.explanation),
                        "",
                        *(
                            f"- 证据（{self._line(item.source)}）：{self._line(item.text)}"
                            for item in strength.evidence
                        ),
                        "",
                    ]
                )
        else:
            lines.extend(["当前暂无可核验的优势证据。", ""])

        lines.extend(
            [
                "## 岗位匹配",
                "",
                f"- 匹配分数：{report.job_fit.match_score}",
                f"- 展示级别：{report.job_fit.level.value}",
                f"- 说明：{self._line(report.job_fit.summary)}",
                "- 为什么匹配："
                + ("；".join(report.job_fit.why_fit) or "当前暂无充分证据。"),
                "- 主要缺口："
                + ("、".join(report.job_fit.main_gaps) or "当前未识别到基于证据的缺口。"),
                "",
            ]
        )
        for gap in report.capability_gaps:
            lines.append(
                f"- {self._line(gap.capability)}（{gap.status}）："
                f"{self._line(gap.explanation)}；需要：{self._line(gap.evidence_needed)}"
            )

        lines.extend(
            [
                "",
                "## 如果转型",
                "",
                f"- 路径：{report.transition_path.current_domain} → {report.transition_path.target_domain}",
                f"- 类型：{report.transition_path.transition_type}",
                f"- 说明：{self._line(report.transition_path.summary)}",
                "- 可迁移能力："
                + (
                    "、".join(report.transition_path.transferable_capabilities)
                    or "当前暂无充分证据。"
                ),
                "- 缺失能力："
                + (
                    "、".join(report.transition_path.missing_capabilities)
                    or "当前未识别到基于证据的缺口。"
                ),
                "",
                "## 下一步行动",
                "",
            ]
        )
        self._append_actions(lines, "立即行动", report.action_plan.immediate)
        self._append_actions(lines, "短期提升", report.action_plan.short_term)
        self._append_actions(lines, "长期发展", report.action_plan.long_term)

        lines.extend(["### 注意事项", ""])
        if report.risks:
            for risk in report.risks:
                lines.append(
                    f"- {self._line(risk.note)} {self._line(risk.verification)}"
                )
        else:
            lines.append("当前暂无额外的证据风险提示。")

        lines.extend(
            [
                "",
                "### 置信度",
                "",
                f"- 级别：{report.confidence.level.value}",
                f"- 说明：{self._line(report.confidence.explanation)}",
                "- 建议补充："
                + ("、".join(report.confidence.missing_information) or "当前无需额外补充。"),
                "",
            ]
        )
        return "\n".join(lines)

    def _append_actions(
        self,
        lines: list[str],
        title: str,
        actions: tuple[ReportAction, ...],
    ) -> None:
        lines.extend([f"### {title}", ""])
        if not actions:
            lines.extend(["当前暂无基于证据的建议。", ""])
            return
        for action in actions:
            lines.extend(
                [
                    f"- **{self._line(action.related_gap)}**：{self._line(action.objective)}",
                    *(f"  - {self._line(step)}" for step in action.steps),
                    f"  - 预期证据：{self._line(action.expected_evidence)}",
                ]
            )
        lines.append("")

    @staticmethod
    def _line(text: str) -> str:
        return " ".join(str(text).split())


__all__ = ["HumanCareerReportFormatter"]
