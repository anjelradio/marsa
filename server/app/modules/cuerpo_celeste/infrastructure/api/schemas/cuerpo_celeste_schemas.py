"""Esquemas Pydantic para la API HTTP de cuerpo_celeste."""

from pydantic import BaseModel, ConfigDict, Field


class CreateCuerpoCelesteRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)


class CuerpoCelesteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
