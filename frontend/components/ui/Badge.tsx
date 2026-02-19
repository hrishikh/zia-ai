"use client";
import { clsx } from "clsx";
import type { RiskLevel, ActionStatus } from "@/lib/types";

interface RiskBadgeProps {
    level: RiskLevel;
    className?: string;
}

const riskStyles: Record<RiskLevel, string> = {
    low: "risk-badge-low",
    medium: "risk-badge-medium",
    high: "risk-badge-high",
    critical: "risk-badge-critical",
};

const riskLabels: Record<RiskLevel, string> = {
    low: "Low Risk",
    medium: "Medium Risk",
    high: "High Risk",
    critical: "Critical",
};

export function RiskBadge({ level, className }: RiskBadgeProps) {
    return (
        <span
            className={clsx(
                "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium font-sora",
                riskStyles[level],
                className
            )}
        >
            {riskLabels[level]}
        </span>
    );
}

interface StatusBadgeProps {
    status: ActionStatus;
    className?: string;
}

const statusDot: Record<string, string> = {
    completed: "status-dot-completed",
    executing: "status-dot-executing",
    pending_confirmation: "status-dot-pending",
    failed: "status-dot-failed",
    queued: "status-dot-queued",
};

const statusLabels: Record<string, string> = {
    completed: "Completed",
    executing: "Executing",
    pending_confirmation: "Awaiting Confirmation",
    failed: "Failed",
    queued: "Queued",
    rejected: "Rejected",
    expired: "Expired",
    retrying: "Retrying",
    auto_approved: "Auto-approved",
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
    return (
        <span
            className={clsx(
                "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium",
                "bg-white/5 border border-white/10 text-white/70",
                className
            )}
        >
            <span className={statusDot[status] ?? "w-2 h-2 rounded-full bg-white/30"} />
            {statusLabels[status] ?? status}
        </span>
    );
}
