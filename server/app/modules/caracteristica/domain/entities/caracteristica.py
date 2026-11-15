"""Entidad principal de dominio para caracteristica."""

from app.modules.caracteristica.domain.exceptions import (
    InvalidCaracteristicaDataException,
)
from app.shared.domain.validators import (
    require_in_range,
    require_non_empty_text,
    require_one_of,
    require_positive_float,
    require_unit_interval,
    validate_optional_text,
)

GRUPOS_CARACTERISTICA = ("fisico", "terreno")


class Caracteristica:
    """Entidad de dominio para una variable física con rango, peso y grupo.

    ``peso`` es el peso dentro de su grupo. ``valor_min`` y ``valor_max`` delimitan los
    valores físicamente posibles y sirven para validar las mediciones.
    """

    def __init__(
        self,
        id: int | None,
        nombre: str,
        rango: float,
        peso: float,
        unidad: str | None = None,
        grupo: str = "fisico",
        valor_min: float | None = None,
        valor_max: float | None = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.unidad = unidad
        self.rango = rango
        self.peso = peso
        self.grupo = grupo
        self.valor_min = valor_min
        self.valor_max = valor_max

    @classmethod
    def create(
        cls,
        *,
        nombre: str,
        rango: float,
        peso: float,
        unidad: str | None = None,
        grupo: str = "fisico",
        valor_min: float | None = None,
        valor_max: float | None = None,
    ) -> "Caracteristica":
        """Crea una característica validando rango > 0, peso en [0, 1], grupo y rango físico."""
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
        valid_grupo = require_one_of(
            grupo, "grupo", GRUPOS_CARACTERISTICA, InvalidCaracteristicaDataException
        )
        valid_min = (
            require_in_range(
                valor_min, "valor_min", -1e12, 1e12, InvalidCaracteristicaDataException
            )
            if valor_min is not None
            else None
        )
        valid_max = (
            require_in_range(
                valor_max, "valor_max", -1e12, 1e12, InvalidCaracteristicaDataException
            )
            if valor_max is not None
            else None
        )
        if valid_min is not None and valid_max is not None and valid_min >= valid_max:
            raise InvalidCaracteristicaDataException(
                "'valor_min' debe ser menor que 'valor_max'."
            )
        return cls(
            id=None,
            nombre=clean_nombre,
            unidad=clean_unidad,
            rango=valid_rango,
            peso=valid_peso,
            grupo=valid_grupo,
            valor_min=valid_min,
            valor_max=valid_max,
        )
