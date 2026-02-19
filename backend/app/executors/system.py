"""
Zia AI — System Command Executor
Run non-privileged system commands with an allowlist.
"""

import asyncio
import shlex
from typing import Any, Dict, List

from app.executors.base import BaseExecutor

# Allowed command prefixes (no sudo, no powershell -encoded, etc.)
COMMAND_ALLOWLIST = [
    "dir", "ls", "echo", "type", "cat", "whoami", "hostname",
    "ping", "ipconfig", "ifconfig", "systeminfo", "date", "time",
    "python", "node", "npm", "pip",
]

COMMAND_BLOCKLIST = [
    "rm -rf", "del /f /s", "format", "shutdown", "reboot",
    "sudo", "runas", "powershell -enc", "cmd /c rd",
    "mkfs", "dd if=", "chmod 777",
]

MAX_OUTPUT_LENGTH = 10_000  # chars
TIMEOUT_SECONDS = 30


class SystemExecutor(BaseExecutor):
    def get_supported_actions(self) -> List[str]:
        return ["system.run_command"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        self.validate_params(action_type, params, ["command"])
        command = params["command"]

        # Security checks
        cmd_lower = command.lower().strip()
        if any(blocked in cmd_lower for blocked in COMMAND_BLOCKLIST):
            raise PermissionError(f"Blocked command pattern detected: {command}")

        cmd_base = cmd_lower.split()[0] if cmd_lower.split() else ""
        if cmd_base not in COMMAND_ALLOWLIST:
            raise PermissionError(
                f"Command '{cmd_base}' not in allowlist. "
                f"Allowed: {', '.join(COMMAND_ALLOWLIST)}"
            )

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=TIMEOUT_SECONDS
            )

            output = stdout.decode(errors="replace")[:MAX_OUTPUT_LENGTH]
            error = stderr.decode(errors="replace")[:MAX_OUTPUT_LENGTH]

            return {
                "status": "command_executed",
                "exit_code": proc.returncode,
                "stdout": output,
                "stderr": error,
            }
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": f"Command timed out after {TIMEOUT_SECONDS}s"}
