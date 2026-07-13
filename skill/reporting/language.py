"""Bounded, evidence-based language for internal human reports."""

from __future__ import annotations

import re


class HumanReportLanguage:
    """Create user-facing copy without guarantees or fatalistic conclusions."""

    _FORBIDDEN = (
        re.compile(r"\bguarantee(?:d|s)?\b", re.IGNORECASE),
        re.compile(r"\bimpossible\b", re.IGNORECASE),
        re.compile(r"\bunsuitable\b", re.IGNORECASE),
        re.compile(r"\bcannot\s+transition\b", re.IGNORECASE),
        re.compile(r"你一定成功"),
        re.compile(r"你不适合"),
        re.compile(r"你无法转型"),
        re.compile(r"保证拿\s*offer", re.IGNORECASE),
    )

    def is_safe(self, text: str) -> bool:
        """Return whether text avoids bounded guarantee and verdict phrases."""

        return not any(pattern.search(text) for pattern in self._FORBIDDEN)

    def sanitize(self, text: str) -> str:
        """Replace an unsafe conclusion with an evidence-based statement."""

        if self.is_safe(text):
            return text
        if re.search(r"[\u4e00-\u9fff]", text):
            return "当前证据不足以支持确定性结论，建议进一步验证。"
        return (
            "Current evidence is insufficient for a definitive conclusion; "
            "further validation is recommended."
        )

    def career_summary(self, domain: str, stage: str) -> str:
        return self.sanitize(
            f"当前证据显示，你的职业积累主要在 {domain}，职业阶段为 {stage}。"
        )

    def profile_summary(self, domain: str) -> str:
        if domain in {"unknown", "other"}:
            return "当前信息不足以识别稳定的职业领域，建议补充具体经历。"
        return self.sanitize(f"当前证据显示，你的主要职业积累位于 {domain}。")

    def stage_explanation(self, stage: str) -> str:
        if stage == "unknown":
            return "当前信息不足以判断职业阶段，建议补充职责、年限和成果。"
        return self.sanitize(f"当前证据支持 {stage} 职业阶段判断。")

    def strength(self, capability: str, *, transferable: bool) -> str:
        if transferable:
            return self.sanitize(
                f"当前证据显示 {capability} 与目标要求存在可迁移关系，建议验证直接负责范围。"
            )
        return self.sanitize(f"当前证据显示，现有经历支持 {capability}。")

    def unknown_gap(self, capability: str) -> str:
        return self.sanitize(
            f"简历中尚未看到 {capability} 的直接证据，可以优先补充相关案例。"
        )

    def partial_gap(self, capability: str) -> str:
        return self.sanitize(
            f"{capability} 已有部分相关证据，建议验证直接负责范围。"
        )

    def missing_gap(self, capability: str) -> str:
        return self.sanitize(
            f"当前材料与 {capability} 要求存在明确差异，可以优先核对并补充真实证据。"
        )

    def development_gap(self, capability: str) -> str:
        return self.sanitize(
            f"{capability} 是当前路径中的发展项，可以优先建立可核验的实践证据。"
        )

    def fit_summary(self, score: int, level: str) -> str:
        if level == "insufficient_evidence":
            return "当前岗位信息不足，匹配分数不能作为岗位适合度结论，建议补充具体要求。"
        return self.sanitize(
            f"当前材料的岗位要求覆盖分为 {score}，展示级别为 {level}；该分数不代表录用结果。"
        )

    def transition_summary(
        self,
        current_domain: str,
        target_domain: str,
        transition_type: str,
    ) -> str:
        return self.sanitize(
            f"当前证据显示路径为 {current_domain} → {target_domain}，转型类型为 {transition_type}。"
        )

    def risk_note(self, factor: str) -> str:
        return self.sanitize(f"当前证据显示需要关注：{factor}")

    def verification(self) -> str:
        return "建议验证相关职责、成果和直接负责范围。"

    def confidence_explanation(self, level: str) -> str:
        return self.sanitize(f"报告置信度为 {level}，表示当前证据的完整程度，不代表候选人质量。")


__all__ = ["HumanReportLanguage"]
