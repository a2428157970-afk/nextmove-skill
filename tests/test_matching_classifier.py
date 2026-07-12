import unittest

from skill.matching.taxonomy import (
    ADJACENT_DOMAINS,
    DOMAIN_FAMILIES,
    CareerDomain,
    JobFamily,
)


class CareerTaxonomyTests(unittest.TestCase):
    def test_v1_domain_values_are_frozen(self):
        self.assertEqual(
            {domain.value for domain in CareerDomain},
            {
                "human_resources",
                "technology",
                "finance",
                "sales",
                "marketing",
                "operations",
                "supply_chain",
                "manufacturing",
                "customer_service",
                "other",
                "unknown",
            },
        )

    def test_v1_job_families_are_small_and_domain_scoped(self):
        self.assertEqual(
            DOMAIN_FAMILIES[CareerDomain.HUMAN_RESOURCES],
            (
                JobFamily.HR_GENERALIST,
                JobFamily.RECRUITMENT,
                JobFamily.COMPENSATION_BENEFITS,
                JobFamily.EMPLOYEE_RELATIONS,
            ),
        )
        self.assertEqual(
            DOMAIN_FAMILIES[CareerDomain.TECHNOLOGY],
            (
                JobFamily.BACKEND,
                JobFamily.FRONTEND,
                JobFamily.DATA,
                JobFamily.DEVOPS,
            ),
        )
        self.assertEqual(DOMAIN_FAMILIES[CareerDomain.OTHER], ())
        self.assertEqual(DOMAIN_FAMILIES[CareerDomain.UNKNOWN], ())

    def test_adjacent_domains_are_symmetric(self):
        self.assertIn(
            (CareerDomain.OPERATIONS, CareerDomain.SUPPLY_CHAIN),
            ADJACENT_DOMAINS,
        )
        self.assertIn(
            (CareerDomain.SUPPLY_CHAIN, CareerDomain.OPERATIONS),
            ADJACENT_DOMAINS,
        )

    def test_other_and_unknown_are_distinct_states(self):
        self.assertNotEqual(CareerDomain.OTHER, CareerDomain.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
