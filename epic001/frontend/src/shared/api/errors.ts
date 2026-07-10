interface ApiResponseBody {
  payload: unknown;
  text: string;
}

export async function readApiResponseBody(
  response: Response,
): Promise<ApiResponseBody> {
  const text = await response.text();
  if (!text) {
    return { payload: null, text };
  }

  try {
    return { payload: JSON.parse(text) as unknown, text };
  } catch {
    return { payload: null, text };
  }
}

export function apiErrorMessage(
  payload: unknown,
  fallback: string,
  rawText = "",
): string {
  const message = messageFromPayload(payload);
  if (message) return message;

  const text = rawText.trim();
  if (text) return text;

  return fallback;
}

function messageFromPayload(payload: unknown): string | null {
  if (!isRecord(payload)) return null;

  const message = stringValue(payload.message);
  if (message) return message;

  const detail = detailMessage(payload.detail);
  if (detail) return detail;

  const error = stringValue(payload.error);
  if (error) return error;

  return stringValue(payload.code);
}

function detailMessage(detail: unknown): string | null {
  const detailText = stringValue(detail);
  if (detailText) return detailText;

  if (!Array.isArray(detail)) return null;

  for (const item of detail) {
    const itemText = stringValue(item);
    if (itemText) return itemText;

    if (isRecord(item)) {
      const message = stringValue(item.msg) ?? stringValue(item.message);
      if (message) return message;
    }
  }

  return null;
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
