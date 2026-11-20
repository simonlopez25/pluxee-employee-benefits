"""Instancia de FastAPI: middlewares, rutas y manejadores de error."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppError
from app.routes import api_router


def create_app() -> FastAPI:
    """Fabrica la instancia de la aplicación."""
    app = FastAPI(
        title="Pluxee Employee Benefits API",
        version="0.1.0",
        docs_url="/docs",
        description="API del catálogo de beneficios para empleados (HU-09).",
        openapi_tags=[
        {
            "name": "benefits",
            "description": "Catálogo de beneficios.",
        },
        {
            "name": "budgets",
            "description": "Presupuestos en 2 niveles y referencias informativas por beneficio.",
        },
        {
            "name": "health",
            "description": "Estado del servidor.",
        },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Respuesta JSON consistente para errores de negocio."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    return app


app = create_app()
