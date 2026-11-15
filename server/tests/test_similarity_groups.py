"""La puntuación única combina grupos y reparte el peso de los grupos sin datos."""

import pytest

from app.modules.analogia.domain.services.similarity import (
    METODO,
    PESOS_GRUPO,
    CaracteristicaSpec,
    calcular_similitud,
)

FISICA = CaracteristicaSpec(1, "Temperatura", "K", 100.0, 1.0, "fisico")
TERRENO = CaracteristicaSpec(2, "Elevación", "m", 100.0, 1.0, "terreno")


def test_group_weights_are_fifty_and_twenty() -> None:
    assert PESOS_GRUPO == {"fisico": 0.5, "terreno": 0.2}
    assert METODO == "grupos-v1"


def test_both_groups_with_data_combine_with_group_weights() -> None:
    # física: 1 - 10/100 = 0.9; terreno: 1 - 50/100 = 0.5
    r = calcular_similitud([FISICA, TERRENO], {1: 50.0, 2: 0.0}, {1: 60.0, 2: 50.0})
    assert r.por_grupo == {"fisico": 0.9, "terreno": 0.5}
    assert r.similitud == pytest.approx((0.5 * 0.9 + 0.2 * 0.5) / 0.7, abs=1e-4)
    assert r.cobertura == 1.0


def test_group_without_data_hands_its_weight_to_the_others() -> None:
    # el terreno no tiene dato en el destino: la puntuación es solo la física
    r = calcular_similitud([FISICA, TERRENO], {1: 50.0, 2: 0.0}, {1: 60.0})
    assert r.por_grupo == {"fisico": 0.9}
    assert r.similitud == pytest.approx(0.9)
    # y la cobertura baja: solo se usó el 50 % de los 70 puntos esperados
    assert r.cobertura == pytest.approx(0.5 / 0.7, abs=1e-4)


def test_partial_coverage_inside_a_group_weighs_by_feature() -> None:
    extra = CaracteristicaSpec(3, "Hielo", "%", 100.0, 1.0, "fisico")
    # física: solo Temperatura con dato (0.9), Hielo sin dato → media del grupo = 0.9
    r = calcular_similitud([FISICA, extra], {1: 50.0}, {1: 60.0})
    assert r.por_grupo["fisico"] == 0.9
    assert r.cobertura == pytest.approx(0.5, abs=1e-4)  # la mitad del peso del grupo


def test_group_weights_only_matter_between_groups() -> None:
    # con un solo grupo presente da igual cuánto pese: la puntuación es la del grupo
    solo_terreno = calcular_similitud([TERRENO], {2: 0.0}, {2: 50.0})
    assert solo_terreno.similitud == 0.5
    assert solo_terreno.cobertura == 1.0


def test_unknown_group_does_not_count() -> None:
    raro = CaracteristicaSpec(9, "Raro", None, 100.0, 1.0, "otro")
    r = calcular_similitud([FISICA, raro], {1: 50.0, 9: 0.0}, {1: 60.0, 9: 100.0})
    assert r.similitud == pytest.approx(0.9)  # el grupo desconocido pesa 0
    assert r.por_grupo["otro"] == 0.0


def test_no_common_data_scores_zero() -> None:
    r = calcular_similitud([FISICA, TERRENO], {1: 1.0}, {2: 1.0})
    assert (r.similitud, r.cobertura, r.por_grupo) == (0.0, 0.0, {})
