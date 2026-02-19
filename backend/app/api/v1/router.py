"""
Zia AI — v1 API Router
Aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.actions import router as actions_router
from app.api.v1.auth import router as auth_router
from app.api.v1.audit import router as audit_router
from app.api.v1.admin import router as admin_router
from app.api.v1.websocket import router as ws_router

api_router = APIRouter()

api_router.include_router(actions_router, prefix="/actions", tags=["actions"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(ws_router, prefix="/ws", tags=["websocket"])
