"""Data Transfer Objects (DTOs) de analogia."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateAnalogiaCommand:
    sitio_tierra_id: int
    sitio_destino_id: int
    similitud: float | None = None
    cobertura: float | None = None
    metodo: str | None = None
    coincide: str | None = None
    difiere: str | None = None


@dataclass(frozen=True)
class AnalogiaDTO:
    id: int
    sitio_tierra_id: int
    sitio_destino_id: int
    similitud: float | None
    cobertura: float | None
    metodo: str | None
    coincide: str | None
    difiere: str | None
