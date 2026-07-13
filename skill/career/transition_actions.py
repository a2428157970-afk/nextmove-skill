"""Bounded action recommendations linked to structured transition gaps."""

from dataclasses import dataclass

from skill.career.transition import TransitionAction, TransitionCapabilityGap


@dataclass(frozen=True, slots=True)
class _ActionTemplate:
    objective: str
    steps: tuple[str, ...]
    expected_evidence: str


_PRODUCT_CASE = _ActionTemplate(
    "Build direct evidence of product planning ownership through a product case.",
    ("Define a user problem and success metric.", "Draft a PRD, prototype, and prioritized roadmap.", "Document validation results."),
    "product case study with PRD, prototype, prioritized roadmap, and validation record",
)
_TEMPLATES = {
    "product planning": _PRODUCT_CASE,
    "产品规划": _PRODUCT_CASE,
    "prd": _ActionTemplate(
        "Demonstrate requirement management with a reviewable artifact.",
        ("Select a bounded user problem.", "Write acceptance criteria and a PRD.", "Record stakeholder review feedback."),
        "reviewed PRD with acceptance criteria",
    ),
    "product delivery ownership": _ActionTemplate(
        "Demonstrate end-to-end product delivery coordination.",
        ("Define a release scope.", "Track engineering and stakeholder dependencies.", "Record launch follow-up and outcomes."),
        "delivery plan, launch record, and outcome review",
    ),
    "recruitment": _ActionTemplate(
        "Build direct evidence of a recruitment workflow.",
        ("Write a fictional role intake.", "Create a screening rubric and structured interview process.", "Record simulated funnel decisions and lessons."),
        "fictional intake, screening rubric, simulated funnel record, and outcome review",
    ),
    "labor relations": _ActionTemplate(
        "Build applied knowledge of labor-relations process boundaries.",
        ("Study an approved policy case.", "Map the escalation and documentation workflow.", "Obtain qualified review of the case analysis."),
        "reviewed labor-relations case analysis",
    ),
    "people leadership": _ActionTemplate(
        "Create direct evidence of people leadership.",
        ("Set a goal for a bounded team initiative.", "Delegate responsibilities and record key decisions.", "Document outcomes and team feedback."),
        "goal, delegation plan, decision record, feedback, and measured outcome",
    ),
}


class TransitionActionBuilder:
    def build(self, gaps: tuple[TransitionCapabilityGap, ...]) -> tuple[TransitionAction, ...]:
        unique = {}
        for gap in gaps:
            if gap.kind.value == "transferable_capability":
                continue
            unique.setdefault(gap.capability.casefold(), gap)
        ordered = sorted(unique.values(), key=lambda gap: (not gap.core, gap.capability.lower()))
        actions = []
        for gap in ordered:
            template = _TEMPLATES.get(gap.capability.lower()) or _ActionTemplate(
                f"Create direct, reviewable evidence for {gap.capability}.",
                (f"Define a fictional, bounded {gap.capability} exercise and label it simulated.", "Record the decision, execution steps, and outcome.", "Request evidence-based review."),
                f"reviewed simulated {gap.capability} decision, execution, and outcome record",
            )
            actions.append(TransitionAction(
                gap.capability,
                template.objective,
                template.steps,
                template.expected_evidence,
                1 if gap.core else 2,
            ))
        return tuple(actions)
