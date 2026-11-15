"""Endpoints FastAPI para el módulo analogia."""

from collections.abc import Sequence

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
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
from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
    AnalogiaModel,
)

router = APIRouter()


@router.get("/", response_model=list[AnalogiaResponse], summary="Listar analogías")
def list_analogias(db: DBSession) -> Sequence[AnalogiaModel]:
    """Devuelve las analogías registradas en la base de datos."""
    return db.exec(select(AnalogiaModel)).all()


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
