#!/usr/bin/env python3
"""
Zia v1 — Personal AI Agent
Entry point: CLI or voice mode.
"""

import sys
import argparse
import logging

from core.config import settings
from core.brain import ZiaBrain
from core.memory import ShortTermMemory
from tools.base_tool import ToolRegistry
from tools.email_tool import EmailTool
from tools.os_tool import OpenFileTool, LaunchAppTool
from tools.browser_tool import YouTubeTool, YouTubeControlTool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-14s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("zia")


def build_agent() -> ZiaBrain:
    """Wire up the tool registry, memory, and brain."""
    # Validate config
    missing = settings.validate()
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Set them in your .env file and restart.")
        sys.exit(1)

    # Tool registry
    registry = ToolRegistry()
    registry.register(EmailTool())
    registry.register(OpenFileTool())
    registry.register(LaunchAppTool())
    registry.register(YouTubeTool())
    registry.register(YouTubeControlTool())

    # Memory
    memory = ShortTermMemory(max_turns=settings.MAX_CONVERSATION_TURNS)

    # Brain
    brain = ZiaBrain(registry=registry, memory=memory)

    logger.info(
        "Zia v1 ready — %d tools loaded: %s",
        len(registry.tool_names),
        ", ".join(registry.tool_names),
    )
    return brain


def run_cli(brain: ZiaBrain):
    """Interactive CLI loop."""
    print("\n" + "=" * 50)
    print("  Zia v1 — Personal AI Agent")
    print("=" * 50)
    print("  Type your request. Say 'exit' to quit.\n")

    while True:
        try:
            user_input = input("💬 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "bye"):
                print("\n👋 Goodbye!")
                break

            response = brain.think(user_input)
            print(f"\n🤖 Zia: {response}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def run_voice(brain: ZiaBrain):
    """Voice input/output loop."""
    from interface.voice import VoiceInterface

    voice = VoiceInterface()
    print("\n🎙️  Zia v1 — Voice Mode Active")
    print("   Listening for commands...\n")

    while True:
        try:
            user_input = voice.listen()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "bye", "stop"):
                voice.speak("Goodbye!")
                break

            response = brain.think(user_input)
            voice.speak(response)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            voice.speak(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Zia v1 — Personal AI Agent")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    args = parser.parse_args()

    brain = build_agent()

    if args.voice:
        run_voice(brain)
    else:
        run_cli(brain)


if __name__ == "__main__":
    main()