"""Qué fuentes usa la ingesta en cada cuerpo y qué archivos necesita."""

from dataclasses import dataclass
from pathlib import Path

from app.shared.infrastructure.external.malla.diviner import DivinerCentral
from app.shared.infrastructure.external.malla.gebco import GebcoOpenTopoData
from app.shared.infrastructure.external.malla.lectura import FuenteCelda
from app.shared.infrastructure.external.malla.power_regional import PowerRegional
from app.shared.infrastructure.external.malla.raster16 import Raster16, RasterElevacion
from app.shared.infrastructure.external.malla.rejilla_marte import RejillaMarte


@dataclass(frozen=True)
class ArchivoRaster:
    """Un raster de topografía del PDS que hay que tener en disco."""

    nombre: str
    url: str
    bytes_esperados: int
    big_endian: bool
    escala: float
    dataset: str


ARCHIVOS_RASTER: dict[str, ArchivoRaster] = {
    "Luna": ArchivoRaster(
        nombre="ldem_16.img",
        url=(
            "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/"
            "data/lola_gdr/cylindrical/img/ldem_16.img"
        ),
        bytes_esperados=33_177_600,
        big_endian=False,  # LSB; altura = valor x 0,5 m sobre la esfera de 1737,4 km
        escala=0.5,
        dataset="NASA LRO LOLA / Diviner",
    ),
    "Marte": ArchivoRaster(
        nombre="megt90n000eb.img",
        url=(
            "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/"
            "mgsl_300x/meg016/megt90n000eb.img"
        ),
        bytes_esperados=33_177_600,
        big_endian=True,  # MSB; el valor ya es la altura en metros
        escala=1.0,
        dataset="NASA MGS MOLA",
    ),
}


def archivos_necesarios(cuerpos: list[str]) -> dict[str, ArchivoRaster]:
    """Los rasters que requieren los cuerpos pedidos (la Tierra no necesita ninguno)."""
    return {c: ARCHIVOS_RASTER[c] for c in cuerpos if c in ARCHIVOS_RASTER}


def construir_planes(cache: Path, cuerpos: list[str]) -> dict[str, list[FuenteCelda]]:
    """Las fuentes reales de cada cuerpo. ``cache`` es la carpeta de los rasters descargados."""
    planes: dict[str, list[FuenteCelda]] = {}
    for cuerpo in cuerpos:
        if cuerpo == "Tierra":
            planes[cuerpo] = [GebcoOpenTopoData(), PowerRegional()]
            continue
        archivo = ARCHIVOS_RASTER[cuerpo]
        raster = RasterElevacion(
            Raster16(
                cache / archivo.nombre,
                big_endian=archivo.big_endian,
                escala=archivo.escala,
            ),
            archivo.dataset,
        )
        planes[cuerpo] = (
            [RejillaMarte(), raster] if cuerpo == "Marte" else [raster, DivinerCentral()]
        )
    return planes
