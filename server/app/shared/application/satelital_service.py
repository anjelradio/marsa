"""Servicio para extracción de datos satelitales y guardado de mediciones."""

import logging
import math
from typing import Any
from sqlmodel import Session, select

from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)
from app.modules.caracteristica.domain.exceptions import CaracteristicaNotFoundException
from app.modules.dataset.domain.exceptions import DatasetNotFoundException
from app.modules.sitio.domain.exceptions import SitioNotFoundException
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.domain.exceptions import SinDatosException, ValidationException
from app.shared.domain.geo_validators import (
    bbox_from_geom,
    validate_bbox,
    validate_datetime_range,
)
from app.shared.infrastructure.external.stac_clients import CopernicusClient, USGSStacClient

logger = logging.getLogger(__name__)


CUERPOS_SOPORTADOS = ("tierra", "marte")

# Colección real de USGS: 28 cuadrángulos con versión nocturna (_nir) y diurna (_dir),
# cobertura entre ±65° de latitud (sin polos).
THEMIS_COLLECTION = "mo_themis_controlled_mosaics"
THEMIS_MAX_LAT = 65.0
THEMIS_ITEMS_LIMIT = 6


def extract_bbox_from_geom(geom: dict[str, Any] | None) -> list[float]:
    """Extrae un bbox [min_lon, min_lat, max_lon, max_lat] válido de un GeoJSON.

    Lanza ``ValidationException`` si la geometría falta o es inválida.
    """
    return bbox_from_geom(geom)


def _validar_valor(valor: float | None, nombre: str) -> float:
    """Rechaza nulos, NaN e infinitos antes de persistir una medición."""
    if valor is None or isinstance(valor, bool) or not math.isfinite(valor):
        raise SinDatosException(f"Sin valor válido de {nombre} en la fuente")
    return float(valor)


def _normalizar(valor: float, rango: float | None, defecto: float, nombre: str) -> float:
    """Normaliza a [0, 1]; un valor fuera de rango es un error, no se recorta en silencio."""
    divisor = rango or defecto
    norm = valor / divisor
    if not 0.0 <= norm <= 1.0:
        raise ValidationException(
            f"{nombre}={valor:g} fuera del rango de la característica (0 a {divisor:g})"
        )
    return norm


class SatelitalService:
    """Orquesta la extracción externa y la persistencia en la tabla Medicion."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.copernicus = CopernicusClient()
        self.usgs = USGSStacClient()

    def procesar_extraccion_sitio(
        self,
        sitio_id: int,
        datetime_range: str | None = None,
    ) -> list[MedicionModel]:
        """Extrae métricas satelitales según el cuerpo celeste del sitio y las persiste."""
        # ── Validación previa: nada se consulta hasta que todo sea válido ──
        if not isinstance(sitio_id, int) or isinstance(sitio_id, bool) or sitio_id <= 0:
            raise ValidationException("sitio_id debe ser un entero positivo")
        datetime_range = validate_datetime_range(datetime_range)

        sitio = self.db.get(SitioModel, sitio_id)
        if not sitio:
            raise SitioNotFoundException(f"Sitio {sitio_id} no encontrado")
        if not sitio.cuerpo or not sitio.cuerpo.nombre:
            raise ValidationException(f"El sitio {sitio_id} no tiene cuerpo celeste asociado")

        cuerpo_nombre = sitio.cuerpo.nombre.strip().lower()
        if cuerpo_nombre not in CUERPOS_SOPORTADOS:
            raise ValidationException(
                f"Sin fuente de datos soportada para el cuerpo '{sitio.cuerpo.nombre}'"
            )
        bbox = validate_bbox(extract_bbox_from_geom(sitio.geom))

        if cuerpo_nombre == "tierra":
            return self._procesar_tierra(sitio, bbox, datetime_range)
        return self._procesar_marte(sitio, bbox, datetime_range)

    def _requerir_dataset_y_caracteristica(
        self, dataset_nombre: str, caracteristica_nombre: str
    ) -> tuple[DatasetModel, CaracteristicaModel]:
        """Obtiene dataset y característica sembrados; si faltan, es un error explícito."""
        dataset = self.db.exec(
            select(DatasetModel).where(DatasetModel.nombre == dataset_nombre)
        ).first()
        if not dataset:
            raise DatasetNotFoundException(f"Dataset '{dataset_nombre}' no existe en la BD")
        caracteristica = self.db.exec(
            select(CaracteristicaModel).where(
                CaracteristicaModel.nombre == caracteristica_nombre
            )
        ).first()
        if not caracteristica:
            raise CaracteristicaNotFoundException(
                f"Característica '{caracteristica_nombre}' no existe en la BD"
            )
        return dataset, caracteristica

    def _procesar_tierra(
        self,
        sitio: SitioModel,
        bbox: list[float],
        datetime_range: str | None,
    ) -> list[MedicionModel]:
        """Procesa datos de Copernicus (Nubosidad Sentinel-2, etc.)."""
        mediciones: list[MedicionModel] = []

        # 1. Nubosidad con Sentinel-2
        ds_s2, car_nub = self._requerir_dataset_y_caracteristica(
            "Copernicus Sentinel-2 L2A", "Nubosidad"
        )

        cl_info = self.copernicus.get_cloud_cover_and_weather(bbox, datetime_range)
        cloud_val = _validar_valor(cl_info.get("cloud_cover"), "nubosidad Sentinel-2")
        norm = _normalizar(cloud_val, car_nub.rango, 100.0, "nubosidad")
        mediciones.append(
            self._upsert_medicion(
                sitio_id=sitio.id,  # type: ignore[arg-type]
                caracteristica_id=car_nub.id,  # type: ignore[arg-type]
                dataset_id=ds_s2.id,  # type: ignore[arg-type]
                valor=cloud_val,
                resolucion=ds_s2.resolucion,
                valor_normalizado=norm,
            )
        )
        return mediciones

    def _procesar_marte(
        self,
        sitio: SitioModel,
        bbox: list[float],
        datetime_range: str | None,
    ) -> list[MedicionModel]:
        """Procesa productos de USGS Astrogeology STAC para Marte."""
        mediciones: list[MedicionModel] = []

        ds_themis, car_temp = self._requerir_dataset_y_caracteristica(
            "USGS THEMIS Infrared Mosaic", "Temperatura Superficial"
        )

        items = self.usgs.search(
            collections=[THEMIS_COLLECTION],
            bbox=bbox,
            datetime_range=datetime_range,
            limit=THEMIS_ITEMS_LIMIT,
        )
        if not items:
            raise SinDatosException(
                f"Sin mosaicos THEMIS para bbox {bbox} "
                f"(cobertura: latitud entre -{THEMIS_MAX_LAT:g} y {THEMIS_MAX_LAT:g})"
            )

        # LIMITACIÓN CONOCIDA: los mosaicos THEMIS de USGS son imágenes de 8 bits
        # cualitativas (no temperatura calibrada en kelvin), así que no se puede
        # leer una temperatura real de ellos. El valor siguiente es un representativo
        # fijo hasta usar un producto calibrado (ver PUNTOS_CLAVE_SATELITAL.md).
        temp_estimada = _validar_valor(215.0, "temperatura")
        norm = _normalizar(temp_estimada, car_temp.rango, 350.0, "temperatura")
        mediciones.append(
            self._upsert_medicion(
                sitio_id=sitio.id,  # type: ignore[arg-type]
                caracteristica_id=car_temp.id,  # type: ignore[arg-type]
                dataset_id=ds_themis.id,  # type: ignore[arg-type]
                valor=temp_estimada,
                resolucion=ds_themis.resolucion,
                valor_normalizado=norm,
            )
        )
        return mediciones

    def _upsert_medicion(
        self,
        sitio_id: int,
        caracteristica_id: int,
        dataset_id: int,
        valor: float,
        resolucion: float | None,
        valor_normalizado: float | None,
    ) -> MedicionModel:
        """Inserta o actualiza una medición para mantener la unicidad (sitio, característica, dataset)."""
        stmt = (
            select(MedicionModel)
            .where(MedicionModel.sitio_id == sitio_id)
            .where(MedicionModel.caracteristica_id == caracteristica_id)
            .where(MedicionModel.dataset_id == dataset_id)
        )
        med = self.db.exec(stmt).first()
        if med:
            med.valor = valor
            med.resolucion = resolucion
            med.valor_normalizado = valor_normalizado
        else:
            med = MedicionModel(
                sitio_id=sitio_id,
                caracteristica_id=caracteristica_id,
                dataset_id=dataset_id,
                valor=valor,
                resolucion=resolucion,
                valor_normalizado=valor_normalizado,
            )
            self.db.add(med)

        self.db.commit()
        self.db.refresh(med)
        return med

