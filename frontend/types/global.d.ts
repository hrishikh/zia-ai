// ── SpeechRecognition Web API Types ──────────────────────────────────────────
// The Web Speech API is not yet part of the TypeScript DOM lib, so we declare
// it here. This file is auto-included by tsconfig "include": ["**/*.ts"].

declare global {
    // ── Result hierarchy ─────────────────────────────────────────────────────

    interface SpeechRecognitionAlternative {
        readonly transcript: string;
        readonly confidence: number;
    }

    interface SpeechRecognitionResult {
        readonly isFinal: boolean;
        readonly length: number;
        item(index: number): SpeechRecognitionAlternative;
        [index: number]: SpeechRecognitionAlternative;
    }

    interface SpeechRecognitionResultList {
        readonly length: number;
        item(index: number): SpeechRecognitionResult;
        [index: number]: SpeechRecognitionResult;
    }

    // ── Events ───────────────────────────────────────────────────────────────

    interface SpeechRecognitionEvent extends Event {
        readonly resultIndex: number;
        readonly results: SpeechRecognitionResultList;
    }

    interface SpeechRecognitionErrorEvent extends Event {
        readonly error: string;
        readonly message: string;
    }

    // ── Main interface ───────────────────────────────────────────────────────

    interface SpeechRecognition extends EventTarget {
        // Config
        continuous: boolean;
        interimResults: boolean;
        lang: string;
        maxAlternatives: number;

        // Methods
        start(): void;
        stop(): void;
        abort(): void;

        // Handlers
        onresult: ((event: SpeechRecognitionEvent) => void) | null;
        onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
        onend: ((event: Event) => void) | null;
        onstart: ((event: Event) => void) | null;
        onspeechstart: ((event: Event) => void) | null;
        onspeechend: ((event: Event) => void) | null;
    }

    // Constructor signature — needed to call `new SpeechRecognition()`
    interface SpeechRecognitionConstructor {
        new(): SpeechRecognition;
        prototype: SpeechRecognition;
    }

    // ── Window augmentation ──────────────────────────────────────────────────

    interface Window {
        SpeechRecognition?: SpeechRecognitionConstructor;
        webkitSpeechRecognition?: SpeechRecognitionConstructor;
    }
}

export { };