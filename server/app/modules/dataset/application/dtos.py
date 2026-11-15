"""Data Transfer Objects (DTOs) de dataset."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateDatasetCommand:
    nombre: str
    agencia: str | None = None
    url: str | None = None
    resolucion: float | None = None
    fecha_descarga: date | None = None


@dataclass(frozen=True)
class DatasetDTO:
    id: int
    nombre: str
    agencia: str | None
    url: str | None
    resolucion: float | None
    fecha_descarga: date | None
