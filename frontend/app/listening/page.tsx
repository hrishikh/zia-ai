"use client";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useVoice } from "@/hooks/useVoice";
import { useActionExecution } from "@/hooks/useActionExecution";
import { MicButton } from "@/components/voice/MicButton";
import { Waveform } from "@/components/voice/Waveform";
import { Transcript } from "@/components/voice/Transcript";
import { Button } from "@/components/ui/Button";

export default function ListeningPage() {
    const router = useRouter();
    const { isAuthenticated } = useAuth();
    const { execute, isLoading: isExecuting } = useActionExecution();

    const {
        state, waveformBars, startListening, stopListening,
        transcript, interimTranscript,
    } = useVoice({
        onFinalTranscript: async (text) => {
            await execute({ input_text: text, source: "voice" });
        },
    });

    useEffect(() => {
        if (!isAuthenticated) router.push("/login");
    }, [isAuthenticated, router]);

    // Auto-start listening on mount
    useEffect(() => {
        startListening();
        return () => stopListening();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <main className="min-h-screen flex flex-col items-center justify-center gap-8 px-5 py-12">
            {/* Ambient background glow */}
            <div className="fixed inset-0 pointer-events-none">
                <motion.div
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full"
                    animate={{
                        background: state === "listening"
                            ? ["radial-gradient(circle, rgba(108,77,230,0.25) 0%, transparent 70%)",
                                "radial-gradient(circle, rgba(108,77,230,0.4) 0%, transparent 70%)",
                                "radial-gradient(circle, rgba(108,77,230,0.25) 0%, transparent 70%)"]
                            : "radial-gradient(circle, rgba(108,77,230,0.1) 0%, transparent 70%)",
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                />
            </div>

            {/* Waveform */}
            <Waveform bars={waveformBars} isActive={state === "listening"} className="h-14" />

            {/* Mic button */}
            <MicButton
                state={isExecuting ? "processing" : state}
                onPress={startListening}
                onRelease={stopListening}
                size="lg"
            />

            {/* Live transcript */}
            <Transcript finalText={transcript} interimText={interimTranscript} />

            {/* Controls */}
            <div className="flex items-center gap-4">
                <Button
                    variant="ghost"
                    onClick={() => { stopListening(); router.push("/"); }}
                >
                    ← Back to Home
                </Button>
                {state === "listening" && (
                    <Button variant="danger" onClick={stopListening}>
                        Stop Listening
                    </Button>
                )}
            </div>
        </main>
    );
}
