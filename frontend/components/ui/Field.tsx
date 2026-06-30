import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";

export function Field({
  children,
  className = "",
  label,
}: {
  children: ReactNode;
  className?: string;
  label: string;
}) {
  return (
    <label className={`grid gap-2 text-sm font-medium text-ink ${className}`}>
      <span>{label}</span>
      {children}
    </label>
  );
}

export function TextInput({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`min-h-10 rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-grass focus:ring-2 focus:ring-mint focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-focus disabled:bg-slate-100 disabled:text-slate-700 ${className}`}
      {...props}
    />
  );
}

export function SelectInput({ className = "", ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`min-h-10 rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-grass focus:ring-2 focus:ring-mint focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-focus ${className}`}
      {...props}
    />
  );
}

export function FormMessage({ id, message }: { id?: string; message?: string }) {
  if (!message) {
    return null;
  }
  return (
    <p className="text-sm font-medium text-coral" id={id} role="alert">
      {message}
    </p>
  );
}

export function FormSuccess({ id, message }: { id?: string; message?: string }) {
  if (!message) {
    return null;
  }
  return (
    <p className="text-sm font-medium text-grass" id={id} role="status">
      {message}
    </p>
  );
}
