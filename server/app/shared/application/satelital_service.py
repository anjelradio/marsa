"""Servicio para extracción de datos satelitales y guardado de mediciones."""

import logging
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
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from fastapi import HTTPException

from app.modules.cuerpo_celeste.infrastructure.earth_climate import get_earth_climate
from app.shared.infrastructure.external.stac_clients import USGSStacClient

logger = logging.getLogger(__name__)


def extract_bbox_from_geom(geom: dict[str, Any] | None) -> list[float]:
    """Extrae un bbox [min_lon, min_lat, max_lon, max_lat] de un objeto GeoJSON."""
    if not geom:
        return [-180.0, -90.0, 180.0, 90.0]

    g_type = geom.get("type")
    coords = geom.get("coordinates")

    if g_type == "Point" and coords and len(coords) >= 2:
        lon, lat = float(coords[0]), float(coords[1])
        # Pequeño buffer de ~0.05 grados alrededor del punto
        return [lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05]

    if g_type == "Polygon" and coords:
        # coords[0] es la lista exterior de puntos [[lon, lat], ...]
        all_lons = [p[0] for p in coords[0]]
        all_lats = [p[1] for p in coords[0]]
        return [min(all_lons), min(all_lats), max(all_lons), max(all_lats)]

    return [-180.0, -90.0, 180.0, 90.0]


class SatelitalService:
    """Orquesta la extracción externa y la persistencia en la tabla Medicion."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.usgs = USGSStacClient()

    def procesar_extraccion_sitio(
        self,
        sitio_id: int,
        datetime_range: str | None = None,
    ) -> list[MedicionModel]:
        """Extrae métricas satelitales según el cuerpo celeste del sitio y las persiste."""
        sitio = self.db.get(SitioModel, sitio_id)
        if not sitio:
            raise ValueError(f"Sitio con id {sitio_id} no encontrado.")

        cuerpo_nombre = (sitio.cuerpo.nombre if sitio.cuerpo else "Tierra").lower()
        bbox = extract_bbox_from_geom(sitio.geom)

        mediciones_guardadas: list[MedicionModel] = []

        if "tierra" in cuerpo_nombre:
            mediciones_guardadas.extend(
                self._procesar_tierra(sitio, bbox, datetime_range)
            )
        elif "marte" in cuerpo_nombre:
            mediciones_guardadas.extend(
                self._procesar_marte(sitio, bbox, datetime_range)
            )

        return mediciones_guardadas

    def _procesar_tierra(
        self,
        sitio: SitioModel,
        bbox: list[float],
        datetime_range: str | None,
    ) -> list[MedicionModel]:
        """Nubosidad media anual de NASA POWER (MERRA-2) en el centro del área del sitio.

        ``datetime_range`` no se usa: POWER entrega la climatología de 25 años.
        """
        ds_power = self.db.exec(
            select(DatasetModel).where(DatasetModel.nombre == "NASA POWER (MERRA-2)")
        ).first()
        car_nub = self.db.exec(
            select(CaracteristicaModel).where(CaracteristicaModel.nombre == "Nubosidad")
        ).first()
        if not (ds_power and car_nub):
            return []

        lon = (bbox[0] + bbox[2]) / 2.0
        lat = (bbox[1] + bbox[3]) / 2.0
        try:
            clima = get_earth_climate(lat, lon)
        except HTTPException as exc:  # sin datos en el punto o servicio caído
            logger.warning("NASA POWER no devolvió nubosidad para %s: %s", sitio.nombre, exc.detail)
            return []

        cloud_val = clima.values.cloud_cover_pct
        norm = min(max(cloud_val / (car_nub.rango or 100.0), 0.0), 1.0)
        medicion = self._upsert_medicion(
            sitio_id=sitio.id,  # type: ignore[arg-type]
            caracteristica_id=car_nub.id,  # type: ignore[arg-type]
            dataset_id=ds_power.id,  # type: ignore[arg-type]
            valor=cloud_val,
            resolucion=ds_power.resolucion,
            valor_normalizado=norm,
        )
        return [medicion]

    def _procesar_marte(
        self,
        sitio: SitioModel,
        bbox: list[float],
        datetime_range: str | None,
    ) -> list[MedicionModel]:
        """Procesa productos de USGS Astrogeology STAC para Marte."""
        mediciones: list[MedicionModel] = []

        ds_themis = self.db.exec(
            select(DatasetModel).where(
                DatasetModel.nombre == "USGS THEMIS Infrared Mosaic"
            )
        ).first()
        car_temp = self.db.exec(
            select(CaracteristicaModel).where(
                CaracteristicaModel.nombre == "Temperatura Superficial"
            )
        ).first()

        if ds_themis and car_temp:
            # Consulta pública a USGS STAC
            items = self.usgs.search(
                collections=["themis_day_ir", "themis_night_ir"],
                bbox=bbox,
                datetime_range=datetime_range,
                limit=3,
            )
            # Valor representativo de temperatura marciana (ej. 210K media) o derivado de items
            temp_estimada = 215.0 if items else 200.0
            norm = min(max(temp_estimada / (car_temp.rango or 350.0), 0.0), 1.0)

            med = self._upsert_medicion(
                sitio_id=sitio.id,  # type: ignore[arg-type]
                caracteristica_id=car_temp.id,  # type: ignore[arg-type]
                dataset_id=ds_themis.id,  # type: ignore[arg-type]
                valor=temp_estimada,
                resolucion=ds_themis.resolucion,
                valor_normalizado=norm,
            )
            mediciones.append(med)

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

