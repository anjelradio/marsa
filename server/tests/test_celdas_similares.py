"""Búsqueda de celdas similares, sensibilidad a los pesos y el ranking solo con referencias."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import get_session
from app.main import app
from app.modules.analogia.domain.services.sensibilidad import (
    escenarios_de_pesos,
    estabilidad_del_ranking,
)
from app.modules.analogia.domain.services.similarity import PESOS_GRUPO, combinar_grupos
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.infrastructure.persistence.models.dataset_model import DatasetModel
from app.modules.medicion.infrastructure.persistence.models.medicion_model import MedicionModel
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.infrastructure.db.seed import seed_initial_data

# ── sensibilidad (dominio puro) ───────────────────────────────────────────────────────


def test_scenarios_scale_each_weight_and_always_sum_to_one() -> None:
    escenarios = escenarios_de_pesos({"fisico": 0.5, "terreno": 0.2})
    assert len(escenarios) == 9  # 3 factores ^ 2 grupos
    assert all(sum(e.values()) == pytest.approx(1.0) for e in escenarios)
    base = {"fisico": 0.5 / 0.7, "terreno": 0.2 / 0.7}
    assert any(e["fisico"] == pytest.approx(base["fisico"]) for e in escenarios)


def test_combine_groups_redistributes_the_weight_of_a_missing_group() -> None:
    assert combinar_grupos({"fisico": 0.8}) == pytest.approx(0.8)
    assert combinar_grupos({"fisico": 1.0, "terreno": 0.0}) == pytest.approx(0.5 / 0.7)
    assert combinar_grupos({}) == 0.0


def test_stability_is_one_for_a_candidate_that_wins_under_every_weighting() -> None:
    por_grupo = {
        1: {"fisico": 0.95, "terreno": 0.95},  # gana con cualquier peso
        2: {"fisico": 0.9, "terreno": 0.1},  # depende de cuánto pese el terreno
        3: {"fisico": 0.1, "terreno": 0.9},
    }
    r = estabilidad_del_ranking(por_grupo, 1)
    assert r[1].estabilidad == 1.0
    assert r[2].estabilidad == 0.0 and r[3].estabilidad == 0.0  # nunca superan al candidato 1
    assert r[2].similitud_min <= combinar_grupos(por_grupo[2]) <= r[2].similitud_max

    # sin el candidato dominante, el 2 y el 3 se turnan según el peso de cada grupo
    rivales = estabilidad_del_ranking({2: por_grupo[2], 3: por_grupo[3]}, 1)
    assert 0 < rivales[2].estabilidad < 1 and 0 < rivales[3].estabilidad < 1
    assert rivales[2].estabilidad + rivales[3].estabilidad == pytest.approx(1.0)
    with pytest.raises(ValueError):
        estabilidad_del_ranking(por_grupo, 0)


# ── endpoint ──────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        seed_initial_data(s)
    return engine


@pytest.fixture()
def client(engine):
    def override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _cuerpo(s: Session, nombre: str) -> int:
    return s.exec(select(CuerpoCelesteModel).where(CuerpoCelesteModel.nombre == nombre)).one().id


def _valores_de(s: Session, sitio_nombre: str) -> dict[str, float]:
    sitio = s.exec(select(SitioModel).where(SitioModel.nombre == sitio_nombre)).one()
    nombres = {c.id: c.nombre for c in s.exec(select(CaracteristicaModel)).all()}
    return {
        nombres[m.caracteristica_id]: m.valor
        for m in s.exec(select(MedicionModel).where(MedicionModel.sitio_id == sitio.id)).all()
    }


def _celda(s: Session, cuerpo: str, codigo: str, lat0: int, lon0: int, valores: dict) -> int:
    """Crea una celda de 10° con sus mediciones y devuelve su id."""
    sitio = SitioModel(
        cuerpo_id=_cuerpo(s, cuerpo),
        nombre=f"Celda {codigo}",
        tipo="Celda de 10°",
        clase="celda",
        codigo=codigo,
        lat_min=lat0,
        lat_max=lat0 + 10,
        lon_min=lon0,
        lon_max=lon0 + 10,
        geom={"type": "Polygon", "coordinates": []},
    )
    s.add(sitio)
    s.flush()
    caracteristicas = {c.nombre: c.id for c in s.exec(select(CaracteristicaModel)).all()}
    dataset = s.exec(select(DatasetModel)).first().id
    for nombre, valor in valores.items():
        s.add(
            MedicionModel(
                sitio_id=sitio.id,
                caracteristica_id=caracteristicas[nombre],
                dataset_id=dataset,
                valor=valor,
                valor_normalizado=0.5,
            )
        )
    s.commit()
    return sitio.id


@pytest.fixture()
def escenario(engine):
    """Un origen terrestre (Atacama) y tres celdas de Marte: igual, distinta y casi sin datos."""
    with Session(engine) as s:
        origen = _valores_de(s, "Desierto de Atacama (Yungay)")
        sitio_origen = s.exec(
            select(SitioModel).where(SitioModel.nombre == "Desierto de Atacama (Yungay)")
        ).one().id
        igual = _celda(s, "Marte", "M_N00_E000", 0, 0, origen)
        lejana = _celda(
            s,
            "Marte",
            "M_N10_E000",
            10,
            0,
            {n: (0.0 if v > 1 else 1.0) for n, v in origen.items()},
        )
        escasa = _celda(
            s,
            "Marte",
            "M_N20_E000",
            20,
            0,
            {"Temperatura Superficial": origen["Temperatura Superficial"]},
        )
    return {"origen": sitio_origen, "igual": igual, "lejana": lejana, "escasa": escasa}


def test_orders_cells_by_similarity_and_counts_the_unusable_ones(client, escenario) -> None:
    r = client.get(
        "/api/analogia/celdas-similares",
        params={"sitio_id": escenario["origen"], "destino": "marte"},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["origen"]["nombre"] == "Desierto de Atacama (Yungay)"
    assert cuerpo["metodo"] == "grupos-v1" and cuerpo["pesos_grupo"] == PESOS_GRUPO
    assert (cuerpo["evaluadas"], cuerpo["validas"], cuerpo["descartadas_por_cobertura"]) == (3, 2, 1)
    primero, segundo = cuerpo["resultados"]
    assert (primero["posicion"], primero["sitio_id"], primero["codigo"]) == (
        1,
        escenario["igual"],
        "M_N00_E000",
    )
    assert primero["similitud"] == 1.0 and segundo["sitio_id"] == escenario["lejana"]
    assert segundo["similitud"] < primero["similitud"]
    assert set(primero["por_grupo"]) == {"fisico", "terreno"}
    assert primero["limites"] == {"lat_min": 0, "lat_max": 10, "lon_min": 0, "lon_max": 10}
    assert escenario["escasa"] not in {x["sitio_id"] for x in cuerpo["resultados"]}


def test_stability_and_the_similarity_range_come_with_each_cell(client, escenario) -> None:
    cuerpo = client.get(
        "/api/analogia/celdas-similares",
        params={"sitio_id": escenario["origen"], "limite": 1},
    ).json()
    assert len(cuerpo["resultados"]) == 1
    mejor = cuerpo["resultados"][0]
    assert mejor["estabilidad"] == 1.0  # la celda idéntica gana con cualquier peso
    assert mejor["similitud_min"] <= mejor["similitud"] <= mejor["similitud_max"]


def test_a_terrestrial_point_resolves_to_its_cell(client, engine, escenario) -> None:
    with Session(engine) as s:
        _celda(s, "Tierra", "T_N40_E010", 40, 10, _valores_de(s, "Desierto de Atacama (Yungay)"))
    r = client.get("/api/analogia/celdas-similares", params={"lat": 45.0, "lng": 15.0})
    assert r.status_code == 200
    assert r.json()["origen"]["codigo"] == "T_N40_E010"
    assert r.json()["resultados"][0]["codigo"] == "M_N00_E000"


@pytest.mark.parametrize(
    ("params", "estado", "texto"),
    [
        ({"sitio_id": 99999}, 404, "No existe"),
        ({"lat": -33.0, "lng": 100.0}, 404, "no está en la base"),
        ({}, 400, "sitio_id"),
        ({"sitio_id": 1, "destino": "venus"}, 422, None),
        ({"lat": 91.0, "lng": 0.0}, 422, None),
        ({"sitio_id": 1, "limite": 0}, 422, None),
    ],
)
def test_invalid_requests_are_rejected_with_a_clear_status(
    client, escenario, params, estado, texto
) -> None:
    r = client.get("/api/analogia/celdas-similares", params=params)
    assert r.status_code == estado
    if texto:
        assert texto in r.json()["error"]["message"]


def test_the_origin_must_be_terrestrial_and_have_measurements(client, engine, escenario) -> None:
    r = client.get("/api/analogia/celdas-similares", params={"sitio_id": escenario["igual"]})
    assert (r.status_code, "Tierra" in r.json()["error"]["message"]) == (400, True)

    with Session(engine) as s:
        vacia = _celda(s, "Tierra", "T_N50_E010", 50, 10, {})
    r = client.get("/api/analogia/celdas-similares", params={"sitio_id": vacia})
    assert (r.status_code, "mediciones" in r.json()["error"]["message"]) == (422, True)


def test_ranking_lists_only_reference_sites_of_the_earth_and_exposes_the_cell(
    client, engine, escenario
) -> None:
    antes = client.get("/api/analogia/ranking", params={"destino": "marte"}).json()
    with Session(engine) as s:
        _celda(s, "Tierra", "T_N40_E010", 40, 10, _valores_de(s, "Desierto de Atacama (Yungay)"))
    despues = client.get("/api/analogia/ranking", params={"destino": "marte"}).json()
    assert len(despues) == len(antes)  # una celda terrestre no entra como sitio del ranking
    assert all(f["sitio_tierra"] != "Celda T_N40_E010" for f in despues)

    atacama = next(f for f in despues if f["sitio_tierra"] == "Desierto de Atacama (Yungay)")
    assert atacama["codigo_destino"] == "M_N00_E000"  # la celda idéntica es su mejor destino
    assert atacama["limites_destino"]["lat_max"] == 10
    assert atacama["similitud"] == 1.0
