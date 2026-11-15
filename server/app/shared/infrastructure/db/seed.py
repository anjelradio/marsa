"""Semillas de datos iniciales para cuerpos celestes, características y datasets."""

import json
import logging
from pathlib import Path

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
            "nombre": "Valores de referencia (literatura)",
            "agencia": "Varias",
            "url": None,
            "resolucion": None,
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
        {
            "nombre": "NASA POWER (MERRA-2)",
            "agencia": "NASA",
            "url": "https://power.larc.nasa.gov/docs/services/api/",
            "resolucion": 55000.0,
        },
        {
            "nombre": "OpenTopoData SRTM 30 m",
            "agencia": "NASA / USGS",
            "url": "https://www.opentopodata.org/datasets/srtm/",
            "resolucion": 30.0,
        },
        {
            "nombre": "LMD Mars Climate Database",
            "agencia": "LMD / CNES / ESA",
            "url": "https://www-mars.lmd.jussieu.fr/mars/info_web/index.html",
            "resolucion": 330000.0,
        },
        {
            "nombre": "Macrostrat API",
            "agencia": "Macrostrat / NSF / UW-Madison",
            "url": "https://macrostrat.org/api/v2/geologic_units/map",
            "resolucion": 1000.0,
        },
        {
            "nombre": "GLiM (Global Lithological Map)",
            "agencia": "Univ. Hamburg / Hartmann & Moosdorf",
            "url": "https://doi.pangaea.de/10.1594/PANGAEA.788537",
            "resolucion": 50000.0,
        },
        {
            "nombre": "USGS SIM 3292 Mars Geologic Map",
            "agencia": "USGS / NASA",
            "url": "https://pubs.usgs.gov/sim/3292/",
            "resolucion": 20000.0,
        },
        {
            "nombre": "ESA Mars Express OMEGA Mineralogy",
            "agencia": "ESA / OMEGA Team",
            "url": "https://www.cosmos.esa.int/web/psa/mars-express",
            "resolucion": 2000.0,
        },
        {
            "nombre": "NASA MSL Curiosity CheMin XRD",
            "agencia": "NASA / PDS Geosciences",
            "url": "https://pds-geosciences.wustl.edu/missions/msl/chemin.htm",
            "resolucion": 0.01,
        },
        {
            "nombre": "USGS Unified Geologic Map of the Moon",
            "agencia": "USGS / NASA / LPI",
            "url": "https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon",
            "resolucion": 5000.0,
        },
        {
            "nombre": "JAXA Kaguya Multiband Imager (MI)",
            "agencia": "JAXA / SELENE",
            "url": "https://darts.isas.jaxa.jp/planet/pdap/selene/",
            "resolucion": 20.0,
        },
        {
            "nombre": "NASA Apollo Lunar Sample Compendium",
            "agencia": "NASA Johnson Space Center",
            "url": "https://curator.jsc.nasa.gov/lunar/lsc/index.cfm",
            "resolucion": 0.001,
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

CARACTERISTICAS_MINERALOGICAS = [
    {"nombre": "Plagioclasa", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Piroxeno (Augita/Pigeonita)", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Olivino (Forsterita)", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Óxidos Férricos (Hematita/Magnetita)", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Filosilicatos / Minerales Hidratados", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Ilmenita", "unidad": "% wt", "rango": 100.0, "peso": 0.15},
    {"nombre": "Sulfatos (Jarosita/Yeso)", "unidad": "% wt", "rango": 100.0, "peso": 0.10},
]

# Mediciones mineralógicas reales/de referencia por sitio (% wt)
MEDICIONES_MINERALOGICAS = {
    "Desierto de Atacama (Yungay)": {
        "dataset": "GLiM (Global Lithological Map)",
        "minerales": {"Plagioclasa": 35.0, "Piroxeno (Augita/Pigeonita)": 18.0, "Olivino (Forsterita)": 5.0, "Óxidos Férricos (Hematita/Magnetita)": 12.0, "Filosilicatos / Minerales Hidratados": 8.0, "Ilmenita": 1.5, "Sulfatos (Jarosita/Yeso)": 20.5}
    },
    "Salar de Uyuni": {
        "dataset": "GLiM (Global Lithological Map)",
        "minerales": {"Plagioclasa": 10.0, "Piroxeno (Augita/Pigeonita)": 5.0, "Olivino (Forsterita)": 0.5, "Óxidos Férricos (Hematita/Magnetita)": 2.0, "Filosilicatos / Minerales Hidratados": 15.0, "Ilmenita": 0.5, "Sulfatos (Jarosita/Yeso)": 67.0}
    },
    "Valles Secos de McMurdo": {
        "dataset": "GLiM (Global Lithological Map)",
        "minerales": {"Plagioclasa": 42.0, "Piroxeno (Augita/Pigeonita)": 26.0, "Olivino (Forsterita)": 12.0, "Óxidos Férricos (Hematita/Magnetita)": 6.0, "Filosilicatos / Minerales Hidratados": 9.0, "Ilmenita": 2.0, "Sulfatos (Jarosita/Yeso)": 3.0}
    },
    "Tarso Toussidé": {
        "dataset": "GLiM (Global Lithological Map)",
        "minerales": {"Plagioclasa": 45.0, "Piroxeno (Augita/Pigeonita)": 30.0, "Olivino (Forsterita)": 15.0, "Óxidos Férricos (Hematita/Magnetita)": 7.0, "Filosilicatos / Minerales Hidratados": 1.0, "Ilmenita": 1.5, "Sulfatos (Jarosita/Yeso)": 0.5}
    },
    "Cueva de los Verdes (Lanzarote)": {
        "dataset": "GLiM (Global Lithological Map)",
        "minerales": {"Plagioclasa": 48.0, "Piroxeno (Augita/Pigeonita)": 28.0, "Olivino (Forsterita)": 18.0, "Óxidos Férricos (Hematita/Magnetita)": 4.5, "Filosilicatos / Minerales Hidratados": 0.5, "Ilmenita": 1.0, "Sulfatos (Jarosita/Yeso)": 0.0}
    },
    "Cráter Gale": {
        "dataset": "NASA MSL Curiosity CheMin XRD",
        "minerales": {"Plagioclasa": 38.0, "Piroxeno (Augita/Pigeonita)": 16.0, "Olivino (Forsterita)": 18.0, "Óxidos Férricos (Hematita/Magnetita)": 4.0, "Filosilicatos / Minerales Hidratados": 14.0, "Ilmenita": 0.8, "Sulfatos (Jarosita/Yeso)": 9.2}
    },
    "Meridiani Planum": {
        "dataset": "ESA Mars Express OMEGA Mineralogy",
        "minerales": {"Plagioclasa": 18.0, "Piroxeno (Augita/Pigeonita)": 12.0, "Olivino (Forsterita)": 4.0, "Óxidos Férricos (Hematita/Magnetita)": 18.0, "Filosilicatos / Minerales Hidratados": 8.0, "Ilmenita": 1.0, "Sulfatos (Jarosita/Yeso)": 39.0}
    },
    "Mare Tranquillitatis": {
        "dataset": "NASA Apollo Lunar Sample Compendium",
        "minerales": {"Plagioclasa": 28.0, "Piroxeno (Augita/Pigeonita)": 47.0, "Olivino (Forsterita)": 4.5, "Óxidos Férricos (Hematita/Magnetita)": 1.0, "Filosilicatos / Minerales Hidratados": 0.0, "Ilmenita": 18.5, "Sulfatos (Jarosita/Yeso)": 0.0}
    },
    "Borde del cráter Shackleton": {
        "dataset": "JAXA Kaguya Multiband Imager (MI)",
        "minerales": {"Plagioclasa": 82.0, "Piroxeno (Augita/Pigeonita)": 12.0, "Olivino (Forsterita)": 4.0, "Óxidos Férricos (Hematita/Magnetita)": 0.5, "Filosilicatos / Minerales Hidratados": 0.0, "Ilmenita": 0.5, "Sulfatos (Jarosita/Yeso)": 0.0}
    },
}


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

# Dataset de las mediciones sembradas a mano: son cifras de referencia de la literatura,
# no lecturas de un instrumento. Las descargadas (real_measurements.json) llevan el suyo.
_DATASET_REFERENCIA = "Valores de referencia (literatura)"
_DATASET_POR_CUERPO = {
    "Tierra": _DATASET_REFERENCIA,
    "Marte": _DATASET_REFERENCIA,
    "Luna": _DATASET_REFERENCIA,
}


_REALES = Path(__file__).with_name("real_measurements.json")


def _cargar_mediciones_reales() -> dict[str, dict[str, dict]]:
    """Lee las mediciones descargadas por scripts/fetch_real_measurements.py."""
    if not _REALES.exists():
        return {}
    return json.loads(_REALES.read_text(encoding="utf-8")).get("sitios", {})


def _seed_sitios_y_mediciones(session: Session) -> None:
    """Crea sitios, mediciones y analogías persistidas si no existen."""
    from app.modules.analogia.application.queries.ranking_query import (
        mejor_coincidencia,
    )
    from app.modules.analogia.domain.services.similarity import (
        METODO,
        CaracteristicaSpec,
    )
    from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
        AnalogiaModel,
    )
    from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
        MedicionModel,
    )
    from app.modules.sitio.infrastructure.persistence.models.sitio_model import (
        SitioModel,
    )

    reales = _cargar_mediciones_reales()
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
            dataset_nombre = _DATASET_POR_CUERPO[cuerpo]
            real = reales.get(nombre, {}).get(car_nombre)
            if real is not None:  # dato descargado de la fuente real
                valor = real["valor"]
                dataset_nombre = real["dataset"]
            dataset_id = datasets[dataset_nombre]
            minimo = _MINIMO.get(car_nombre, 0.0)
            normalizado = max(0.0, min(1.0, (valor - minimo) / car.rango))
            existente = session.exec(
                select(MedicionModel).where(
                    MedicionModel.sitio_id == sitio.id,
                    MedicionModel.caracteristica_id == car.id,
                )
            ).first()
            if existente:
                existente.valor = float(valor)
                existente.dataset_id = dataset_id
                existente.valor_normalizado = normalizado
                session.add(existente)
            else:
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
    # Las analogías sembradas se recalculan siempre con los datos vigentes.
    for vieja in session.exec(
        select(AnalogiaModel).where(AnalogiaModel.metodo == METODO)
    ).all():
        session.delete(vieja)
    session.flush()
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

