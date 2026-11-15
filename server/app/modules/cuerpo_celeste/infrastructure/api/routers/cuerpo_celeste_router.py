"""Endpoints FastAPI para el módulo cuerpo_celeste."""

from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.cuerpo_celeste.infrastructure.api.schemas.cuerpo_celeste_schemas import (
    CuerpoCelesteResponse,
)
from app.modules.cuerpo_celeste.infrastructure.mars_climate import (
    MarsClimateResponse,
    get_mars_climate,
)
from app.modules.cuerpo_celeste.infrastructure.mars_images import MarsImage, get_mars_images
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)

router = APIRouter()
MarsLatitude = Annotated[float, Query(ge=-90, le=90, description="Latitud norte en grados")]
MarsLongitude = Annotated[float, Query(ge=-180, le=180, description="Longitud este en grados")]


@router.get(
    "/",
    response_model=list[CuerpoCelesteResponse],
    summary="Listar cuerpos celestes",
)
def list_cuerpo_celestes(db: DBSession) -> Sequence[CuerpoCelesteModel]:
    """Devuelve los cuerpos celestes registrados en la base de datos."""
    return db.exec(select(CuerpoCelesteModel)).all()


@router.get("/marte/clima", summary="Consultar climatología de Marte por coordenadas")
def read_mars_climate(
    lat: MarsLatitude,
    lon: MarsLongitude,
) -> MarsClimateResponse:
    """Devuelve el promedio diurno de la celda más cercana de MCD 6.2 para Ls 105°."""
    return get_mars_climate(lat, lon)


@router.get("/marte/imagenes", summary="Buscar imágenes orbitales de Marte por coordenadas")
def read_mars_images(
    lat: MarsLatitude, lon: MarsLongitude, view: Literal["regional", "detail"] = "detail"
) -> list[MarsImage]:
    """Devuelve el mosaico regional Viking o miniaturas de detalle de la zona."""
    return get_mars_images(lat, lon, view)
