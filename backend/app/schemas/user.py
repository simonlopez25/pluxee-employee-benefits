from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def _validate(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("La nueva contraseña y su confirmación no coinciden")
        if self.new_password == self.current_password:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        return self
