"use client";
import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { VoiceState } from "@/lib/types";

interface MicButtonProps {
    state: VoiceState;
    onPress: () => void;
    onRelease?: () => void;
    size?: "sm" | "lg";
}

export function MicButton({ state, onPress, onRelease, size = "lg" }: MicButtonProps) {
    const isListening = state === "listening";
    const isProcessing = state === "processing";

    return (
        <div className="relative flex items-center justify-center">
            {/* Pulsing outer rings when listening */}
            {isListening && (
                <>
                    {[1, 2, 3].map((i) => (
                        <motion.div
                            key={i}
                            className="absolute rounded-full border border-zia-purple/30"
                            initial={{ opacity: 0, scale: 1 }}
                            animate={{ opacity: [0.6, 0], scale: [1, 1 + i * 0.5] }}
                            transition={{ duration: 2, delay: i * 0.4, repeat: Infinity }}
                            style={{
                                width: size === "lg" ? 120 : 72,
                                height: size === "lg" ? 120 : 72,
                            }}
                        />
                    ))}
                </>
            )}

            {/* Main button */}
            <motion.button
                onClick={isListening ? onRelease : onPress}
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.94 }}
                animate={
                    isListening
                        ? { boxShadow: ["0 0 40px rgba(139,92,246,0.4)", "0 0 80px rgba(139,92,246,0.8)", "0 0 40px rgba(139,92,246,0.4)"] }
                        : { boxShadow: "0 0 40px rgba(139,92,246,0.3)" }
                }
                transition={{ duration: 1.5, repeat: isListening ? Infinity : 0 }}
                className={clsx(
                    "relative rounded-full flex items-center justify-center bg-zia-mic",
                    "transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-zia-violet",
                    size === "lg" ? "w-28 h-28" : "w-16 h-16"
                )}
            >
                {/* Spinning arc when processing */}
                {isProcessing && (
                    <svg
                        className="absolute inset-0 w-full h-full animate-spin-slow"
                        viewBox="0 0 100 100"
                    >
                        <circle
                            cx="50" cy="50" r="46"
                            fill="none" stroke="rgba(245,158,11,0.6)" strokeWidth="3"
                            strokeDasharray="60 230"
                            strokeLinecap="round"
                        />
                    </svg>
                )}

                {/* Mic icon */}
                <svg
                    className={clsx(
                        "text-white transition-all duration-300",
                        size === "lg" ? "w-10 h-10" : "w-6 h-6"
                    )}
                    fill="currentColor" viewBox="0 0 24 24"
                >
                    <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" fillRule="nonzero"
                        fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" />
                </svg>
            </motion.button>

            {/* Status label */}
            <motion.p
                className="absolute -bottom-8 text-sm text-white/50 font-sora"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: isListening ? Infinity : 0 }}
            >
                {state === "idle" && "Tap to speak"}
                {state === "listening" && "Listening…"}
                {state === "processing" && "Processing…"}
                {state === "error" && "Mic error"}
            </motion.p>
        </div>
    );
}
