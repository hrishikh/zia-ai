"use client";
import { motion } from "framer-motion";
import { useState } from "react";
import { revokeService } from "@/lib/api/services";
import { Button } from "@/components/ui/Button";
import { GlassCard } from "@/components/ui/GlassCard";
import type { ConnectedService } from "@/lib/types";

const SERVICE_META: Record<string, { label: string; icon: string }> = {
    gmail: { label: "Gmail", icon: "✉️" },
    spotify: { label: "Spotify", icon: "🎵" },
};

interface ConnectedServicesProps {
    services: ConnectedService[];
    onRevoked: (service: string) => void;
}

export function ConnectedServices({ services, onRevoked }: ConnectedServicesProps) {
    const [revoking, setRevoking] = useState<string | null>(null);

    const handleRevoke = async (service: string) => {
        setRevoking(service);
        try {
            await revokeService(service);
            onRevoked(service);
        } finally {
            setRevoking(null);
        }
    };

    if (services.length === 0) {
        return (
            <div className="text-center py-10">
                <p className="text-white/40 text-sm">No services connected.</p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {services.map((svc, i) => {
                const meta = SERVICE_META[svc.service] ?? { label: svc.service, icon: "🔗" };
                return (
                    <motion.div
                        key={svc.service}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.07 }}
                    >
                        <GlassCard padding="sm" className="flex items-center gap-4">
                            <span className="text-2xl">{meta.icon}</span>
                            <div className="flex-1 min-w-0">
                                <p className="text-white/90 font-semibold text-sm">{meta.label}</p>
                                <div className="flex items-center gap-1.5 mt-0.5">
                                    <div
                                        className={`w-1.5 h-1.5 rounded-full ${svc.status === "active"
                                                ? "bg-emerald-400"
                                                : "bg-red-400"
                                            }`}
                                    />
                                    <p className="text-white/40 text-xs capitalize">{svc.status}</p>
                                    {svc.connected_at && (
                                        <p className="text-white/30 text-xs">
                                            · since {new Date(svc.connected_at).toLocaleDateString()}
                                        </p>
                                    )}
                                </div>
                                {svc.scopes.length > 0 && (
                                    <p className="text-white/30 text-xs mt-0.5 truncate">
                                        {svc.scopes.join(", ")}
                                    </p>
                                )}
                            </div>
                            <Button
                                variant="danger"
                                size="sm"
                                isLoading={revoking === svc.service}
                                onClick={() => handleRevoke(svc.service)}
                            >
                                Revoke
                            </Button>
                        </GlassCard>
                    </motion.div>
                );
            })}
        </div>
    );
}
