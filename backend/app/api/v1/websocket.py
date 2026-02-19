"""
Zia AI — WebSocket API
Real-time voice I/O and action status push.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.action_engine import ActionEngine
from app.core.security import decode_token
from app.middleware.metrics import ACTIVE_WS_CONNECTIONS
from app.schemas.action import ActionRequest

router = APIRouter()
engine = ActionEngine()
logger = logging.getLogger("zia.ws")


@router.websocket("/voice")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket for voice/realtime interaction.
    Auth: pass JWT as query param ?token=xxx
    Messages: JSON with {type: "action", input_text: "..."}
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user = {"id": payload["sub"], "role": payload.get("role", "user")}

    await websocket.accept()
    ACTIVE_WS_CONNECTIONS.inc()
    logger.info(f"WebSocket connected: user={user['id']}")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            msg_type = data.get("type", "action")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "action":
                request = ActionRequest(
                    input_text=data.get("input_text"),
                    action_type=data.get("action_type"),
                    params=data.get("params"),
                    source="voice",
                )
                result = await engine.process_action(request, user)
                await websocket.send_json({
                    "type": "action_result",
                    "data": result.model_dump(),
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user={user['id']}")
    finally:
        ACTIVE_WS_CONNECTIONS.dec()
