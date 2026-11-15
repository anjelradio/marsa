"""Entidad principal de dominio para sitio."""

from typing import Any

from app.modules.sitio.domain.exceptions import InvalidSitioDataException
from app.shared.domain.validators import (
    require_in_range,
    require_non_empty_text,
    require_one_of,
    require_positive_id,
    validate_optional_text,
)

CLASES_SITIO = ("referencia", "celda")


class Sitio:
    """Entidad de dominio que representa un sitio de estudio geográfico/planetario.

    Un sitio es de clase ``referencia`` (lugar con nombre propio) o ``celda`` (celda de la
    malla global, que exige código y límites).
    """

    def __init__(
        self,
        id: int | None,
        cuerpo_id: int,
        nombre: str,
        tipo: str | None = None,
        geom: dict[str, Any] | None = None,
        clase: str = "referencia",
        codigo: str | None = None,
        lat_min: float | None = None,
        lat_max: float | None = None,
        lon_min: float | None = None,
        lon_max: float | None = None,
    ) -> None:
        self.id = id
        self.cuerpo_id = cuerpo_id
        self.nombre = nombre
        self.tipo = tipo
        self.geom = geom
        self.clase = clase
        self.codigo = codigo
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max

    @classmethod
    def create(
        cls,
        *,
        cuerpo_id: int,
        nombre: str,
        tipo: str | None = None,
        geom: dict[str, Any] | None = None,
        clase: str = "referencia",
        codigo: str | None = None,
        lat_min: float | None = None,
        lat_max: float | None = None,
        lon_min: float | None = None,
        lon_max: float | None = None,
    ) -> "Sitio":
        """Crea un nuevo sitio validando sus atributos e invariantes de relación."""
        valid_cuerpo_id = require_positive_id(
            cuerpo_id, "cuerpo_id", InvalidSitioDataException
        )
        clean_nombre = require_non_empty_text(
            nombre, "nombre", 100, InvalidSitioDataException
        )
        clean_tipo = validate_optional_text(
            tipo, "tipo", 50, InvalidSitioDataException
        )
        valid_clase = require_one_of(
            clase, "clase", CLASES_SITIO, InvalidSitioDataException
        )
        clean_codigo = validate_optional_text(
            codigo, "codigo", 60, InvalidSitioDataException
        )

        limites = {"lat_min": lat_min, "lat_max": lat_max, "lon_min": lon_min, "lon_max": lon_max}
        if valid_clase == "celda":
            if clean_codigo is None:
                raise InvalidSitioDataException("Una celda necesita el campo 'codigo'.")
            faltan = [name for name, value in limites.items() if value is None]
            if faltan:
                raise InvalidSitioDataException(
                    f"Una celda necesita los límites: {', '.join(faltan)}."
                )
        for name, value in limites.items():
            if value is not None:
                bound = 90.0 if name.startswith("lat") else 180.0
                limites[name] = require_in_range(
                    value, name, -bound, bound, InvalidSitioDataException
                )
        if (
            limites["lat_min"] is not None
            and limites["lat_max"] is not None
            and limites["lat_min"] >= limites["lat_max"]
        ):
            raise InvalidSitioDataException("'lat_min' debe ser menor que 'lat_max'.")
        if (
            limites["lon_min"] is not None
            and limites["lon_max"] is not None
            and limites["lon_min"] >= limites["lon_max"]
        ):
            raise InvalidSitioDataException("'lon_min' debe ser menor que 'lon_max'.")

        return cls(
            id=None,
            cuerpo_id=valid_cuerpo_id,
            nombre=clean_nombre,
            tipo=clean_tipo,
            geom=geom,
            clase=valid_clase,
            codigo=clean_codigo,
            **limites,
        )
