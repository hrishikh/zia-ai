"use client";
import { motion } from "framer-motion";
import { useConfirmContext } from "@/contexts/ConfirmContext";
import { useConfirmation } from "@/hooks/useConfirmation";
import { RiskBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { clsx } from "clsx";

export function ConfirmModal() {
    const { pending } = useConfirmContext();
    const {
        secondsRemaining,
        isExpired,
        isConfirming,
        isRejecting,
        confirm,
        reject,
        error,
    } = useConfirmation();

    if (!pending) return null;

    const isHighRisk = pending.risk_level === "high" || pending.risk_level === "critical";
    const isCritical = pending.risk_level === "critical";
    const progressPct = (secondsRemaining / 300) * 100;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={() => reject("dismissed")}
            />

            {/* Card */}
            <motion.div
                initial={{ opacity: 0, scale: 0.92, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.92, y: 20 }}
                transition={{ type: "spring", damping: 28, stiffness: 400 }}
                className={clsx(
                    "relative z-10 w-full max-w-md glass-card p-6 space-y-5",
                    isCritical && "border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.2)]",
                    isHighRisk && !isCritical && "border-orange-500/40 shadow-[0_0_30px_rgba(249,115,22,0.15)]"
                )}
            >
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                        <p className="text-white/50 text-xs uppercase tracking-widest font-medium">
                            Confirmation Required
                        </p>
                        <h2 className="text-white text-lg font-bold leading-tight">
                            {pending.action_preview.action}
                        </h2>
                    </div>
                    <RiskBadge level={pending.risk_level} className="shrink-0 mt-1" />
                </div>

                {/* Description */}
                <p className="text-white/60 text-sm leading-relaxed">
                    {pending.action_preview.description}
                </p>

                {/* Triggered rules */}
                {pending.action_preview.reasons.length > 0 && (
                    <div className="space-y-1.5">
                        <p className="text-white/40 text-xs uppercase tracking-wider">Why confirmation?</p>
                        <ul className="space-y-1">
                            {pending.action_preview.reasons.map((reason, i) => (
                                <li key={i} className="flex items-start gap-2 text-white/60 text-sm">
                                    <span className="text-zia-amber mt-0.5 shrink-0">›</span>
                                    {reason}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Action params preview */}
                {Object.keys(pending.action_preview.params).length > 0 && (
                    <div className="bg-white/[0.04] rounded-xl p-3 border border-white/[0.06] space-y-1.5">
                        {Object.entries(pending.action_preview.params)
                            .filter(([k]) => !["body", "content"].includes(k)) // don't show big text fields
                            .map(([k, v]) => (
                                <div key={k} className="flex items-center gap-2 text-xs">
                                    <span className="text-white/40 w-20 shrink-0 capitalize">{k}</span>
                                    <span className="text-white/80 truncate">{String(v)}</span>
                                </div>
                            ))}
                    </div>
                )}

                {/* Critical warning */}
                {isCritical && (
                    <div className="flex items-start gap-2 bg-red-500/10 border border-red-500/30 rounded-xl p-3">
                        <span className="text-red-400 text-base shrink-0">⚠</span>
                        <p className="text-red-300 text-sm">This action is irreversible and cannot be undone.</p>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <p className="text-red-400 text-sm bg-red-500/10 rounded-xl p-3">{error}</p>
                )}

                {/* TTL progress bar */}
                <div className="space-y-1">
                    <div className="flex justify-between text-xs text-white/40">
                        <span>Expires in</span>
                        <span className={clsx(secondsRemaining < 30 && "text-red-400")}>
                            {Math.floor(secondsRemaining / 60)}:{String(secondsRemaining % 60).padStart(2, "0")}
                        </span>
                    </div>
                    <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                            className={clsx(
                                "h-full rounded-full transition-colors",
                                secondsRemaining > 60 ? "bg-zia-purple" : "bg-red-500"
                            )}
                            animate={{ width: `${progressPct}%` }}
                            transition={{ duration: 1, ease: "linear" }}
                        />
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-1">
                    <Button
                        variant="ghost"
                        className="flex-1"
                        onClick={() => reject("user_declined")}
                        isLoading={isRejecting}
                        disabled={isConfirming}
                    >
                        Reject
                    </Button>
                    <Button
                        variant={isCritical ? "danger" : "primary"}
                        className={clsx("flex-1", isCritical && "bg-red-600 hover:bg-red-700 shadow-none")}
                        onClick={confirm}
                        isLoading={isConfirming}
                        disabled={isExpired || isRejecting}
                    >
                        {isExpired ? "Expired" : "Confirm"}
                    </Button>
                </div>
            </motion.div>
        </div>
    );
}
