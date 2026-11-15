"""Entidad principal de dominio para dataset."""

from datetime import date

from app.modules.dataset.domain.exceptions import InvalidDatasetDataException
from app.shared.domain.validators import (
    require_non_empty_text,
    validate_optional_text,
)


class Dataset:
    """Entidad de dominio que representa un conjunto de datos o fuente científica."""

    def __init__(
        self,
        id: int | None,
        nombre: str,
        agencia: str | None = None,
        url: str | None = None,
        resolucion: float | None = None,
        fecha_descarga: date | None = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.agencia = agencia
        self.url = url
        self.resolucion = resolucion
        self.fecha_descarga = fecha_descarga

    @classmethod
    def create(
        cls,
        *,
        nombre: str,
        agencia: str | None = None,
        url: str | None = None,
        resolucion: float | None = None,
        fecha_descarga: date | None = None,
    ) -> "Dataset":
        """Crea un nuevo dataset validando sus metadatos."""
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 150, InvalidDatasetDataException
        )
        clean_agencia = validate_optional_text(
            agencia, "agencia", 100, InvalidDatasetDataException
        )
        clean_url = validate_optional_text(
            url, "url", None, InvalidDatasetDataException
        )
        return cls(
            id=None,
            nombre=clean_nombre,
            agencia=clean_agencia,
            url=clean_url,
            resolucion=resolucion,
            fecha_descarga=fecha_descarga,
        )
