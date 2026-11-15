"""Esquemas Pydantic para la API HTTP de analogia."""

from pydantic import BaseModel, ConfigDict, Field


class CreateAnalogiaRequest(BaseModel):
    sitio_tierra_id: int = Field(gt=0)
    sitio_destino_id: int = Field(gt=0)
    similitud: float | None = Field(default=None, ge=0, le=1)
    cobertura: float | None = Field(default=None, ge=0, le=1)
    metodo: str | None = None
    coincide: str | None = None
    difiere: str | None = None


class AnalogiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sitio_tierra_id: int
    sitio_destino_id: int
    similitud: float | None
    cobertura: float | None
    metodo: str | None
    coincide: str | None
    difiere: str | None
