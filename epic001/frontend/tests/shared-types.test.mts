import assert from "node:assert/strict";
import test from "node:test";

import type {
  CareerProfile,
  JobProfile,
  ResumeProfile,
} from "../src/shared/types/career.ts";

test("shared career profiles expose stable identifiers", () => {
  const resume: ResumeProfile = { id: "resume-1" };
  const career: CareerProfile = { id: "career-1" };
  const job: JobProfile = { id: "job-1" };

  assert.deepEqual(
    [resume.id, career.id, job.id],
    ["resume-1", "career-1", "job-1"],
  );
});
