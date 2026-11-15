"""Endpoints FastAPI para el módulo analogia."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.analogia.infrastructure.api.schemas.analogia_schemas import (
    AnalogiaResponse,
)
from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
    AnalogiaModel,
)

router = APIRouter()


@router.get("/", response_model=list[AnalogiaResponse], summary="Listar analogías")
def list_analogias(db: DBSession) -> Sequence[AnalogiaModel]:
    """Devuelve las analogías registradas en la base de datos."""
    return db.exec(select(AnalogiaModel)).all()
