"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useActionStore } from "@/stores/actionStore";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { ACTION_ICONS } from "@/lib/constants";
import { clsx } from "clsx";

export function ActionFeed() {
    const feedItems = useActionStore((s) => s.feedItems);

    if (feedItems.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-white/30 text-sm">No recent activity yet.</p>
                <p className="text-white/20 text-xs mt-1">Actions you execute will appear here.</p>
            </div>
        );
    }

    return (
        <ul className="flex flex-col gap-2">
            <AnimatePresence initial={false}>
                {feedItems.slice(0, 8).map((item) => (
                    <motion.li
                        key={item.execution_id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 10 }}
                        transition={{ duration: 0.25 }}
                        className={clsx(
                            "flex items-center gap-3 px-4 py-3 rounded-xl",
                            "bg-white/[0.04] border border-white/[0.06]",
                            "hover:bg-white/[0.07] hover:border-white/10 transition-all duration-200"
                        )}
                    >
                        <span className="text-xl shrink-0">
                            {ACTION_ICONS[item.action_type] ?? "✨"}
                        </span>
                        <div className="flex-1 min-w-0">
                            <p className="text-white/80 text-sm font-medium truncate">
                                {item.action_type.replace(".", " › ")}
                            </p>
                            {item.message && (
                                <p className="text-white/40 text-xs truncate">{item.message}</p>
                            )}
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                            <RiskBadge level={item.risk_level} />
                            <StatusBadge status={item.status} />
                        </div>
                    </motion.li>
                ))}
            </AnimatePresence>
        </ul>
    );
}
