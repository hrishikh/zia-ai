"""
Zia Brain — LLM-based reasoning engine with JSON action routing.

Instead of API-level function calling (tools= parameter), the model is
instructed via system prompt to emit structured JSON when an action is needed.
The brain parses the JSON, validates arguments, executes the tool, feeds the
result back, and gets a final human-readable response.

Security:
  - Max action rounds enforced (MAX_TOOL_ROUNDS)
  - Arguments validated via jsonschema before execution
  - API errors caught and surfaced cleanly
  - Malformed model output handled gracefully
"""

import json
import logging
import re
from groq import Groq, APIError, RateLimitError, AuthenticationError, APIConnectionError

from core.config import settings
from core.memory import ShortTermMemory, LongTermMemory
from tools.base_tool import ToolRegistry

logger = logging.getLogger("zia.brain")

MAX_TOOL_ROUNDS = 3


def _build_system_prompt(registry: ToolRegistry) -> str:
    """Build system prompt that includes available tools as JSON instructions."""
    tool_descriptions = []
    for name in registry.tool_names:
        tool = registry.get_tool(name)
        params = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])
        param_lines = []
        for pname, pinfo in params.items():
            req = " (required)" if pname in required else ""
            param_lines.append(f'      "{pname}": "{pinfo.get("description", "")}"{req}')
        param_block = ",\n".join(param_lines)
        tool_descriptions.append(
            f'  - {name}: {tool.description}\n    Arguments:\n{{{{\n{param_block}\n    }}}}'
        )

    tools_section = "\n".join(tool_descriptions)

    return f"""You are Zia, a personal AI assistant for Hrishik.

Your personality:
- Direct, efficient, and friendly
- You execute tasks, don't just suggest
- You take real actions using the tools listed below

Available tools:
{tools_section}

CRITICAL RULES FOR TOOL USE:
When you need to use a tool, respond with ONLY a JSON object in this exact format — no extra text, no markdown fences, no explanation before or after:

{{"action": "tool_name", "arguments": {{"param1": "value1"}}}}

When no tool is needed, respond with plain text only.
Never wrap JSON in markdown code blocks.
Never add text before or after the JSON when using a tool.
Never fabricate tool results — wait for the actual result.
If a tool fails, tell the user honestly.
Keep responses concise."""


class ZiaBrain:
    """
    Central reasoning engine.
    Uses structured JSON action mode instead of API-level function calling.
    """

    def __init__(self, registry: ToolRegistry, memory: ShortTermMemory):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.registry = registry
        self.memory = memory
        self.long_term = LongTermMemory()
        self._system_prompt = _build_system_prompt(registry)

        logger.info("Brain initialized — model: %s", self.model)
        logger.info("Available tools: %s", registry.tool_names)

    def think(self, user_input: str) -> str:
        """
        Process user input, detect JSON actions, execute tools,
        and return the final text response.
        """
        self.memory.add("user", user_input)

        messages = [{"role": "system", "content": self._system_prompt}]
        messages.extend(self.memory.get_messages())

        try:
            final_text = self._action_loop(messages)
        except RateLimitError as e:
            logger.error("Groq rate limit: %s", e)
            final_text = "Rate limit reached. Please wait a moment and try again."
        except AuthenticationError as e:
            logger.error("Groq auth error: %s", e)
            final_text = "Invalid GROQ_API_KEY. Check your .env file."
        except APIConnectionError as e:
            logger.error("Groq connection error: %s", e)
            final_text = "Cannot reach Groq API. Check your internet connection."
        except APIError as e:
            logger.error("Groq API error: %s", e)
            final_text = f"Sorry, API error: {e}"
        except Exception as e:
            logger.error("Unexpected error in think(): %s", e, exc_info=True)
            final_text = f"Sorry, something went wrong: {e}"

        self.memory.add("assistant", final_text)
        return final_text

    def _action_loop(self, messages: list[dict]) -> str:
        """
        Call the LLM, parse response for JSON actions, execute, loop.
        Capped at MAX_TOOL_ROUNDS.
        """
        for round_num in range(MAX_TOOL_ROUNDS + 1):
            logger.debug("Action round %d", round_num)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            content = response.choices[0].message.content or ""
            messages.append({"role": "assistant", "content": content})

            # Try to parse as a tool action
            action = self._extract_action(content)

            # No action detected — this is a plain text reply
            if action is None:
                return content

            # Depth limit reached — ask for a text summary
            if round_num >= MAX_TOOL_ROUNDS:
                logger.warning("Max action rounds (%d) reached.", MAX_TOOL_ROUNDS)
                messages.append({
                    "role": "user",
                    "content": "Action limit reached. Please summarize what you've done so far in plain text.",
                })
                summary = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return summary.choices[0].message.content or ""

            # Execute the action
            tool_name = action["action"]
            tool_args = action.get("arguments", {})
            logger.info("Action detected [round %d]: %s", round_num, tool_name)

            result = self.registry.execute(tool_name, tool_args)

            # Feed result back to model for a human-readable response
            messages.append({
                "role": "user",
                "content": f"Tool result for {tool_name}: {json.dumps(result)}\n\nNow respond to the user about what happened. Use plain text only.",
            })

        return "I wasn't able to complete the request."

    @staticmethod
    def _extract_action(text: str) -> dict | None:
        """
        Try to extract a {"action": ..., "arguments": ...} JSON from model output.
        Returns the parsed dict or None if the text is not a tool action.
        """
        stripped = text.strip()

        # Remove markdown code fences if the model wraps JSON in them
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
        stripped = stripped.strip()

        # Quick check — must look like JSON
        if not stripped.startswith("{"):
            return None

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return None

        # Must have the "action" key to be a tool call
        if isinstance(parsed, dict) and "action" in parsed:
            return parsed

        return None
