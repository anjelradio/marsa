"""Pruebas unitarias de esquema, relaciones SQLModel y reglas de dominio."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, UniqueConstraint, create_engine
from sqlalchemy.dialects.postgresql import dialect as pg_dialect
from sqlalchemy.orm import configure_mappers
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateTable
from sqlmodel import Session, SQLModel

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import get_session
from app.main import app
from app.modules.analogia.domain.entities.analogia import Analogia
from app.modules.analogia.domain.exceptions import InvalidAnalogiaDataException
from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
    AnalogiaModel,
)
from app.modules.caracteristica.domain.entities.caracteristica import Caracteristica
from app.modules.caracteristica.domain.exceptions import (
    InvalidCaracteristicaDataException,
)
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.cuerpo_celeste.domain.entities.cuerpo_celeste import CuerpoCeleste
from app.modules.cuerpo_celeste.domain.exceptions import (
    InvalidCuerpoCelesteDataException,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.domain.entities.dataset import Dataset
from app.modules.dataset.domain.exceptions import InvalidDatasetDataException
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)
from app.modules.medicion.domain.entities.medicion import Medicion
from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)
from app.modules.sitio.domain.entities.sitio import Sitio
from app.modules.sitio.domain.exceptions import InvalidSitioDataException
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel


def test_metadata_registers_all_six_tables_and_columns() -> None:
    expected_columns = {
        "cuerpo_celeste": {"id", "nombre"},
        "sitio": {"id", "cuerpo_id", "nombre", "tipo", "geom"},
        "dataset": {
            "id",
            "nombre",
            "agencia",
            "url",
            "resolucion",
            "fecha_descarga",
        },
        "caracteristica": {"id", "nombre", "unidad", "rango", "peso"},
        "medicion": {
            "id",
            "sitio_id",
            "caracteristica_id",
            "dataset_id",
            "valor",
            "resolucion",
            "valor_normalizado",
        },
        "analogia": {
            "id",
            "sitio_tierra_id",
            "sitio_destino_id",
            "similitud",
            "cobertura",
            "metodo",
            "coincide",
            "difiere",
        },
    }

    assert set(SQLModel.metadata.tables.keys()) == set(expected_columns.keys())
    for table_name, cols in expected_columns.items():
        table = SQLModel.metadata.tables[table_name]
        assert set(table.columns.keys()) == cols


def test_foreign_keys_checks_unique_and_postgresql_ddl() -> None:
    configure_mappers()

    tables = SQLModel.metadata.tables

    assert {
        fk.target_fullname for fk in tables["sitio"].foreign_keys
    } == {"cuerpo_celeste.id"}
    assert {
        fk.target_fullname for fk in tables["medicion"].foreign_keys
    } == {"sitio.id", "caracteristica.id", "dataset.id"}
    assert {
        (fk.parent.name, fk.target_fullname) for fk in tables["analogia"].foreign_keys
    } == {
        ("sitio_tierra_id", "sitio.id"),
        ("sitio_destino_id", "sitio.id"),
    }

    caract_checks = {
        c.name
        for c in tables["caracteristica"].constraints
        if isinstance(c, CheckConstraint)
    }
    assert caract_checks == {
        "ck_caracteristica_rango_positivo",
        "ck_caracteristica_peso_rango",
    }

    medicion_uniques = [
        tuple(c.columns.keys())
        for c in tables["medicion"].constraints
        if isinstance(c, UniqueConstraint)
    ]
    assert ("sitio_id", "caracteristica_id", "dataset_id") in medicion_uniques

    analogia_uniques = [
        tuple(c.columns.keys())
        for c in tables["analogia"].constraints
        if isinstance(c, UniqueConstraint)
    ]
    assert ("sitio_tierra_id", "sitio_destino_id") in analogia_uniques

    ddl_by_table = {
        t.name: str(CreateTable(t).compile(dialect=pg_dialect()))
        for t in SQLModel.metadata.sorted_tables
    }
    assert "geom JSONB" in ddl_by_table["sitio"]
    assert "DOUBLE PRECISION" in ddl_by_table["caracteristica"]
    assert "SERIAL NOT NULL" in ddl_by_table["cuerpo_celeste"]


def test_sqlmodel_relationships_wire_bidirectionally() -> None:
    configure_mappers()

    assert set(CuerpoCelesteModel.__sqlmodel_relationships__.keys()) == {"sitios"}
    assert set(SitioModel.__sqlmodel_relationships__.keys()) == {
        "cuerpo",
        "mediciones",
        "analogias_como_tierra",
        "analogias_como_destino",
    }
    assert set(DatasetModel.__sqlmodel_relationships__.keys()) == {"mediciones"}
    assert set(CaracteristicaModel.__sqlmodel_relationships__.keys()) == {"mediciones"}
    assert set(MedicionModel.__sqlmodel_relationships__.keys()) == {
        "sitio",
        "caracteristica",
        "dataset",
    }
    assert set(AnalogiaModel.__sqlmodel_relationships__.keys()) == {
        "sitio_tierra",
        "sitio_destino",
    }


def test_domain_entities_enforce_invariants() -> None:
    cuerpo = CuerpoCeleste.create(nombre="  Marte ")
    assert cuerpo.nombre == "Marte"
    with pytest.raises(InvalidCuerpoCelesteDataException):
        CuerpoCeleste.create(nombre="   ")

    sitio = Sitio.create(cuerpo_id=1, nombre="Cráter Jezero", tipo="lago fósil")
    assert sitio.nombre == "Cráter Jezero"
    with pytest.raises(InvalidSitioDataException):
        Sitio.create(cuerpo_id=0, nombre="Inválido")

    ds = Dataset.create(nombre="CTX", fecha_descarga=date(2026, 1, 1))
    assert ds.nombre == "CTX"
    with pytest.raises(InvalidDatasetDataException):
        Dataset.create(nombre="")

    caract = Caracteristica.create(nombre="Pendiente", unidad="grados", rango=90.0, peso=0.2)
    assert caract.peso == pytest.approx(0.2)
    with pytest.raises(InvalidCaracteristicaDataException):
        Caracteristica.create(nombre="Mala", rango=0.0, peso=0.5)
    with pytest.raises(InvalidCaracteristicaDataException):
        Caracteristica.create(nombre="Peso alto", rango=10.0, peso=1.5)

    med = Medicion.create(
        sitio_id=1,
        caracteristica_id=1,
        dataset_id=1,
        valor=12.5,
        valor_normalizado=0.8,
    )
    assert med.valor_normalizado == pytest.approx(0.8)
    with pytest.raises(InvalidMedicionDataException):
        Medicion.create(
            sitio_id=1,
            caracteristica_id=1,
            dataset_id=1,
            valor=1.0,
            valor_normalizado=1.2,
        )

    analogia = Analogia.create(
        sitio_tierra_id=1,
        sitio_destino_id=2,
        similitud=0.85,
        cobertura=0.9,
        metodo="Coseno ponderado",
    )
    assert analogia.similitud == pytest.approx(0.85)
    with pytest.raises(InvalidAnalogiaDataException):
        Analogia.create(sitio_tierra_id=1, sitio_destino_id=2, cobertura=-0.1)


def test_api_module_routes_return_empty_lists_when_tables_empty() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        client = TestClient(app)
        for endpoint in (
            "/api/cuerpo-celeste/",
            "/api/sitio/",
            "/api/dataset/",
            "/api/caracteristica/",
            "/api/medicion/",
            "/api/analogia/",
        ):
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.json() == []
    finally:
        app.dependency_overrides.clear()
