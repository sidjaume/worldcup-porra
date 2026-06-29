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
        grass: "#256d45",
        mint: "#e8f5ee",
        gold: "#8f6518",
        coral: "#b23b31",
        line: "#c9d3cb",
        focus: "#0f5f45",
      },
      boxShadow: {
        soft: "0 10px 30px rgba(23, 32, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
