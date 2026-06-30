import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#020617",
        canvas: "#f6f8f4",
        paper: "#ffffff",
        grass: "#12c353",
        mint: "#e9f9ef",
        gold: "#f59e0b",
        coral: "#ef4444",
        sky: "#3b82f6",
        violet: "#5b21b6",
        line: "#dbe5df",
        focus: "#12c353",
      },
      boxShadow: {
        soft: "0 12px 28px rgba(2, 6, 23, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
