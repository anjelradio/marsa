"""Validaciones del esquema v2: se valida primero y, si el dato no es válido, se lanza una excepción."""

from datetime import date

import pytest

from app.modules.analogia.domain.entities.analogia import Analogia
from app.modules.analogia.domain.exceptions import InvalidAnalogiaDataException
from app.modules.caracteristica.domain.entities.caracteristica import Caracteristica
from app.modules.caracteristica.domain.exceptions import (
    InvalidCaracteristicaDataException,
)
from app.modules.composicion_celda.domain.entities.composicion_celda import (
    ComposicionCelda,
)
from app.modules.composicion_celda.domain.exceptions import (
    InvalidComposicionCeldaDataException,
)
from app.modules.corrida_analisis.domain.entities.corrida_analisis import CorridaAnalisis
from app.modules.corrida_analisis.domain.exceptions import (
    InvalidCorridaAnalisisDataException,
)
from app.modules.cuerpo_celeste.domain.entities.cuerpo_celeste import CuerpoCeleste
from app.modules.cuerpo_celeste.domain.exceptions import (
    InvalidCuerpoCelesteDataException,
)
from app.modules.medicion.domain.entities.medicion import Medicion
from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.modules.sitio.domain.entities.sitio import Sitio
from app.modules.sitio.domain.exceptions import InvalidSitioDataException

MEDICION = dict(sitio_id=1, caracteristica_id=1, dataset_id=1)


# ── Medición: rango físico, incertidumbre, muestras y periodo ──────────────────────────


def test_medicion_within_physical_range_is_accepted() -> None:
    m = Medicion.create(valor=292.1, rango_fisico=(0.0, 500.0), **MEDICION)
    assert m.valor == 292.1


@pytest.mark.parametrize("valor", [-1.0, 501.0, float("nan"), float("inf")])
def test_medicion_outside_physical_range_raises(valor: float) -> None:
    with pytest.raises(InvalidMedicionDataException):
        Medicion.create(valor=valor, rango_fisico=(0.0, 500.0), **MEDICION)


def test_medicion_without_physical_range_still_rejects_non_finite() -> None:
    with pytest.raises(InvalidMedicionDataException):
        Medicion.create(valor=float("nan"), **MEDICION)
    # sin rango físico, cualquier número finito es válido
    assert Medicion.create(valor=-8000.0, **MEDICION).valor == -8000.0


def test_medicion_open_ended_physical_range() -> None:
    assert Medicion.create(valor=0.0, rango_fisico=(0.0, None), **MEDICION).valor == 0.0
    with pytest.raises(InvalidMedicionDataException):
        Medicion.create(valor=-0.1, rango_fisico=(0.0, None), **MEDICION)


def test_medicion_metadata_is_validated() -> None:
    ok = Medicion.create(
        valor=1.0,
        incertidumbre=0.5,
        n_muestras=12,
        periodo_inicio=date(2000, 1, 1),
        periodo_fin=date(2024, 12, 31),
        **MEDICION,
    )
    assert (ok.incertidumbre, ok.n_muestras) == (0.5, 12)
    for extra in (
        {"incertidumbre": -0.1},
        {"n_muestras": 0},
        {"periodo_inicio": date(2025, 1, 1), "periodo_fin": date(2024, 1, 1)},
    ):
        with pytest.raises(InvalidMedicionDataException):
            Medicion.create(valor=1.0, **extra, **MEDICION)


# ── Característica: grupo y rango físico ───────────────────────────────────────────────


def test_caracteristica_group_and_physical_range() -> None:
    c = Caracteristica.create(
        nombre="Elevación",
        rango=30000.0,
        peso=0.4,
        grupo="terreno",
        valor_min=-12000.0,
        valor_max=22000.0,
    )
    assert (c.grupo, c.valor_min, c.valor_max) == ("terreno", -12000.0, 22000.0)
    assert Caracteristica.create(nombre="X", rango=1.0, peso=1.0).grupo == "fisico"
    with pytest.raises(InvalidCaracteristicaDataException):
        Caracteristica.create(nombre="X", rango=1.0, peso=0.5, grupo="mineral")
    with pytest.raises(InvalidCaracteristicaDataException):
        Caracteristica.create(nombre="X", rango=1.0, peso=0.5, valor_min=5.0, valor_max=5.0)


# ── Sitio: referencia o celda ──────────────────────────────────────────────────────────

LIMITES = dict(lat_min=-30.0, lat_max=-20.0, lon_min=-70.0, lon_max=-60.0)


def test_sitio_cell_requires_code_and_bounds() -> None:
    celda = Sitio.create(
        cuerpo_id=1, nombre="Celda S30 W070", clase="celda", codigo="T_S30_W070", **LIMITES
    )
    assert celda.codigo == "T_S30_W070"
    with pytest.raises(InvalidSitioDataException):
        Sitio.create(cuerpo_id=1, nombre="Sin código", clase="celda", **LIMITES)
    with pytest.raises(InvalidSitioDataException):
        Sitio.create(cuerpo_id=1, nombre="Sin límites", clase="celda", codigo="T_X")


@pytest.mark.parametrize(
    "cambio",
    [
        dict(lat_min=-95.0),
        dict(lon_max=190.0),
        dict(lat_min=-20.0, lat_max=-30.0),
        dict(lon_min=-60.0, lon_max=-70.0),
    ],
)
def test_sitio_invalid_bounds_raise(cambio: dict) -> None:
    with pytest.raises(InvalidSitioDataException):
        Sitio.create(
            cuerpo_id=1, nombre="Mala", clase="celda", codigo="T_X", **{**LIMITES, **cambio}
        )


def test_sitio_reference_is_the_default_and_class_is_closed() -> None:
    assert Sitio.create(cuerpo_id=1, nombre="Atacama").clase == "referencia"
    with pytest.raises(InvalidSitioDataException):
        Sitio.create(cuerpo_id=1, nombre="Atacama", clase="region")


# ── Cuerpo, composición, corrida y analogía ────────────────────────────────────────────


def test_cuerpo_radius_must_be_positive() -> None:
    assert CuerpoCeleste.create(nombre="Luna", radio_km=1737.4).radio_km == 1737.4
    with pytest.raises(InvalidCuerpoCelesteDataException):
        CuerpoCeleste.create(nombre="Luna", radio_km=0)


def test_composicion_celda_validates_type_and_percentage() -> None:
    ok = ComposicionCelda.create(
        sitio_id=1, dataset_id=1, tipo="mineral", nombre="Olivino", porcentaje=12.5
    )
    assert ok.porcentaje == 12.5
    for malo in (
        dict(tipo="roca", nombre="X", porcentaje=10.0),
        dict(tipo="mineral", nombre="X", porcentaje=100.1),
        dict(tipo="mineral", nombre="X", porcentaje=-1.0),
        dict(tipo="mineral", nombre="  ", porcentaje=10.0),
    ):
        with pytest.raises(InvalidComposicionCeldaDataException):
            ComposicionCelda.create(sitio_id=1, dataset_id=1, **malo)


def test_corrida_requires_version_and_method() -> None:
    assert CorridaAnalisis.create(version="v2", metodo="grupos-v1").version == "v2"
    with pytest.raises(InvalidCorridaAnalisisDataException):
        CorridaAnalisis.create(version=" ", metodo="grupos-v1")


def test_analogia_scores_stay_between_zero_and_one() -> None:
    a = Analogia.create(
        sitio_tierra_id=1,
        sitio_destino_id=2,
        corrida_id=3,
        similitud=0.8,
        sim_fisica=0.9,
        sim_terreno=0.7,
        sim_geologica=None,
        estabilidad=0.95,
    )
    # el grupo sin datos queda vacío, no en cero
    assert (a.corrida_id, a.sim_geologica) == (3, None)
    for campo in ("sim_fisica", "sim_terreno", "sim_geologica", "estabilidad"):
        with pytest.raises(InvalidAnalogiaDataException):
            Analogia.create(sitio_tierra_id=1, sitio_destino_id=2, **{campo: 1.01})
    with pytest.raises(InvalidAnalogiaDataException):
        Analogia.create(sitio_tierra_id=1, sitio_destino_id=2, corrida_id=0)
