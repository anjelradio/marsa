"""Data Transfer Objects (DTOs) de cuerpo_celeste."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCuerpoCelesteCommand:
    nombre: str


@dataclass(frozen=True)
class CuerpoCelesteDTO:
    id: int
    nombre: str
