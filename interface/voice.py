"""
Voice interface — speech-to-text and text-to-speech for Zia.
Refactored from the original voice_interface.py.
"""

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class VoiceInterface:
    """Microphone input (STT) and speaker output (TTS)."""

    def __init__(self):
        self.recognizer = sr.Recognizer() if STT_AVAILABLE else None
        self.tts_engine = pyttsx3.init() if TTS_AVAILABLE else None

        if self.tts_engine:
            voices = self.tts_engine.getProperty("voices")
            self.tts_engine.setProperty("voice", voices[0].id)
            self.tts_engine.setProperty("rate", 175)

    def listen(self, timeout: int = 5) -> str:
        """Listen for voice input and return transcribed text."""
        if not STT_AVAILABLE or not self.recognizer:
            raise RuntimeError("SpeechRecognition is not installed.")

        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                print(f"   You said: {text}")
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""

    def speak(self, text: str):
        """Speak text aloud via TTS."""
        if not TTS_AVAILABLE or not self.tts_engine:
            print(f"🔊 Zia: {text}")
            return

        print(f"🔊 Zia: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
