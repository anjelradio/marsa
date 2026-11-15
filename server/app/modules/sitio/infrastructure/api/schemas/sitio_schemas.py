"""Esquemas Pydantic para la API HTTP de sitio."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateSitioRequest(BaseModel):
    cuerpo_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    tipo: str | None = Field(default=None, max_length=50)
    geom: dict[str, Any] | None = None
    clase: str = Field(default="referencia", pattern="^(referencia|celda)$")
    codigo: str | None = Field(default=None, max_length=60)
    lat_min: float | None = Field(default=None, ge=-90, le=90)
    lat_max: float | None = Field(default=None, ge=-90, le=90)
    lon_min: float | None = Field(default=None, ge=-180, le=180)
    lon_max: float | None = Field(default=None, ge=-180, le=180)


class SitioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cuerpo_id: int
    nombre: str
    tipo: str | None
    geom: dict[str, Any] | None
    clase: str = "referencia"
    codigo: str | None = None
    lat_min: float | None = None
    lat_max: float | None = None
    lon_min: float | None = None
    lon_max: float | None = None
