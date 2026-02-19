"use client";
import useSWR from "swr";
import { useState } from "react";
import { getAuditLogs } from "@/lib/api/audit";
import type { AuditLogEntry } from "@/lib/types";

interface UseAuditLogsReturn {
    logs: AuditLogEntry[];
    total: number;
    isLoading: boolean;
    error: unknown;
    page: number;
    setPage: (p: number) => void;
    perPage: number;
}

export function useAuditLogs(perPage = 20): UseAuditLogsReturn {
    const [page, setPage] = useState(1);

    const { data, isLoading, error } = useSWR(
        ["audit-logs", page, perPage],
        () => getAuditLogs({ page, per_page: perPage }),
        {
            revalidateOnFocus: false,
            keepPreviousData: true,
        }
    );

    return {
        logs: data?.items ?? [],
        total: data?.total ?? 0,
        isLoading,
        error,
        page,
        setPage,
        perPage,
    };
}
