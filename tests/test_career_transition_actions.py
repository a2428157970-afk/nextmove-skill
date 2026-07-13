import unittest

from skill.career.transition import TransitionCapabilityGap, TransitionGapKind
from skill.career.transition_actions import TransitionActionBuilder
from skill.matching.schemas import RequirementStatus


class TransitionActionBuilderTests(unittest.TestCase):
    def gap(self, capability, kind=TransitionGapKind.DIRECT_CAPABILITY, core=True):
        return TransitionCapabilityGap(capability, kind, RequirementStatus.UNKNOWN, "Direct evidence is not available.", core)

    def test_product_action_is_gap_linked_and_creates_direct_evidence(self):
        action = TransitionActionBuilder().build((self.gap("Product Planning"),))[0]
        self.assertEqual(action.related_gap, "Product Planning")
        self.assertIn("PRD", action.expected_evidence)
        self.assertIn("roadmap", action.expected_evidence.lower())
        self.assertIn("case study", action.expected_evidence.lower())
        self.assertIn("direct evidence", action.objective.lower())
        self.assertTrue(action.steps)

    def test_hr_and_leadership_actions_are_specific(self):
        actions = TransitionActionBuilder().build((self.gap("Recruitment"), self.gap("People Leadership", TransitionGapKind.DEVELOPMENT_AREA)))
        self.assertEqual({item.related_gap for item in actions}, {"Recruitment", "People Leadership"})
        self.assertTrue(all(item.objective and item.expected_evidence for item in actions))
        recruitment = next(item for item in actions if item.related_gap == "Recruitment")
        self.assertIn("outcome review", recruitment.expected_evidence.lower())

    def test_every_gap_gets_a_bounded_fallback_action_and_core_orders_first(self):
        actions = TransitionActionBuilder().build((self.gap("Optional Skill", core=False), self.gap("Core Skill")))
        self.assertEqual([item.related_gap for item in actions], ["Core Skill", "Optional Skill"])
        self.assertEqual([item.priority for item in actions], [1, 2])

    def test_transferable_gap_does_not_create_a_direct_evidence_action(self):
        transfer_gap = self.gap("Customer Insight", TransitionGapKind.TRANSFERABLE_CAPABILITY)
        self.assertEqual(TransitionActionBuilder().build((transfer_gap,)), ())

    def test_duplicate_canonical_gaps_create_one_action(self):
        actions = TransitionActionBuilder().build((self.gap("PRD"), self.gap("prd")))
        self.assertEqual(len(actions), 1)

    def test_fallback_is_explicitly_simulated_and_reviewable(self):
        action = TransitionActionBuilder().build((self.gap("Novel Capability"),))[0]
        rendered = " ".join((*action.steps, action.expected_evidence)).lower()
        self.assertIn("simulated", rendered)
        self.assertIn("decision", rendered)
        self.assertIn("outcome", rendered)

    def test_action_output_does_not_repeat_gap_reason_or_raw_content(self):
        gap = TransitionCapabilityGap("Custom Capability", TransitionGapKind.DIRECT_CAPABILITY, RequirementStatus.UNKNOWN, "SECRET RAW RESUME", True)
        rendered = repr(TransitionActionBuilder().build((gap,)))
        self.assertNotIn("SECRET RAW RESUME", rendered)


if __name__ == "__main__":
    unittest.main()
