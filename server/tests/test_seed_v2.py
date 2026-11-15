"""El seed del esquema v2: minerales en composición, códigos, validación y corridas."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import get_session
from app.main import app
from app.modules.analogia.infrastructure.persistence.models.analogia_model import AnalogiaModel
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.composicion_celda.infrastructure.persistence.models.composicion_celda_model import (
    ComposicionCeldaModel,
)
from app.modules.corrida_analisis.infrastructure.persistence.models.corrida_analisis_model import (
    CorridaAnalisisModel,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.infrastructure.persistence.models.dataset_model import DatasetModel
from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.modules.medicion.infrastructure.persistence.models.medicion_model import MedicionModel
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.infrastructure.db import seed as seed_module
from app.shared.infrastructure.db.seed import seed_initial_data


def _count(session: Session, model) -> int:
    return session.exec(select(func.count()).select_from(model)).one()


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        seed_initial_data(s)
        yield s


def test_minerals_are_composition_not_physical_features(session: Session) -> None:
    assert _count(session, CaracteristicaModel) == 8  # las 7 físicas y Relieve Regional
    assert {c.grupo for c in session.exec(select(CaracteristicaModel)).all()} == {
        "fisico",
        "terreno",
    }
    composicion = session.exec(select(ComposicionCeldaModel)).all()
    assert len(composicion) == 63  # 9 sitios x 7 minerales
    assert {c.tipo for c in composicion} == {"mineral"}
    datasets = {d.id: d.nombre for d in session.exec(select(DatasetModel)).all()}
    assert "GLiM (Global Lithological Map)" in {datasets[c.dataset_id] for c in composicion}
    # ninguna medición queda atada a un mineral
    assert _count(session, MedicionModel) == 63  # 9 sitios x 7 variables físicas


def test_reference_sites_get_unique_codes_and_bodies_get_a_radius(session: Session) -> None:
    sitios = session.exec(select(SitioModel)).all()
    codigos = [s.codigo for s in sitios]
    assert len(set(codigos)) == len(codigos) == 9
    assert all(c.startswith("R_") for c in codigos)
    assert "R_desierto-de-atacama-yungay" in codigos
    assert {s.clase for s in sitios} == {"referencia"}
    radios = {c.nombre: c.radio_km for c in session.exec(select(CuerpoCelesteModel)).all()}
    assert radios == {"Tierra": 6371.0, "Marte": 3389.5, "Luna": 1737.4}


def test_normalized_value_uses_the_physical_range(session: Session) -> None:
    elevacion = session.exec(
        select(CaracteristicaModel).where(CaracteristicaModel.nombre == "Elevación")
    ).one()
    fila = session.exec(
        select(MedicionModel).where(MedicionModel.caracteristica_id == elevacion.id)
    ).first()
    esperado = (fila.valor - elevacion.valor_min) / (elevacion.valor_max - elevacion.valor_min)
    assert fila.valor_normalizado == pytest.approx(min(1.0, max(0.0, esperado)))


def test_persisted_analogies_carry_group_scores_and_their_run(session: Session) -> None:
    analogias = session.exec(select(AnalogiaModel)).all()
    assert len(analogias) == 10
    corrida = session.exec(select(CorridaAnalisisModel)).one()
    assert (corrida.version, corrida.metodo) == ("v2-grupos", "grupos-v1")
    assert corrida.parametros["pesos_grupo"] == {"fisico": 0.5, "terreno": 0.2}
    for a in analogias:
        assert a.corrida_id == corrida.id
        assert 0 <= a.similitud <= 1
        assert a.sim_fisica is not None and a.sim_terreno is not None
        assert a.sim_geologica is None  # la geología aún no entra en la puntuación


def test_seed_twice_keeps_one_run_and_no_duplicates(session: Session) -> None:
    antes = {m: _count(session, m) for m in (MedicionModel, ComposicionCeldaModel, AnalogiaModel)}
    seed_initial_data(session)
    assert _count(session, CorridaAnalisisModel) == 1
    assert {m: _count(session, m) for m in antes} == antes


def test_seed_keeps_the_history_of_other_runs(session: Session) -> None:
    vieja = CorridaAnalisisModel(version="v1-inicial", metodo="ponderado-v1")
    session.add(vieja)
    session.flush()
    session.add(
        AnalogiaModel(
            corrida_id=vieja.id, sitio_tierra_id=1, sitio_destino_id=6, similitud=0.5, metodo="ponderado-v1"
        )
    )
    session.commit()

    seed_initial_data(session)

    historial = session.exec(select(AnalogiaModel).where(AnalogiaModel.corrida_id == vieja.id)).all()
    assert len(historial) == 1  # el seed solo recalcula su propia corrida
    assert _count(session, AnalogiaModel) == 11


def test_seed_rejects_a_value_outside_the_physical_range(engine, monkeypatch) -> None:
    """Validar primero: un dato imposible lanza la excepción y no se guarda ni se corrige."""
    monkeypatch.setattr(
        seed_module,
        "_cargar_mediciones_reales",
        lambda: {
            "Desierto de Atacama (Yungay)": {
                "Temperatura Superficial": {"valor": 9999.0, "dataset": "NASA POWER (MERRA-2)"}
            }
        },
    )
    with Session(engine) as s:
        with pytest.raises(InvalidMedicionDataException, match="valor"):
            seed_initial_data(s)
        s.rollback()
        assert _count(s, MedicionModel) == 0
        assert _count(s, AnalogiaModel) == 0


# ── API: la lista de analogías por corrida ────────────────────────────────────────────


@pytest.fixture()
def client(engine, session):
    def override_get_session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_list_defaults_to_the_latest_run_and_can_filter(client: TestClient, engine) -> None:
    with Session(engine) as s:
        nueva = CorridaAnalisisModel(version="v3", metodo="grupos-v1")
        s.add(nueva)
        s.flush()
        s.add(
            AnalogiaModel(
                corrida_id=nueva.id, sitio_tierra_id=1, sitio_destino_id=6, similitud=0.7, metodo="grupos-v1"
            )
        )
        s.commit()
        nueva_id = nueva.id

    ultima = client.get("/api/analogia/").json()
    assert [a["corrida_id"] for a in ultima] == [nueva_id]  # solo la corrida más reciente
    primera = client.get("/api/analogia/", params={"corrida_id": 1}).json()
    assert len(primera) == 10
    assert client.get("/api/analogia/", params={"corrida_id": 999}).json() == []
    assert client.get("/api/analogia/", params={"corrida_id": 0}).status_code == 422
