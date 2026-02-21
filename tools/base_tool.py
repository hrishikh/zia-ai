"""
Base tool and tool registry for Zia AI.

Every tool subclasses BaseTool and provides:
  - name, description, parameters (JSON Schema)
  - execute(**kwargs) -> dict

Security: ToolRegistry validates arguments against JSON schemas
before execution. Malformed inputs are rejected.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import jsonschema

logger = logging.getLogger("zia.tools")

# ── Sensitive fields to redact in logs ──
_REDACT_FIELDS = {"body", "content", "password", "token", "secret", "key"}
_MAX_LOG_VALUE_LEN = 80


def _redact_args(args: dict) -> dict:
    """Return a copy of args with sensitive/long values truncated."""
    safe = {}
    for k, v in args.items():
        if k.lower() in _REDACT_FIELDS:
            safe[k] = f"<redacted {len(str(v))} chars>"
        elif isinstance(v, str) and len(v) > _MAX_LOG_VALUE_LEN:
            safe[k] = v[:_MAX_LOG_VALUE_LEN] + "…"
        else:
            safe[k] = v
    return safe


class BaseTool(ABC):
    """Abstract base class for all Zia tools."""

    name: str = ""
    description: str = ""
    parameters: dict = {}  # JSON Schema for the tool's inputs

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """Run the tool and return a result dict."""
        ...

    def tool_schema(self) -> dict:
        """Return the tool schema (OpenAI-compatible format, used by Groq)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """
    Central registry of all available tools.
    Provides schemas for the LLM and dispatches execution.
    Validates arguments before execution.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Register a tool instance."""
        if not tool.name:
            raise ValueError(f"Tool {type(tool).__name__} has no name.")
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    def get_tool(self, name: str) -> BaseTool | None:
        """Look up a tool by name."""
        return self._tools.get(name)

    def get_tool_schemas(self) -> list[dict]:
        """Return all tool schemas for the LLM tools parameter."""
        return [tool.tool_schema() for tool in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> dict:
        """
        Validate arguments against the tool's JSON schema,
        then execute. Returns a result dict or an error dict.
        """
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}

        # ── VALIDATION GATE ──
        try:
            jsonschema.validate(instance=arguments, schema=tool.parameters)
        except jsonschema.ValidationError as ve:
            logger.warning("Validation failed for %s: %s", name, ve.message)
            return {"error": f"Invalid arguments for {name}: {ve.message}"}

        # ── EXECUTION ──
        try:
            safe_args = _redact_args(arguments)
            logger.info("Executing tool %s with args: %s", name, safe_args)
            result = tool.execute(**arguments)
            logger.info("Tool %s completed successfully.", name)
            return result
        except Exception as e:
            logger.error("Tool %s failed: %s", name, e)
            return {"error": str(e)}

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
