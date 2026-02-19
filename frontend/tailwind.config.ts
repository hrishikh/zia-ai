import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./app/**/*.{ts,tsx}",
        "./components/**/*.{ts,tsx}",
        "./contexts/**/*.{ts,tsx}",
        "./hooks/**/*.{ts,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sora: ["Sora", "sans-serif"],
            },
            colors: {
                "zia-navy": "#0b0d1a",
                "zia-deep": "#10122a",
                "zia-surface": "#141628",
                "zia-purple": "#6c4de6",
                "zia-glow": "#8b5cf6",
                "zia-violet": "#a78bfa",
                "zia-amber": "#f59e0b",
                "zia-amber-dim": "#d97706",
                "zia-glass": "rgba(255,255,255,0.06)",
                "zia-border": "rgba(255,255,255,0.08)",
                "zia-muted": "rgba(255,255,255,0.35)",
            },
            backgroundImage: {
                "zia-gradient":
                    "radial-gradient(ellipse 80% 60% at 50% 0%, #2a1060 0%, #0b0d1a 60%), radial-gradient(ellipse 40% 40% at 80% 80%, #3d1a0a 0%, transparent 70%)",
                "zia-card":
                    "linear-gradient(135deg, rgba(108,77,230,0.15) 0%, rgba(11,13,26,0.4) 100%)",
                "zia-mic":
                    "radial-gradient(circle at center, #8b5cf6 0%, #6c4de6 50%, #4c1d95 100%)",
            },
            boxShadow: {
                glass: "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)",
                "mic-idle": "0 0 40px rgba(139,92,246,0.3), 0 0 80px rgba(139,92,246,0.15)",
                "mic-active": "0 0 60px rgba(139,92,246,0.8), 0 0 120px rgba(139,92,246,0.4)",
                "glow-amber": "0 0 30px rgba(245,158,11,0.4)",
            },
            backdropBlur: {
                glass: "16px",
                heavy: "32px",
            },
            borderRadius: {
                "2.5xl": "1.25rem",
                "3xl": "1.5rem",
                "4xl": "2rem",
            },
            animation: {
                "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "spin-slow": "spin 4s linear infinite",
                "float": "float 6s ease-in-out infinite",
                "waveform": "waveform 1.2s ease-in-out infinite",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translateY(0px)" },
                    "50%": { transform: "translateY(-8px)" },
                },
                waveform: {
                    "0%, 100%": { transform: "scaleY(0.3)" },
                    "50%": { transform: "scaleY(1)" },
                },
            },
        },
    },
    plugins: [],
};

export default config;
