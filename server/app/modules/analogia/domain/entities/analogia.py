"""Entidad principal de dominio para analogia."""

from app.modules.analogia.domain.exceptions import InvalidAnalogiaDataException
from app.shared.domain.validators import (
    require_positive_id,
    require_unit_interval,
    validate_optional_text,
)


def _unit_or_none(value: float | None, name: str) -> float | None:
    """Valida un valor opcional en [0, 1]."""
    if value is None:
        return None
    return require_unit_interval(value, name, InvalidAnalogiaDataException)


class Analogia:
    """Entidad de dominio que relaciona un sitio terrestre con un sitio destino.

    ``similitud`` es la puntuación única; ``sim_fisica``, ``sim_terreno`` y
    ``sim_geologica`` son las puntuaciones de cada grupo (vacías si el grupo no tenía datos).
    """

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
        corrida_id: int | None = None,
        sim_fisica: float | None = None,
        sim_terreno: float | None = None,
        sim_geologica: float | None = None,
        estabilidad: float | None = None,
    ) -> None:
        self.id = id
        self.sitio_tierra_id = sitio_tierra_id
        self.sitio_destino_id = sitio_destino_id
        self.similitud = similitud
        self.cobertura = cobertura
        self.metodo = metodo
        self.coincide = coincide
        self.difiere = difiere
        self.corrida_id = corrida_id
        self.sim_fisica = sim_fisica
        self.sim_terreno = sim_terreno
        self.sim_geologica = sim_geologica
        self.estabilidad = estabilidad

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
        corrida_id: int | None = None,
        sim_fisica: float | None = None,
        sim_terreno: float | None = None,
        sim_geologica: float | None = None,
        estabilidad: float | None = None,
    ) -> "Analogia":
        """Crea una analogía validando IDs y que toda puntuación esté en [0, 1]."""
        valid_tierra_id = require_positive_id(
            sitio_tierra_id, "sitio_tierra_id", InvalidAnalogiaDataException
        )
        valid_destino_id = require_positive_id(
            sitio_destino_id, "sitio_destino_id", InvalidAnalogiaDataException
        )
        valid_corrida_id = (
            require_positive_id(corrida_id, "corrida_id", InvalidAnalogiaDataException)
            if corrida_id is not None
            else None
        )
        return cls(
            id=None,
            sitio_tierra_id=valid_tierra_id,
            sitio_destino_id=valid_destino_id,
            similitud=_unit_or_none(similitud, "similitud"),
            cobertura=_unit_or_none(cobertura, "cobertura"),
            metodo=validate_optional_text(
                metodo, "metodo", None, InvalidAnalogiaDataException
            ),
            coincide=validate_optional_text(
                coincide, "coincide", None, InvalidAnalogiaDataException
            ),
            difiere=validate_optional_text(
                difiere, "difiere", None, InvalidAnalogiaDataException
            ),
            corrida_id=valid_corrida_id,
            sim_fisica=_unit_or_none(sim_fisica, "sim_fisica"),
            sim_terreno=_unit_or_none(sim_terreno, "sim_terreno"),
            sim_geologica=_unit_or_none(sim_geologica, "sim_geologica"),
            estabilidad=_unit_or_none(estabilidad, "estabilidad"),
        )
