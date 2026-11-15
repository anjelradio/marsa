"""Malla global de celdas de 10° sobre un cuerpo celeste.

El código de una celda usa el mismo formato que los archivos de geología:
``{T|M|L}_{N|S}{lat}_{E|W}{lon}``, donde lat y lon son el borde sur y el borde oeste
(``T_S30_W070`` es la celda de latitud −30 a −20 y longitud −70 a −60 de la Tierra).
"""

import math
from collections.abc import Iterator
from dataclasses import dataclass

PREFIJOS = {"Tierra": "T", "Marte": "M", "Luna": "L"}
PASO = 10  # grados


@dataclass(frozen=True)
class Celda:
    """Una celda de la malla: sus cuatro bordes y el prefijo del cuerpo."""

    prefijo: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    @property
    def codigo(self) -> str:
        hemisferio_lat = "N" if self.lat_min >= 0 else "S"
        hemisferio_lon = "E" if self.lon_min >= 0 else "W"
        return (
            f"{self.prefijo}_{hemisferio_lat}{abs(int(self.lat_min)):02d}"
            f"_{hemisferio_lon}{abs(int(self.lon_min)):03d}"
        )

    @property
    def centro_lat(self) -> float:
        return (self.lat_min + self.lat_max) / 2

    @property
    def centro_lon(self) -> float:
        return (self.lon_min + self.lon_max) / 2

    def poligono(self) -> dict:
        """El contorno de la celda como GeoJSON (longitud, latitud)."""
        w, e, s, n = self.lon_min, self.lon_max, self.lat_min, self.lat_max
        return {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}


def _prefijo(cuerpo: str) -> str:
    try:
        return PREFIJOS[cuerpo]
    except KeyError:
        raise ValueError(f"No hay malla definida para el cuerpo '{cuerpo}'.") from None


def generar_malla(cuerpo: str, paso: int = PASO) -> list[Celda]:
    """Todas las celdas del cuerpo, de sur a norte y de oeste a este (648 con paso 10)."""
    if paso <= 0 or 180 % paso or 360 % paso:
        raise ValueError("El paso debe dividir 180 y 360 grados exactamente.")
    prefijo = _prefijo(cuerpo)
    return [
        Celda(prefijo, lat, lat + paso, lon, lon + paso)
        for lat in range(-90, 90, paso)
        for lon in range(-180, 180, paso)
    ]


def celda_de(cuerpo: str, latitud: float, longitud: float, paso: int = PASO) -> Celda:
    """La celda que contiene el punto. Los bordes pertenecen a la celda de su lado norte y este,
    salvo el polo norte y el meridiano 180°, que pertenecen a la última fila y columna."""
    if not -90 <= latitud <= 90 or not -180 <= longitud <= 180:
        raise ValueError("Latitud o longitud fuera de rango.")
    lat = min(math.floor(latitud / paso) * paso, 90 - paso)
    lon = min(math.floor(longitud / paso) * paso, 180 - paso)
    return Celda(_prefijo(cuerpo), lat, lat + paso, lon, lon + paso)


def puntos_muestreo(celda: Celda, por_lado: int) -> Iterator[tuple[float, float]]:
    """Malla regular de ``por_lado`` x ``por_lado`` puntos (latitud, longitud) dentro de la celda,
    centrados en sub-celdas iguales, de modo que ninguno cae justo en un borde."""
    if por_lado < 1:
        raise ValueError("por_lado debe ser al menos 1.")
    alto = (celda.lat_max - celda.lat_min) / por_lado
    ancho = (celda.lon_max - celda.lon_min) / por_lado
    for i in range(por_lado):
        for j in range(por_lado):
            yield (celda.lat_min + (i + 0.5) * alto, celda.lon_min + (j + 0.5) * ancho)
