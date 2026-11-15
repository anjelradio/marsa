"""La ingesta de la malla con fuentes falsas: validar primero, no inventar datos, ser idempotente."""

from datetime import date

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

import app.shared.infrastructure.db.models  # noqa: F401
from app.modules.caracteristica.domain.exceptions import CaracteristicaNotFoundException
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.corrida_analisis.infrastructure.persistence.models.corrida_analisis_model import (
    CorridaAnalisisModel,
)
from app.modules.cuerpo_celeste.domain.exceptions import (
    CuerpoCelesteNotFoundException,
    InvalidCuerpoCelesteDataException,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.domain.exceptions import DatasetNotFoundException
from app.modules.medicion.infrastructure.persistence.models.medicion_model import MedicionModel
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.application.ingesta_malla import IngestaMalla
from app.shared.infrastructure.db.seed import seed_initial_data
from app.shared.infrastructure.external.malla.errores import FuenteSinDatos
from app.shared.infrastructure.external.malla.lectura import Lectura

DATASET = "NASA POWER (MERRA-2)"


class Falsa:
    """Fuente de pruebas: da siempre las mismas lecturas y anota qué se le pidió."""

    def __init__(self, lecturas, dataset=DATASET, descartar=None, fallo=None):
        self.dataset = dataset
        self.lecturas = lecturas
        self.variables = tuple(lecturas)
        self._descartar = descartar
        self._fallo = fallo
        self.leidas: list[str] = []
        self.precargadas: list[int] = []

    def precargar(self, celdas):
        self.precargadas.append(len(celdas))

    def descartar(self, celda):
        return self._descartar(celda) if self._descartar else None

    def leer(self, celda):
        self.leidas.append(celda.codigo)
        if self._fallo and self._fallo(celda):
            raise FuenteSinDatos("sin datos de prueba")
        return self.lecturas


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        seed_initial_data(s)
        yield s


def _contar(session: Session, modelo, *condiciones) -> int:
    consulta = select(func.count()).select_from(modelo)
    for condicion in condiciones:
        consulta = consulta.where(condicion)
    return session.exec(consulta).one()


def _celdas(session: Session) -> list[SitioModel]:
    return session.exec(select(SitioModel).where(SitioModel.clase == "celda")).all()


def _temperatura(valor: float = 250.0) -> dict[str, Lectura]:
    return {
        "Temperatura Superficial": Lectura(valor, 4.0, 12, date(2000, 1, 1), date(2024, 12, 31))
    }


def test_cells_are_saved_with_uncertainty_sample_size_and_period(session: Session) -> None:
    fuente = Falsa(_temperatura())
    informe = IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=3)

    celdas = _celdas(session)
    assert [c.codigo for c in celdas] == ["M_S90_W180", "M_S90_W170", "M_S90_W160"]
    assert {c.clase for c in celdas} == {"celda"}
    assert celdas[0].lat_min == -90 and celdas[0].lon_max == -170
    assert celdas[0].geom["type"] == "Polygon"
    medicion = session.exec(
        select(MedicionModel).where(MedicionModel.sitio_id == celdas[0].id)
    ).one()
    assert (medicion.valor, medicion.incertidumbre, medicion.n_muestras) == (250.0, 4.0, 12)
    assert (medicion.periodo_inicio, medicion.periodo_fin) == (date(2000, 1, 1), date(2024, 12, 31))
    assert 0 <= medicion.valor_normalizado <= 1
    assert fuente.precargadas == [3]
    assert (informe.celdas_guardadas, informe.mediciones_guardadas, informe.errores) == (
        {"Marte": 3},
        3,
        [],
    )


def test_an_invalid_value_is_reported_and_never_saved(session: Session) -> None:
    fuente = Falsa(
        {
            "Temperatura Superficial": Lectura(9999.0, 1.0, 5),  # fuera del rango físico
            "Nubosidad": Lectura(0.5, 0.1, 5),
        }
    )
    informe = IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=1)

    temperatura = session.exec(
        select(CaracteristicaModel).where(CaracteristicaModel.nombre == "Temperatura Superficial")
    ).one()
    assert _contar(session, MedicionModel, MedicionModel.caracteristica_id == temperatura.id) == 9
    assert informe.mediciones_guardadas == 1  # solo la nubosidad de la celda
    assert [(e.celda, e.variable) for e in informe.errores] == [
        ("M_S90_W180", "Temperatura Superficial")
    ]
    assert "valor" in informe.errores[0].causa
    assert informe.celdas_guardadas == {"Marte": 1}


def test_a_cell_with_no_valid_measurement_is_not_left_empty(session: Session) -> None:
    fuente = Falsa(_temperatura(9999.0))
    informe = IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=2)

    assert _celdas(session) == []
    assert informe.celdas_guardadas == {"Marte": 0}
    assert informe.celdas_sin_datos == {"Marte": 2}
    assert len(informe.errores) == 2


def test_source_errors_are_reported_without_stopping_the_other_cells(session: Session) -> None:
    fuente = Falsa(_temperatura(), fallo=lambda celda: celda.codigo == "M_S90_W180")
    informe = IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=3)

    assert [c.codigo for c in _celdas(session)] == ["M_S90_W170", "M_S90_W160"]
    assert informe.celdas_sin_datos == {"Marte": 1}
    assert informe.errores[0].celda == "M_S90_W180"
    assert informe.errores[0].causa == "sin datos de prueba"


def test_discarded_cells_are_counted_by_reason_and_not_saved(session: Session) -> None:
    fuente = Falsa(_temperatura(), descartar=lambda c: "océano" if c.lon_min < -170 else None)
    informe = IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=3)

    assert [c.codigo for c in _celdas(session)] == ["M_S90_W170", "M_S90_W160"]
    assert informe.celdas_descartadas == {"Marte": {"océano": 1}}
    assert "descartadas (océano: 1)" in informe.resumen()
    assert "M_S90_W180" not in fuente.leidas  # una celda descartada no se lee


def test_running_twice_updates_in_place_without_duplicates(session: Session) -> None:
    plan = {"Marte": [Falsa(_temperatura(250.0))]}
    IngestaMalla(session, plan).ejecutar(["Marte"], limite=3)
    antes = (_contar(session, SitioModel), _contar(session, MedicionModel))

    plan_nuevo = {"Marte": [Falsa(_temperatura(260.0))]}
    IngestaMalla(session, plan_nuevo).ejecutar(["Marte"], limite=3)

    assert (_contar(session, SitioModel), _contar(session, MedicionModel)) == antes
    valores = {
        m.valor
        for m in session.exec(
            select(MedicionModel).where(
                MedicionModel.sitio_id.in_([c.id for c in _celdas(session)])
            )
        ).all()
    }
    assert valores == {260.0}
    assert _contar(session, CorridaAnalisisModel, CorridaAnalisisModel.metodo == "ingesta-malla") == 1


def test_the_run_is_recorded_with_its_summary(session: Session) -> None:
    IngestaMalla(session, {"Marte": [Falsa(_temperatura())]}).ejecutar(["Marte"], limite=2)
    corrida = session.exec(
        select(CorridaAnalisisModel).where(CorridaAnalisisModel.metodo == "ingesta-malla")
    ).one()
    assert corrida.version == "malla-10"
    assert corrida.parametros["celdas_guardadas"] == {"Marte": 2}
    assert corrida.parametros["errores"] == 0


# ── validar primero: nada de red si el catálogo no cuadra ─────────────────────────────


def _sin_tocar_la_red(fuente: Falsa) -> None:
    assert fuente.precargadas == [] and fuente.leidas == []


def test_unknown_characteristic_fails_before_any_source_is_used(session: Session) -> None:
    fuente = Falsa({"Magnetismo": Lectura(1.0)})
    with pytest.raises(CaracteristicaNotFoundException, match="Magnetismo"):
        IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=1)
    _sin_tocar_la_red(fuente)
    assert _celdas(session) == []


def test_unknown_dataset_fails_before_any_source_is_used(session: Session) -> None:
    fuente = Falsa(_temperatura(), dataset="Dataset inventado")
    with pytest.raises(DatasetNotFoundException, match="inventado"):
        IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte"], limite=1)
    _sin_tocar_la_red(fuente)


def test_unknown_body_or_missing_plan_fails_before_any_source_is_used(session: Session) -> None:
    fuente = Falsa(_temperatura())
    with pytest.raises(InvalidCuerpoCelesteDataException, match="Luna"):
        IngestaMalla(session, {"Marte": [fuente]}).ejecutar(["Marte", "Luna"], limite=1)
    _sin_tocar_la_red(fuente)  # Marte iba primero, pero se valida todo antes de empezar

    with pytest.raises(CuerpoCelesteNotFoundException, match="Venus"):
        IngestaMalla(session, {"Venus": [fuente]}).ejecutar(["Venus"], limite=1)
    _sin_tocar_la_red(fuente)


def test_the_real_catalog_covers_every_source_of_the_plans(session: Session, tmp_path) -> None:
    """Los nombres de dataset y característica de las fuentes reales existen en el seed."""
    from app.shared.infrastructure.external.malla.catalogo import construir_planes

    cuerpos = ["Tierra", "Marte", "Luna"]
    ingesta = IngestaMalla(session, construir_planes(tmp_path, cuerpos))
    ingesta._validar_catalogo(cuerpos)  # no lanza
    assert _contar(session, CuerpoCelesteModel) == 3
