"""
Zia AI — Base Executor
Abstract base class all executors must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseExecutor(ABC):
    """Base class for all action executors."""

    @abstractmethod
    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Execute the action and return a result dict."""
        ...

    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """Return list of action_type strings this executor handles."""
        ...

    def validate_params(
        self, action_type: str, params: Dict[str, Any], required: List[str]
    ) -> None:
        """Validate that all required params are present and non-empty."""
        missing = [p for p in required if p not in params or not params[p]]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
