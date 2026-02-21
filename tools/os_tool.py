"""
OS tool — open files and applications.
Restricted to an allowed list of directories for safety.
"""

import os
import subprocess
from pathlib import Path

from tools.base_tool import BaseTool
from core.config import settings


class OpenFileTool(BaseTool):
    name = "open_file"
    description = (
        "Open a file or folder on the user's computer. "
        "Use this when the user asks to open a directory, document, or application."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute path to the file or folder to open.",
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    }

    def execute(self, *, path: str) -> dict:
        resolved = Path(path).resolve()

        # Security: only allow paths under configured directories
        allowed = any(
            str(resolved).startswith(str(Path(d).resolve()))
            for d in settings.ALLOWED_DIRECTORIES
        )
        if not allowed:
            return {
                "error": f"Access denied. Path not in allowed directories: "
                         f"{settings.ALLOWED_DIRECTORIES}"
            }

        if not resolved.exists():
            return {"error": f"Path does not exist: {resolved}"}

        os.startfile(str(resolved))
        return {"status": "opened", "path": str(resolved)}


class LaunchAppTool(BaseTool):
    name = "launch_app"
    description = (
        "Launch a Windows application by name. "
        "Use this when the user asks to open an app like Notepad, Calculator, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of the application to launch (e.g. 'notepad', 'calc', 'explorer').",
            },
        },
        "required": ["app_name"],
        "additionalProperties": False,
    }

    # Allowed executables — SAFE GUI APPS ONLY.
    # No shells, terminals, or command interpreters.
    ALLOWED_APPS = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "paint": "mspaint.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "snipping tool": "snippingtool.exe",
    }

    def execute(self, *, app_name: str) -> dict:
        key = app_name.lower().strip()

        # 1. Exact match
        executable = self.ALLOWED_APPS.get(key)

        # 2. Partial match: input contained in a key, or key contained in input
        if not executable:
            for wl_key, wl_exe in self.ALLOWED_APPS.items():
                if key in wl_key or wl_key in key:
                    executable = wl_exe
                    break

        if not executable:
            return {
                "error": f"Application not allowed: '{app_name}'. "
                         f"Allowed: {list(self.ALLOWED_APPS.keys())}"
            }

        # shell=False — never invoke through a shell interpreter
        subprocess.Popen([executable])
        return {"status": "launched", "app": app_name}
