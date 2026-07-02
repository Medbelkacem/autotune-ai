import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0b0f19",
          soft: "#121826",
          card: "#161d2b",
        },
        line: "#1f2937",
        text: {
          DEFAULT: "#e5e7eb",
          muted: "#9ca3af",
        },
        brand: {
          DEFAULT: "#7c3aed",
          soft: "#a78bfa",
        },
        ok: "#22c55e",
        warn: "#eab308",
        risk: "#ef4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        xl: "12px",
      },
    },
  },
  plugins: [],
} satisfies Config;
