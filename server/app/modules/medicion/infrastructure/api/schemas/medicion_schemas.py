"""Esquemas Pydantic para la API HTTP de medicion."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CreateMedicionRequest(BaseModel):
    sitio_id: int = Field(gt=0)
    caracteristica_id: int = Field(gt=0)
    dataset_id: int = Field(gt=0)
    valor: float
    resolucion: float | None = None
    valor_normalizado: float | None = Field(default=None, ge=0, le=1)
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    incertidumbre: float | None = Field(default=None, ge=0)
    n_muestras: int | None = Field(default=None, ge=1)


class MedicionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sitio_id: int
    caracteristica_id: int
    dataset_id: int
    valor: float
    resolucion: float | None
    valor_normalizado: float | None
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    incertidumbre: float | None = None
    n_muestras: int | None = None


class ExtraerSatelitalRequest(BaseModel):
    sitio_id: int = Field(gt=0, description="ID del sitio a procesar")
    datetime_range: str | None = Field(
        default=None,
        description="Rango de fecha ISO 8601 (ej. '2024-01-01T00:00:00Z/2024-01-31T23:59:59Z')",
    )
