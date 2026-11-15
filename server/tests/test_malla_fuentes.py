"""Malla de 10°, estadística y fuentes de datos, todo sin red."""

import sys
from array import array
from datetime import date
from types import SimpleNamespace

import httpx
import pytest

from app.modules.sitio.domain.services.malla import (
    Celda,
    celda_de,
    generar_malla,
    puntos_muestreo,
)
from app.shared.domain.estadistica import resumir
from app.shared.infrastructure.external.malla import gebco as gebco_mod
from app.shared.infrastructure.external.malla.descargas import descargar_si_falta
from app.shared.infrastructure.external.malla.diviner import DivinerCentral
from app.shared.infrastructure.external.malla.errores import (
    FuenteNoDisponible,
    FuenteSinDatos,
)
from app.shared.infrastructure.external.malla.gebco import GebcoOpenTopoData
from app.shared.infrastructure.external.malla.http import http_json
from app.shared.infrastructure.external.malla.power_regional import (
    PowerRegional,
    interpretar,
)
from app.shared.infrastructure.external.malla.raster16 import Raster16, RasterElevacion
from app.shared.infrastructure.external.malla.rejilla_marte import RejillaMarte

# ── malla ─────────────────────────────────────────────────────────────────────────────


def test_grid_has_648_cells_with_unique_codes() -> None:
    celdas = generar_malla("Tierra")
    assert len(celdas) == 648
    assert len({c.codigo for c in celdas}) == 648
    assert {c.prefijo for c in generar_malla("Marte")} == {"M"}
    assert {c.prefijo for c in generar_malla("Luna")} == {"L"}


def test_cell_code_uses_south_and_west_edges() -> None:
    celda = Celda("T", -30, -20, -70, -60)
    assert celda.codigo == "T_S30_W070"
    assert Celda("M", 0, 10, 0, 10).codigo == "M_N00_E000"
    assert (celda.centro_lat, celda.centro_lon) == (-25, -65)
    anillo = celda.poligono()["coordinates"][0]
    assert anillo[0] == anillo[-1] and len(anillo) == 5


def test_grid_rejects_unknown_body_and_bad_step() -> None:
    with pytest.raises(ValueError, match="Venus"):
        generar_malla("Venus")
    with pytest.raises(ValueError, match="paso"):
        generar_malla("Tierra", paso=7)


def test_cell_of_a_point_and_its_edges() -> None:
    assert celda_de("Tierra", -25.0, -65.0).codigo == "T_S30_W070"
    assert celda_de("Tierra", 0.0, 0.0).codigo == "T_N00_E000"  # el borde va a la celda norte-este
    assert celda_de("Tierra", 90.0, 180.0).codigo == "T_N80_E170"  # polo y antimeridiano
    with pytest.raises(ValueError):
        celda_de("Tierra", 91.0, 0.0)


def test_sampling_points_are_inside_and_never_on_an_edge() -> None:
    celda = Celda("T", 0, 10, 0, 10)
    puntos = list(puntos_muestreo(celda, 5))
    assert len(puntos) == 25
    assert all(0 < lat < 10 and 0 < lon < 10 for lat, lon in puntos)
    assert list(puntos_muestreo(celda, 1)) == [(5.0, 5.0)]
    with pytest.raises(ValueError):
        list(puntos_muestreo(celda, 0))


# ── estadística ───────────────────────────────────────────────────────────────────────


def test_resumir_ignores_missing_and_non_finite_values() -> None:
    media, desviacion, n = resumir([1.0, 3.0, None, float("nan"), float("inf")])
    assert (media, desviacion, n) == (2.0, 1.0, 2)
    assert resumir([None, float("nan")]) is None
    assert resumir([]) is None


# ── NASA POWER ────────────────────────────────────────────────────────────────────────


def _power(valores: list[float], parametro: str) -> dict:
    return {
        "features": [
            {"properties": {"parameter": {parametro: {"ANN": v}}}} for v in valores
        ]
    }


def test_power_interpret_skips_fill_values() -> None:
    media, desviacion, n = interpretar(_power([10.0, 20.0, -999.0], "TS"), "TS")
    assert (media, desviacion, n) == (15.0, 5.0, 2)
    with pytest.raises(FuenteSinDatos):
        interpretar(_power([-999.0], "TS"), "TS")


def test_power_regional_reads_three_parameters_and_converts_to_kelvin() -> None:
    pedidas = []

    def obtener(url, params):
        pedidas.append(params["parameters"])
        return _power([10.0, 20.0], params["parameters"])

    lecturas = PowerRegional(obtener).leer(Celda("T", 0, 10, 0, 10))
    assert pedidas == ["TS", "CLOUD_AMT", "AOD_55"]
    ts = lecturas["Temperatura Superficial"]
    assert ts.valor == pytest.approx(15.0 + 273.15)
    assert ts.incertidumbre == pytest.approx(5.0)  # la desviación no cambia con la escala
    assert ts.n_muestras == 2
    assert lecturas["Nubosidad"].valor == 15.0


# ── GEBCO / OpenTopoData ──────────────────────────────────────────────────────────────


def _gebco_falso(elevacion_por_celda: dict[int, float]):
    """Responde con una elevación constante según el orden de la celda en la petición."""
    peticiones: list[int] = []

    def obtener(url, params):
        puntos = params["locations"].split("|")
        peticiones.append(len(puntos))
        resultados = []
        for i, _ in enumerate(puntos):
            celda = i // 25
            resultados.append({"elevation": elevacion_por_celda.get(celda, 100.0)})
        return {"results": resultados}

    return obtener, peticiones


def test_gebco_groups_four_cells_per_request_and_pauses_between_requests() -> None:
    obtener, peticiones = _gebco_falso({})
    pausas: list[float] = []
    fuente = GebcoOpenTopoData(obtener, pausas.append)
    celdas = generar_malla("Tierra")[:5]

    fuente.precargar(celdas)

    assert peticiones == [100, 25]
    assert pausas == [gebco_mod.PAUSA_S]  # una sola pausa, entre las dos peticiones
    fuente.leer(celdas[0])
    assert peticiones == [100, 25]  # ya estaba en caché


def test_gebco_reads_mean_and_regional_relief() -> None:
    def obtener(url, params):
        n = len(params["locations"].split("|"))
        return {"results": [{"elevation": 0.0 if i % 2 else 100.0} for i in range(n)]}

    lecturas = GebcoOpenTopoData(obtener, lambda _s: None).leer(Celda("T", 0, 10, 0, 10))
    assert lecturas["Elevación"].valor == pytest.approx(52.0)  # 13 de 25 puntos valen 100
    assert lecturas["Relieve Regional"].valor == lecturas["Elevación"].incertidumbre
    assert lecturas["Elevación"].n_muestras == 25


def test_gebco_discards_ocean_cells_but_keeps_land() -> None:
    obtener, _ = _gebco_falso({0: -3000.0, 1: 250.0})
    fuente = GebcoOpenTopoData(obtener, lambda _s: None)
    oceano, tierra = generar_malla("Tierra")[:2]
    fuente.precargar([oceano, tierra])
    assert fuente.descartar(oceano) == "océano"
    assert fuente.descartar(tierra) is None


def test_gebco_fails_when_the_answer_is_incomplete_or_mostly_empty() -> None:
    celda = Celda("T", 0, 10, 0, 10)
    corta = GebcoOpenTopoData(lambda u, p: {"results": [{"elevation": 1.0}]}, lambda _s: None)
    with pytest.raises(FuenteSinDatos, match="puntos"):
        corta.leer(celda)

    vacia = GebcoOpenTopoData(
        lambda u, p: {"results": [{"elevation": None}] * 25}, lambda _s: None
    )
    with pytest.raises(FuenteSinDatos, match="válidos"):
        vacia.descartar(celda)


# ── Marte: rejilla local ──────────────────────────────────────────────────────────────


def _punto(temperatura: float, polvo: float):
    return SimpleNamespace(surface_temperature_k=temperatura, dust_optical_depth=polvo)


def test_mars_grid_averages_the_points_inside_the_cell() -> None:
    rejilla = RejillaMarte(
        {(3.0, 5.0): _punto(200.0, 0.4), (6.0, 8.0): _punto(220.0, 0.6), (50.0, 5.0): _punto(1.0, 1.0)}
    )
    lecturas = rejilla.leer(Celda("M", 0, 10, 0, 10))
    temperatura = lecturas["Temperatura Superficial"]
    assert temperatura.valor == pytest.approx(210.0)
    assert temperatura.incertidumbre == pytest.approx(10.0)
    assert temperatura.n_muestras == 2
    assert lecturas["Profundidad Óptica de Polvo"].valor == pytest.approx(0.5)


def test_mars_grid_uses_the_nearest_point_for_an_empty_cell() -> None:
    rejilla = RejillaMarte({(50.0, 5.0): _punto(180.0, 0.3)})
    lectura = rejilla.leer(Celda("M", 0, 10, 0, 10))["Temperatura Superficial"]
    assert (lectura.valor, lectura.incertidumbre, lectura.n_muestras) == (180.0, None, 1)
    with pytest.raises(FuenteSinDatos):
        RejillaMarte({}).leer(Celda("M", 0, 10, 0, 10))


# ── rasters de 16 bits ────────────────────────────────────────────────────────────────


def _escribir_raster(ruta, rellenos: dict[tuple[int, int, int, int], int], *, big_endian=False):
    """Raster de 1 píxel por grado (180 filas x 360 columnas). ``rellenos`` da
    (fila0, fila1, col0, col1) -> valor."""
    datos = array("h", [0] * (180 * 360))
    for (f0, f1, c0, c1), valor in rellenos.items():
        for fila in range(f0, f1):
            for col in range(c0, c1):
                datos[fila * 360 + col] = valor
    if big_endian != (sys.byteorder == "big"):
        datos.byteswap()
    ruta.write_bytes(datos.tobytes())
    return ruta


@pytest.mark.parametrize("big_endian", [False, True])
def test_raster_mean_and_deviation_of_a_cell(tmp_path, big_endian: bool) -> None:
    ruta = _escribir_raster(
        tmp_path / "r.img",
        {(80, 90, 0, 5): 100, (80, 90, 5, 10): 200},  # la celda 0-10°N, 0-10°E
        big_endian=big_endian,
    )
    raster = Raster16(ruta, ppd=1, big_endian=big_endian, escala=0.5)
    media, desviacion, n = raster.estadisticas(Celda("L", 0, 10, 0, 10))
    assert (media, desviacion, n) == (pytest.approx(75.0), pytest.approx(25.0), 100)


def test_raster_reads_cells_with_negative_longitude(tmp_path) -> None:
    ruta = _escribir_raster(tmp_path / "r.img", {(80, 90, 350, 360): 40})
    raster = Raster16(ruta, ppd=1)
    media, desviacion, n = raster.estadisticas(Celda("L", 0, 10, -10, 0))
    assert (media, desviacion, n) == (40.0, 0.0, 100)


def test_raster_rejects_a_missing_or_wrongly_sized_file(tmp_path) -> None:
    with pytest.raises(FuenteNoDisponible, match="Falta"):
        Raster16(tmp_path / "no-existe.img", ppd=1).estadisticas(Celda("L", 0, 10, 0, 10))
    corto = tmp_path / "corto.img"
    corto.write_bytes(b"\x00\x00" * 10)
    with pytest.raises(FuenteNoDisponible, match="esperaban"):
        Raster16(corto, ppd=1).estadisticas(Celda("L", 0, 10, 0, 10))
    largo = tmp_path / "largo.img"
    largo.write_bytes(b"\x00\x00" * (180 * 360 + 1))
    with pytest.raises(FuenteNoDisponible, match="más grande"):
        Raster16(largo, ppd=1).estadisticas(Celda("L", 0, 10, 0, 10))


def test_raster_source_gives_elevation_and_relief(tmp_path) -> None:
    ruta = _escribir_raster(tmp_path / "r.img", {(80, 90, 0, 5): 100, (80, 90, 5, 10): 200})
    fuente = RasterElevacion(Raster16(ruta, ppd=1), "NASA MGS MOLA")
    lecturas = fuente.leer(Celda("M", 0, 10, 0, 10))
    assert fuente.dataset == "NASA MGS MOLA"
    assert lecturas["Elevación"].valor == pytest.approx(150.0)
    assert lecturas["Relieve Regional"].valor == pytest.approx(50.0)


# ── Diviner ───────────────────────────────────────────────────────────────────────────


def test_diviner_reads_the_central_bin_with_its_period() -> None:
    vistos = []

    def obtener(lat, lon):
        vistos.append((lat, lon))
        return {"mean_k": 250.0}

    lectura = DivinerCentral(obtener).leer(Celda("L", 0, 10, 0, 10))["Temperatura Superficial"]
    assert vistos == [(5.0, 5.0)]
    assert (lectura.valor, lectura.incertidumbre, lectura.n_muestras) == (250.0, None, 1)
    assert lectura.periodo_inicio == date(2009, 7, 5)
    assert lectura.periodo_fin == date(2015, 4, 1)


def test_diviner_maps_failures_to_source_errors() -> None:
    def sin_datos(lat, lon):
        raise ValueError("pocas observaciones")

    def sin_red(lat, lon):
        raise OSError("sin conexión")

    celda = Celda("L", 0, 10, 0, 10)
    with pytest.raises(FuenteSinDatos):
        DivinerCentral(sin_datos).leer(celda)
    with pytest.raises(FuenteNoDisponible):
        DivinerCentral(sin_red).leer(celda)


# ── HTTP con reintentos ───────────────────────────────────────────────────────────────


def _cliente(respuestas: list[httpx.Response]) -> tuple[httpx.Client, list[httpx.Request]]:
    recibidas: list[httpx.Request] = []
    pendientes = iter(respuestas)

    def manejar(request: httpx.Request) -> httpx.Response:
        recibidas.append(request)
        return next(pendientes)

    return httpx.Client(transport=httpx.MockTransport(manejar)), recibidas


def test_http_json_returns_the_body() -> None:
    cliente, recibidas = _cliente([httpx.Response(200, json={"ok": 1})])
    assert http_json("https://x.test/a", {"q": "1"}, cliente=cliente, dormir=lambda _s: None) == {
        "ok": 1
    }
    assert recibidas[0].url.params["q"] == "1"


def test_http_json_retries_server_errors_and_rate_limits() -> None:
    cliente, recibidas = _cliente(
        [httpx.Response(429), httpx.Response(503), httpx.Response(200, json={"ok": 2})]
    )
    pausas: list[float] = []
    assert http_json("https://x.test/a", {}, cliente=cliente, dormir=pausas.append) == {"ok": 2}
    assert len(recibidas) == 3 and len(pausas) == 2


def test_http_json_gives_up_after_three_attempts() -> None:
    cliente, recibidas = _cliente([httpx.Response(500)] * 3)
    with pytest.raises(FuenteNoDisponible, match="3 intentos"):
        http_json("https://x.test/a", {}, cliente=cliente, dormir=lambda _s: None)
    assert len(recibidas) == 3


def test_http_json_does_not_retry_a_client_error_or_bad_json() -> None:
    cliente, recibidas = _cliente([httpx.Response(404)])
    with pytest.raises(FuenteNoDisponible, match="404"):
        http_json("https://x.test/a", {}, cliente=cliente, dormir=lambda _s: None)
    assert len(recibidas) == 1

    cliente, _ = _cliente([httpx.Response(200, content=b"<html>")])
    with pytest.raises(FuenteNoDisponible, match="JSON"):
        http_json("https://x.test/a", {}, cliente=cliente, dormir=lambda _s: None)


# ── descargas ─────────────────────────────────────────────────────────────────────────


def _cliente_descarga(contenido: bytes, estado: int = 200):
    peticiones: list[str] = []

    def manejar(request: httpx.Request) -> httpx.Response:
        peticiones.append(str(request.url))
        return httpx.Response(estado, content=contenido)

    return httpx.Client(transport=httpx.MockTransport(manejar)), peticiones


def test_download_writes_the_file_when_the_size_matches(tmp_path) -> None:
    cliente, _ = _cliente_descarga(b"x" * 10)
    destino = tmp_path / "datos" / "a.img"
    avances: list[tuple[int, int]] = []
    assert descargar_si_falta("https://x.test/a.img", destino, 10, cliente=cliente, progreso=lambda a, b: avances.append((a, b))) == destino
    assert destino.read_bytes() == b"x" * 10
    assert avances[-1] == (10, 10)
    assert not list(destino.parent.glob("*.part"))


def test_download_skips_a_file_that_is_already_complete(tmp_path) -> None:
    destino = tmp_path / "a.img"
    destino.write_bytes(b"y" * 10)
    cliente, peticiones = _cliente_descarga(b"x" * 10)
    descargar_si_falta("https://x.test/a.img", destino, 10, cliente=cliente)
    assert peticiones == [] and destino.read_bytes() == b"y" * 10


def test_download_replaces_a_corrupt_file(tmp_path) -> None:
    destino = tmp_path / "a.img"
    destino.write_bytes(b"corto")
    cliente, peticiones = _cliente_descarga(b"x" * 10)
    descargar_si_falta("https://x.test/a.img", destino, 10, cliente=cliente)
    assert len(peticiones) == 1 and destino.read_bytes() == b"x" * 10


def test_download_never_leaves_a_partial_file(tmp_path) -> None:
    destino = tmp_path / "a.img"
    cliente, _ = _cliente_descarga(b"x" * 7)
    with pytest.raises(FuenteNoDisponible, match="esperaban 10"):
        descargar_si_falta("https://x.test/a.img", destino, 10, cliente=cliente)
    assert not destino.exists() and not list(tmp_path.glob("*.part"))

    cliente, _ = _cliente_descarga(b"", estado=404)
    with pytest.raises(FuenteNoDisponible, match="404"):
        descargar_si_falta("https://x.test/a.img", destino, 10, cliente=cliente)
    assert not destino.exists() and not list(tmp_path.glob("*.part"))
