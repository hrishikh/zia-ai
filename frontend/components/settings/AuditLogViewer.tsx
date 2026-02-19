"use client";
import { useAuditLogs } from "@/hooks/useAuditLogs";
import { RiskBadge, StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ACTION_ICONS } from "@/lib/constants";

export function AuditLogViewer() {
    const { logs, total, isLoading, page, setPage, perPage } = useAuditLogs(15);
    const totalPages = Math.ceil(total / perPage);

    if (isLoading && logs.length === 0) {
        return <div className="flex justify-center py-12"><Spinner /></div>;
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <p className="text-white/50 text-sm">{total} total entries</p>
            </div>

            <div className="overflow-x-auto no-scrollbar">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="text-white/40 text-xs uppercase tracking-wider">
                            <th className="text-left pb-3 pr-4">Action</th>
                            <th className="text-left pb-3 pr-4">Status</th>
                            <th className="text-left pb-3 pr-4">Risk</th>
                            <th className="text-left pb-3 pr-4">Source</th>
                            <th className="text-left pb-3">Time</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                        {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-white/[0.02] transition-colors">
                                <td className="py-3 pr-4">
                                    <div className="flex items-center gap-2">
                                        <span>{ACTION_ICONS[log.action_type] ?? "✨"}</span>
                                        <span className="text-white/70 font-mono text-xs">{log.action_type}</span>
                                    </div>
                                </td>
                                <td className="py-3 pr-4"><StatusBadge status={log.status} /></td>
                                <td className="py-3 pr-4"><RiskBadge level={log.risk_level} /></td>
                                <td className="py-3 pr-4">
                                    <span className="text-white/40 text-xs capitalize">{log.source}</span>
                                </td>
                                <td className="py-3">
                                    <span className="text-white/40 text-xs">
                                        {new Date(log.created_at).toLocaleString()}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-3">
                    <Button variant="ghost" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
                        ← Prev
                    </Button>
                    <span className="text-white/40 text-sm">{page} / {totalPages}</span>
                    <Button variant="ghost" size="sm" disabled={page === totalPages} onClick={() => setPage(page + 1)}>
                        Next →
                    </Button>
                </div>
            )}
        </div>
    );
}
