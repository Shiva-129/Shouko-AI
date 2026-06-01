import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#0D0D0D",
        workspace: "#141414",
        card: "#1E1E1E",
        border: "#2A2A2A",
        
        // Brand Primary Accent
        lime: "#C8F04A",
        
        // Brand Secondary Accents
        coral: "#FF6B6B",
        violet: "#A78BFA",
        blue: "#5B8DEF",
        
        // Typography Colors
        primaryText: "#E8E6DF",
        secondaryText: "#888882",
        tertiaryText: "#444440",
        lightBg: "#FAFAF7",
        
        // Keeping fallback/original compatibility names mapped to the new flat theme
        background: "#0D0D0D",
        surface: "#141414",
        muted: "#888882",
        text: "#E8E6DF",
      },
      fontFamily: {
        syne: ["Syne", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

