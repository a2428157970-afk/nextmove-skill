import assert from "node:assert/strict";
import test from "node:test";

import { uploadResume } from "../app/upload-resume.ts";

test("uploads the selected file as multipart form data", async () => {
  const file = new File(["resume content"], "resume.pdf", {
    type: "application/pdf",
  });
  let requestUrl: string | URL | Request | undefined;
  let requestInit: RequestInit | undefined;

  const fetcher: typeof fetch = async (url, init) => {
    requestUrl = url;
    requestInit = init;

    return new Response(
      JSON.stringify({
        success: true,
        filename: "resume.pdf",
        size: file.size,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      },
    );
  };

  const result = await uploadResume(file, fetcher);

  assert.equal(requestUrl, "http://127.0.0.1:8000/upload");
  assert.equal(requestInit?.method, "POST");
  assert.ok(requestInit?.body instanceof FormData);
  assert.equal(requestInit.body.get("file"), file);
  assert.equal(requestInit.headers, undefined);
  assert.deepEqual(result, {
    success: true,
    filename: "resume.pdf",
    size: file.size,
  });
});

test("throws the backend error message when upload fails", async () => {
  const file = new File(["resume content"], "resume.pdf");
  const fetcher: typeof fetch = async () =>
    new Response(JSON.stringify({ detail: "Upload failed" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });

  await assert.rejects(
    () => uploadResume(file, fetcher),
    new Error("Upload failed"),
  );
});
