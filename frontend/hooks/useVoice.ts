"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type { VoiceState } from "@/lib/types";

interface UseVoiceOptions {
    onFinalTranscript?: (text: string) => void;
    onInterimTranscript?: (text: string) => void;
    language?: string;
}

interface UseVoiceReturn {
    state: VoiceState;
    transcript: string;
    interimTranscript: string;
    startListening: () => void;
    stopListening: () => void;
    waveformBars: number[];     // Normalised amplitudes 0-1 for 16 bars
    error: string | null;
    isSupported: boolean;
}

const NUM_BARS = 16;

export function useVoice({
    onFinalTranscript,
    onInterimTranscript,
    language = "en-US",
}: UseVoiceOptions = {}): UseVoiceReturn {
    const [state, setState] = useState<VoiceState>("idle");
    const [transcript, setTranscript] = useState("");
    const [interimTranscript, setInterimTranscript] = useState("");
    const [waveformBars, setWaveformBars] = useState<number[]>(Array(NUM_BARS).fill(0));
    const [error, setError] = useState<string | null>(null);

    const recognitionRef = useRef<any>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const animFrameRef = useRef<number>();

    const isSupported =
        typeof window !== "undefined" &&
        ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

    // Waveform animation loop
    const startWaveform = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaStreamRef.current = stream;
            const ctx = new AudioContext();
            const analyser = ctx.createAnalyser();
            analyser.fftSize = 64;
            ctx.createMediaStreamSource(stream).connect(analyser);
            audioContextRef.current = ctx;
            analyserRef.current = analyser;

            const buffer = new Uint8Array(analyser.frequencyBinCount);
            const tick = () => {
                analyser.getByteFrequencyData(buffer);
                const bars = Array.from({ length: NUM_BARS }, (_, i) => {
                    const idx = Math.floor((i / NUM_BARS) * buffer.length);
                    return buffer[idx] / 255;
                });
                setWaveformBars(bars);
                animFrameRef.current = requestAnimationFrame(tick);
            };
            animFrameRef.current = requestAnimationFrame(tick);
        } catch {
            // Microphone access denied — graceful fallback
        }
    }, []);

    const stopWaveform = useCallback(() => {
        cancelAnimationFrame(animFrameRef.current!);
        mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
        audioContextRef.current?.close();
        setWaveformBars(Array(NUM_BARS).fill(0));
    }, []);

    const startListening = useCallback(() => {
        if (!isSupported) {
            setError("Speech recognition not supported in this browser");
            return;
        }

        const SpeechRecognitionImpl =
            window.SpeechRecognition || (window as unknown as { webkitSpeechRecognition: typeof SpeechRecognition }).webkitSpeechRecognition;

        const recognition = new SpeechRecognitionImpl();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = language;

        recognition.onresult = (event) => {
            let interim = "";
            let final = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const r = event.results[i];
                if (r.isFinal) final += r[0].transcript;
                else interim += r[0].transcript;
            }
            if (final) {
                setTranscript((prev) => prev + final);
                onFinalTranscript?.(final.trim());
            }
            setInterimTranscript(interim);
            onInterimTranscript?.(interim);
        };

        recognition.onerror = (event) => {
            setError(event.error);
            setState("error");
        };

        recognition.onend = () => {
            if (state === "listening") recognition.start(); // keep alive
        };

        recognitionRef.current = recognition;
        recognition.start();
        startWaveform();
        setState("listening");
        setTranscript("");
        setInterimTranscript("");
        setError(null);
    }, [isSupported, language, onFinalTranscript, onInterimTranscript, startWaveform, state]);

    const stopListening = useCallback(() => {
        recognitionRef.current?.stop();
        recognitionRef.current = null;
        stopWaveform();
        setState("idle");
        setInterimTranscript("");
    }, [stopWaveform]);

    useEffect(() => {
        return () => {
            recognitionRef.current?.stop();
            stopWaveform();
        };
    }, [stopWaveform]);

    return {
        state,
        transcript,
        interimTranscript,
        startListening,
        stopListening,
        waveformBars,
        error,
        isSupported,
    };
}
