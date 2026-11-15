"""Contrato común de las fuentes de la malla."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.modules.sitio.domain.services.malla import Celda


@dataclass(frozen=True)
class Lectura:
    """Valor de una variable en una celda, con su incertidumbre y el tamaño de la muestra."""

    valor: float
    incertidumbre: float | None = None
    n_muestras: int | None = None
    periodo_inicio: date | None = None
    periodo_fin: date | None = None


class FuenteCelda(Protocol):
    """Una fuente lee varias variables de una celda a la vez.

    ``dataset`` es el nombre del dataset en la base de datos y ``variables`` los nombres de las
    características que produce. Opcionalmente puede tener ``precargar(celdas)`` para agrupar
    peticiones y ``descartar(celda)``, que devuelve el motivo si la celda no debe ingerirse.
    """

    dataset: str
    variables: tuple[str, ...]

    def leer(self, celda: Celda) -> dict[str, Lectura]: ...
