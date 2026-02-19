"use client";
import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useState,
} from "react";
import { getMe, login as apiLogin, logout as apiLogout } from "@/lib/api/auth";
import { setAccessToken, getAccessToken, setRefreshToken, getRefreshToken } from "@/lib/api/client";
import type { TokenResponse, User } from "@/lib/types";

interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Boot: only try to restore session if we already have tokens in memory
    useEffect(() => {
        (async () => {
            const hasToken = getAccessToken();
            if (!hasToken) {
                // No token → not logged in, skip network call entirely
                setIsLoading(false);
                return;
            }
            try {
                const me = await getMe();
                setUser(me);
            } catch {
                // Token expired / invalid — clear tokens, remain unauthenticated
                setAccessToken(null);
                setRefreshToken(null);
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        })();
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        const tokens: TokenResponse = await apiLogin(email, password);
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);
        const me = await getMe();
        setUser(me);
    }, []);

    const logout = useCallback(async () => {
        try {
            await apiLogout();
        } catch {
            // Ignore errors during logout (e.g. already expired token)
        } finally {
            setAccessToken(null);
            setRefreshToken(null);
            setUser(null);
        }
    }, []);

    const refresh = useCallback(async () => {
        if (!getRefreshToken()) return;
        try {
            const me = await getMe();
            setUser(me);
        } catch {
            setAccessToken(null);
            setRefreshToken(null);
            setUser(null);
        }
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                isAuthenticated: !!user,
                login,
                logout,
                refresh,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextValue {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}

