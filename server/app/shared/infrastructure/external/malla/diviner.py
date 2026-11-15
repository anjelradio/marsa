"""Temperatura de la Luna por celda con LRO Diviner.

Los ficheros de Diviner pesan 2,8 GB, así que no se descargan: se leen por rango de bytes los
96 registros del bin de 0,5° del centro de cada celda. El valor es el de ese bin (n_muestras = 1) y
no la media de toda la celda; por eso no lleva incertidumbre.
"""

from collections.abc import Callable
from datetime import date

from app.modules.cuerpo_celeste.infrastructure.moon_lro import get_moon_temperature
from app.modules.sitio.domain.services.malla import Celda
from app.shared.infrastructure.external.malla.errores import FuenteNoDisponible, FuenteSinDatos
from app.shared.infrastructure.external.malla.lectura import Lectura

# Periodo de observación de los productos globales acumulados de Diviner (GCP).
PERIODO_INICIO = date(2009, 7, 5)
PERIODO_FIN = date(2015, 4, 1)


class DivinerCentral:
    """Temperatura media diurna del bin central de cada celda."""

    dataset = "NASA LRO LOLA / Diviner"
    variables = ("Temperatura Superficial",)

    def __init__(
        self,
        obtener: Callable[[float, float], dict[str, float]] = get_moon_temperature,
    ) -> None:
        self._obtener = obtener

    def leer(self, celda: Celda) -> dict[str, Lectura]:
        try:
            resumen = self._obtener(celda.centro_lat, celda.centro_lon)
        except ValueError as exc:  # sin observaciones suficientes en ese bin
            raise FuenteSinDatos(f"Diviner sin datos en {celda.codigo}: {exc}") from exc
        except (OSError, RuntimeError) as exc:  # red caída, servidor sin soporte de rangos...
            raise FuenteNoDisponible(f"Diviner no respondió en {celda.codigo}: {exc}") from exc
        return {
            "Temperatura Superficial": Lectura(
                resumen["mean_k"], None, 1, PERIODO_INICIO, PERIODO_FIN
            )
        }
