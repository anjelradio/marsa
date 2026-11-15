"""Pruebas del endpoint de clima de la Tierra (NASA POWER simulado)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.cuerpo_celeste.infrastructure import earth_climate

FAKE = {
    "TS": {"ANN": 17.07},
    "PS": {"ANN": 88.4},
    "WS10M": {"ANN": 3.5},
    "CLOUD_AMT": {"ANN": 20.57},
    "AOD_55": {"ANN": 0.04},
}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_earth_climate_converts_units(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(earth_climate, "_fetch_power", lambda lat, lon: FAKE)
    response = client.get("/api/cuerpo-celeste/tierra/clima", params={"lat": -24.1, "lon": -69.9})
    assert response.status_code == 200
    body = response.json()
    assert body["coordinates"] == {"latitude": -24.1, "longitude": -69.9}
    assert body["values"]["surface_temperature_k"] == pytest.approx(290.22)
    assert body["values"]["surface_pressure_pa"] == pytest.approx(88400.0)
    assert body["values"]["cloud_cover_pct"] == pytest.approx(20.57)
    assert "NASA POWER" in body["source"]


def test_earth_climate_fill_value_is_404(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        earth_climate,
        "_fetch_power",
        lambda lat, lon: {**FAKE, "AOD_55": {"ANN": -999.0}},
    )
    response = client.get("/api/cuerpo-celeste/tierra/clima", params={"lat": 0, "lon": 0})
    assert response.status_code == 404


def test_earth_climate_upstream_failure_is_502(client: TestClient, monkeypatch) -> None:
    import httpx

    def boom(lat, lon):
        raise httpx.ConnectError("sin red")

    monkeypatch.setattr(earth_climate, "_fetch_power", boom)
    response = client.get("/api/cuerpo-celeste/tierra/clima", params={"lat": 0, "lon": 0})
    assert response.status_code == 502


def test_earth_climate_validates_coordinates(client: TestClient) -> None:
    response = client.get("/api/cuerpo-celeste/tierra/clima", params={"lat": 95, "lon": 0})
    assert response.status_code == 422
