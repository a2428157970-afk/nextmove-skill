import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { parseResume } from "../src/features/resume/api/parse-resume.ts";
import {
  fileInputEventProps,
  ResumeFilePicker,
  selectedFileFromInput,
} from "../src/features/resume/components/resume-file-picker.ts";
import {
  displayValue,
  resumeActionLabel,
} from "../src/features/resume/profile-display.ts";

test("parses a PDF through the resume intelligence endpoint", async () => {
  const file = new File(["pdf"], "resume.pdf", { type: "application/pdf" });
  const fetcher: typeof fetch = async (url, init) => {
    assert.equal(url, "http://127.0.0.1:8010/api/resumes/parse");
    assert.equal(init?.method, "POST");
    assert.ok(init?.body instanceof FormData);
    return new Response(
      JSON.stringify({
        success: true,
        profile: {
          personal_information: {
            name: "Ada Lovelace",
            email: null,
            phone: null,
            location: null,
            links: [],
          },
          summary: null,
          education: [],
          experience: [],
          skills: ["Python"],
          projects: [],
          certifications: [],
          languages: [],
          raw_text: "Ada Lovelace",
        },
        metadata: {
          filename: "resume.pdf",
          size: file.size,
          parser: "rule_based_v1",
        },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  };

  const result = await parseResume(file, fetcher);

  assert.equal(result.profile.personal_information.name, "Ada Lovelace");
});

test("surfaces structured API errors", async () => {
  const file = new File([], "resume.pdf");
  const fetcher: typeof fetch = async () =>
    new Response(
      JSON.stringify({
        success: false,
        code: "NO_TEXT_EXTRACTED",
        message: "No readable text was found in this PDF.",
      }),
      { status: 422, headers: { "Content-Type": "application/json" } },
    );

  await assert.rejects(
    () => parseResume(file, fetcher),
    new Error("No readable text was found in this PDF."),
  );
});

test("surfaces FastAPI validation details instead of a generic parse failure", async () => {
  const file = new File(["pdf"], "resume.pdf", { type: "application/pdf" });
  const fetcher: typeof fetch = async () =>
    new Response(
      JSON.stringify({
        detail: [
          {
            loc: ["body", "file"],
            msg: "Field required",
            type: "missing",
          },
        ],
      }),
      { status: 422, headers: { "Content-Type": "application/json" } },
    );

  await assert.rejects(
    () => parseResume(file, fetcher),
    new Error("Field required"),
  );
});

test("surfaces backend text errors when parse response is not JSON", async () => {
  const file = new File(["pdf"], "resume.pdf", { type: "application/pdf" });
  const fetcher: typeof fetch = async () =>
    new Response("Internal Server Error", {
      status: 500,
      headers: { "Content-Type": "text/plain" },
    });

  await assert.rejects(
    () => parseResume(file, fetcher),
    new Error("Internal Server Error"),
  );
});

test("uses a friendly empty-field label", () => {
  assert.equal(displayValue(null), "Not detected");
  assert.equal(displayValue(""), "Not detected");
  assert.equal(displayValue("Ada"), "Ada");
});

test("shows an analyzing label while parsing", () => {
  assert.equal(
    resumeActionLabel({
      isAnalyzing: true,
      isUploading: true,
      hasSelection: true,
    }),
    "Analyzing...",
  );
});

test("exposes a directly interactive native resume file input", () => {
  const markup = renderToStaticMarkup(
    createElement(ResumeFilePicker, {
      buttonLabel: "Choose File",
      disabled: false,
      onChange: () => undefined,
      onAnalyze: () => undefined,
    }),
  );

  assert.match(
    markup,
    /<input[^>]+id="resume-file-input"[^>]+type="file"[^>]+class="native-file-input"/,
  );
  assert.doesNotMatch(markup, /class="visually-hidden"/);
  assert.match(markup, /<button[^>]+type="button"[^>]*>Analyze Resume<\/button>/);
});

test("handles both input and change events from embedded browsers", () => {
  const handler = () => undefined;

  const props = fileInputEventProps(handler);

  assert.equal(props.onInput, handler);
  assert.equal(props.onChange, handler);
});

test("reads the selected file directly when the analyze button is clicked", () => {
  const file = new File(["pdf"], "resume.pdf", { type: "application/pdf" });
  const files = {
    0: file,
    length: 1,
    item: (index: number) => (index === 0 ? file : null),
  } as unknown as FileList;

  assert.equal(selectedFileFromInput({ files }), file);
  assert.equal(selectedFileFromInput({ files: null }), null);
});
