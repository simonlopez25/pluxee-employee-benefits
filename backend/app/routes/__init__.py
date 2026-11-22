"""Montaje de todos los routers bajo el prefijo /api."""

from __future__ import annotations

from fastapi import APIRouter

from app.routes import benefit, department, health

api_router = APIRouter(prefix="/api")
api_router.include_router(benefit.router)
api_router.include_router(health.router)
api_router.include_router(department.router)
