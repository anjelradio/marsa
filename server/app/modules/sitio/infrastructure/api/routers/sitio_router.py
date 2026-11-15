"""Endpoints FastAPI para el módulo sitio."""

from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.sitio.infrastructure.api.schemas.sitio_schemas import (
    CreateSitioRequest,
    SitioResponse,
)
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel

router = APIRouter()


@router.get("/", response_model=list[SitioResponse], summary="Listar sitios")
def list_sitios(db: DBSession, cuerpo_id: int | None = None) -> Sequence[SitioModel]:
    """Devuelve los sitios registrados en la base de datos (filtro opcional por cuerpo celeste)."""
    stmt = select(SitioModel)
    if cuerpo_id is not None:
        stmt = stmt.where(SitioModel.cuerpo_id == cuerpo_id)
    return db.exec(stmt).all()


@router.get("/{sitio_id}", response_model=SitioResponse, summary="Obtener sitio por ID")
def get_sitio(sitio_id: int, db: DBSession) -> SitioModel:
    """Devuelve un sitio específico por su ID."""
    sitio = db.get(SitioModel, sitio_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    return sitio


@router.post("/", response_model=SitioResponse, status_code=201, summary="Crear nuevo sitio")
def create_sitio(payload: CreateSitioRequest, db: DBSession) -> SitioModel:
    """Registra un nuevo sitio de estudio (Tierra, Marte o Luna) con su geometría."""
    sitio = SitioModel(
        cuerpo_id=payload.cuerpo_id,
        nombre=payload.nombre,
        tipo=payload.tipo,
        geom=payload.geom,
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    return sitio
