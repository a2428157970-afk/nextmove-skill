import type { ResumeParseResponse } from "../types";
import {
  API_BASE_URL,
  apiErrorMessage,
  readApiResponseBody,
} from "../../../shared/api/index.ts";

export async function parseResume(
  file: File,
  fetcher: typeof fetch = fetch,
): Promise<ResumeParseResponse> {
  const formData = new FormData();
  formData.append("file", file);
  let response: Response;
  try {
    response = await fetcher(`${API_BASE_URL}/api/resumes/parse`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? `Unable to reach resume parse API at ${API_BASE_URL}: ${error.message}`
        : `Unable to reach resume parse API at ${API_BASE_URL}`,
    );
  }

  const { payload, text } = await readApiResponseBody(response);

  if (!response.ok) {
    throw new Error(apiErrorMessage(payload, "Resume analysis failed", text));
  }
  return payload as ResumeParseResponse;
}
