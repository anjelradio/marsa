"""Clientes HTTP para consultas a los catálogos satelitales STAC (Copernicus y USGS)."""

import logging
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class CopernicusClient:
    """Cliente para la STAC API de Copernicus Data Space Ecosystem (CDSE)."""

    def __init__(self) -> None:
        self.base_url = settings.CDSE_STAC_API_URL.rstrip("/")
        self.token_url = settings.CDSE_TOKEN_URL
        self._token: str | None = None

    def _get_token(self) -> str | None:
        """Obtiene un token Bearer OAuth2 si se configuraron credenciales."""
        if not settings.CDSE_USERNAME or not settings.CDSE_PASSWORD:
            return None

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    self.token_url,
                    data={
                        "client_id": settings.CDSE_CLIENT_ID,
                        "grant_type": "password",
                        "username": settings.CDSE_USERNAME,
                        "password": settings.CDSE_PASSWORD,
                    },
                )
                if res.status_code == 200:
                    self._token = res.json().get("access_token")
                    return self._token
        except Exception as e:
            logger.warning("No se pudo obtener token de Copernicus: %s", e)
        return None

    def search(
        self,
        collections: list[str],
        bbox: list[float],
        datetime_range: str | None = None,
        limit: int = 5,
        query: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca productos satelitales en Copernicus STAC."""
        headers = {"Content-Type": "application/json"}
        token = self._token or self._get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        payload: dict[str, Any] = {
            "collections": collections,
            "bbox": bbox,
            "limit": limit,
        }
        if datetime_range:
            payload["datetime"] = datetime_range
        if query:
            payload["query"] = query

        url = f"{self.base_url}/search"
        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("features", [])
                logger.error("Error consultando Copernicus STAC (%s): %s", res.status_code, res.text)
        except Exception as e:
            logger.error("Fallo de red en Copernicus STAC: %s", e)
        return []

    def get_cloud_cover_and_weather(
        self,
        bbox: list[float],
        datetime_range: str | None = None,
    ) -> dict[str, float | None]:
        """
        Extrae el porcentaje promedio de cobertura de nubes desde Sentinel-2 L2A.
        """
        items = self.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime_range=datetime_range,
            limit=5,
        )
        if not items:
            return {"cloud_cover": None}

        # Extraer propiedad estándar 'eo:cloud_cover' de los items
        cloud_values = [
            f["properties"]["eo:cloud_cover"]
            for f in items
            if "properties" in f and "eo:cloud_cover" in f["properties"]
        ]
        avg_cloud = sum(cloud_values) / len(cloud_values) if cloud_values else None
        return {"cloud_cover": avg_cloud}


class USGSStacClient:
    """Cliente para la STAC API de USGS Astrogeology (Planetary ARD - Marte, Luna)."""

    def __init__(self) -> None:
        self.base_url = settings.USGS_STAC_API_URL.rstrip("/")
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def search(
        self,
        collections: list[str] | None = None,
        bbox: list[float] | None = None,
        datetime_range: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Busca productos en el catálogo planetario STAC de USGS.
        Nota: AWS CloudFront en USGS bloquea POST con 403, por lo que usamos GET con query params.
        """
        params: dict[str, Any] = {"limit": limit}
        if collections:
            params["collections"] = ",".join(collections)
        if bbox:
            params["bbox"] = ",".join(map(str, bbox))
        if datetime_range:
            params["datetime"] = datetime_range

        url = f"{self.base_url}/search"
        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.get(url, params=params, headers=self.headers)
                if res.status_code == 200:
                    return res.json().get("features", [])
                logger.error("Error consultando USGS STAC (%s): %s", res.status_code, res.text)
        except Exception as e:
            logger.error("Fallo de red en USGS STAC: %s", e)
        return []

