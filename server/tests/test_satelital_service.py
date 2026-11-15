"""Pruebas de SatelitalService: la nubosidad de la Tierra sale de NASA POWER."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

import app.shared.infrastructure.db.models  # noqa: F401
from app.modules.dataset.infrastructure.persistence.models.dataset_model import DatasetModel
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.application import satelital_service
from app.shared.application.satelital_service import SatelitalService
from app.shared.infrastructure.db.seed import seed_initial_data


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        seed_initial_data(s)
        yield s


def _atacama(session: Session) -> SitioModel:
    return session.exec(
        select(SitioModel).where(SitioModel.nombre.like("Desierto de Atacama%"))
    ).one()


def test_earth_cloudiness_is_saved_from_nasa_power(session: Session, monkeypatch) -> None:
    fake = SimpleNamespace(values=SimpleNamespace(cloud_cover_pct=33.0))
    monkeypatch.setattr(satelital_service, "get_earth_climate", lambda lat, lon: fake)

    medidas = SatelitalService(session).procesar_extraccion_sitio(_atacama(session).id)

    assert len(medidas) == 1
    assert medidas[0].valor == 33.0
    assert medidas[0].valor_normalizado == pytest.approx(0.33)
    assert session.get(DatasetModel, medidas[0].dataset_id).nombre == "NASA POWER (MERRA-2)"


def test_earth_extraction_returns_nothing_when_power_has_no_data(
    session: Session, monkeypatch
) -> None:
    def sin_datos(lat: float, lon: float):
        raise HTTPException(status_code=404, detail="Sin datos para estas coordenadas")

    monkeypatch.setattr(satelital_service, "get_earth_climate", sin_datos)

    assert SatelitalService(session).procesar_extraccion_sitio(_atacama(session).id) == []
