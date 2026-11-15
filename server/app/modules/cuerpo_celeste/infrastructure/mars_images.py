"""Búsqueda de imágenes orbitales cerca de un punto de Marte."""

from math import floor
from typing import Literal

from pydantic import BaseModel

from app.shared.infrastructure.external.stac_clients import USGSStacClient

_HIRISE_COLLECTION = "mro_hirise_uncontrolled_observations"
_SEARCH_RADIUS_DEG = 0.1
_PREVIEW_LIMIT = 3
_REGIONAL_ZOOM = 3
_LOCAL_ZOOM = 5
_VIKING_TILE_ROOT = (
    "https://trek.nasa.gov/tiles/Mars/EQ/"
    "Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm"
)


class MarsImage(BaseModel):
    id: str
    source: Literal["HiRISE", "Viking"]
    preview_url: str


def _search_bounds(lat: float, lon: float) -> list[list[float]]:
    south = max(-90, lat - _SEARCH_RADIUS_DEG)
    north = min(90, lat + _SEARCH_RADIUS_DEG)
    west = lon - _SEARCH_RADIUS_DEG
    east = lon + _SEARCH_RADIUS_DEG

    # Separate the two sides of the antimeridian into valid STAC bounding boxes.
    if west < -180:
        return [[-180, south, east, north], [west + 360, south, 180, north]]
    if east > 180:
        return [[west, south, 180, north], [-180, south, east - 360, north]]
    return [[west, south, east, north]]


def _viking_tile(lat: float, lon: float, zoom: int) -> MarsImage:
    rows = 2**zoom
    cols = 2 * rows
    row = min(rows - 1, floor((90 - lat) * rows / 180))
    col = min(cols - 1, floor((lon + 180) * cols / 360))
    return MarsImage(
        id=f"viking-{zoom}-{row}-{col}",
        source="Viking",
        preview_url=f"{_VIKING_TILE_ROOT}/{zoom}/{row}/{col}.jpg",
    )


def get_mars_images(
    lat: float, lon: float, view: Literal["regional", "detail"] = "detail"
) -> list[MarsImage]:
    lon = -180 if lon == 180 else lon
    if view == "regional":
        return [_viking_tile(lat, lon, _REGIONAL_ZOOM)]

    client = USGSStacClient()
    previews: dict[str, MarsImage] = {}
    for bounds in _search_bounds(lat, lon):
        for item in client.search(
            collections=[_HIRISE_COLLECTION],
            bbox=bounds,
            limit=5,
            timeout=5.0,
        ):
            item_id = item.get("id")
            thumbnail = (item.get("assets") or {}).get("thumbnail") or {}
            url = thumbnail.get("href")
            if (
                item.get("collection") == _HIRISE_COLLECTION
                and isinstance(item_id, str)
                and item_id
                and isinstance(url, str)
                and url.startswith("https://")
            ):
                previews[item_id] = MarsImage(id=item_id, source="HiRISE", preview_url=url)
                if len(previews) == _PREVIEW_LIMIT:
                    return list(previews.values())

    return list(previews.values()) or [_viking_tile(lat, lon, _LOCAL_ZOOM)]
