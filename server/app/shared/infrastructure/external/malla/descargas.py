"""Descarga de los archivos de topografía del PDS, solo cuando se pide expresamente."""

from collections.abc import Callable
from pathlib import Path

import httpx

from app.shared.infrastructure.external.malla.errores import FuenteNoDisponible
from app.shared.infrastructure.external.malla.http import USER_AGENT

BLOQUE = 1024 * 1024


def descargar_si_falta(
    url: str,
    destino: Path,
    bytes_esperados: int,
    *,
    cliente: httpx.Client | None = None,
    progreso: Callable[[int, int], None] | None = None,
) -> Path:
    """Baja ``url`` a ``destino`` si no está ya, comprobando que el tamaño sea el esperado.

    Se escribe en un archivo temporal que solo se renombra si el tamaño coincide, así que nunca
    queda un archivo a medias con el nombre final. Si ya existe con otro tamaño se considera
    corrupto y se vuelve a descargar.
    """
    destino = Path(destino)
    if destino.exists():
        if destino.stat().st_size == bytes_esperados:
            return destino
        destino.unlink()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".part")
    propio = cliente is None
    http = cliente or httpx.Client(
        timeout=httpx.Timeout(60.0, read=300.0),
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )
    try:
        recibido = 0
        with http.stream("GET", url) as respuesta:
            if respuesta.status_code != 200:
                raise FuenteNoDisponible(f"{url}: HTTP {respuesta.status_code}")
            with temporal.open("wb") as salida:
                for bloque in respuesta.iter_bytes(BLOQUE):
                    salida.write(bloque)
                    recibido += len(bloque)
                    if progreso:
                        progreso(recibido, bytes_esperados)
        if recibido != bytes_esperados:
            raise FuenteNoDisponible(
                f"{url}: se esperaban {bytes_esperados} bytes y llegaron {recibido}."
            )
        temporal.replace(destino)
        return destino
    except httpx.HTTPError as exc:
        raise FuenteNoDisponible(f"{url}: {exc}") from exc
    finally:
        temporal.unlink(missing_ok=True)
        if propio:
            http.close()
