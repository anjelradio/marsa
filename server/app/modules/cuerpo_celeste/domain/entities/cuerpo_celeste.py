"""Entidad principal de dominio para cuerpo_celeste."""

from app.modules.cuerpo_celeste.domain.exceptions import (
    InvalidCuerpoCelesteDataException,
)
from app.shared.domain.validators import require_non_empty_text, require_positive_float


class CuerpoCeleste:
    """Entidad de dominio que representa un cuerpo celeste (Tierra, Luna, Marte)."""

    def __init__(self, id: int | None, nombre: str, radio_km: float | None = None) -> None:
        self.id = id
        self.nombre = nombre
        self.radio_km = radio_km

    @classmethod
    def create(cls, *, nombre: str, radio_km: float | None = None) -> "CuerpoCeleste":
        """Crea un nuevo cuerpo celeste validando sus invariantes de negocio."""
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 50, InvalidCuerpoCelesteDataException
        )
        valid_radio = (
            require_positive_float(radio_km, "radio_km", InvalidCuerpoCelesteDataException)
            if radio_km is not None
            else None
        )
        return cls(id=None, nombre=clean_nombre, radio_km=valid_radio)
