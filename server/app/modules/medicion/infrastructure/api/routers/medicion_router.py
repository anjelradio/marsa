"""Endpoints FastAPI para el módulo medicion."""

from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.medicion.infrastructure.api.schemas.medicion_schemas import (
    ExtraerSatelitalRequest,
    MedicionResponse,
)
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)
from app.shared.application.satelital_service import SatelitalService

router = APIRouter()


@router.get("/", response_model=list[MedicionResponse], summary="Listar mediciones")
def list_medicions(db: DBSession, sitio_id: int | None = None) -> Sequence[MedicionModel]:
    """Devuelve las mediciones registradas en la base de datos (con filtro opcional por sitio)."""
    stmt = select(MedicionModel)
    if sitio_id is not None:
        stmt = stmt.where(MedicionModel.sitio_id == sitio_id)
    return db.exec(stmt).all()


@router.post(
    "/extraer-satelital",
    response_model=list[MedicionResponse],
    summary="Extraer métricas satelitales externas y guardar en BD",
)
def extraer_satelital(
    request: ExtraerSatelitalRequest,
    db: DBSession,
) -> Sequence[MedicionModel]:
    """Consulta la API satelital correspondiente (NASA POWER o USGS) según el cuerpo celeste del sitio."""
    service = SatelitalService(db)
    try:
        mediciones = service.procesar_extraccion_sitio(
            sitio_id=request.sitio_id,
            datetime_range=request.datetime_range,
        )
        return mediciones
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante la extracción satelital: {e}"
        )
