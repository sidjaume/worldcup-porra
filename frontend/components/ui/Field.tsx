import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";

export function Field({
  children,
  label,
}: {
  children: ReactNode;
  label: string;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-ink">
      <span>{label}</span>
      {children}
    </label>
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="min-h-10 rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-grass focus:ring-2 focus:ring-mint"
      {...props}
    />
  );
}

export function SelectInput(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className="min-h-10 rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-grass focus:ring-2 focus:ring-mint"
      {...props}
    />
  );
}

export function FormMessage({ message }: { message?: string }) {
  if (!message) {
    return null;
  }
  return <p className="text-sm font-medium text-coral">{message}</p>;
}
