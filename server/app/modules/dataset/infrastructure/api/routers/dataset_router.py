"""Endpoints FastAPI para el módulo dataset."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlmodel import select

from app.core.dependencies import DBSession
from app.modules.dataset.infrastructure.api.schemas.dataset_schemas import (
    DatasetResponse,
)
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)

router = APIRouter()


@router.get("/", response_model=list[DatasetResponse], summary="Listar datasets")
def list_datasets(db: DBSession) -> Sequence[DatasetModel]:
    """Devuelve los datasets registrados en la base de datos."""
    return db.exec(select(DatasetModel)).all()
