"""Entidad principal de dominio para cuerpo_celeste."""

from app.modules.cuerpo_celeste.domain.exceptions import (
    InvalidCuerpoCelesteDataException,
)
from app.shared.domain.validators import require_non_empty_text


class CuerpoCeleste:
    """Entidad de dominio que representa un cuerpo celeste (Tierra, Luna, Marte)."""

    def __init__(self, id: int | None, nombre: str) -> None:
        self.id = id
        self.nombre = nombre

    @classmethod
    def create(cls, *, nombre: str) -> "CuerpoCeleste":
        """Crea un nuevo cuerpo celeste validando sus invariantes de negocio."""
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 50, InvalidCuerpoCelesteDataException
        )
        return cls(id=None, nombre=clean_nombre)
