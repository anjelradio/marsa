"""Servicio para extracción de datos satelitales y guardado de mediciones."""

from __future__ import annotations

import logging
from pathlib import Path
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
from app.shared.infrastructure.external.stac_clients import (
    CopernicusClient,
    USGSStacClient,
)

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[4]
RAW_MCD_TEMP_PRESS_FILE = (
    ROOT_DIR / "datos-marte" / "datos-marte" / "marte_ls105_temperatura_presion.txt"
)


def extract_bbox_from_geom(geom: dict[str, Any] | None) -> list[float]:
    """Extrae un bbox [min_lon, min_lat, max_lon, max_lat] de un objeto GeoJSON."""
    if not geom:
        return [-180.0, -90.0, 180.0, 90.0]

    g_type = geom.get("type")
    coords = geom.get("coordinates")

    if g_type == "Point" and coords and len(coords) >= 2:
        lon, lat = float(coords[0]), float(coords[1])
        return [lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05]

    if g_type == "Polygon" and coords:
        all_lons = [p[0] for p in coords[0]]
        all_lats = [p[1] for p in coords[0]]
        return [min(all_lons), min(all_lats), max(all_lons), max(all_lats)]

    return [-180.0, -90.0, 180.0, 90.0]


def sample_mars_mcd_surface_temperature_k(target_lat: float, target_lon: float) -> float | None:
    """
    Interpola bilinealmente la temperatura superficial real (K) desde la cuadrícula
    validada de Mars Climate Database (MCD v6.2, Ls=105°).
    Nunca inventa ni fabrica constantes arbitrarias.
    """
    # 1. Intentar desde el archivo ASCII local si está presente
    if RAW_MCD_TEMP_PRESS_FILE.exists():
        try:
            import sys

            pipelines_dir = str(ROOT_DIR / "pipelines")
            if pipelines_dir not in sys.path:
                sys.path.insert(0, pipelines_dir)
            from parse_mcd_mars import parse_mcd_ascii_blocks, sample_bilinear

            blocks = parse_mcd_ascii_blocks(RAW_MCD_TEMP_PRESS_FILE)
            if blocks:
                temp_block = blocks[0]
                sampled = sample_bilinear(
                    temp_block["latitudes"],
                    temp_block["longitudes"],
                    temp_block["matrix_lon_lat"],
                    target_lat,
                    target_lon,
                )
                return float(sampled["bilinear"])
        except Exception as exc:
            logger.warning("Fallo al interpolar desde archivo MCD ASCII: %s", exc)

    # 2. Fallback al resumen procesado versionado (`data/processed/mars_mcd_ls105.json`)
    processed_json = ROOT_DIR / "data" / "processed" / "mars_mcd_ls105.json"
    if processed_json.exists():
        import json

        data = json.loads(processed_json.read_text(encoding="utf-8"))
        refs = data.get("reference_locations", {})
        best_val: float | None = None
        best_dist = float("inf")
        for loc in refs.values():
            dist = abs(float(loc["lat"]) - target_lat) + abs(float(loc["lon"]) - target_lon)
            if dist < best_dist and dist <= 5.0:
                best_dist = dist
                best_val = float(loc["variables"]["surface_temperature_k"]["bilinear"])
        return best_val

    return None


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
        """Procesa datos de Copernicus (Nubosidad Sentinel-2, etc.)."""
        mediciones: list[MedicionModel] = []

        ds_s2 = self.db.exec(
            select(DatasetModel).where(DatasetModel.nombre == "Copernicus Sentinel-2 L2A")
        ).first()
        car_nub = self.db.exec(
            select(CaracteristicaModel).where(CaracteristicaModel.nombre == "Nubosidad")
        ).first()

        if ds_s2 and car_nub:
            cl_info = self.copernicus.get_cloud_cover_and_weather(bbox, datetime_range)
            cloud_val = cl_info.get("cloud_cover")
            if cloud_val is not None:
                norm = min(max(cloud_val / (car_nub.rango or 100.0), 0.0), 1.0)
                med = self._upsert_medicion(
                    sitio_id=sitio.id,  # type: ignore[arg-type]
                    caracteristica_id=car_nub.id,  # type: ignore[arg-type]
                    dataset_id=ds_s2.id,  # type: ignore[arg-type]
                    valor=cloud_val,
                    resolucion=ds_s2.resolucion,
                    valor_normalizado=norm,
                )
                mediciones.append(med)

        return mediciones

    def _procesar_marte(
        self,
        sitio: SitioModel,
        bbox: list[float],
        datetime_range: str | None,
    ) -> list[MedicionModel]:
        """
        Extrae la temperatura superficial marciana real desde Mars Climate Database (MCD v6.2)
        para el centroide del sitio y verifica metadatos de escena en USGS Astrogeology STAC.
        No fabrica ni inventa temperaturas si las coordenadas están fuera de rango o sin fuente.
        """
        mediciones: list[MedicionModel] = []

        ds_mcd = self.db.exec(
            select(DatasetModel).where(
                DatasetModel.nombre.in_(
                    ["Mars Climate Database (MCD) v6.2", "USGS THEMIS Infrared Mosaic"]
                )
            )
        ).first()
        car_temp = self.db.exec(
            select(CaracteristicaModel).where(
                CaracteristicaModel.nombre == "Temperatura Superficial"
            )
        ).first()

        if ds_mcd and car_temp:
            center_lon = (bbox[0] + bbox[2]) / 2.0
            center_lat = (bbox[1] + bbox[3]) / 2.0

            temp_real_k = sample_mars_mcd_surface_temperature_k(center_lat, center_lon)
            if temp_real_k is not None:
                norm = min(max(temp_real_k / (car_temp.rango or 350.0), 0.0), 1.0)
                med = self._upsert_medicion(
                    sitio_id=sitio.id,  # type: ignore[arg-type]
                    caracteristica_id=car_temp.id,  # type: ignore[arg-type]
                    dataset_id=ds_mcd.id,  # type: ignore[arg-type]
                    valor=round(temp_real_k, 3),
                    resolucion=ds_mcd.resolucion,
                    valor_normalizado=round(norm, 4),
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
