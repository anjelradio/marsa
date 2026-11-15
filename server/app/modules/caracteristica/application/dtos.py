"""Data Transfer Objects (DTOs) de caracteristica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCaracteristicaCommand:
    nombre: str
    rango: float
    peso: float
    unidad: str | None = None


@dataclass(frozen=True)
class CaracteristicaDTO:
    id: int
    nombre: str
    unidad: str | None
    rango: float
    peso: float
