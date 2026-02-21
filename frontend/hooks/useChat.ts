"use client";
// ── useChat ──
// Sends a transcript to ZiaBrain via POST /chat.
// Manages loading/response state and fires browser TTS on reply.

import { useCallback, useRef, useState } from "react";
import { sendMessage } from "@/lib/api/chat";

interface UseChatReturn {
    sendToZia: (text: string) => Promise<void>;
    response: string | null;
    isLoading: boolean;
    error: string | null;
}

export function useChat(): UseChatReturn {
    const [response, setResponse] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Keep a reference to the active utterance so we can cancel on new request
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    const sendToZia = useCallback(async (text: string) => {
        if (!text.trim()) return;

        // Cancel any ongoing speech before starting new request
        if (typeof window !== "undefined" && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }

        setIsLoading(true);
        setError(null);

        try {
            const result = await sendMessage(text);
            const reply = result.response;
            setResponse(reply);

            // Speak the reply via browser TTS
            if (typeof window !== "undefined" && window.speechSynthesis && reply) {
                const utterance = new SpeechSynthesisUtterance(reply);
                utterance.lang = "en-US";
                utterance.rate = 1.0;
                utteranceRef.current = utterance;
                window.speechSynthesis.speak(utterance);
            }
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : "Failed to reach Zia.";
            setError(msg);
            setResponse("Sorry, I couldn't reach the server. Please try again.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { sendToZia, response, isLoading, error };
}
