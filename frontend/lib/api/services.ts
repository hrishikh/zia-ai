// ── OAuth service management ──
import api from "./client";
import type { ConnectedService } from "@/lib/types";

/** GET /api/v1/auth/services — list connected OAuth services for current user */
export async function getConnectedServices(): Promise<ConnectedService[]> {
    const { data } = await api.get<ConnectedService[]>("/auth/services");
    return data;
}

/** GET /api/v1/auth/oauth/{service}/authorize — get OAuth redirect URL */
export async function getOAuthUrl(service: string): Promise<{ authorization_url: string }> {
    const { data } = await api.get(`/auth/oauth/${service}/authorize`);
    return data;
}

/** DELETE /api/v1/auth/services/{service}/revoke — revoke a connected service */
export async function revokeService(service: string): Promise<void> {
    await api.delete(`/auth/services/${service}/revoke`);
}
