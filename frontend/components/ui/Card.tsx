import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-lg border border-line bg-paper p-5 shadow-soft ${className}`}>
      {children}
    </section>
  );
}
