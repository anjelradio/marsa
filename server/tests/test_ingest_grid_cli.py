"""El script de ingesta: el plan no usa red y no descarga nada sin --descargar."""

import importlib.util
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[1] / "scripts" / "ingest_grid.py"


@pytest.fixture(scope="module")
def cli():
    spec = importlib.util.spec_from_file_location("ingest_grid", RUTA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_dry_run_prints_the_plan_and_touches_nothing(cli, capsys, tmp_path) -> None:
    assert cli.main(["--dry-run", "--cache", str(tmp_path)]) == 0
    salida = capsys.readouterr().out
    assert "Tierra: 648 celdas" in salida
    assert "162 peticiones" in salida  # 648 celdas, 4 por petición
    assert "ldem_16.img" in salida and "megt90n000eb.img" in salida
    assert list(tmp_path.iterdir()) == []


def test_limit_shrinks_the_planned_requests(cli, capsys, tmp_path) -> None:
    cli.main(["--dry-run", "--cuerpos", "Tierra", "--limite", "8", "--cache", str(tmp_path)])
    salida = capsys.readouterr().out
    assert "Tierra: 8 celdas" in salida and "2 peticiones" in salida
    assert "Marte" not in salida


def test_missing_rasters_stop_the_run_unless_download_is_allowed(cli, capsys, tmp_path) -> None:
    assert cli.main(["--cuerpos", "Luna", "--cache", str(tmp_path)]) == 2
    salida = capsys.readouterr().out
    assert "ldem_16.img" in salida and "pds-geosciences" in salida and "--descargar" in salida
    assert list(tmp_path.iterdir()) == []  # no descargó nada


def test_unknown_body_is_rejected(cli, capsys, tmp_path) -> None:
    assert cli.main(["--dry-run", "--cuerpos", "Venus", "--cache", str(tmp_path)]) == 2
    assert "Venus" in capsys.readouterr().out
