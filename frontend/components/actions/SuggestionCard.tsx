"use client";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/ui/GlassCard";
import { RiskBadge } from "@/components/ui/Badge";
import { ACTION_ICONS } from "@/lib/constants";
import type { ActionSchema } from "@/lib/types";

// Inline minimal type for card display (not full ActionSchema)
interface SuggestionCardProps {
    actionType: string;
    displayName: string;
    description: string;
    riskLevel: "low" | "medium" | "high" | "critical";
    onSelect: (actionType: string) => void;
    index?: number;
}

export function SuggestionCard({
    actionType,
    displayName,
    description,
    riskLevel,
    onSelect,
    index = 0,
}: SuggestionCardProps) {
    const icon = ACTION_ICONS[actionType] ?? "✨";

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08, duration: 0.4, ease: "easeOut" }}
        >
            <GlassCard
                hover
                glow="purple"
                padding="sm"
                onClick={() => onSelect(actionType)}
                className="cursor-pointer select-none h-full"
            >
                <div className="flex flex-col gap-2 h-full">
                    <div className="flex items-center justify-between">
                        <span className="text-2xl" role="img">{icon}</span>
                        <RiskBadge level={riskLevel} />
                    </div>
                    <p className="text-white/90 font-semibold text-sm leading-tight">{displayName}</p>
                    <p className="text-white/45 text-xs leading-relaxed mt-auto">{description}</p>
                </div>
            </GlassCard>
        </motion.div>
    );
}
