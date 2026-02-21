"""
Zia AI — Actions API
POST /execute routes text through ZiaBrain (Groq LLM + tool registry).
All other legacy endpoints preserved for frontend compatibility.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.action_registry import list_action_schemas
from app.schemas.action import (
    ActionRequest,
    ConfirmActionRequest,
    RejectActionRequest,
)

logger = logging.getLogger("zia.api.actions")

router = APIRouter()

# ── Brain singleton (lazy import from main.py) ──
_brain = None


def get_brain():
    global _brain
    if _brain is None:
        from app.main import brain
        _brain = brain
        logger.info("Brain loaded into actions route: %s", _brain.model)
    return _brain


class BrainResponse(BaseModel):
    """Simple response — what the frontend expects."""
    response: str


print("✅ ACTIONS.PY LOADED — ZIA BRAIN ROUTE ACTIVE")


@router.post("/execute", response_model=BrainResponse)
async def execute_action(
    request: ActionRequest, user: dict = Depends(get_current_user)
):
    """
    Send user text to ZiaBrain.
    No old action detection. No action engine. Just brain.think().
    """
    print(f"🧠 ZIA BRAIN ROUTE HIT — input: {request.input_text}")

    input_text = request.input_text or ""
    if not input_text.strip():
        raise HTTPException(status_code=400, detail="input_text is required")

    brain = get_brain()

    try:
        reply = brain.think(input_text)
    except Exception as e:
        logger.error("Brain error: %s", e, exc_info=True)
        return BrainResponse(response=f"Sorry, something went wrong: {str(e)}")

    return BrainResponse(response=reply)


# ── Legacy endpoints (preserved for frontend compatibility) ──

@router.post("/confirm")
async def confirm_action(
    request: ConfirmActionRequest, user: dict = Depends(get_current_user)
):
    return {
        "execution_id": request.execution_id,
        "status": "queued",
        "message": "Action confirmed and queued for execution",
    }


@router.post("/reject")
async def reject_action(
    request: RejectActionRequest, user: dict = Depends(get_current_user)
):
    return {
        "execution_id": request.execution_id,
        "status": "rejected",
        "message": "Action rejected",
        "reason": request.reason,
    }


@router.get("/pending")
async def get_pending(user: dict = Depends(get_current_user)):
    return {"items": [], "total": 0}


@router.get("/history")
async def get_history(
    page: int = 1,
    per_page: int = 20,
    user: dict = Depends(get_current_user),
):
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.get("/schemas")
async def get_schemas(user: dict = Depends(get_current_user)):
    schemas = list_action_schemas()
    return {"schemas": [s.model_dump() for s in schemas], "total": len(schemas)}
