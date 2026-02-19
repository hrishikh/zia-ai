"""
Zia AI — Actions API
POST /execute, /confirm, /reject, GET /pending, /history
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.core.action_engine import ActionEngine
from app.core.action_registry import list_action_schemas
from app.schemas.action import (
    ActionRequest,
    ActionResponse,
    ConfirmActionRequest,
    RejectActionRequest,
)

router = APIRouter()
engine = ActionEngine()


@router.post("/execute", response_model=ActionResponse)
async def execute_action(
    request: ActionRequest, user: dict = Depends(get_current_user)
):
    """Submit an action for execution (text or structured)."""
    return await engine.process_action(request, user)


@router.post("/confirm", response_model=ActionResponse)
async def confirm_action(
    request: ConfirmActionRequest, user: dict = Depends(get_current_user)
):
    """Confirm a pending action with the confirmation token."""
    # In full implementation: validate token, transition FSM, enqueue to worker
    return ActionResponse(
        execution_id=request.execution_id,
        status="queued",
        message="Action confirmed and queued for execution",
    )


@router.post("/reject")
async def reject_action(
    request: RejectActionRequest, user: dict = Depends(get_current_user)
):
    """Reject a pending action."""
    return {
        "execution_id": request.execution_id,
        "status": "rejected",
        "message": "Action rejected",
        "reason": request.reason,
    }


@router.get("/pending")
async def get_pending(user: dict = Depends(get_current_user)):
    """List all pending confirmations for the current user."""
    return {"items": [], "total": 0}


@router.get("/history")
async def get_history(
    page: int = 1,
    per_page: int = 20,
    user: dict = Depends(get_current_user),
):
    """Get paginated action history."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.get("/schemas")
async def get_schemas(user: dict = Depends(get_current_user)):
    """List all registered action schemas."""
    schemas = list_action_schemas()
    return {"schemas": [s.model_dump() for s in schemas], "total": len(schemas)}
