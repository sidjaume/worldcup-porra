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
        ink: "#17202a",
        grass: "#2f7d4f",
        mint: "#e8f5ee",
        gold: "#c9932f",
        coral: "#c95d4f",
        line: "#d7ded8",
      },
      boxShadow: {
        soft: "0 10px 30px rgba(23, 32, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
