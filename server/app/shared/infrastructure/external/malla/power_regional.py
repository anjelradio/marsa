"""NASA POWER (MERRA-2): climatología de 25 años de una celda completa.

El endpoint regional devuelve todos los puntos de malla de la celda (unos 357 en 10°x10°), así que
la media y la desviación son de la celda y no de un solo punto. Admite una variable por petición.
https://power.larc.nasa.gov/docs/services/api/
"""

from collections.abc import Callable
from typing import Any

from app.modules.sitio.domain.services.malla import Celda
from app.shared.domain.estadistica import resumir
from app.shared.infrastructure.external.malla.errores import FuenteSinDatos
from app.shared.infrastructure.external.malla.http import http_json
from app.shared.infrastructure.external.malla.lectura import Lectura

URL = "https://power.larc.nasa.gov/api/temporal/climatology/regional"
FILL = -999.0
# parámetro de POWER -> característica
PARAMETROS = {
    "TS": "Temperatura Superficial",
    "CLOUD_AMT": "Nubosidad",
    "AOD_55": "Profundidad Óptica de Polvo",
}
KELVIN = 273.15


def interpretar(respuesta: dict, parametro: str) -> tuple[float, float, int]:
    """Media, desviación y número de puntos válidos (valor anual) de un parámetro."""
    valores = []
    for punto in respuesta.get("features") or []:
        serie = (punto.get("properties") or {}).get("parameter", {}).get(parametro) or {}
        valor = serie.get("ANN")
        if valor is not None and valor != FILL:
            valores.append(valor)
    resumen = resumir(valores)
    if resumen is None:
        raise FuenteSinDatos(f"NASA POWER no tiene datos válidos de {parametro} en la celda.")
    return resumen


class PowerRegional:
    """Temperatura, nubosidad y aerosoles de la celda (tres peticiones por celda)."""

    dataset = "NASA POWER (MERRA-2)"
    variables = tuple(PARAMETROS.values())

    def __init__(self, obtener: Callable[[str, dict[str, Any]], dict] | None = None) -> None:
        self._obtener = obtener or http_json

    def leer(self, celda: Celda) -> dict[str, Lectura]:
        lecturas: dict[str, Lectura] = {}
        for parametro, nombre in PARAMETROS.items():
            respuesta = self._obtener(
                URL,
                {
                    "parameters": parametro,
                    "community": "SB",
                    "latitude-min": celda.lat_min,
                    "latitude-max": celda.lat_max,
                    "longitude-min": celda.lon_min,
                    "longitude-max": celda.lon_max,
                    "format": "JSON",
                },
            )
            media, desviacion, n = interpretar(respuesta, parametro)
            if parametro == "TS":
                media += KELVIN  # POWER da la temperatura de la piel en °C; la desviación no cambia
            lecturas[nombre] = Lectura(media, desviacion, n)
        return lecturas
