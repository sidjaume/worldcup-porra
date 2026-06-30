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
        canvas: "#f7f4ec",
        paper: "#fffdf8",
        grass: "#126b45",
        mint: "#e7f5ec",
        gold: "#9b6b1b",
        coral: "#c73e35",
        sky: "#1f66b1",
        line: "#d9d2c4",
        focus: "#126b45",
      },
      boxShadow: {
        soft: "0 10px 24px rgba(23, 32, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
