export function getApiBaseUrl(): string {
  return (
    process.env.API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

export function getBrowserApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
    /\/$/,
    "",
  );
}

export function getFrontendBaseUrl(): string {
  return (
    process.env.FRONTEND_BASE_URL ??
    process.env.NEXT_PUBLIC_FRONTEND_BASE_URL ??
    "http://localhost:3000"
  ).replace(/\/$/, "");
}
