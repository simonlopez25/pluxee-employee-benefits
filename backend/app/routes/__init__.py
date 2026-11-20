"""Montaje de todos los routers bajo el prefijo /api."""

from __future__ import annotations

from fastapi import APIRouter

from app.routes import health
from app.routes.users import router as users_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(users_router)
