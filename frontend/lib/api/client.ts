import { getApiBaseUrl } from "@/lib/config";
import type { ApiErrorBody } from "@/types/api";

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type RequestOptions = {
  accessToken?: string;
  body?: unknown;
  cache?: RequestCache;
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  params?: Record<string, string | undefined>;
};

export async function apiRequest<T>(
  path: string,
  {
    accessToken,
    body,
    cache = "no-store",
    method = "GET",
    params,
  }: RequestOptions = {},
): Promise<T> {
  const url = new URL(`${getApiBaseUrl()}${path}`);
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) {
      url.searchParams.set(key, value);
    }
  });

  const headers = new Headers();
  if (body !== undefined) {
    headers.set("content-type", "application/json");
  }
  if (accessToken) {
    headers.set("authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(url, {
    body: body === undefined ? undefined : JSON.stringify(body),
    cache,
    headers,
    method,
  });

  if (response.status === 204) {
    return undefined as T;
  }
  if (!response.ok) {
    throw await toApiError(response);
  }
  return (await response.json()) as T;
}

async function toApiError(response: Response): Promise<ApiError> {
  let payload: ApiErrorBody | undefined;
  try {
    payload = (await response.json()) as ApiErrorBody;
  } catch {
    payload = undefined;
  }

  const message =
    payload?.error?.message ??
    payload?.detail ??
    response.statusText ??
    "Unexpected backend error.";

  return new ApiError(message, response.status, payload?.error?.code);
}
