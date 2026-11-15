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

    datasets_extra = [
        {
            "nombre": "NASA LRO LOLA / Diviner",
            "agencia": "NASA",
            "url": "https://pds-geosciences.wustl.edu/lro/",
            "resolucion": 118.0,
        },
        {
            "nombre": "NASA MGS MOLA",
            "agencia": "NASA",
            "url": "https://pds-geosciences.wustl.edu/mgs/",
            "resolucion": 463.0,
        },
    ]
    for d in datasets_extra:
        if not session.exec(
            select(DatasetModel).where(DatasetModel.nombre == d["nombre"])
        ).first():
            session.add(DatasetModel(**d))

    # 3. Características (los pesos suman 1.0). Si ya existen se actualizan.
    for car in CARACTERISTICAS:
        existente = session.exec(
            select(CaracteristicaModel).where(CaracteristicaModel.nombre == car["nombre"])
        ).first()
        if existente:
            existente.unidad = car["unidad"]
            existente.rango = car["rango"]
            existente.peso = car["peso"]
            session.add(existente)
        else:
            session.add(CaracteristicaModel(**car))

    session.commit()
    _seed_sitios_y_mediciones(session)
    logger.info("Datos iniciales de Cuerpos, Datasets, Características y Sitios asegurados.")


# Rango y mínimo usados para normalizar a [0, 1] cada característica.
CARACTERISTICAS = [
    {"nombre": "Temperatura Superficial", "unidad": "K", "rango": 350.0, "peso": 0.25},
    {"nombre": "Nubosidad", "unidad": "%", "rango": 100.0, "peso": 0.10},
    {
        "nombre": "Inercia Térmica",
        "unidad": "J m^-2 K^-1 s^-1/2",
        "rango": 800.0,
        "peso": 0.15,
    },
    {"nombre": "Elevación", "unidad": "m", "rango": 30000.0, "peso": 0.10},
    {"nombre": "Profundidad Óptica de Polvo", "unidad": "tau", "rango": 5.0, "peso": 0.10},
    {"nombre": "Hielo/Agua Superficial", "unidad": "%", "rango": 100.0, "peso": 0.15},
    {"nombre": "Rugosidad del Terreno", "unidad": "m", "rango": 100.0, "peso": 0.15},
]
_MINIMO = {"Elevación": -8000.0}

# (cuerpo, nombre, tipo, lon, lat, valores en el orden de CARACTERISTICAS)
# Valores de referencia aproximados a partir de literatura publicada; sustituir
# por medias zonales de los datasets cuando se integre el procesamiento real.
SITIOS = [
    ("Tierra", "Desierto de Atacama (Yungay)", "Desierto hiperárido", -69.9, -24.1,
     [290, 2, 400, 1000, 0.15, 0, 20]),
    ("Tierra", "Salar de Uyuni", "Salar", -67.5, -20.2,
     [283, 15, 700, 3656, 0.10, 1, 2]),
    ("Tierra", "Valles Secos de McMurdo", "Desierto polar", 161.8, -77.5,
     [250, 40, 600, 800, 0.05, 15, 35]),
    ("Tierra", "Tarso Toussidé", "Campo volcánico", 16.4, 21.0,
     [303, 3, 500, 2800, 0.40, 0, 70]),
    ("Tierra", "Cueva de los Verdes (Lanzarote)", "Tubo de lava", -13.43, 29.16,
     [290, 20, 800, 100, 0.05, 0, 80]),
    ("Marte", "Cráter Gale", "Cráter de impacto", 137.4, -5.4,
     [228, 5, 300, -4400, 0.6, 2, 40]),
    ("Marte", "Meridiani Planum", "Llanura", -0.0, -2.0,
     [223, 3, 200, -1400, 0.5, 1, 10]),
    ("Luna", "Borde del cráter Shackleton", "Región polar", 0.0, -89.9,
     [90, 0, 50, 1900, 0.0, 5, 60]),
    ("Luna", "Mare Tranquillitatis", "Mar lunar", 31.4, 8.5,
     [250, 0, 50, -1900, 0.0, 0, 15]),
]

# Dataset de origen por cuerpo para las mediciones sembradas.
_DATASET_POR_CUERPO = {
    "Tierra": "Copernicus Sentinel-3 SLSTR",
    "Marte": "NASA MGS MOLA",
    "Luna": "NASA LRO LOLA / Diviner",
}


def _seed_sitios_y_mediciones(session: Session) -> None:
    """Crea sitios, mediciones y analogías persistidas si no existen."""
    from app.modules.analogia.application.queries.ranking_query import (
        mejor_coincidencia,
    )
    from app.modules.analogia.domain.services.similarity import CaracteristicaSpec
    from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
        AnalogiaModel,
    )
    from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
        MedicionModel,
    )
    from app.modules.sitio.infrastructure.persistence.models.sitio_model import (
        SitioModel,
    )

    cuerpos = {c.nombre: c.id for c in session.exec(select(CuerpoCelesteModel)).all()}
    datasets = {d.nombre: d.id for d in session.exec(select(DatasetModel)).all()}
    cars = {c.nombre: c for c in session.exec(select(CaracteristicaModel)).all()}
    orden = [c["nombre"] for c in CARACTERISTICAS]

    for cuerpo, nombre, tipo, lon, lat, valores in SITIOS:
        sitio = session.exec(
            select(SitioModel).where(
                SitioModel.nombre == nombre, SitioModel.cuerpo_id == cuerpos[cuerpo]
            )
        ).first()
        if sitio is None:
            sitio = SitioModel(
                cuerpo_id=cuerpos[cuerpo],
                nombre=nombre,
                tipo=tipo,
                geom={"type": "Point", "coordinates": [lon, lat]},
            )
            session.add(sitio)
            session.flush()
        for car_nombre, valor in zip(orden, valores):
            car = cars[car_nombre]
            dataset_id = datasets[_DATASET_POR_CUERPO[cuerpo]]
            if session.exec(
                select(MedicionModel).where(
                    MedicionModel.sitio_id == sitio.id,
                    MedicionModel.caracteristica_id == car.id,
                    MedicionModel.dataset_id == dataset_id,
                )
            ).first():
                continue
            minimo = _MINIMO.get(car_nombre, 0.0)
            normalizado = max(0.0, min(1.0, (valor - minimo) / car.rango))
            session.add(
                MedicionModel(
                    sitio_id=sitio.id,
                    caracteristica_id=car.id,
                    dataset_id=dataset_id,
                    valor=float(valor),
                    valor_normalizado=normalizado,
                )
            )
    session.commit()

    # Analogías persistidas: cada sitio terrestre contra su mejor destino por cuerpo.
    specs = [
        CaracteristicaSpec(c.id, c.nombre, c.unidad, c.rango, c.peso)
        for c in cars.values()
    ]
    valores_por_sitio: dict[int, dict[int, float]] = {}
    for m in session.exec(select(MedicionModel)).all():
        valores_por_sitio.setdefault(m.sitio_id, {})[m.caracteristica_id] = m.valor
    sitios = session.exec(select(SitioModel)).all()
    tierra = [s for s in sitios if s.cuerpo_id == cuerpos["Tierra"]]
    for destino in ("Marte", "Luna"):
        destinos = [s for s in sitios if s.cuerpo_id == cuerpos[destino]]
        for t in tierra:
            par = mejor_coincidencia(specs, valores_por_sitio, t, destinos)
            if par is None:
                continue
            sitio_destino, r = par
            if session.exec(
                select(AnalogiaModel).where(
                    AnalogiaModel.sitio_tierra_id == t.id,
                    AnalogiaModel.sitio_destino_id == sitio_destino.id,
                )
            ).first():
                continue
            session.add(
                AnalogiaModel(
                    sitio_tierra_id=t.id,
                    sitio_destino_id=sitio_destino.id,
                    similitud=r.similitud,
                    cobertura=r.cobertura,
                    metodo=r.metodo,
                    coincide=r.coincide,
                    difiere=r.difiere,
                )
            )
    session.commit()

