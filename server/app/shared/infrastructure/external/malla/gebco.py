"""Elevación y relieve de la Tierra con GEBCO 2020 a través de OpenTopoData.

SRTM no cubre los polos ni el océano; GEBCO 2020 es global (incluye la superficie del hielo antártico
y la batimetría). Cada celda se muestrea con una malla de 5x5 puntos y, para gastar pocas
peticiones, se agrupan hasta 4 celdas (100 puntos) en cada una. El servicio público admite
1 petición por segundo y 1.000 al día.
"""

import time
from collections.abc import Callable
from typing import Any

from app.modules.sitio.domain.services.malla import Celda, puntos_muestreo
from app.shared.domain.estadistica import resumir
from app.shared.infrastructure.external.malla.errores import FuenteSinDatos
from app.shared.infrastructure.external.malla.http import http_json
from app.shared.infrastructure.external.malla.lectura import Lectura

URL = "https://api.opentopodata.org/v1/gebco2020"
PUNTOS_POR_LADO = 5
MAX_PUNTOS_POR_PETICION = 100
PAUSA_S = 1.1
MINIMO_PUNTOS = 13  # más de la mitad de los 25 puntos deben tener dato
FRACCION_TIERRA_MINIMA = 0.5


class GebcoOpenTopoData:
    """Elevación media, relieve regional (desviación) y filtro de tierra firme."""

    dataset = "GEBCO 2020 (OpenTopoData)"
    variables = ("Elevación", "Relieve Regional")

    def __init__(
        self,
        obtener: Callable[[str, dict[str, Any]], dict] | None = None,
        dormir: Callable[[float], None] = time.sleep,
    ) -> None:
        self._obtener = obtener or http_json
        self._dormir = dormir
        self._cache: dict[str, list[float | None]] = {}

    def _puntos(self, celda: Celda) -> list[tuple[float, float]]:
        return list(puntos_muestreo(celda, PUNTOS_POR_LADO))

    def _pedir(self, celdas: list[Celda]) -> None:
        puntos = [p for c in celdas for p in self._puntos(c)]
        localizaciones = "|".join(f"{lat},{lon}" for lat, lon in puntos)
        respuesta = self._obtener(URL, {"locations": localizaciones})
        resultados = respuesta.get("results") or []
        if len(resultados) != len(puntos):
            raise FuenteSinDatos(
                f"OpenTopoData devolvió {len(resultados)} puntos y se pidieron {len(puntos)}."
            )
        elevaciones = [r.get("elevation") for r in resultados]
        por_celda = PUNTOS_POR_LADO**2
        for i, celda in enumerate(celdas):
            self._cache[celda.codigo] = elevaciones[i * por_celda : (i + 1) * por_celda]

    def precargar(self, celdas: list[Celda]) -> None:
        """Pide las elevaciones de todas las celdas, agrupadas en peticiones de hasta 100 puntos."""
        por_peticion = MAX_PUNTOS_POR_PETICION // PUNTOS_POR_LADO**2
        pendientes = [c for c in celdas if c.codigo not in self._cache]
        for i in range(0, len(pendientes), por_peticion):
            if i:
                self._dormir(PAUSA_S)
            self._pedir(pendientes[i : i + por_peticion])

    def _elevaciones(self, celda: Celda) -> list[float]:
        if celda.codigo not in self._cache:
            self._pedir([celda])
        validas = [e for e in self._cache[celda.codigo] if e is not None]
        if len(validas) < MINIMO_PUNTOS:
            raise FuenteSinDatos(f"GEBCO solo tiene {len(validas)} puntos válidos en {celda.codigo}.")
        return validas

    def descartar(self, celda: Celda) -> str | None:
        """Motivo para no ingerir la celda: es sobre todo océano."""
        elevaciones = self._elevaciones(celda)
        tierra = sum(1 for e in elevaciones if e >= 0) / len(elevaciones)
        return "océano" if tierra < FRACCION_TIERRA_MINIMA else None

    def leer(self, celda: Celda) -> dict[str, Lectura]:
        media, desviacion, n = resumir(self._elevaciones(celda))  # type: ignore[misc]
        return {
            "Elevación": Lectura(media, desviacion, n),
            "Relieve Regional": Lectura(desviacion, None, n),
        }
