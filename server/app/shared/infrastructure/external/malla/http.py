"""Cliente HTTP con reintentos para las APIs públicas de la malla."""

import time
from collections.abc import Callable
from typing import Any

import httpx

from app.shared.infrastructure.external.malla.errores import FuenteNoDisponible

USER_AGENT = "naseando-ingesta/1.0"
REINTENTOS = 3
PAUSA_REINTENTO_S = 2.0


def http_json(
    url: str,
    params: dict[str, Any],
    *,
    cliente: httpx.Client | None = None,
    dormir: Callable[[float], None] = time.sleep,
    timeout: float = 60.0,
) -> dict:
    """GET que devuelve el JSON. Reintenta los fallos de red, el error 429 y los 5xx.

    Un error 4xx (salvo 429) no se reintenta. Si al final no hay respuesta, lanza
    ``FuenteNoDisponible``.
    """
    propio = cliente is None
    http = cliente or httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT})
    ultimo: str = "sin respuesta"
    try:
        for intento in range(1, REINTENTOS + 1):
            try:
                respuesta = http.get(url, params=params)
            except httpx.HTTPError as exc:
                ultimo = f"fallo de red: {exc}"
            else:
                if respuesta.status_code == 200:
                    try:
                        return respuesta.json()
                    except ValueError as exc:
                        raise FuenteNoDisponible(f"{url} devolvió algo que no es JSON") from exc
                ultimo = f"HTTP {respuesta.status_code}"
                if respuesta.status_code != 429 and respuesta.status_code < 500:
                    raise FuenteNoDisponible(f"{url}: {ultimo}")
            if intento < REINTENTOS:
                dormir(PAUSA_REINTENTO_S * intento)
        raise FuenteNoDisponible(f"{url}: {ultimo} tras {REINTENTOS} intentos")
    finally:
        if propio:
            http.close()
