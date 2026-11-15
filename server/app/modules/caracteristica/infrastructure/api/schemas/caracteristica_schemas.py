"""Esquemas Pydantic para la API HTTP de caracteristica."""

from pydantic import BaseModel, ConfigDict, Field


class CreateCaracteristicaRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    unidad: str | None = Field(default=None, max_length=20)
    rango: float = Field(gt=0)
    peso: float = Field(ge=0, le=1)
    grupo: str = Field(default="fisico", pattern="^(fisico|terreno)$")
    valor_min: float | None = None
    valor_max: float | None = None


class CaracteristicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    unidad: str | None
    rango: float
    peso: float
    grupo: str = "fisico"
    valor_min: float | None = None
    valor_max: float | None = None
