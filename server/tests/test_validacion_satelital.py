"""Validación de entradas y manejo de nulos en la extracción satelital."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import get_session
from app.main import app
from app.modules.caracteristica.domain.exceptions import CaracteristicaNotFoundException
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.domain.exceptions import DatasetNotFoundException
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)
from app.modules.sitio.domain.exceptions import SitioNotFoundException
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.application.satelital_service import SatelitalService
from app.shared.domain.exceptions import (
    FuenteExternaException,
    SinDatosException,
    ValidationException,
)
from app.shared.domain.geo_validators import (
    bbox_from_geom,
    validate_bbox,
    validate_datetime_range,
    validate_lat_lon,
)

PUNTO_ATACAMA = {"type": "Point", "coordinates": [-69.25, -24.5]}


# ── Validadores puros ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("lat", "lon"),
    [(91, 0), (-91, 0), (0, 181), (0, -181), (None, 0), (0, None), ("x", 0), (float("nan"), 0)],
)
def test_lat_lon_invalidas_lanzan_validation(lat, lon) -> None:
    with pytest.raises(ValidationException):
        validate_lat_lon(lat, lon)


def test_lat_lon_validas() -> None:
    assert validate_lat_lon(-24.5, -69.25) == (-24.5, -69.25)


@pytest.mark.parametrize(
    "bbox",
    [None, [], [0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0], [0, 0, 200, 1], [-180, -90, 180, 90]],
)
def test_bbox_invalido_lanza_validation(bbox) -> None:
    with pytest.raises(ValidationException):
        validate_bbox(bbox)


@pytest.mark.parametrize("geom", [None, {}, {"type": "Point"}, {"type": "Point", "coordinates": []}])
def test_geom_ausente_o_vacia_ya_no_devuelve_planeta_entero(geom) -> None:
    with pytest.raises(ValidationException):
        bbox_from_geom(geom)


def test_punto_en_borde_no_se_sale_de_rango() -> None:
    bbox = bbox_from_geom({"type": "Point", "coordinates": [180, 90]})
    assert bbox[2] <= 180 and bbox[3] <= 90


def test_polygon_y_multipolygon() -> None:
    poly = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 1], [0, 1], [0, 0]]]}
    assert bbox_from_geom(poly) == [0.0, 0.0, 2.0, 1.0]
    multi = {"type": "MultiPolygon", "coordinates": [poly["coordinates"]]}
    assert bbox_from_geom(multi) == [0.0, 0.0, 2.0, 1.0]


def test_geom_con_coordenada_fuera_de_rango() -> None:
    with pytest.raises(ValidationException):
        bbox_from_geom({"type": "Point", "coordinates": [10, 95]})


@pytest.mark.parametrize(
    "texto",
    ["", "  ", "no-es-fecha", "2024-01-31/2024-01-01", "../..", "a/b/c", "2999-01-01T00:00:00Z"],
)
def test_datetime_range_invalido(texto) -> None:
    with pytest.raises(ValidationException):
        validate_datetime_range(texto)


@pytest.mark.parametrize(
    "texto",
    ["2024-01-01T00:00:00Z/2024-01-31T23:59:59Z", "2024-01-01/..", "../2024-01-31", "2024-05-01"],
)
def test_datetime_range_valido(texto) -> None:
    assert validate_datetime_range(texto) == texto


def test_datetime_range_none_es_permitido() -> None:
    assert validate_datetime_range(None) is None


# ── Servicio con BD en memoria y clientes simulados ──────────────────────────


class _CopernicusFake:
    def __init__(self, cloud=42.0, error=None) -> None:
        self.cloud, self.error = cloud, error

    def get_cloud_cover_and_weather(self, bbox, datetime_range=None):
        if self.error:
            raise self.error
        return {"cloud_cover": self.cloud}


class _UsgsFake:
    def __init__(self, items=None, error=None) -> None:
        self.items, self.error = items if items is not None else [], error
        self.llamadas: list[dict] = []

    def search(self, **kwargs):
        self.llamadas.append(kwargs)
        if self.error:
            raise self.error
        return self.items


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _sembrar(db: Session, *, con_catalogos: bool = True) -> None:
    db.add_all([CuerpoCelesteModel(nombre="Tierra"), CuerpoCelesteModel(nombre="Marte"),
                CuerpoCelesteModel(nombre="Luna")])
    db.commit()
    if con_catalogos:
        db.add_all([
            DatasetModel(nombre="Copernicus Sentinel-2 L2A", resolucion=10.0),
            DatasetModel(nombre="USGS THEMIS Infrared Mosaic", resolucion=100.0),
            CaracteristicaModel(nombre="Nubosidad", rango=100.0, peso=0.3),
            CaracteristicaModel(nombre="Temperatura Superficial", rango=350.0, peso=0.4),
        ])
        db.commit()


def _sitio(db: Session, cuerpo_id: int, geom=PUNTO_ATACAMA) -> int:
    sitio = SitioModel(cuerpo_id=cuerpo_id, nombre="S", geom=geom)
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    return sitio.id


def _servicio(db, copernicus=None, usgs=None) -> SatelitalService:
    service = SatelitalService(db)
    service.copernicus = copernicus or _CopernicusFake()
    service.usgs = usgs or _UsgsFake()
    return service


def test_tierra_ok_guarda_medicion(db) -> None:
    _sembrar(db)
    resultado = _servicio(db).procesar_extraccion_sitio(_sitio(db, 1))
    assert len(resultado) == 1
    assert resultado[0].valor == 42.0 and resultado[0].valor_normalizado == pytest.approx(0.42)


def test_sitio_inexistente(db) -> None:
    _sembrar(db)
    with pytest.raises(SitioNotFoundException):
        _servicio(db).procesar_extraccion_sitio(999)


@pytest.mark.parametrize("sitio_id", [0, -1, None, True])
def test_sitio_id_invalido(db, sitio_id) -> None:
    with pytest.raises(ValidationException):
        _servicio(db).procesar_extraccion_sitio(sitio_id)


def test_fecha_invalida_se_rechaza_antes_de_consultar(db) -> None:
    _sembrar(db)
    sitio_id = _sitio(db, 1)
    espia = _CopernicusFake(error=AssertionError("no debe consultarse"))
    with pytest.raises(ValidationException):
        _servicio(db, copernicus=espia).procesar_extraccion_sitio(sitio_id, "basura")


def test_sitio_sin_geom_ya_no_consulta_el_planeta(db) -> None:
    _sembrar(db)
    with pytest.raises(ValidationException):
        _servicio(db).procesar_extraccion_sitio(_sitio(db, 1, geom=None))


def test_luna_no_soportada_es_error_explicito(db) -> None:
    _sembrar(db)
    with pytest.raises(ValidationException):
        _servicio(db).procesar_extraccion_sitio(_sitio(db, 3))


def test_catalogos_faltantes_son_error_explicito(db) -> None:
    _sembrar(db, con_catalogos=False)
    with pytest.raises(DatasetNotFoundException):
        _servicio(db).procesar_extraccion_sitio(_sitio(db, 1))
    db.add(DatasetModel(nombre="Copernicus Sentinel-2 L2A"))
    db.commit()
    with pytest.raises(CaracteristicaNotFoundException):
        _servicio(db).procesar_extraccion_sitio(_sitio(db, 1))


def test_nubosidad_nula_lanza_sin_datos(db) -> None:
    _sembrar(db)
    with pytest.raises(SinDatosException):
        _servicio(db, copernicus=_CopernicusFake(cloud=None)).procesar_extraccion_sitio(_sitio(db, 1))


def test_valor_nan_lanza_sin_datos(db) -> None:
    _sembrar(db)
    with pytest.raises(SinDatosException):
        _servicio(db, copernicus=_CopernicusFake(cloud=float("nan"))).procesar_extraccion_sitio(
            _sitio(db, 1)
        )


def test_valor_fuera_de_rango_no_se_recorta_en_silencio(db) -> None:
    _sembrar(db)
    with pytest.raises(ValidationException):
        _servicio(db, copernicus=_CopernicusFake(cloud=150.0)).procesar_extraccion_sitio(
            _sitio(db, 1)
        )


def test_fuente_caida_se_propaga_como_fuente_externa(db) -> None:
    _sembrar(db)
    falla = FuenteExternaException("Copernicus STAC respondió HTTP 503")
    with pytest.raises(FuenteExternaException):
        _servicio(db, copernicus=_CopernicusFake(error=falla)).procesar_extraccion_sitio(
            _sitio(db, 1)
        )


def test_marte_sin_productos_ya_no_inventa_200k(db) -> None:
    _sembrar(db)
    with pytest.raises(SinDatosException):
        _servicio(db, usgs=_UsgsFake(items=[])).procesar_extraccion_sitio(_sitio(db, 2))


def test_marte_consulta_la_coleccion_real_de_themis(db) -> None:
    _sembrar(db)
    usgs = _UsgsFake(items=[{"id": "mc12_arabia_nir"}])
    _servicio(db, usgs=usgs).procesar_extraccion_sitio(_sitio(db, 2))
    assert usgs.llamadas[0]["collections"] == ["mo_themis_controlled_mosaics"]


def test_marte_sin_cobertura_themis_explica_el_limite_de_latitud(db) -> None:
    _sembrar(db)
    polo = {"type": "Point", "coordinates": [0, 85]}
    with pytest.raises(SinDatosException, match="latitud entre -65 y 65"):
        _servicio(db, usgs=_UsgsFake(items=[])).procesar_extraccion_sitio(_sitio(db, 2, geom=polo))


def test_marte_con_productos_guarda_medicion(db) -> None:
    _sembrar(db)
    resultado = _servicio(db, usgs=_UsgsFake(items=[{"id": "x"}])).procesar_extraccion_sitio(
        _sitio(db, 2)
    )
    assert len(resultado) == 1


# ── API: códigos HTTP y formato de error ─────────────────────────────────────


@pytest.fixture()
def client(db):
    def _override():
        yield db

    app.dependency_overrides[get_session] = _override
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.clear()


def test_api_fecha_invalida_422(client) -> None:
    r = client.post("/api/medicion/extraer-satelital", json={"sitio_id": 1, "datetime_range": "hola"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "SCHEMA_VALIDATION_ERROR"


def test_api_sitio_inexistente_404(client, db) -> None:
    _sembrar(db)
    r = client.post("/api/medicion/extraer-satelital", json={"sitio_id": 999})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "SITIO_NOT_FOUND"


def test_api_sin_geom_400(client, db) -> None:
    _sembrar(db)
    sitio_id = _sitio(db, 1, geom=None)
    r = client.post("/api/medicion/extraer-satelital", json={"sitio_id": sitio_id})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_api_fuente_externa_502(client, db, monkeypatch) -> None:
    _sembrar(db)
    sitio_id = _sitio(db, 1)

    def _falla(self, *a, **k):
        raise FuenteExternaException("Copernicus STAC respondió HTTP 503")

    monkeypatch.setattr(
        "app.shared.infrastructure.external.stac_clients.CopernicusClient.search", _falla
    )
    r = client.post("/api/medicion/extraer-satelital", json={"sitio_id": sitio_id})
    assert r.status_code == 502
    assert r.json()["error"]["code"] == "FUENTE_EXTERNA_ERROR"
