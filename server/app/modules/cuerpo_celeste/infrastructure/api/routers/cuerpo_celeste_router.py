"""Endpoints FastAPI para el módulo cuerpo_celeste."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.cuerpo_celeste.infrastructure.api.schemas.cuerpo_celeste_schemas import (
    CuerpoCelesteResponse,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[CuerpoCelesteResponse],
    summary="Listar cuerpos celestes",
)
def list_cuerpo_celestes(db: DBSession) -> Sequence[CuerpoCelesteModel]:
    """Devuelve los cuerpos celestes registrados en la base de datos."""
    return db.exec(select(CuerpoCelesteModel)).all()
