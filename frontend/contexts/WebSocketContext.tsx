"use client";
import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from "react";
import { WS_URL, WS_RECONNECT_ATTEMPTS, WS_RECONNECT_BASE_DELAY_MS } from "@/lib/constants";
import { getAccessToken } from "@/lib/api/client";
import { useActionStore } from "@/stores/actionStore";
import type { WsMessage } from "@/lib/types";

type WsStatus = "connecting" | "connected" | "disconnected" | "error";

interface WsContextValue {
    status: WsStatus;
    send: (message: object) => void;
    connect: () => void;
    disconnect: () => void;
}

const WebSocketContext = createContext<WsContextValue | null>(null);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
    const ws = useRef<WebSocket | null>(null);
    const retryCount = useRef(0);
    const retryTimer = useRef<ReturnType<typeof setTimeout>>();
    const [status, setStatus] = useState<WsStatus>("disconnected");
    const pushActionResult = useActionStore((s) => s.pushActionResult);

    const connect = useCallback(() => {
        const token = getAccessToken();
        if (!token) return;

        if (ws.current?.readyState === WebSocket.OPEN) return;

        const url = `${WS_URL}/voice?token=${token}`;
        const socket = new WebSocket(url);
        ws.current = socket;
        setStatus("connecting");

        socket.onopen = () => {
            setStatus("connected");
            retryCount.current = 0;
        };

        socket.onmessage = (event) => {
            try {
                const msg: WsMessage = JSON.parse(event.data);
                if (msg.type === "action_result" && msg.data) {
                    pushActionResult(msg.data);
                }
            } catch {
                // ignore malformed messages
            }
        };

        socket.onerror = () => setStatus("error");

        socket.onclose = () => {
            setStatus("disconnected");
            // Exponential backoff reconnect
            if (retryCount.current < WS_RECONNECT_ATTEMPTS) {
                const delay = WS_RECONNECT_BASE_DELAY_MS * 2 ** retryCount.current;
                retryCount.current += 1;
                retryTimer.current = setTimeout(connect, delay);
            }
        };
    }, [pushActionResult]);

    const disconnect = useCallback(() => {
        clearTimeout(retryTimer.current);
        retryCount.current = WS_RECONNECT_ATTEMPTS; // prevent reconnect
        ws.current?.close();
        ws.current = null;
        setStatus("disconnected");
    }, []);

    const send = useCallback((message: object) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => () => disconnect(), [disconnect]);

    // Send periodic pings
    useEffect(() => {
        if (status !== "connected") return;
        const interval = setInterval(() => send({ type: "ping" }), 30_000);
        return () => clearInterval(interval);
    }, [status, send]);

    return (
        <WebSocketContext.Provider value={{ status, send, connect, disconnect }}>
            {children}
        </WebSocketContext.Provider>
    );
}

export function useWebSocket(): WsContextValue {
    const ctx = useContext(WebSocketContext);
    if (!ctx) throw new Error("useWebSocket must be inside WebSocketProvider");
    return ctx;
}
