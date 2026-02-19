"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { AppShell } from "@/components/layout/AppShell";
import { ConnectedServices } from "@/components/settings/ConnectedServices";
import { AuditLogViewer } from "@/components/settings/AuditLogViewer";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { getConnectedServices } from "@/lib/api/services";
import type { ConnectedService } from "@/lib/types";
import { clsx } from "clsx";

type Tab = "services" | "audit" | "profile";

export default function SettingsPage() {
    const { user, isAuthenticated, isLoading, logout } = useAuth();
    const router = useRouter();
    const [tab, setTab] = useState<Tab>("services");
    const [services, setServices] = useState<ConnectedService[]>([]);
    const [loadingServices, setLoadingServices] = useState(true);

    useEffect(() => {
        if (!isLoading && !isAuthenticated) router.push("/login");
    }, [isLoading, isAuthenticated, router]);

    useEffect(() => {
        if (!isAuthenticated) return;
        getConnectedServices().then(setServices).finally(() => setLoadingServices(false));
    }, [isAuthenticated]);

    if (isLoading) return <div className="min-h-screen flex items-center justify-center"><Spinner size="lg" /></div>;
    if (!isAuthenticated) return null;

    const tabLabel = (t: Tab, label: string) => (
        <button
            onClick={() => setTab(t)}
            className={clsx(
                "px-4 py-2 text-sm font-medium rounded-xl transition-all",
                tab === t
                    ? "bg-zia-purple/30 text-white border border-zia-purple/40"
                    : "text-white/50 hover:text-white/80 hover:bg-white/5"
            )}
        >
            {label}
        </button>
    );

    return (
        <AppShell>
            <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-white">Settings</h1>
                    <p className="text-white/40 text-sm mt-1">Manage your account and connected services</p>
                </div>

                {/* Tab bar */}
                <div className="flex gap-2">
                    {tabLabel("services", "Connected Services")}
                    {tabLabel("audit", "Audit Log")}
                    {tabLabel("profile", "Profile")}
                </div>

                {/* Tab panels */}
                <GlassCard padding="md">
                    {tab === "services" && (
                        loadingServices
                            ? <div className="flex justify-center py-8"><Spinner /></div>
                            : <ConnectedServices services={services} onRevoked={(s) => setServices((prev) => prev.filter((x) => x.service !== s))} />
                    )}
                    {tab === "audit" && <AuditLogViewer />}
                    {tab === "profile" && (
                        <div className="space-y-5">
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 rounded-full bg-zia-mic flex items-center justify-center text-2xl font-bold shadow-mic-idle">
                                    {(user?.display_name ?? user?.email ?? "A")[0].toUpperCase()}
                                </div>
                                <div>
                                    <p className="text-white font-semibold">{user?.display_name ?? "—"}</p>
                                    <p className="text-white/50 text-sm">{user?.email}</p>
                                    <p className="text-white/30 text-xs capitalize mt-0.5">{user?.role}</p>
                                </div>
                            </div>
                            <div className="border-t border-white/[0.06] pt-4">
                                <Button
                                    variant="danger"
                                    onClick={async () => { await logout(); router.push("/login"); }}
                                >
                                    Sign Out
                                </Button>
                            </div>
                        </div>
                    )}
                </GlassCard>
            </div>
        </AppShell>
    );
}
