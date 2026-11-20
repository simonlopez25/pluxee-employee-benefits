"""Errores centralizados de la aplicación."""

from __future__ import annotations


class AppError(Exception):
    """Error con código HTTP y código legible por máquina.

    Se lanza desde services/ y se captura en app/main.py
    para devolver una respuesta JSON consistente.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "internal_error",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class NotFoundError(AppError):
    """Recurso inexistente (404)."""

    def __init__(self, message: str = "resource not found") -> None:
        super().__init__(message, status_code=404, code="not_found")


class ConflictError(AppError):
    """Conflicto con el estado actual del recurso (409)."""

    def __init__(self, message: str = "resource conflict") -> None:
        super().__init__(message, status_code=409, code="conflict")
