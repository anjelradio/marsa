"""Esquemas Pydantic para la API HTTP de medicion."""

from pydantic import BaseModel, ConfigDict, Field


class CreateMedicionRequest(BaseModel):
    sitio_id: int = Field(gt=0)
    caracteristica_id: int = Field(gt=0)
    dataset_id: int = Field(gt=0)
    valor: float
    resolucion: float | None = None
    valor_normalizado: float | None = Field(default=None, ge=0, le=1)


class MedicionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sitio_id: int
    caracteristica_id: int
    dataset_id: int
    valor: float
    resolucion: float | None
    valor_normalizado: float | None
