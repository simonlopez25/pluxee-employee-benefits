from __future__ import annotations


class AppError(Exception):
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
    def __init__(self, message: str = "resource not found") -> None:
        super().__init__(message, status_code=404, code="not_found")


class ConflictError(AppError):
    def __init__(self, message: str = "resource conflict") -> None:
        super().__init__(message, status_code=409, code="conflict")
