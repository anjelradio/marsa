"""Esquemas Pydantic para la API HTTP de sitio."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateSitioRequest(BaseModel):
    cuerpo_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    tipo: str | None = Field(default=None, max_length=50)
    geom: dict[str, Any] | None = None


class SitioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cuerpo_id: int
    nombre: str
    tipo: str | None
    geom: dict[str, Any] | None
