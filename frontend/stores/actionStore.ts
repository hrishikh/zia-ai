// ── Zustand store for action feed + pending confirmations ──
import { create } from "zustand";
import type { ActionHistoryItem, ActionResponse, PendingConfirmation } from "@/lib/types";

interface ActionStore {
    // Feed
    feedItems: ActionHistoryItem[];
    pushActionResult: (result: ActionResponse) => void;
    setFeedItems: (items: ActionHistoryItem[]) => void;
    clearFeed: () => void;

    // Pending confirmations open in UI
    pendingConfirmations: PendingConfirmation[];
    addPending: (c: PendingConfirmation) => void;
    removePending: (execution_id: string) => void;
}

export const useActionStore = create<ActionStore>((set) => ({
    feedItems: [],
    pendingConfirmations: [],

    pushActionResult: (result) => {
        // Convert ActionResponse → ActionHistoryItem for the feed
        const item: ActionHistoryItem = {
            execution_id: result.execution_id,
            action_type: result.action_preview?.action ?? "unknown",
            status: result.status,
            source: "text",
            risk_level: result.action_preview?.risk_level ?? "low",
            created_at: new Date().toISOString(),
            message: result.message,
        };
        set((state) => ({
            feedItems: [item, ...state.feedItems].slice(0, 50), // cap at 50
        }));
    },

    setFeedItems: (items) => set({ feedItems: items }),
    clearFeed: () => set({ feedItems: [] }),

    addPending: (c) =>
        set((state) => ({
            pendingConfirmations: [...state.pendingConfirmations, c],
        })),

    removePending: (execution_id) =>
        set((state) => ({
            pendingConfirmations: state.pendingConfirmations.filter(
                (c) => c.execution_id !== execution_id
            ),
        })),
}));
