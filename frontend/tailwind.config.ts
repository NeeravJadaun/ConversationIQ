import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}", "./__tests__/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0A0F1E",
        surface: "#111827",
        healthy: "#10B981",
        warning: "#F59E0B",
        critical: "#EF4444",
        accent: "#3B82F6",
        muted: "#6B7280",
      },
    },
  },
  plugins: [],
};

export default config;
