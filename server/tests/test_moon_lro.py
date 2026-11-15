"""Pruebas de la lectura de datos lunares reales (LOLA y Diviner), sin red."""

import pytest

from app.modules.cuerpo_celeste.infrastructure import moon_lro as m


def test_ldem_offset_corners_and_wrap() -> None:
    assert m.ldem_offset(90.0, 0.0) == 0
    assert m.ldem_offset(0.0, 0.0) == (1440 * 5760) * 2
    assert m.ldem_offset(0.0, 360.0) == m.ldem_offset(0.0, 0.0)  # 360° equivale a 0°
    assert m.ldem_offset(0.0, -90.0) == m.ldem_offset(0.0, 270.0)  # lon oeste → este
    last = m.ldem_offset(-90.0, 359.99)
    assert last == (2879 * 5760 + 5759) * 2  # no se sale del fichero


def test_decode_ldem_scales_and_keeps_sign() -> None:
    assert m.decode_ldem((200).to_bytes(2, "little", signed=True)) == 100.0
    assert m.decode_ldem((-3830).to_bytes(2, "little", signed=True)) == -1915.0


@pytest.mark.parametrize(
    ("lat", "band", "min_lat"),
    [
        (8.5, "00N10N", 0.0),
        (0.0, "00N10N", 0.0),
        (45.0, "40N50N", 40.0),
        (90.0, "80N90N", 80.0),
        (-5.0, "10S00S", -10.0),
        (-89.9, "90S80S", -90.0),
        (-90.0, "90S80S", -90.0),
    ],
)
def test_gcp_band_names(lat: float, band: str, min_lat: float) -> None:
    assert m.gcp_band(lat) == (band, min_lat)


def test_gcp_offset_matches_record_layout() -> None:
    band, offset, clon, clat = m.gcp_offset(8.5, 31.4)
    assert band == "00N10N"
    assert (clon, clat) == (31.25, 8.75)
    assert offset == (1 + (422 * 20 + 17) * 96) * 113  # cabecera + 422 lon x 20 lat x 96 horas
    band, offset, clon, clat = m.gcp_offset(-89.9, 0.0)
    assert (band, clat) == ("90S80S", -89.75)


def _rows(values: dict[int, float]) -> list[dict[str, float]]:
    return [
        {"clon": 0, "clat": 0, "ltim": (i + 0.5) * 0.25, "tbol": values.get(i, -9999.0)}
        for i in range(96)
    ]


def test_summary_of_a_complete_day() -> None:
    summary = m.summarize_diurnal(_rows({i: 100.0 + i for i in range(96)}))
    assert summary["max_k"] == 195.0
    assert summary["min_k"] == 100.0
    assert summary["mean_k"] == pytest.approx(147.5)
    assert summary["valid_bins"] == 96


def test_missing_hours_are_interpolated_not_averaged_away() -> None:
    # Solo hay dato en las horas calientes: la media simple saldría 300 K,
    # pero al interpolar el resto del ciclo debe bajar claramente.
    hot = {i: 300.0 for i in range(24, 72)}
    hot.update({0: 100.0, 95: 100.0})
    summary = m.summarize_diurnal(_rows(hot))
    assert summary["valid_bins"] == 50
    assert summary["max_k"] == 300.0
    assert 100.0 < summary["mean_k"] < 290.0


def test_too_few_bins_raises() -> None:
    with pytest.raises(ValueError):
        m.summarize_diurnal(_rows({0: 100.0, 1: 101.0}))


def test_parse_ignores_the_header_line() -> None:
    text = "   clon,   clat,   ltim,        t3,        t4,        t5,        t6,        t7,        t8,        t9,      tbol\n"
    text += "-179.75,   0.25,   0.38, -134.4756, -130.4954,  133.1989,  102.8571,  100.9078,   99.5392,  101.1129,  101.2984\n"
    rows = m.parse_gcp_rows(text)
    assert len(rows) == 1
    assert rows[0]["tbol"] == pytest.approx(101.2984)
