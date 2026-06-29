"use client";

import { AlertCircle, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function LoadingState({ label = "Loading page" }: { label?: string }) {
  return (
    <main className="mx-auto grid min-h-screen max-w-7xl content-start gap-4 px-4 py-6 sm:px-6">
      <div className="h-8 w-44 animate-pulse rounded-md bg-line" aria-hidden="true" />
      <div
        aria-label={label}
        aria-live="polite"
        className="grid gap-3 rounded-lg border border-line bg-white p-5 shadow-soft"
        role="status"
      >
        <div className="h-4 w-3/4 animate-pulse rounded-md bg-line" />
        <div className="h-4 w-1/2 animate-pulse rounded-md bg-line" />
        <span className="sr-only">{label}</span>
      </div>
    </main>
  );
}

export function RouteErrorState({
  message = "This page could not be loaded.",
  reset,
}: {
  message?: string;
  reset: () => void;
}) {
  return (
    <main className="mx-auto grid min-h-screen max-w-2xl content-center gap-4 px-4 py-10 sm:px-6">
      <div
        className="grid gap-4 rounded-lg border border-coral bg-white p-5 shadow-soft"
        role="alert"
      >
        <div className="flex gap-3">
          <AlertCircle className="mt-0.5 text-coral" aria-hidden="true" size={22} />
          <div>
            <h1 className="text-xl font-bold">Unable to load this page</h1>
            <p className="mt-1 text-sm text-slate-700">{message}</p>
          </div>
        </div>
        <Button className="w-fit" onClick={reset} type="button" variant="secondary">
          <RotateCw aria-hidden="true" size={16} />
          Try again
        </Button>
      </div>
    </main>
  );
}
