"""Entidad principal de dominio para caracteristica."""

from app.modules.caracteristica.domain.exceptions import (
    InvalidCaracteristicaDataException,
)
from app.shared.domain.validators import (
    require_non_empty_text,
    require_positive_float,
    require_unit_interval,
    validate_optional_text,
)


class Caracteristica:
    """Entidad de dominio para una variable física/química con rango y peso."""

    def __init__(
        self,
        id: int | None,
        nombre: str,
        rango: float,
        peso: float,
        unidad: str | None = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.unidad = unidad
        self.rango = rango
        self.peso = peso

    @classmethod
    def create(
        cls,
        *,
        nombre: str,
        rango: float,
        peso: float,
        unidad: str | None = None,
    ) -> "Caracteristica":
        """Crea una característica validando rango > 0 y peso en [0, 1]."""
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 100, InvalidCaracteristicaDataException
        )
        clean_unidad = validate_optional_text(
            unidad, "unidad", 20, InvalidCaracteristicaDataException
        )
        valid_rango = require_positive_float(
            rango, "rango", InvalidCaracteristicaDataException
        )
        valid_peso = require_unit_interval(
            peso, "peso", InvalidCaracteristicaDataException
        )
        return cls(
            id=None,
            nombre=clean_nombre,
            unidad=clean_unidad,
            rango=valid_rango,
            peso=valid_peso,
        )
