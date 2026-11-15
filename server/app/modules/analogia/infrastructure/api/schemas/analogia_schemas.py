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
    corrida_id: int | None = Field(default=None, gt=0)
    sim_fisica: float | None = Field(default=None, ge=0, le=1)
    sim_terreno: float | None = Field(default=None, ge=0, le=1)
    sim_geologica: float | None = Field(default=None, ge=0, le=1)
    estabilidad: float | None = Field(default=None, ge=0, le=1)


class DetalleCaracteristicaResponse(BaseModel):
    caracteristica: str
    unidad: str | None
    valor_tierra: float
    valor_destino: float
    similitud: float
    grupo: str = "fisico"


class RankingItemResponse(BaseModel):
    posicion: int
    sitio_tierra_id: int
    sitio_tierra: str
    tipo: str | None
    geom: dict | None
    sitio_destino_id: int
    sitio_destino: str
    geom_destino: dict | None
    similitud: float
    por_grupo: dict[str, float] = {}
    cobertura: float
    metodo: str
    coincide: str
    difiere: str
    detalle: list[DetalleCaracteristicaResponse]


class AnalogiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    corrida_id: int
    sitio_tierra_id: int
    sitio_destino_id: int
    similitud: float | None
    sim_fisica: float | None = None
    sim_terreno: float | None = None
    sim_geologica: float | None = None
    cobertura: float | None
    estabilidad: float | None = None
    metodo: str | None
    coincide: str | None
    difiere: str | None
