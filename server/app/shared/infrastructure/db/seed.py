"""Semillas de datos iniciales para cuerpos celestes, características y datasets."""

import logging
from sqlmodel import Session, select

from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)

logger = logging.getLogger(__name__)


def seed_initial_data(session: Session) -> None:
    """Inserta cuerpos celestes, características y datasets iniciales si no existen."""
    # 1. Cuerpos celestes
    cuerpos = [
        {"nombre": "Tierra", "tipo": "Planeta rocoso", "radio_km": 6371.0},
        {"nombre": "Marte", "tipo": "Planeta rocoso", "radio_km": 3389.5},
        {"nombre": "Luna", "tipo": "Satélite natural", "radio_km": 1737.4},
    ]
    for c in cuerpos:
        exists = session.exec(
            select(CuerpoCelesteModel).where(CuerpoCelesteModel.nombre == c["nombre"])
        ).first()
        if not exists:
            session.add(CuerpoCelesteModel(**c))

    # 2. Datasets
    datasets = [
        {
            "nombre": "Copernicus Sentinel-2 L2A",
            "agencia": "ESA",
            "url": "https://stac.dataspace.copernicus.eu/v1",
            "resolucion": 10.0,
        },
        {
            "nombre": "Copernicus Sentinel-3 SLSTR",
            "agencia": "ESA",
            "url": "https://stac.dataspace.copernicus.eu/v1",
            "resolucion": 1000.0,
        },
        {
            "nombre": "USGS THEMIS Infrared Mosaic",
            "agencia": "NASA / USGS",
            "url": "https://stac.astrogeology.usgs.gov/api",
            "resolucion": 100.0,
        },
        {
            "nombre": "USGS Mars Context Camera (CTX)",
            "agencia": "NASA / USGS",
            "url": "https://stac.astrogeology.usgs.gov/api",
            "resolucion": 6.0,
        },
        {
            "nombre": "OpenTopography Global DEM",
            "agencia": "OpenTopography / NSF",
            "url": "https://portal.opentopography.org/apidocs/",
            "resolucion": 30.0,
        },
    ]
    for d in datasets:
        exists = session.exec(
            select(DatasetModel).where(DatasetModel.nombre == d["nombre"])
        ).first()
        if not exists:
            session.add(DatasetModel(**d))

    # 3. Características
    caracteristicas = [
        {
            "nombre": "Temperatura Superficial",
            "unidad": "K",
            "rango": 350.0,  # 0 a 350 K aprox
            "peso": 0.35,
        },
        {
            "nombre": "Nubosidad",
            "unidad": "%",
            "rango": 100.0,  # 0 a 100%
            "peso": 0.25,
        },
        {
            "nombre": "Inercia Térmica",
            "unidad": "J m^-2 K^-1 s^-1/2",
            "rango": 800.0,
            "peso": 0.20,
        },
        {
            "nombre": "Elevación",
            "unidad": "m",
            "rango": 30000.0,  # De -8000 a +22000m en Marte
            "peso": 0.20,
        },
    ]
    for car in caracteristicas:
        exists = session.exec(
            select(CaracteristicaModel).where(CaracteristicaModel.nombre == car["nombre"])
        ).first()
        if not exists:
            session.add(CaracteristicaModel(**car))

    session.commit()
    logger.info("Datos iniciales de Cuerpos, Datasets y Características asegurados.")

