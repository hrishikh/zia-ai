// ── Audit API calls ──
import api from "./client";
import type { AuditLogEntry, AuditStats } from "@/lib/types";

interface AuditLogsParams {
    page?: number;
    per_page?: number;
    action_type?: string;
    status?: string;
}

export async function getAuditLogs(
    params: AuditLogsParams = {}
): Promise<{ items: AuditLogEntry[]; total: number; page: number; per_page: number }> {
    const { data } = await api.get("/audit/logs", { params });
    return data;
}

export async function getAuditStats(): Promise<AuditStats> {
    const { data } = await api.get<AuditStats>("/audit/stats");
    return data;
}

export async function exportAuditLogs(format: "json" | "csv" = "json"): Promise<{
    format: string;
    download_url: string | null;
}> {
    const { data } = await api.get("/audit/export", { params: { format } });
    return data;
}
