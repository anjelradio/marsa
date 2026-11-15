"""Ingesta de la malla global de celdas de 10° en la base de datos.

Para cada cuerpo (Tierra, Marte, Luna) lee las fuentes públicas y guarda cada celda con su
temperatura, polvo, nubosidad, elevación y relieve regional, junto con la incertidumbre y el
número de muestras. Un dato inválido nunca se guarda ni se sustituye: se anota en el informe.

Uso (desde server/):

    # ver qué haría, sin red ni escritura
    venv/Scripts/python.exe scripts/ingest_grid.py --dry-run

    # ensayo con pocas celdas
    venv/Scripts/python.exe scripts/ingest_grid.py --cuerpos Tierra --limite 8

    # ingesta completa; --descargar autoriza bajar los dos rasters del PDS (33 MB cada uno)
    venv/Scripts/python.exe scripts/ingest_grid.py --descargar --informe ingesta_informe.json

Sin --descargar, si falta algún raster el script se detiene y dice qué archivos hacen falta.
"""

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlmodel import Session  # noqa: E402

from app.core.database import engine, run_migrations  # noqa: E402
from app.modules.sitio.domain.services.malla import generar_malla  # noqa: E402
from app.shared.application.ingesta_malla import IngestaMalla  # noqa: E402
from app.shared.infrastructure.db.seed import seed_initial_data  # noqa: E402
from app.shared.infrastructure.external.malla.catalogo import (  # noqa: E402
    ARCHIVOS_RASTER,
    archivos_necesarios,
    construir_planes,
)
from app.shared.infrastructure.external.malla.descargas import descargar_si_falta  # noqa: E402
from app.shared.infrastructure.external.malla.errores import FuenteError  # noqa: E402
from app.shared.infrastructure.external.malla.gebco import (  # noqa: E402
    MAX_PUNTOS_POR_PETICION,
    PUNTOS_POR_LADO,
)

CUERPOS = ["Tierra", "Marte", "Luna"]
CACHE = ROOT / "data_cache"


def _faltan(cuerpos: list[str], cache: Path) -> dict:
    return {
        cuerpo: archivo
        for cuerpo, archivo in archivos_necesarios(cuerpos).items()
        if not (cache / archivo.nombre).exists()
        or (cache / archivo.nombre).stat().st_size != archivo.bytes_esperados
    }


def _mb(bytes_: int) -> str:
    return f"{bytes_ / 1_000_000:.1f} MB"


def plan(cuerpos: list[str], limite: int | None, cache: Path) -> str:
    """Texto con lo que hará la ingesta: celdas, peticiones y archivos. No usa la red."""
    lineas = []
    for cuerpo in cuerpos:
        n = len(generar_malla(cuerpo)) if limite is None else min(limite, len(generar_malla(cuerpo)))
        lineas.append(f"{cuerpo}: {n} celdas de 10°")
        if cuerpo == "Tierra":
            por_peticion = MAX_PUNTOS_POR_PETICION // PUNTOS_POR_LADO**2
            lineas.append(
                f"  GEBCO (OpenTopoData): {math.ceil(n / por_peticion)} peticiones, 1 por segundo "
                "(límite público: 1.000 al día); descarta las celdas de océano"
            )
            lineas.append(
                f"  NASA POWER: 3 peticiones por celda de tierra firme (hasta {3 * n} si ninguna "
                "se descartara)"
            )
        elif cuerpo == "Marte":
            lineas.append("  Mars Climate Database: rejilla local, sin red")
        elif cuerpo == "Luna":
            lineas.append(f"  Diviner: {n} lecturas por rango de bytes (unos 11 KB cada una)")
        if cuerpo in ARCHIVOS_RASTER:
            archivo = ARCHIVOS_RASTER[cuerpo]
            estado = "ya descargado" if cuerpo not in _faltan([cuerpo], cache) else "falta"
            lineas.append(
                f"  Raster {archivo.nombre} ({_mb(archivo.bytes_esperados)}, {archivo.dataset}): "
                f"{estado}"
            )
    return "\n".join(lineas)


def _mensaje_faltan(faltan: dict, cache: Path) -> str:
    lineas = [f"Faltan archivos de topografía en {cache}:"]
    for cuerpo, archivo in faltan.items():
        lineas.append(f"  - {archivo.nombre} ({_mb(archivo.bytes_esperados)}, {cuerpo}) <- {archivo.url}")
    lineas.append("Repite con --descargar para bajarlos, o déjalos en esa carpeta.")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingesta de la malla global de celdas de 10°.")
    parser.add_argument("--cuerpos", default=",".join(CUERPOS), help="Tierra,Marte,Luna")
    parser.add_argument("--limite", type=int, default=None, help="solo las N primeras celdas")
    parser.add_argument("--dry-run", action="store_true", help="muestra el plan y termina")
    parser.add_argument("--descargar", action="store_true", help="autoriza bajar los rasters del PDS")
    parser.add_argument("--cache", type=Path, default=CACHE, help="carpeta de los rasters")
    parser.add_argument("--informe", type=Path, default=None, help="guarda el informe en JSON")
    args = parser.parse_args(argv)

    cuerpos = [c.strip() for c in args.cuerpos.split(",") if c.strip()]
    desconocidos = [c for c in cuerpos if c not in CUERPOS]
    if desconocidos:
        print(f"Cuerpos desconocidos: {', '.join(desconocidos)}. Usa {', '.join(CUERPOS)}.")
        return 2

    print(plan(cuerpos, args.limite, args.cache))
    if args.dry_run:
        return 0

    faltan = _faltan(cuerpos, args.cache)
    if faltan and not args.descargar:
        print(_mensaje_faltan(faltan, args.cache))
        return 2
    for archivo in faltan.values():
        print(f"Descargando {archivo.nombre} ({_mb(archivo.bytes_esperados)})...")
        try:
            descargar_si_falta(archivo.url, args.cache / archivo.nombre, archivo.bytes_esperados)
        except FuenteError as exc:
            print(f"No se pudo descargar {archivo.nombre}: {exc}")
            return 1

    run_migrations()
    with Session(engine) as session:
        seed_initial_data(session)  # asegura cuerpos, datasets y características
        informe = IngestaMalla(session, construir_planes(args.cache, cuerpos)).ejecutar(
            cuerpos, args.limite
        )
    print(informe.resumen())
    if args.informe:
        args.informe.write_text(
            json.dumps(informe.como_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Informe guardado en {args.informe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
