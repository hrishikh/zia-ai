"""
Zia AI — Macro Executor
Composite routines that chain multiple actions (e.g. Work Mode).
"""

from typing import Any, Dict, List

from app.executors.base import BaseExecutor


class MacroExecutor(BaseExecutor):
    """Executes composite macro routines."""

    def get_supported_actions(self) -> List[str]:
        return ["macro.work_mode"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        if action_type == "macro.work_mode":
            return await self._work_mode(params, user_id)
        raise ValueError(f"Unsupported macro: {action_type}")

    async def _work_mode(self, params: Dict, user_id: str) -> Dict:
        """
        Work Mode routine. In production, this enqueues sub-actions
        to the worker queue. For now, returns the planned steps.
        """
        steps = [
            {"action": "filesystem.open_file", "params": {"path": "D:\\Zia AI"}, "status": "planned"},
            {"action": "browser.youtube_play", "params": {"query": "Lofi Hip Hop radio"}, "status": "planned"},
            {"action": "gmail.send_email", "params": {
                "recipient": params.get("notify_email", ""),
                "subject": "Zia Work Mode: ACTIVE",
                "body": "Work Mode has been activated. Automated monitoring is now live.",
            }, "status": "planned"},
        ]

        return {
            "status": "macro_queued",
            "macro": "work_mode",
            "steps": steps,
            "total_steps": len(steps),
        }
