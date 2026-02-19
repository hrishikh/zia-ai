"use client";
import { motion, AnimatePresence } from "framer-motion";

interface TranscriptProps {
    finalText: string;
    interimText: string;
}

export function Transcript({ finalText, interimText }: TranscriptProps) {
    if (!finalText && !interimText) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-xl text-center px-6"
        >
            {finalText && (
                <p className="text-white/90 text-lg leading-relaxed font-medium mb-1">
                    {finalText}
                </p>
            )}
            {interimText && (
                <p className="text-white/40 text-base italic">
                    {interimText}
                    <motion.span
                        animate={{ opacity: [1, 0] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                    >
                        |
                    </motion.span>
                </p>
            )}
        </motion.div>
    );
}
