"""Endpoints FastAPI para el módulo sitio."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.sitio.infrastructure.api.schemas.sitio_schemas import SitioResponse
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel

router = APIRouter()


@router.get("/", response_model=list[SitioResponse], summary="Listar sitios")
def list_sitios(db: DBSession) -> Sequence[SitioModel]:
    """Devuelve los sitios registrados en la base de datos."""
    return db.exec(select(SitioModel)).all()
