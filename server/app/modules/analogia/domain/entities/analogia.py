"""Entidad principal de dominio para analogia."""

from app.modules.analogia.domain.exceptions import InvalidAnalogiaDataException
from app.shared.domain.validators import (
    require_positive_id,
    require_unit_interval,
    validate_optional_text,
)


class Analogia:
    """Entidad de dominio que relaciona un sitio terrestre con un sitio destino."""

    def __init__(
        self,
        id: int | None,
        sitio_tierra_id: int,
        sitio_destino_id: int,
        similitud: float | None = None,
        cobertura: float | None = None,
        metodo: str | None = None,
        coincide: str | None = None,
        difiere: str | None = None,
    ) -> None:
        self.id = id
        self.sitio_tierra_id = sitio_tierra_id
        self.sitio_destino_id = sitio_destino_id
        self.similitud = similitud
        self.cobertura = cobertura
        self.metodo = metodo
        self.coincide = coincide
        self.difiere = difiere

    @classmethod
    def create(
        cls,
        *,
        sitio_tierra_id: int,
        sitio_destino_id: int,
        similitud: float | None = None,
        cobertura: float | None = None,
        metodo: str | None = None,
        coincide: str | None = None,
        difiere: str | None = None,
    ) -> "Analogia":
        """Crea una analogía validando IDs y rangos en [0, 1] para similitud y cobertura."""
        valid_tierra_id = require_positive_id(
            sitio_tierra_id, "sitio_tierra_id", InvalidAnalogiaDataException
        )
        valid_destino_id = require_positive_id(
            sitio_destino_id, "sitio_destino_id", InvalidAnalogiaDataException
        )
        valid_similitud = (
            require_unit_interval(
                similitud, "similitud", InvalidAnalogiaDataException
            )
            if similitud is not None
            else None
        )
        valid_cobertura = (
            require_unit_interval(
                cobertura, "cobertura", InvalidAnalogiaDataException
            )
            if cobertura is not None
            else None
        )
        return cls(
            id=None,
            sitio_tierra_id=valid_tierra_id,
            sitio_destino_id=valid_destino_id,
            similitud=valid_similitud,
            cobertura=valid_cobertura,
            metodo=validate_optional_text(
                metodo, "metodo", None, InvalidAnalogiaDataException
            ),
            coincide=validate_optional_text(
                coincide, "coincide", None, InvalidAnalogiaDataException
            ),
            difiere=validate_optional_text(
                difiere, "difiere", None, InvalidAnalogiaDataException
            ),
        )
