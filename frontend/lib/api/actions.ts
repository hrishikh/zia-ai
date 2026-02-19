// ── Actions API calls ──
import api from "./client";
import type { ActionRequest, ActionResponse, ActionHistoryItem } from "@/lib/types";

export async function executeAction(request: ActionRequest): Promise<ActionResponse> {
    const { data } = await api.post<ActionResponse>("/actions/execute", request);
    return data;
}

export async function confirmAction(
    execution_id: string,
    confirmation_token: string
): Promise<ActionResponse> {
    const { data } = await api.post<ActionResponse>("/actions/confirm", {
        execution_id,
        confirmation_token,
    });
    return data;
}

export async function rejectAction(
    execution_id: string,
    reason?: string
): Promise<void> {
    await api.post("/actions/reject", { execution_id, reason });
}

export async function getActionHistory(
    page = 1,
    per_page = 20
): Promise<{ items: ActionHistoryItem[]; total: number; page: number; per_page: number }> {
    const { data } = await api.get("/actions/history", {
        params: { page, per_page },
    });
    return data;
}

export async function getPendingActions(): Promise<{ items: ActionHistoryItem[] }> {
    const { data } = await api.get("/actions/pending");
    return data;
}
