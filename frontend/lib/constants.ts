// ── App-wide constants ──
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "Zia AI";

// ── API / WebSocket base URLs ─────────────────────────────────────────────────
// These MUST be set as environment variables. There is no localhost fallback:
// silently falling back to localhost would cause every production API call to fail.

if (!process.env.NEXT_PUBLIC_API_URL) {
    throw new Error(
        "NEXT_PUBLIC_API_URL is not set. " +
        "Add it to .env.local for local dev, or to Vercel → Settings → Environment Variables for production."
    );
}
if (!process.env.NEXT_PUBLIC_WS_URL) {
    throw new Error(
        "NEXT_PUBLIC_WS_URL is not set. " +
        "Add it to .env.local for local dev, or to Vercel → Settings → Environment Variables for production."
    );
}

export const API_URL: string = process.env.NEXT_PUBLIC_API_URL;
export const WS_URL: string = process.env.NEXT_PUBLIC_WS_URL;

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
