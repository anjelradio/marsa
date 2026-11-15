"""Cliente HTTP para consultas al catálogo STAC de USGS Astrogeology (Marte y Luna)."""

import logging
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        *,
        timeout: float = 20.0,
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
            with httpx.Client(timeout=timeout) as client:
                res = client.get(url, params=params, headers=self.headers)
                if res.status_code == 200:
                    return res.json().get("features", [])
                logger.error("Error consultando USGS STAC (%s): %s", res.status_code, res.text)
        except Exception as e:
            logger.error("Fallo de red en USGS STAC: %s", e)
        return []
