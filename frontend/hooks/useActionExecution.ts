"use client";
import { useCallback, useState } from "react";
import { executeAction } from "@/lib/api/actions";
import { useConfirmContext } from "@/contexts/ConfirmContext";
import { useActionStore } from "@/stores/actionStore";
import type { ActionRequest, ActionResponse, PendingConfirmation } from "@/lib/types";

interface UseActionExecutionReturn {
    execute: (request: ActionRequest) => Promise<ActionResponse | null>;
    isLoading: boolean;
    error: string | null;
}

export function useActionExecution(): UseActionExecutionReturn {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { openConfirm } = useConfirmContext();
    const pushActionResult = useActionStore((s) => s.pushActionResult);

    const execute = useCallback(
        async (request: ActionRequest): Promise<ActionResponse | null> => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await executeAction(request);
                pushActionResult(response);

                // If confirmation required → open modal
                if (
                    response.confirmation_required &&
                    response.confirmation_token &&
                    response.action_preview
                ) {
                    const pending: PendingConfirmation = {
                        execution_id: response.execution_id,
                        confirmation_token: response.confirmation_token,
                        action_preview: response.action_preview,
                        risk_level: response.action_preview.risk_level,
                        created_at: new Date().toISOString(),
                    };
                    openConfirm(pending);
                }

                return response;
            } catch (err: unknown) {
                const msg =
                    err instanceof Error ? err.message : "Action execution failed";
                setError(msg);
                return null;
            } finally {
                setIsLoading(false);
            }
        },
        [openConfirm, pushActionResult]
    );

    return { execute, isLoading, error };
}
