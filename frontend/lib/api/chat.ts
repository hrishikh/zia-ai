// ── Zia Brain Chat API ──
// Calls POST /chat on the backend (no auth required — brain endpoint is public).
// Uses native fetch so the JWT axios interceptor doesn't interfere.

import { API_URL } from "@/lib/constants";

export interface ChatResponse {
    response: string;
}

export async function sendMessage(message: string): Promise<ChatResponse> {
    const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    });

    if (!res.ok) {
        const detail = await res.text().catch(() => "Unknown error");
        throw new Error(`Chat API error ${res.status}: ${detail}`);
    }

    return res.json() as Promise<ChatResponse>;
}
