"use client";

import { RouteErrorState } from "@/components/layout/RouteState";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return <RouteErrorState reset={reset} />;
}
