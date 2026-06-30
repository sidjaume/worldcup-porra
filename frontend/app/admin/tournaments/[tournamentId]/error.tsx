"use client";

import { RouteErrorState } from "@/components/layout/RouteState";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <RouteErrorState message={error.message} reset={reset} />;
}
