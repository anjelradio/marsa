"""Climatología global de Marte a Ls 105°, extraída de MCD v6.2.

Fuente: Mars Climate Database (LMD/OU/IAA/ESA/CNES), escenario climatológico
con actividad solar media y promedio de todas las horas locales.
https://www-mars.lmd.jussieu.fr/mars/info_web/index.html#quotes
"""

from csv import DictReader
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class MarsClimateValues(BaseModel):
    surface_temperature_k: float
    surface_pressure_pa: float
    cloud_ice_kg_m2: float
    dust_optical_depth: float
    wind_10m_m_s: float


class MarsClimateResponse(BaseModel):
    coordinates: Coordinates
    grid_point: Coordinates
    solar_longitude_deg: int = 105
    source: str = "Mars Climate Database v6.2"
    values: MarsClimateValues


@lru_cache(maxsize=1)
def _load_grid() -> tuple[tuple[float, ...], tuple[float, ...], dict[tuple[float, float], MarsClimateValues]]:
    points = {}
    path = Path(__file__).with_name("mars_climate_ls105.csv")
    with path.open(encoding="utf-8", newline="") as file:
        for row in DictReader(file):
            longitude = float(row.pop("longitude"))
            latitude = float(row.pop("latitude"))
            # +180° duplicates the -180° meridian in the exported grid.
            if longitude != 180:
                points[longitude, latitude] = MarsClimateValues.model_validate(row)

    longitudes = tuple(sorted({longitude for longitude, _ in points}))
    latitudes = tuple(sorted({latitude for _, latitude in points}))
    return longitudes, latitudes, points


def get_mars_climate(latitude: float, longitude: float) -> MarsClimateResponse:
    longitudes, latitudes, points = _load_grid()
    grid_lat = min(latitudes, key=lambda lat: abs(lat - latitude))
    grid_lon = min(longitudes, key=lambda lon: abs((lon - longitude + 180) % 360 - 180))
    return MarsClimateResponse(
        coordinates=Coordinates(latitude=latitude, longitude=longitude),
        grid_point=Coordinates(latitude=grid_lat, longitude=grid_lon),
        values=points[grid_lon, grid_lat],
    )
