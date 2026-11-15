"""Entidad de dominio: una corrida del cálculo de analogías, con su versión y parámetros."""

from datetime import datetime
from typing import Any

from app.modules.corrida_analisis.domain.exceptions import (
    InvalidCorridaAnalisisDataException,
)
from app.shared.domain.validators import require_non_empty_text


class CorridaAnalisis:
    """Ejecución del análisis: permite guardar el historial y comparar versiones."""

    def __init__(
        self,
        id: int | None,
        version: str,
        metodo: str,
        fecha: datetime | None = None,
        parametros: dict[str, Any] | None = None,
    ) -> None:
        self.id = id
        self.version = version
        self.metodo = metodo
        self.fecha = fecha
        self.parametros = parametros

    @classmethod
    def create(
        cls,
        *,
        version: str,
        metodo: str,
        fecha: datetime | None = None,
        parametros: dict[str, Any] | None = None,
    ) -> "CorridaAnalisis":
        """Crea una corrida validando que versión y método no estén vacíos."""
        exc = InvalidCorridaAnalisisDataException
        return cls(
            id=None,
            version=require_non_empty_text(version, "version", 30, exc),
            metodo=require_non_empty_text(metodo, "metodo", 60, exc),
            fecha=fecha,
            parametros=parametros,
        )
