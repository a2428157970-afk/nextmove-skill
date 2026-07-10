import type { UploadResponse } from "../types";
import {
  API_BASE_URL,
  apiErrorMessage,
  readApiResponseBody,
} from "../../../shared/api/index.ts";

export async function uploadResume(
  file: File,
  fetcher: typeof fetch = fetch,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetcher(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? `Unable to reach upload API at ${API_BASE_URL}: ${error.message}`
        : `Unable to reach upload API at ${API_BASE_URL}`,
    );
  }

  const { payload, text } = await readApiResponseBody(response);

  if (!response.ok) {
    throw new Error(apiErrorMessage(payload, "Upload failed", text));
  }

  return payload as UploadResponse;
}
