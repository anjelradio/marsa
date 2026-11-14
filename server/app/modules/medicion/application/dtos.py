"""Data Transfer Objects (DTOs) de medicion."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateMedicionCommand:
    sitio_id: int
    caracteristica_id: int
    dataset_id: int
    valor: float
    resolucion: float | None = None
    valor_normalizado: float | None = None


@dataclass(frozen=True)
class MedicionDTO:
    id: int
    sitio_id: int
    caracteristica_id: int
    dataset_id: int
    valor: float
    resolucion: float | None
    valor_normalizado: float | None
