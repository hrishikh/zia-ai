"""
Memory system for Zia AI.

ShortTermMemory — rolling conversation buffer for LLM context.
LongTermMemory  — placeholder for future vector-based retrieval.
"""

import json
import os
from datetime import datetime
from typing import Optional


class ShortTermMemory:
    """
    Rolling conversation buffer.
    Stores the last N message pairs for LLM context window.
    """

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self._messages: list[dict] = []

    def add(self, role: str, content: str):
        """Add a message to the buffer."""
        self._messages.append({"role": role, "content": content})
        # Trim to keep system + last N user/assistant pairs
        self._trim()

    def get_messages(self) -> list[dict]:
        """Return the current conversation history."""
        return list(self._messages)

    def clear(self):
        """Reset conversation history."""
        self._messages.clear()

    def _trim(self):
        """Keep only the last max_turns * 2 messages (user + assistant pairs)."""
        max_messages = self.max_turns * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]


class LongTermMemory:
    """
    Placeholder for persistent memory.
    Currently writes to a JSON file. Will be replaced with a vector DB
    (ChromaDB/Pinecone) in a future phase.
    """

    def __init__(self, storage_path: str = "~/.zia/memory.json"):
        self._path = os.path.expanduser(storage_path)
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

    def store(self, key: str, value: str, metadata: Optional[dict] = None):
        """Store a fact or task result."""
        entries = self._load()
        entries.append({
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        })
        self._save(entries)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        Basic substring search. Placeholder for semantic search.
        """
        entries = self._load()
        results = [
            e for e in entries
            if query.lower() in e["key"].lower()
            or query.lower() in e["value"].lower()
        ]
        return results[-limit:]

    def _load(self) -> list[dict]:
        if not os.path.exists(self._path):
            return []
        with open(self._path, "r") as f:
            return json.load(f)

    def _save(self, entries: list[dict]):
        with open(self._path, "w") as f:
            json.dump(entries, f, indent=2)
