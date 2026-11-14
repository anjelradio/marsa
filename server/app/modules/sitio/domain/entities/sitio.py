"""Entidad principal de dominio para sitio."""

from typing import Any

from app.modules.sitio.domain.exceptions import InvalidSitioDataException
from app.shared.domain.validators import (
    require_non_empty_text,
    require_positive_id,
    validate_optional_text,
)


class Sitio:
    """Entidad de dominio que representa un sitio de estudio geográfico/planetario."""

    def __init__(
        self,
        id: int | None,
        cuerpo_id: int,
        nombre: str,
        tipo: str | None = None,
        geom: dict[str, Any] | None = None,
    ) -> None:
        self.id = id
        self.cuerpo_id = cuerpo_id
        self.nombre = nombre
        self.tipo = tipo
        self.geom = geom

    @classmethod
    def create(
        cls,
        *,
        cuerpo_id: int,
        nombre: str,
        tipo: str | None = None,
        geom: dict[str, Any] | None = None,
    ) -> "Sitio":
        """Crea un nuevo sitio validando sus atributos e invariantes de relación."""
        valid_cuerpo_id = require_positive_id(
            cuerpo_id, "cuerpo_id", InvalidSitioDataException
        )
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 100, InvalidSitioDataException
        )
        clean_tipo = validate_optional_text(
            tipo, "tipo", 50, InvalidSitioDataException
        )
        return cls(
            id=None,
            cuerpo_id=valid_cuerpo_id,
            nombre=clean_nombre,
            tipo=clean_tipo,
            geom=geom,
        )
