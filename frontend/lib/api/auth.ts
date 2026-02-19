// ── Auth API calls ──
import api from "./client";
import type { TokenResponse, User } from "@/lib/types";

export async function login(email: string, password: string): Promise<TokenResponse> {
    console.log("[auth] POST /auth/login", { email, password: "***" });
    const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
    console.log("[auth] login response:", { access_token: data.access_token ? "✓" : "✗", refresh_token: data.refresh_token ? "✓" : "✗" });
    return data;
}

export async function register(
    email: string,
    password: string,
    display_name?: string
): Promise<User> {
    console.log("[auth] POST /auth/register", { email, display_name });
    const { data } = await api.post<User>("/auth/register", {
        email,
        password,
        display_name,
    });
    console.log("[auth] register response:", data);
    return data;
}

export async function getMe(): Promise<User> {
    console.log("[auth] GET /auth/me");
    const { data } = await api.get<User>("/auth/me");
    console.log("[auth] me response:", data.email);
    return data;
}

export async function logout(): Promise<void> {
    console.log("[auth] POST /auth/logout");
    await api.post("/auth/logout");
}
