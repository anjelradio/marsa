"""Validadores de parámetros geoespaciales y temporales para consultas satelitales.

Cada validador lanza ``ValidationException`` con un mensaje corto; nunca devuelve
valores por defecto silenciosos.
"""

import math
from datetime import datetime, timezone
from typing import Any

from app.shared.domain.exceptions import ValidationException

MIN_LAT, MAX_LAT = -90.0, 90.0
MIN_LON, MAX_LON = -180.0, 180.0
# Evita consultas de planeta completo: el lado máximo de un bbox, en grados.
MAX_BBOX_SPAN_DEG = 90.0
POINT_BUFFER_DEG = 0.05


def _finite(value: Any, nombre: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValidationException(f"{nombre} es obligatorio y debe ser numérico")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationException(f"{nombre} debe ser numérico") from None
    if not math.isfinite(number):
        raise ValidationException(f"{nombre} no puede ser NaN ni infinito")
    return number


def validate_lat_lon(lat: Any, lon: Any) -> tuple[float, float]:
    """Valida una coordenada: latitud en [-90, 90] y longitud en [-180, 180]."""
    lat_f = _finite(lat, "latitud")
    lon_f = _finite(lon, "longitud")
    if not MIN_LAT <= lat_f <= MAX_LAT:
        raise ValidationException(f"latitud {lat_f} fuera de [{MIN_LAT:g}, {MAX_LAT:g}]")
    if not MIN_LON <= lon_f <= MAX_LON:
        raise ValidationException(f"longitud {lon_f} fuera de [{MIN_LON:g}, {MAX_LON:g}]")
    return lat_f, lon_f


def validate_bbox(bbox: Any) -> list[float]:
    """Valida [min_lon, min_lat, max_lon, max_lat]."""
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise ValidationException("bbox debe tener 4 valores [min_lon, min_lat, max_lon, max_lat]")
    min_lon, min_lat, max_lon, max_lat = (
        _finite(v, n)
        for v, n in zip(bbox, ("min_lon", "min_lat", "max_lon", "max_lat"))
    )
    validate_lat_lon(min_lat, min_lon)
    validate_lat_lon(max_lat, max_lon)
    if min_lon >= max_lon or min_lat >= max_lat:
        raise ValidationException("bbox inválido: el mínimo debe ser menor que el máximo")
    if (max_lon - min_lon) > MAX_BBOX_SPAN_DEG or (max_lat - min_lat) > MAX_BBOX_SPAN_DEG:
        raise ValidationException(
            f"bbox demasiado grande: el lado máximo es {MAX_BBOX_SPAN_DEG:g} grados"
        )
    return [min_lon, min_lat, max_lon, max_lat]


def _collect_points(coords: Any, out: list[tuple[Any, Any]]) -> None:
    """Aplana coordenadas GeoJSON anidadas a una lista de pares [lon, lat]."""
    if (
        isinstance(coords, (list, tuple))
        and len(coords) >= 2
        and not isinstance(coords[0], (list, tuple))
    ):
        out.append((coords[0], coords[1]))
        return
    if isinstance(coords, (list, tuple)):
        for item in coords:
            _collect_points(item, out)


def bbox_from_geom(geom: dict[str, Any] | None) -> list[float]:
    """Calcula un bbox válido desde GeoJSON (Point, Polygon, MultiPolygon, LineString...)."""
    if not geom or not isinstance(geom, dict):
        raise ValidationException("El sitio no tiene geometría (geom) definida")

    g_type = geom.get("type")
    coords = geom.get("coordinates")
    if not g_type or not coords:
        raise ValidationException("La geometría del sitio no tiene 'type' o 'coordinates'")

    puntos: list[tuple[Any, Any]] = []
    _collect_points(coords, puntos)
    if not puntos:
        raise ValidationException("La geometría del sitio no contiene coordenadas")

    pares = [validate_lat_lon(lat, lon) for lon, lat in puntos]
    lons = [lon for _, lon in pares]
    lats = [lat for lat, _ in pares]

    if g_type == "Point":
        return validate_bbox(
            [
                max(MIN_LON, lons[0] - POINT_BUFFER_DEG),
                max(MIN_LAT, lats[0] - POINT_BUFFER_DEG),
                min(MAX_LON, lons[0] + POINT_BUFFER_DEG),
                min(MAX_LAT, lats[0] + POINT_BUFFER_DEG),
            ]
        )
    return validate_bbox([min(lons), min(lats), max(lons), max(lats)])


def validate_datetime_range(value: str | None) -> str | None:
    """Valida un instante o intervalo ISO 8601 ('inicio/fin', admite '..' como extremo abierto).

    Devuelve el texto sin espacios sobrantes, o ``None`` si no se indicó rango.
    """
    if value is None:
        return None
    texto = value.strip()
    if not texto:
        raise ValidationException("datetime_range no puede estar vacío")

    partes = texto.split("/")
    if len(partes) > 2:
        raise ValidationException("datetime_range admite un instante o 'inicio/fin'")

    ahora = datetime.now(timezone.utc)
    fechas: list[datetime | None] = []
    for parte in partes:
        if parte in ("..", ""):
            fechas.append(None)
            continue
        try:
            fecha = datetime.fromisoformat(parte.replace("Z", "+00:00"))
        except ValueError:
            raise ValidationException(f"Fecha ISO 8601 inválida: '{parte}'") from None
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        if fecha > ahora:
            raise ValidationException(f"La fecha '{parte}' está en el futuro")
        fechas.append(fecha)

    if all(f is None for f in fechas):
        raise ValidationException("datetime_range necesita al menos una fecha")
    if len(fechas) == 2 and fechas[0] and fechas[1] and fechas[0] > fechas[1]:
        raise ValidationException("datetime_range: la fecha de inicio es posterior a la de fin")
    return texto
