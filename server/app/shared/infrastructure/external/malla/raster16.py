"""Rasters globales de topografía (LOLA en la Luna, MOLA en Marte) leídos con la biblioteca estándar.

Son archivos de enteros de 16 bits, sin cabecera, con 16 píxeles por grado: 5.760 columnas
(longitud 0° a 360° este) por 2.880 filas (latitud 90° a −90°). La media y la desviación de una
celda salen de todos sus píxeles (unos 25.600).
"""

import sys
from array import array
from pathlib import Path

from app.modules.sitio.domain.services.malla import Celda
from app.shared.infrastructure.external.malla.errores import FuenteNoDisponible, FuenteSinDatos
from app.shared.infrastructure.external.malla.lectura import Lectura


class Raster16:
    """Raster equirrectangular de int16 con ``ppd`` píxeles por grado."""

    def __init__(
        self,
        ruta: Path,
        *,
        ppd: int = 16,
        big_endian: bool = False,
        escala: float = 1.0,
        desplazamiento: float = 0.0,
    ) -> None:
        self.ruta = Path(ruta)
        self.ppd = ppd
        self.big_endian = big_endian
        self.escala = escala
        self.desplazamiento = desplazamiento
        self._datos: array | None = None

    @property
    def columnas(self) -> int:
        return 360 * self.ppd

    @property
    def filas(self) -> int:
        return 180 * self.ppd

    def _cargar(self) -> array:
        if self._datos is None:
            if not self.ruta.exists():
                raise FuenteNoDisponible(f"Falta el archivo {self.ruta}.")
            datos = array("h")
            esperado = self.filas * self.columnas
            with self.ruta.open("rb") as archivo:
                try:
                    datos.fromfile(archivo, esperado)
                except EOFError:  # archivo más corto: fromfile deja lo que alcanzó a leer
                    raise FuenteNoDisponible(
                        f"{self.ruta} tiene {len(datos)} valores y se esperaban {esperado}."
                    ) from None
                if archivo.read(1):
                    raise FuenteNoDisponible(f"{self.ruta} es más grande de lo esperado.")
            if len(datos) != esperado:
                raise FuenteNoDisponible(
                    f"{self.ruta} tiene {len(datos)} valores y se esperaban {esperado}."
                )
            if self.big_endian != (sys.byteorder == "big"):
                datos.byteswap()
            self._datos = datos
        return self._datos

    def estadisticas(self, celda: Celda) -> tuple[float, float, int]:
        """Media, desviación y número de píxeles de la celda, ya con la escala aplicada."""
        datos = self._cargar()
        fila0 = int(round((90 - celda.lat_max) * self.ppd))
        fila1 = int(round((90 - celda.lat_min) * self.ppd))
        col0 = int(round((celda.lon_min % 360) * self.ppd))
        col1 = col0 + int(round((celda.lon_max - celda.lon_min) * self.ppd))
        suma = 0
        suma_cuadrados = 0
        n = 0
        for fila in range(fila0, fila1):
            tramo = datos[fila * self.columnas + col0 : fila * self.columnas + col1]
            suma += sum(tramo)
            suma_cuadrados += sum(v * v for v in tramo)
            n += len(tramo)
        if n == 0:
            raise FuenteSinDatos(f"El raster no cubre la celda {celda.codigo}.")
        media = suma / n
        varianza = max(0.0, suma_cuadrados / n - media * media)
        return (
            media * self.escala + self.desplazamiento,
            (varianza**0.5) * self.escala,
            n,
        )


class RasterElevacion:
    """Elevación media y relieve regional de una celda a partir de un raster de topografía."""

    variables = ("Elevación", "Relieve Regional")

    def __init__(self, raster: Raster16, dataset: str) -> None:
        self.raster = raster
        self.dataset = dataset

    def leer(self, celda: Celda) -> dict[str, Lectura]:
        media, desviacion, n = self.raster.estadisticas(celda)
        return {
            "Elevación": Lectura(media, desviacion, n),
            "Relieve Regional": Lectura(desviacion, None, n),
        }
