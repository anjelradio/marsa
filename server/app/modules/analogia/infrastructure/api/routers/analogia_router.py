"""Endpoints FastAPI para el módulo analogia y geología planetaria en tiempo real."""

from collections.abc import Sequence
from typing import Annotated, Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.analogia.application.queries.ranking_query import (
    DestinoNoEncontrado,
    ranking_analogos,
)
from app.modules.analogia.infrastructure.api.schemas.analogia_schemas import (
    AnalogiaResponse,
    RankingItemResponse,
)
from app.modules.analogia.infrastructure.api.schemas.geology_schemas import (
    MetadatosFuente,
    RespuestaComparacion,
    RespuestaGeologiaPunto,
    RespuestaMacrostratPuntual,
)
from app.modules.analogia.infrastructure.geology_service import (
    analizar_geologia_punto,
    comparar_analogo_tierra,
    consultar_macrostrat,
)
from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
    AnalogiaModel,
)

router = APIRouter()


@router.get("/", response_model=list[AnalogiaResponse], summary="Listar analogías")
def list_analogias(
    db: DBSession,
    corrida_id: Annotated[
        int | None,
        Query(gt=0, description="Corrida del análisis; por defecto, la más reciente."),
    ] = None,
) -> Sequence[AnalogiaModel]:
    """Devuelve las analogías de una corrida (la más reciente si no se indica otra)."""
    if corrida_id is None:
        corrida_id = db.exec(select(func.max(AnalogiaModel.corrida_id))).one()
    if corrida_id is None:
        return []
    return db.exec(
        select(AnalogiaModel).where(AnalogiaModel.corrida_id == corrida_id)
    ).all()


@router.get(
    "/ranking",
    response_model=list[RankingItemResponse],
    summary="Ranking de sitios terrestres análogos a Marte o la Luna",
)
def ranking(
    db: DBSession,
    destino: Annotated[Literal["marte", "luna"], Query()] = "marte",
) -> list[dict]:
    """Ordena los sitios de la Tierra por similitud con el destino indicado."""
    nombre = {"marte": "Marte", "luna": "Luna"}[destino]
    try:
        return ranking_analogos(db, nombre)
    except DestinoNoEncontrado as exc:
        raise HTTPException(status_code=404, detail=f"Destino no encontrado: {exc}")


# ==============================================================================
# ENDPOINTS DE GEOLOGÍA Y MINERALOGÍA PLANETARIA EN TIEMPO REAL
# ==============================================================================

@router.get(
    "/geologia/tierra/macrostrat",
    response_model=RespuestaMacrostratPuntual,
    summary="Unidades geológicas puntuales de Macrostrat (Tierra)",
)
async def get_macrostrat_puntual(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitud decimal (-90 a 90)"),
    lng: float = Query(..., ge=-180.0, le=180.0, description="Longitud decimal (-180 a 180)"),
    scale: Optional[str] = Query(None, description="Escala opcional: small, medium, large"),
) -> RespuestaMacrostratPuntual:
    """Consulta las unidades geológicas en tiempo real de Macrostrat para una coordenada en la Tierra."""
    unidades = await consultar_macrostrat(lat, lng, scale)
    return RespuestaMacrostratPuntual(
        coordenadas={"lat": lat, "lng": lng},
        total_unidades=len(unidades),
        unidades=unidades,
        atribucion=MetadatosFuente(
            fuente="Macrostrat API (macrostrat.org)",
            licencia="CC BY 4.0",
            resolucion_o_escala="Continental a Local (1:250k - 1:5M)",
            nota_metodologica="Consulta en tiempo real al punto geográfico seleccionado en el mapa.",
        ),
    )


@router.get(
    "/comparar-analogo",
    response_model=RespuestaComparacion,
    summary="Comparar punto terrestre con análogos en Marte o la Luna",
)
async def comparar_analogo_endpoint(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitud terrestre (-90 a 90)"),
    lng: float = Query(..., ge=-180.0, le=180.0, description="Longitud terrestre (-180 a 180)"),
    destino: str = Query("marte", description="Cuerpo celeste destino: 'marte' o 'luna'"),
) -> RespuestaComparacion:
    """
    Compara en tiempo real la geología del punto terrestre seleccionado contra
    las celdas 10°x10° de Marte (USGS SIM 3292) o la Luna (USGS Lunar).
    Calcula la similitud coseno y adjunta muestras minerales (CheMin / Apolo).
    """
    return await comparar_analogo_tierra(lat, lng, destino)


@router.get(
    "/geologia/punto",
    response_model=RespuestaGeologiaPunto,
    summary="Análisis geológico y mineralógico completo para cualquier punto en Tierra, Marte o Luna",
)
async def geologia_punto_endpoint(
    cuerpo: str = Query("Tierra", description="Nombre del cuerpo celeste: Tierra, Marte o Luna"),
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitud decimal (-90 a 90)"),
    lng: float = Query(..., ge=-180.0, le=180.0, description="Longitud decimal (-180 a 180)"),
    destino: Optional[str] = Query(None, description="Cuerpo análogo a comparar (ej. Marte o Luna si cuerpo es Tierra)"),
) -> RespuestaGeologiaPunto:
    """
    Devuelve los datos en tiempo real de rocas, minerales, litología y análogos
    para el punto exacto seleccionado en el globo 3D.
    """
    return await analizar_geologia_punto(cuerpo, lat, lng, destino)

