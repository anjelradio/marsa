"""Data Transfer Objects (DTOs) de sitio."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CreateSitioCommand:
    cuerpo_id: int
    nombre: str
    tipo: str | None = None
    geom: dict[str, Any] | None = None


@dataclass(frozen=True)
class SitioDTO:
    id: int
    cuerpo_id: int
    nombre: str
    tipo: str | None
    geom: dict[str, Any] | None
