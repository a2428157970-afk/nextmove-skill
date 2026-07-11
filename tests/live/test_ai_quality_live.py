"""Optional, content-safe quality observation through external live assembly."""

import importlib
import os
import unittest


@unittest.skipUnless(
    os.getenv("RUN_LIVE_AI_TEST") == "true",
    "Set RUN_LIVE_AI_TEST=true to run live AI tests.",
)
class LiveAIQualityTests(unittest.TestCase):
    """Use only an externally supplied validator; never load credentials here."""

    def test_external_quality_validator_reports_only_safe_measurements(self):
        factory_path = os.getenv("NEXTMOVE_LIVE_TRANSPORT_FACTORY")
        if not factory_path:
            self.skipTest("External live transport factory is not configured.")
        module_name, factory_name = factory_path.rsplit(":", 1)
        validator = getattr(importlib.import_module(module_name), factory_name)()
        quality_validator = getattr(validator, "evaluate_quality", None)
        if quality_validator is None:
            self.skipTest("External validator does not expose evaluate_quality.")

        measurements = quality_validator()
        allowed = {"case_id", "contract_version", "success", "latency", "output_length", "passed_checks", "failed_checks"}
        self.assertTrue(all(set(item).issubset(allowed) for item in measurements))


if __name__ == "__main__":
    unittest.main()
