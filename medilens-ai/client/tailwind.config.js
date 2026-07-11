/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2E6BE6",
          50: "#EDF3FE",
          100: "#D6E4FC",
          400: "#5A8CF0",
          500: "#2E6BE6",
          600: "#1E52C2",
          700: "#173F97",
        },
        emerald: {
          DEFAULT: "#12A594",
          50: "#E7F8F5",
          100: "#C6EEE8",
          500: "#12A594",
          600: "#0D8577",
        },
        ink: {
          DEFAULT: "#12181F",
          soft: "#5B6672",
          faint: "#8993A1",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          subtle: "#F5F8FA",
          border: "#E4E9EF",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "system-ui",
          "sans-serif",
        ],
      },
      fontSize: {
        base: ["1.0625rem", { lineHeight: "1.65rem" }],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(18, 24, 31, 0.04), 0 8px 24px rgba(18, 24, 31, 0.06)",
        "card-hover": "0 2px 4px rgba(18, 24, 31, 0.06), 0 12px 32px rgba(18, 24, 31, 0.09)",
      },
    },
  },
  plugins: [],
};
