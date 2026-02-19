"use client";
import React, { createContext, useCallback, useContext, useState } from "react";
import type { PendingConfirmation } from "@/lib/types";

interface ConfirmContextValue {
    pending: PendingConfirmation | null;
    openConfirm: (confirmation: PendingConfirmation) => void;
    closeConfirm: () => void;
}

const ConfirmContext = createContext<ConfirmContextValue | null>(null);

export function ConfirmProvider({ children }: { children: React.ReactNode }) {
    const [pending, setPending] = useState<PendingConfirmation | null>(null);

    const openConfirm = useCallback((confirmation: PendingConfirmation) => {
        setPending(confirmation);
    }, []);

    const closeConfirm = useCallback(() => {
        setPending(null);
    }, []);

    return (
        <ConfirmContext.Provider value={{ pending, openConfirm, closeConfirm }}>
            {children}
        </ConfirmContext.Provider>
    );
}

export function useConfirmContext(): ConfirmContextValue {
    const ctx = useContext(ConfirmContext);
    if (!ctx) throw new Error("useConfirmContext must be inside ConfirmProvider");
    return ctx;
}
