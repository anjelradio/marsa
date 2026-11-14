"""Esquemas Pydantic para la API HTTP de dataset."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CreateDatasetRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    agencia: str | None = Field(default=None, max_length=100)
    url: str | None = None
    resolucion: float | None = None
    fecha_descarga: date | None = None


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    agencia: str | None
    url: str | None
    resolucion: float | None
    fecha_descarga: date | None
