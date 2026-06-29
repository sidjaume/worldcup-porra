"use client";

import { RouteErrorState } from "@/components/layout/RouteState";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return <RouteErrorState message="This pool could not be loaded." reset={reset} />;
}
