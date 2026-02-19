// ── App-wide constants ──
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "Zia AI";
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/v1/ws";

export const RISK_LABELS: Record<string, string> = {
    low: "Low Risk",
    medium: "Medium Risk",
    high: "High Risk",
    critical: "Critical",
};

export const STATUS_LABELS: Record<string, string> = {
    created: "Created",
    rules_eval: "Evaluating",
    auto_approved: "Auto-approved",
    pending_confirmation: "Awaiting Confirmation",
    confirmed: "Confirmed",
    rejected: "Rejected",
    expired: "Expired",
    escalated: "Escalated",
    queued: "Queued",
    executing: "Executing",
    completed: "Completed",
    failed: "Failed",
    retrying: "Retrying",
};

export const ACTION_ICONS: Record<string, string> = {
    "gmail.send_email": "✉️",
    "gmail.read_inbox": "📬",
    "twilio.make_call": "📞",
    "twilio.send_whatsapp": "💬",
    "filesystem.read_file": "📄",
    "filesystem.search": "🔍",
    "filesystem.open_file": "📂",
    "browser.open_url": "🌐",
    "browser.youtube_play": "▶️",
    "system.run_command": "⚡",
    "macro.work_mode": "💼",
};

export const CONFIRMATION_TTL_SECONDS = 300; // 5 minutes
export const WS_RECONNECT_ATTEMPTS = 5;
export const WS_RECONNECT_BASE_DELAY_MS = 1000;
