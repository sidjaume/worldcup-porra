import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "World Cup Pool",
  description: "Private FIFA World Cup 2026 knockout prediction pool.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
