import unittest

from skill.matching import JobMatcher
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class JobMatcherTests(unittest.TestCase):
    def test_high_skill_match_returns_strong_score(self):
        profile = ResumeProfile(
            skills=["Python", "FastAPI", "SQL", "Docker"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python APIs with FastAPI and SQL."],
                )
            ],
        )
        job_description = "Backend Engineer role using Python, FastAPI, SQL, Docker, and APIs."

        result = JobMatcher().match(profile, job_description)

        self.assertIsInstance(result, JobMatchResult)
        self.assertGreaterEqual(result.match_score, 80)
        self.assertEqual(result.missing_skills, [])
        self.assertIn("Python", result.matched_skills)
        self.assertIn("FastAPI", result.matched_skills)
        self.assertTrue(result.strengths)
        self.assertTrue(result.recommendations)

    def test_skill_gaps_are_reported_from_job_keywords(self):
        profile = ResumeProfile(
            skills=["Python", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Data Analyst",
                    highlights=["Analyzed product data with SQL."],
                )
            ],
        )
        job_description = "Data role requiring Python, SQL, Tableau, AWS, and Docker."

        result = JobMatcher().match(profile, job_description)

        self.assertLess(result.match_score, 80)
        self.assertIn("Python", result.matched_skills)
        self.assertIn("Tableau", result.missing_skills)
        self.assertIn("AWS", result.missing_skills)
        self.assertIn("Docker", result.missing_skills)
        self.assertTrue(result.gaps)

    def test_empty_resume_returns_zero_score_and_recommendations(self):
        job_description = "Backend Engineer role requiring Python, FastAPI, SQL, and Docker."

        result = JobMatcher().match(ResumeProfile(), job_description)

        self.assertEqual(result.match_score, 0)
        self.assertEqual(result.matched_skills, [])
        self.assertIn("Python", result.missing_skills)
        self.assertTrue(result.gaps)
        self.assertTrue(result.recommendations)

    def test_hr_role_matches_domain_specific_requirements(self):
        profile = ResumeProfile(
            skills=["招聘", "考勤", "劳动关系"],
            experience=[
                ExperienceEntry(
                    role="人事行政专员",
                    highlights=["负责招聘、员工考勤和劳动关系协调。"],
                )
            ],
        )
        job_description = "人事行政专员，要求招聘、考勤、薪酬和劳动关系经验。"

        result = JobMatcher().match(profile, job_description)

        self.assertGreater(result.match_score, 0)
        self.assertIn("招聘", result.matched_skills)
        self.assertIn("考勤", result.matched_skills)
        self.assertIn("劳动关系", result.matched_skills)
        self.assertIn("薪酬", result.missing_skills)
        self.assertNotIn("Python", result.missing_skills)
        self.assertTrue(any("human_resources" in item for item in result.strengths))

    def test_finance_role_does_not_fall_through_to_technology_keywords(self):
        profile = ResumeProfile(
            skills=["财务报表", "账目核对", "Excel"],
            experience=[ExperienceEntry(role="会计专员")],
        )
        job_description = "会计专员负责财务报表、月度结账、账目核对和Excel。"

        result = JobMatcher().match(profile, job_description)

        self.assertGreater(result.match_score, 0)
        self.assertIn("财务报表", result.matched_skills)
        self.assertIn("月度结账", result.missing_skills)
        self.assertNotIn("Docker", result.missing_skills)

    def test_operations_role_uses_operations_vocabulary(self):
        profile = ResumeProfile(
            skills=["办公室管理", "供应商协调"],
            experience=[ExperienceEntry(role="行政专员")],
        )
        job_description = "行政专员负责办公室管理、供应商协调和流程优化。"

        result = JobMatcher().match(profile, job_description)

        self.assertGreater(result.match_score, 0)
        self.assertIn("办公室管理", result.matched_skills)
        self.assertIn("供应商协调", result.matched_skills)
        self.assertIn("流程优化", result.missing_skills)

    def test_empty_and_weak_job_descriptions_return_stable_low_information_result(self):
        profile = ResumeProfile(skills=["Excel"], experience=[ExperienceEntry(role="专员")])

        for job_description in ("", "欢迎加入我们的团队。"):
            with self.subTest(job_description=job_description):
                result = JobMatcher().match(profile, job_description)
                self.assertEqual(result.match_score, 0)
                self.assertEqual(result.matched_skills, [])
                self.assertEqual(result.missing_skills, [])
                self.assertTrue(any("information" in item.lower() for item in result.gaps))


if __name__ == "__main__":
    unittest.main()
