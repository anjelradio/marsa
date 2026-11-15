"""Climatología de la Tierra por coordenadas, desde NASA POWER (MERRA-2).

Se consulta la climatología de 25 años (media anual) del punto pedido:
temperatura de la piel (TS), presión (PS), viento a 10 m (WS10M), nubosidad
(CLOUD_AMT) y profundidad óptica de aerosoles (AOD_55).
https://power.larc.nasa.gov/docs/services/api/
"""

import logging
from typing import Any

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

from app.modules.cuerpo_celeste.infrastructure.mars_climate import Coordinates

logger = logging.getLogger(__name__)

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
PARAMETERS = "TS,PS,WS10M,CLOUD_AMT,AOD_55"
FILL_VALUE = -999.0


class EarthClimateValues(BaseModel):
    surface_temperature_k: float
    surface_pressure_pa: float
    cloud_cover_pct: float
    aerosol_optical_depth: float
    wind_10m_m_s: float


class EarthClimateResponse(BaseModel):
    coordinates: Coordinates
    source: str = "NASA POWER · MERRA-2 (media anual de 25 años)"
    values: EarthClimateValues


def _fetch_power(latitude: float, longitude: float) -> dict[str, Any]:
    response = httpx.get(
        POWER_URL,
        params={
            "parameters": PARAMETERS,
            "community": "SB",
            "latitude": latitude,
            "longitude": longitude,
            "format": "JSON",
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["properties"]["parameter"]


def get_earth_climate(latitude: float, longitude: float) -> EarthClimateResponse:
    try:
        params = _fetch_power(latitude, longitude)
        annual = {name: series["ANN"] for name, series in params.items()}
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.error("Fallo consultando NASA POWER: %s", exc)
        raise HTTPException(status_code=502, detail="NASA POWER no disponible") from exc

    if any(annual.get(name, FILL_VALUE) == FILL_VALUE for name in PARAMETERS.split(",")):
        raise HTTPException(status_code=404, detail="Sin datos para estas coordenadas")

    return EarthClimateResponse(
        coordinates=Coordinates(latitude=latitude, longitude=longitude),
        values=EarthClimateValues(
            surface_temperature_k=annual["TS"] + 273.15,
            surface_pressure_pa=annual["PS"] * 1000.0,  # POWER entrega kPa
            cloud_cover_pct=annual["CLOUD_AMT"],
            aerosol_optical_depth=annual["AOD_55"],
            wind_10m_m_s=annual["WS10M"],
        ),
    )
