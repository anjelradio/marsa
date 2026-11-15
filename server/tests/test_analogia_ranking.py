"""Pruebas del cálculo de similitud y del endpoint de ranking de analogías."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import get_session
from app.main import app
from app.modules.analogia.domain.services.similarity import (
    CaracteristicaSpec,
    calcular_similitud,
    similitud_caracteristica,
)
from app.shared.infrastructure.db.seed import CARACTERISTICAS, seed_initial_data


def test_pesos_de_caracteristicas_suman_uno() -> None:
    assert sum(c["peso"] for c in CARACTERISTICAS) == pytest.approx(1.0)


def test_similitud_caracteristica_extremos_y_acotado() -> None:
    assert similitud_caracteristica(10, 10, 100) == 1.0
    assert similitud_caracteristica(0, 100, 100) == 0.0
    assert similitud_caracteristica(0, 500, 100) == 0.0
    assert similitud_caracteristica(0, 25, 100) == pytest.approx(0.75)


def test_similitud_caracteristica_rechaza_rango_no_positivo() -> None:
    with pytest.raises(ValueError):
        similitud_caracteristica(1, 2, 0)


def test_calcular_similitud_cobertura_parcial_y_explicacion() -> None:
    specs = [
        CaracteristicaSpec(1, "Temp", "K", 100.0, 0.5),
        CaracteristicaSpec(2, "Hielo", "%", 100.0, 0.3),
        CaracteristicaSpec(3, "Polvo", "tau", 5.0, 0.2),
    ]
    r = calcular_similitud(specs, {1: 50.0, 2: 0.0}, {1: 50.0, 2: 80.0})
    # Temp coincide (1.0), Hielo difiere (0.2), Polvo sin dato.
    assert r.cobertura == pytest.approx(0.8)
    assert r.similitud == pytest.approx((0.5 * 1.0 + 0.3 * 0.2) / 0.8, abs=1e-3)
    assert r.coincide == "Temp"
    assert r.difiere == "Hielo"
    assert [d.caracteristica for d in r.detalle] == ["Temp", "Hielo"]


def test_calcular_similitud_sin_datos_comunes_es_cero() -> None:
    specs = [CaracteristicaSpec(1, "Temp", "K", 100.0, 1.0)]
    r = calcular_similitud(specs, {}, {1: 5.0})
    assert r.similitud == 0.0
    assert r.cobertura == 0.0


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_initial_data(session)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("destino", ["marte", "luna"])
def test_ranking_ordenado_y_con_explicacion(client: TestClient, destino: str) -> None:
    response = client.get("/api/analogia/ranking", params={"destino": destino})
    assert response.status_code == 200
    filas = response.json()
    assert len(filas) == 5
    similitudes = [f["similitud"] for f in filas]
    assert similitudes == sorted(similitudes, reverse=True)
    assert [f["posicion"] for f in filas] == [1, 2, 3, 4, 5]
    for f in filas:
        assert 0 <= f["similitud"] <= 1
        assert f["cobertura"] == pytest.approx(1.0)
        assert f["metodo"] == "ponderado-v1"
        assert f["geom"]["type"] == "Point"
        assert len(f["detalle"]) == len(CARACTERISTICAS)


def test_ranking_destino_por_defecto_es_marte(client: TestClient) -> None:
    default = client.get("/api/analogia/ranking").json()
    marte = client.get("/api/analogia/ranking", params={"destino": "marte"}).json()
    assert default == marte
    assert all(f["sitio_destino"] in ("Cráter Gale", "Meridiani Planum") for f in marte)


def test_ranking_rechaza_destino_invalido(client: TestClient) -> None:
    assert client.get("/api/analogia/ranking", params={"destino": "venus"}).status_code == 422


def test_seed_es_idempotente_y_persiste_analogias(client: TestClient) -> None:
    primera = client.get("/api/analogia/").json()
    assert len(primera) == 10  # 5 sitios terrestres x (Marte, Luna)
    assert all(a["coincide"] is not None and a["metodo"] == "ponderado-v1" for a in primera)
