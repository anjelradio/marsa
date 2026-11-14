"""Endpoints FastAPI para el módulo medicion."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.medicion.infrastructure.api.schemas.medicion_schemas import (
    MedicionResponse,
)
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)

router = APIRouter()


@router.get("/", response_model=list[MedicionResponse], summary="Listar mediciones")
def list_medicions(db: DBSession) -> Sequence[MedicionModel]:
    """Devuelve las mediciones registradas en la base de datos."""
    return db.exec(select(MedicionModel)).all()
