"""Temperatura y polvo de Marte por celda, desde la rejilla local de la Mars Climate Database.

La rejilla (3.072 puntos, cada 6° de longitud y unos 3,8° de latitud) está en el repositorio, así
que no usa red. Cada celda promedia los puntos de rejilla que caen dentro de ella.
"""

import math
from typing import Any

from app.modules.cuerpo_celeste.infrastructure.mars_climate import _load_grid
from app.modules.sitio.domain.services.malla import Celda
from app.shared.domain.estadistica import resumir
from app.shared.infrastructure.external.malla.errores import FuenteSinDatos
from app.shared.infrastructure.external.malla.lectura import Lectura


class RejillaMarte:
    """Clima de Marte (época Ls 105°): temperatura superficial y profundidad óptica del polvo."""

    dataset = "LMD Mars Climate Database"
    variables = ("Temperatura Superficial", "Profundidad Óptica de Polvo")

    def __init__(self, puntos: dict[tuple[float, float], Any] | None = None) -> None:
        # puntos: (longitud, latitud) -> valores con surface_temperature_k y dust_optical_depth
        self._puntos = puntos if puntos is not None else _load_grid()[2]

    def _dentro(self, celda: Celda) -> list[Any]:
        valores = [
            v
            for (lon, lat), v in self._puntos.items()
            if celda.lon_min <= lon < celda.lon_max
            and (celda.lat_min <= lat < celda.lat_max or (lat == celda.lat_max == 90))
        ]
        if valores:
            return valores
        # celda sin ningún punto de rejilla: se usa el más cercano a su centro
        if not self._puntos:
            raise FuenteSinDatos("La rejilla de Marte está vacía.")
        cercano = min(
            self._puntos,
            key=lambda p: math.hypot(p[1] - celda.centro_lat, p[0] - celda.centro_lon),
        )
        return [self._puntos[cercano]]

    def leer(self, celda: Celda) -> dict[str, Lectura]:
        valores = self._dentro(celda)
        lecturas: dict[str, Lectura] = {}
        for nombre, atributo in (
            ("Temperatura Superficial", "surface_temperature_k"),
            ("Profundidad Óptica de Polvo", "dust_optical_depth"),
        ):
            media, desviacion, n = resumir(getattr(v, atributo) for v in valores)  # type: ignore[misc]
            lecturas[nombre] = Lectura(media, desviacion if n > 1 else None, n)
        return lecturas
