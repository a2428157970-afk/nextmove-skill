export type UploadResponse = {
  success: boolean;
  filename: string;
  size: number;
};

export async function uploadResume(
  file: File,
  fetcher: typeof fetch = fetch,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetcher("http://127.0.0.1:8000/upload", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof result.detail === "string" ? result.detail : "Upload failed",
    );
  }

  return result;
}
