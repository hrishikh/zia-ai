"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { confirmAction, rejectAction } from "@/lib/api/actions";
import { useConfirmContext } from "@/contexts/ConfirmContext";
import { useActionStore } from "@/stores/actionStore";
import { CONFIRMATION_TTL_SECONDS } from "@/lib/constants";

interface UseConfirmationReturn {
    secondsRemaining: number;
    isExpired: boolean;
    isConfirming: boolean;
    isRejecting: boolean;
    confirm: () => Promise<void>;
    reject: (reason?: string) => Promise<void>;
    error: string | null;
}

export function useConfirmation(): UseConfirmationReturn {
    const { pending, closeConfirm } = useConfirmContext();
    const removePending = useActionStore((s) => s.removePending);
    const [secondsRemaining, setSecondsRemaining] = useState(CONFIRMATION_TTL_SECONDS);
    const [isConfirming, setIsConfirming] = useState(false);
    const [isRejecting, setIsRejecting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const timerRef = useRef<ReturnType<typeof setInterval>>();

    // Countdown timer keyed to when the confirmation was created
    useEffect(() => {
        if (!pending) {
            setSecondsRemaining(CONFIRMATION_TTL_SECONDS);
            return;
        }
        const created = new Date(pending.created_at).getTime();
        const tick = () => {
            const elapsed = Math.floor((Date.now() - created) / 1000);
            const remaining = Math.max(0, CONFIRMATION_TTL_SECONDS - elapsed);
            setSecondsRemaining(remaining);
            if (remaining === 0) {
                clearInterval(timerRef.current);
                closeConfirm();
            }
        };
        tick();
        timerRef.current = setInterval(tick, 1000);
        return () => clearInterval(timerRef.current);
    }, [pending, closeConfirm]);

    const confirm = useCallback(async () => {
        if (!pending) return;
        setIsConfirming(true);
        setError(null);
        try {
            await confirmAction(pending.execution_id, pending.confirmation_token);
            removePending(pending.execution_id);
            closeConfirm();
        } catch {
            setError("Confirmation failed. The token may have expired.");
        } finally {
            setIsConfirming(false);
        }
    }, [pending, closeConfirm, removePending]);

    const reject = useCallback(
        async (reason?: string) => {
            if (!pending) return;
            setIsRejecting(true);
            try {
                await rejectAction(pending.execution_id, reason);
                removePending(pending.execution_id);
                closeConfirm();
            } finally {
                setIsRejecting(false);
            }
        },
        [pending, closeConfirm, removePending]
    );

    return {
        secondsRemaining,
        isExpired: secondsRemaining === 0,
        isConfirming,
        isRejecting,
        confirm,
        reject,
        error,
    };
}
