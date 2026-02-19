"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useWebSocket } from "@/contexts/WebSocketContext";
import { useActionExecution } from "@/hooks/useActionExecution";
import { useVoice } from "@/hooks/useVoice";
import { AppShell } from "@/components/layout/AppShell";
import { MicButton } from "@/components/voice/MicButton";
import { Waveform } from "@/components/voice/Waveform";
import { SuggestionCard } from "@/components/actions/SuggestionCard";
import { ActionFeed } from "@/components/actions/ActionFeed";
import { Spinner } from "@/components/ui/Spinner";
import { GlassCard } from "@/components/ui/GlassCard";

const SUGGESTIONS = [
    { actionType: "gmail.send_email", displayName: "Send Email", description: "Draft and send via Gmail", riskLevel: "high" as const },
    { actionType: "gmail.read_inbox", displayName: "Read Inbox", description: "Summarise latest emails", riskLevel: "low" as const },
    { actionType: "browser.youtube_play", displayName: "Play Music", description: "Play anything on YouTube", riskLevel: "low" as const },
    { actionType: "macro.work_mode", displayName: "Work Mode", description: "Focus routine with notifications off", riskLevel: "medium" as const },
];

export default function HomePage() {
    const { user, isLoading, isAuthenticated } = useAuth();
    const { connect } = useWebSocket();
    const { execute, isLoading: isExecuting } = useActionExecution();
    const router = useRouter();

    const { state: voiceState, waveformBars, startListening, stopListening, transcript } =
        useVoice({
            onFinalTranscript: async (text) => {
                await execute({ input_text: text, source: "voice" });
            },
        });

    // Redirect to login if not authenticated after loading
    useEffect(() => {
        if (!isLoading && !isAuthenticated) router.push("/login");
    }, [isLoading, isAuthenticated, router]);

    // Connect WS after auth
    useEffect(() => {
        if (isAuthenticated) connect();
    }, [isAuthenticated, connect]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    if (!isAuthenticated) return null;

    return (
        <AppShell>
            <div className="max-w-2xl mx-auto px-5 py-8 flex flex-col gap-8">
                {/* Greeting */}
                <motion.div
                    initial={{ opacity: 0, y: -12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-center space-y-1 pt-4"
                >
                    <p className="text-white/50 text-sm tracking-widest uppercase">
                        Hello, {user?.display_name ?? user?.email.split("@")[0]}
                    </p>
                    <h1 className="text-3xl md:text-4xl font-bold zia-gradient-text leading-tight">
                        What are we going<br />to do today?
                    </h1>
                </motion.div>

                {/* Mic area */}
                <div className="flex flex-col items-center gap-6 py-4">
                    <Waveform bars={waveformBars} isActive={voiceState === "listening"} className="h-10" />
                    <MicButton
                        state={isExecuting ? "processing" : voiceState}
                        onPress={startListening}
                        onRelease={stopListening}
                    />
                </div>

                {/* Suggestion cards */}
                <div>
                    <p className="text-white/40 text-xs uppercase tracking-widest mb-3">Quick Actions</p>
                    <div className="grid grid-cols-2 gap-3">
                        {SUGGESTIONS.map((s, i) => (
                            <SuggestionCard
                                key={s.actionType}
                                {...s}
                                index={i}
                                onSelect={(type) => execute({ action_type: type, source: "text" })}
                            />
                        ))}
                    </div>
                </div>

                {/* Activity feed */}
                <GlassCard padding="sm">
                    <p className="text-white/40 text-xs uppercase tracking-widest mb-3 px-1">Recent Activity</p>
                    <ActionFeed />
                </GlassCard>
            </div>
        </AppShell>
    );
}
