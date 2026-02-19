// ── Shared TypeScript Types for Zia AI Frontend ──

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type ActionStatus =
    | "created"
    | "rules_eval"
    | "auto_approved"
    | "pending_confirmation"
    | "confirmed"
    | "rejected"
    | "expired"
    | "escalated"
    | "queued"
    | "executing"
    | "completed"
    | "failed"
    | "retrying";

export type ActionSource = "voice" | "text" | "api" | "macro";

// ── Auth ───────────────────────────────────────
export interface User {
    id: string;
    email: string;
    display_name: string | null;
    role: "user" | "admin";
    is_active: boolean;
    created_at: string;
    last_login: string | null;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

// ── Actions ────────────────────────────────────
export interface ActionRequest {
    input_text?: string;
    action_type?: string;
    params?: Record<string, unknown>;
    source?: ActionSource;
}

export interface ActionPreview {
    action: string;
    description: string;
    risk_level: RiskLevel;
    params: Record<string, unknown>;
    reasons: string[];
    expires_in_seconds: number;
}

export interface ActionResponse {
    execution_id: string;
    status: ActionStatus;
    message: string;
    data?: Record<string, unknown>;
    confirmation_required: boolean;
    confirmation_token?: string;
    action_preview?: ActionPreview;
}

export interface ActionHistoryItem {
    execution_id: string;
    action_type: string;
    status: ActionStatus;
    source: ActionSource;
    risk_level: RiskLevel;
    created_at: string;
    completed_at?: string;
    duration_ms?: number;
    message?: string;
}

// ── Confirmation ───────────────────────────────
export interface PendingConfirmation {
    execution_id: string;
    confirmation_token: string;
    action_preview: ActionPreview;
    risk_level: RiskLevel;
    created_at: string;
}

// ── Connected Services ─────────────────────────
export interface ConnectedService {
    service: string;
    status: "active" | "expired" | "revoked";
    connected_at: string | null;
    scopes: string[];
}

// ── Audit ──────────────────────────────────────
export interface AuditLogEntry {
    id: string;
    user_id: string;
    action_type: string;
    execution_id: string;
    risk_level: RiskLevel;
    status: ActionStatus;
    source: ActionSource;
    ip_address?: string;
    created_at: string;
    completed_at?: string;
    duration_ms?: number;
    message?: string;
}

export interface AuditStats {
    total_actions: number;
    actions_today: number;
    success_rate: number;
    most_used_actions: Record<string, number>;
    risk_distribution: Record<RiskLevel, number>;
}

// ── WebSocket ──────────────────────────────────
export interface WsMessage {
    type: "action_result" | "status_update" | "pong" | "error";
    data?: ActionResponse;
    execution_id?: string;
    status?: ActionStatus;
    error?: string;
}

// ── Voice ──────────────────────────────────────
export type VoiceState = "idle" | "listening" | "processing" | "error";
