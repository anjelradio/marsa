"""Pruebas unitarias para los endpoints de geología, rocas, minerales y análogos planetarios."""

import pytest
from fastapi.testclient import TestClient


def test_endpoint_comparar_analogo_tierra_marte(client: TestClient) -> None:
    # Coordenadas cerca de Atacama (-24.1, -69.9)
    response = client.get("/api/analogia/comparar-analogo", params={"lat": -24.1, "lng": -69.9, "destino": "marte"})
    assert response.status_code == 200
    data = response.json()
    assert data["cuerpo_origen"] == "Tierra"
    assert data["cuerpo_destino"] == "Marte"
    assert "celda_origen_id" in data
    assert "distribucion_litologica_celda" in data
    assert data["celda_analoga_mas_similar"] is not None
    assert "minerales_detectados" in data["celda_analoga_mas_similar"]
    assert "rocas_principales" in data["celda_analoga_mas_similar"]
    assert len(data["muestras_minerales_relacionadas"]) > 0
    # Chequear muestra de CheMin con abundancias wt%
    sample = data["muestras_minerales_relacionadas"][0]
    assert sample["cuerpo"] == "Marte"
    assert len(sample["minerales"]) > 0
    assert any("Plagioclasa" in m["nombre"] or "Forsterita" in m["nombre"] for m in sample["minerales"])


def test_endpoint_comparar_analogo_tierra_luna(client: TestClient) -> None:
    # Coordenadas de prueba
    response = client.get("/api/analogia/comparar-analogo", params={"lat": 29.16, "lng": -13.43, "destino": "luna"})
    assert response.status_code == 200
    data = response.json()
    assert data["cuerpo_destino"] == "Luna"
    assert data["celda_analoga_mas_similar"] is not None
    assert len(data["muestras_minerales_relacionadas"]) > 0
    sample = data["muestras_minerales_relacionadas"][0]
    assert sample["cuerpo"] == "Luna"


def test_endpoint_geologia_punto_marte(client: TestClient) -> None:
    # Cráter Gale (-4.59, 137.44)
    response = client.get("/api/analogia/geologia/punto", params={"cuerpo": "Marte", "lat": -4.59, "lng": 137.44})
    assert response.status_code == 200
    data = response.json()
    assert data["cuerpo"] == "Marte"
    assert "Cráter Gale" in data["region_nombre"]
    assert len(data["rocas_predominantes"]) > 0
    assert len(data["minerales_principales"]) > 0
    assert len(data["muestras_laboratorio_in_situ"]) > 0
    assert data["mejor_analogo"] is not None
    assert len(data["atribuciones"]) >= 3


def test_endpoint_geologia_punto_luna(client: TestClient) -> None:
    # Mare Tranquillitatis (0.67, 23.47)
    response = client.get("/api/analogia/geologia/punto", params={"cuerpo": "Luna", "lat": 0.67, "lng": 23.47})
    assert response.status_code == 200
    data = response.json()
    assert data["cuerpo"] == "Luna"
    assert "Mare Tranquillitatis" in data["region_nombre"]
    assert any("Ilmenita" in m for m in data["minerales_principales"])
    assert len(data["muestras_laboratorio_in_situ"]) > 0


def test_compatibilidad_api_v1(client: TestClient) -> None:
    # Test ruta directa /api/v1/comparar-analogo
    response = client.get("/api/v1/comparar-analogo", params={"lat": -20.2, "lng": -67.5})
    assert response.status_code == 200
    data = response.json()
    assert data["cuerpo_origen"] == "Tierra"
    assert data["celda_analoga_mas_similar"]["indice_similitud_algoritmo_pct"] >= 0
