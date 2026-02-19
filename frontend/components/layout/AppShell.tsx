"use client";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useWebSocket } from "@/contexts/WebSocketContext";
import { ConfirmModal } from "@/components/confirmation/ConfirmModal";
import { useConfirmContext } from "@/contexts/ConfirmContext";
import { clsx } from "clsx";

interface AppShellProps {
    children: React.ReactNode;
    className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
    const { user, logout } = useAuth();
    const { status: wsStatus } = useWebSocket();
    const { pending } = useConfirmContext();
    const router = useRouter();
    const pathname = usePathname();

    const isHome = pathname === "/";

    // Back: use browser history if available, otherwise fall back to home
    const handleBack = () => {
        if (typeof window !== "undefined" && window.history.length > 1) {
            router.back();
        } else {
            router.push("/");
        }
    };

    return (
        <div className={clsx("min-h-screen font-sora", className)}>
            {/* Top nav */}
            <header className="fixed top-0 inset-x-0 z-40 flex items-center justify-between px-6 py-4">

                {/* Left: back button + logo */}
                <div className="flex items-center gap-2">
                    {/* Back button — hidden on home */}
                    <AnimatePresence>
                        {!isHome && (
                            <motion.button
                                key="back-btn"
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -8 }}
                                transition={{ duration: 0.15 }}
                                onClick={handleBack}
                                aria-label="Go back"
                                className="flex items-center justify-center w-7 h-7 rounded-lg
                                           text-white/50 hover:text-white/90 hover:bg-white/[0.07]
                                           transition-all duration-150"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M15 19l-7-7 7-7" />
                                </svg>
                            </motion.button>
                        )}
                    </AnimatePresence>

                    {/* Logo — always navigates to / via client-side Link */}
                    <Link
                        href="/"
                        className="flex items-center gap-2.5 group"
                        aria-label="Zia AI home"
                    >
                        <div className="w-8 h-8 rounded-full bg-zia-mic flex items-center justify-center
                                        text-sm font-bold shadow-mic-idle
                                        group-hover:scale-105 transition-transform duration-150">
                            Z
                        </div>
                        <span className="text-white/60 text-sm hidden sm:block
                                         group-hover:text-white/90 transition-colors duration-150">
                            Zia AI
                        </span>
                    </Link>
                </div>

                {/* Right: WS status, settings, sign out */}
                <div className="flex items-center gap-4">
                    {/* WebSocket status dot */}
                    <div className="flex items-center gap-1.5">
                        <div
                            className={clsx("w-2 h-2 rounded-full", {
                                "bg-emerald-400": wsStatus === "connected",
                                "bg-amber-400 animate-pulse": wsStatus === "connecting",
                                "bg-red-400": wsStatus === "disconnected" || wsStatus === "error",
                            })}
                        />
                        <span className="text-white/40 text-xs hidden sm:block">
                            {wsStatus === "connected" ? "Live" : wsStatus}
                        </span>
                    </div>

                    <button
                        onClick={() => router.push("/settings")}
                        className="text-white/50 hover:text-white/80 transition-colors"
                        aria-label="Settings"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </button>

                    <button
                        onClick={async () => { await logout(); router.push("/login"); }}
                        className="text-white/50 hover:text-white/80 transition-colors text-xs"
                    >
                        Sign out
                    </button>
                </div>
            </header>

            <main className="pt-16">{children}</main>

            {/* Global confirmation modal */}
            <AnimatePresence>{pending && <ConfirmModal />}</AnimatePresence>
        </div>
    );
}

