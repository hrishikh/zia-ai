"use client";
import { motion } from "framer-motion";

interface WaveformProps {
    bars: number[];       // 0-1 normalised amplitudes
    isActive: boolean;
    className?: string;
}

export function Waveform({ bars, isActive, className }: WaveformProps) {
    return (
        <div
            className={`flex items-center gap-1 h-16 ${className ?? ""}`}
            aria-hidden="true"
        >
            {bars.map((amplitude, i) => (
                <motion.div
                    key={i}
                    className="w-1 rounded-full bg-gradient-to-t from-zia-purple to-zia-violet"
                    animate={{
                        scaleY: isActive ? Math.max(0.15, amplitude) : 0.12,
                        opacity: isActive ? 0.7 + amplitude * 0.3 : 0.3,
                    }}
                    transition={{
                        duration: 0.08,
                        ease: "linear",
                    }}
                    style={{ originY: 0.5, height: "100%" }}
                />
            ))}
        </div>
    );
}
