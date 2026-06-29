"use client";

import { RouteErrorState } from "@/components/layout/RouteState";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return <RouteErrorState message="Your profile could not be loaded." reset={reset} />;
}
