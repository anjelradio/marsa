"""Endpoints FastAPI para el módulo caracteristica."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.caracteristica.infrastructure.api.schemas.caracteristica_schemas import (
    CaracteristicaResponse,
)
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[CaracteristicaResponse],
    summary="Listar características",
)
def list_caracteristicas(db: DBSession) -> Sequence[CaracteristicaModel]:
    """Devuelve las características registradas en la base de datos."""
    return db.exec(select(CaracteristicaModel)).all()
