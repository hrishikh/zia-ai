"""
Zia AI — Filesystem Executor
Read, search, and open local files (sandboxed).
"""

import glob
import os
from typing import Any, Dict, List

from app.executors.base import BaseExecutor

# Sandbox: only allow access under these paths
ALLOWED_ROOTS = [
    os.path.expanduser("~"),
    "D:\\",
]

BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".ps1", ".vbs", ".msi"}


class FilesystemExecutor(BaseExecutor):
    def get_supported_actions(self) -> List[str]:
        return ["filesystem.read_file", "filesystem.search", "filesystem.open_file"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        if action_type == "filesystem.read_file":
            self.validate_params(action_type, params, ["path"])
            return self._read_file(params["path"])
        elif action_type == "filesystem.search":
            self.validate_params(action_type, params, ["query"])
            return self._search(params)
        elif action_type == "filesystem.open_file":
            self.validate_params(action_type, params, ["path"])
            return self._open_file(params["path"])
        raise ValueError(f"Unsupported: {action_type}")

    def _check_path(self, path: str) -> str:
        """Resolve and validate path is within sandbox."""
        resolved = os.path.realpath(path)
        if not any(resolved.startswith(root) for root in ALLOWED_ROOTS):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        _, ext = os.path.splitext(resolved)
        if ext.lower() in BLOCKED_EXTENSIONS:
            raise PermissionError(f"Blocked extension: {ext}")
        return resolved

    def _read_file(self, path: str) -> Dict:
        resolved = self._check_path(path)
        if not os.path.isfile(resolved):
            return {"error": f"Not a file: {path}"}
        size = os.path.getsize(resolved)
        if size > 1_000_000:  # 1MB limit
            return {"error": "File too large (>1MB)", "size": size}
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"status": "read", "path": resolved, "size": size, "content": content}

    def _search(self, params: Dict) -> Dict:
        query = params["query"]
        directory = params.get("directory", os.path.expanduser("~"))
        extension = params.get("extension", "*")
        directory = self._check_path(directory)

        pattern = os.path.join(directory, "**", f"*{query}*.{extension}")
        matches = glob.glob(pattern, recursive=True)[:50]
        return {"status": "search_complete", "matches": matches, "count": len(matches)}

    def _open_file(self, path: str) -> Dict:
        resolved = self._check_path(path)
        os.startfile(resolved)
        return {"status": "opened", "path": resolved}
