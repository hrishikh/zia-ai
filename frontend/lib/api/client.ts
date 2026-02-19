"use client";
// ── Axios client with JWT bearer injection and silent refresh on 401 ──

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { API_URL } from "@/lib/constants";

let accessToken: string | null = null;
let refreshToken: string | null = null;
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (value?: unknown) => void;
    reject: (error?: unknown) => void;
}> = [];

export function setAccessToken(token: string | null) {
    accessToken = token;
}

export function getAccessToken(): string | null {
    return accessToken;
}

export function setRefreshToken(token: string | null) {
    refreshToken = token;
}

export function getRefreshToken(): string | null {
    return refreshToken;
}

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error);
        else resolve(token);
    });
    failedQueue = [];
};

console.log("[api-client] baseURL =", API_URL);

const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    timeout: 15_000,
    headers: { "Content-Type": "application/json" },
});

// ── Request interceptor: inject Bearer token ──
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        console.log(`[api] ${config.method?.toUpperCase()} ${config.url}`, {
            hasAuth: !!config.headers.Authorization,
        });
        return config;
    },
    (error) => Promise.reject(error)
);

// ── Response interceptor: silent refresh on 401 ──
api.interceptors.response.use(
    (response) => {
        console.log(`[api] ✓ ${response.status} ${response.config.url}`);
        return response;
    },
    async (error: AxiosError) => {
        const original = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean;
        };

        console.log(`[api] ✗ ${error.response?.status} ${original?.url}`, {
            _retry: original?._retry,
            hasRefreshToken: !!refreshToken,
        });

        // Only attempt refresh on 401, and only once, and only if we have a refresh token
        if (
            error.response?.status !== 401 ||
            original._retry ||
            !refreshToken
        ) {
            return Promise.reject(error);
        }

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then((token) => {
                original.headers.Authorization = `Bearer ${token}`;
                return api(original);
            });
        }

        original._retry = true;
        isRefreshing = true;

        try {
            console.log("[api] attempting token refresh...");
            const { data } = await api.post("/auth/refresh", {
                refresh_token: refreshToken,
            });
            const newAccessToken = data.access_token;
            setAccessToken(newAccessToken);
            if (data.refresh_token) {
                setRefreshToken(data.refresh_token);
            }
            console.log("[api] token refresh successful");
            processQueue(null, newAccessToken);
            original.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(original);
        } catch (refreshError) {
            console.log("[api] token refresh failed", refreshError);
            processQueue(refreshError, null);
            setAccessToken(null);
            setRefreshToken(null);
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;
