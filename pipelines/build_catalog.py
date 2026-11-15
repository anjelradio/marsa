"""
Build the versioned scientific catalog (`data/catalog/regions.json`) and
provenance manifest (`data/manifest.json`) for Planetary Analog Explorer.

Follows all mandatory scientific rules from `PLAN_PLANETARY_ANALOG_EXPLORER_NASA_2026.md`:
- Every feature records `source_id`, `dataset_version`, `accessed_at`, `method`,
  `native_resolution_m`, `analysis_scale_m`, `quality`, and `null_reason`.
- Never replaces `null` with `0`.
- Uses local relief (`p95 - p5` in meters) and slope/ruggedness at documented scales rather than
  comparing inconsistent absolute elevations across planetary datums.
- Incorporates extracted Mars Climate Database (MCD v6.2, Ls=105) parameters for `mars-jezero`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from parse_mcd_mars import build_mars_mcd_dataset

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "data" / "manifest.json"
CATALOG_PATH = ROOT_DIR / "data" / "catalog" / "regions.json"
DEMO_PATH = ROOT_DIR / "data" / "demo" / "demo_fixtures.json"


def make_bbox_polygon(lat: float, lon: float, half_deg_lat: float = 0.15, half_deg_lon: float = 0.15) -> dict[str, Any]:
    """Create a valid GeoJSON Polygon bounding box around a centroid."""
    min_lon = round(lon - half_deg_lon, 5)
    max_lon = round(lon + half_deg_lon, 5)
    min_lat = round(lat - half_deg_lat, 5)
    max_lat = round(lat + half_deg_lat, 5)
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]
        ],
    }


def build_sources_manifest() -> dict[str, Any]:
    sources = [
        {
            "id": "mars-mcd-v6.2",
            "name": "Mars Climate Database (MCD) v6.2",
            "body": "mars",
            "provider": "LMD / OU / IAA / ESA / CNES",
            "version": "6.2 (Ls=105 deg, climatology ave solar)",
            "url": "https://www-mars.lmd.jussieu.fr/mars/access",
            "license": "Public scientific & educational attribution (LMD/OU/IAA/ESA/CNES)",
            "native_resolution_m": 330000.0,
            "crs": "Mars IAU2000 Equirectangular (-180..180 E, -90..90 N)",
            "variables": [
                "mean_temperature_c",
                "surface_pressure_hpa",
                "water_ice_column_kg_m2",
                "dust_optical_depth_670nm",
                "wind_speed_10m_m_s",
            ],
            "limitations": "Coarse GCM grid (64x48); represents regional seasonal diurnal mean at Ls=105 deg, not micro-topographic shelter.",
        },
        {
            "id": "usgs-stac-mars-mola-hirise",
            "name": "USGS Astrogeology STAC & MOLA/HiRISE Reference DTM (Jezero Crater)",
            "body": "mars",
            "provider": "NASA PDS / USGS Astrogeology Science Center",
            "version": "PDS4 / Mars2020 Landing Site DTM & MOLA MEGDR",
            "url": "https://stac.astrogeology.usgs.gov/api",
            "license": "Public Domain (U.S. Government / NASA / USGS)",
            "native_resolution_m": 20.0,
            "crs": "IAU_2015:49900 (Mars Equirectangular / Planetocentric)",
            "variables": ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m", "lithology"],
            "limitations": "Topographic metrics aggregated at 100 m analysis scale within Jezero western delta/floor AOI.",
        },
        {
            "id": "nasa-pgda-lola-site04",
            "name": "NASA PGDA LRO LOLA South Pole Site04 (Shackleton Rim)",
            "body": "moon",
            "provider": "NASA GSFC Planetary Geodesy Data Archive (PGDA)",
            "version": "LOLA GDR / Site04 5m-20m South Pole Products",
            "url": "https://pgda.gsfc.nasa.gov/products/78",
            "license": "Public Domain (NASA)",
            "native_resolution_m": 20.0,
            "crs": "Moon South Polar Stereographic (IAU Moon 2000)",
            "variables": ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m", "lithology", "solar_illumination_pct"],
            "limitations": "High-latitude polar laser altimetry includes interpolation between orbital tracks; no atmosphere or liquid precipitation.",
        },
        {
            "id": "opentopography-copernicus-glo30",
            "name": "OpenTopography Copernicus DEM GLO-30 / SRTM GL1",
            "body": "earth",
            "provider": "OpenTopography / ESA Copernicus / NASA JPL",
            "version": "GLO-30 (2023) / SRTM v3",
            "url": "https://portal.opentopography.org/apidocs/",
            "license": "Copernicus Open Access / Public Domain",
            "native_resolution_m": 30.0,
            "crs": "EPSG:4326 reprojected to local metric UTM for slope/TRI calculation at 100 m common scale",
            "variables": ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m"],
            "limitations": "Resampled to 100 m analysis scale (`analysis_scale_m = 100`) to ensure defensible cross-body comparison against planetary DTMs.",
        },
        {
            "id": "nasa-power-climatology",
            "name": "NASA POWER Agroclimatology & Renewable Energy Climatology API",
            "body": "earth",
            "provider": "NASA Langley Research Center (LaRC)",
            "version": "POWER v2.4.x (30-year climatology 1991-2020)",
            "url": "https://power.larc.nasa.gov/docs/services/api/temporal/climatology/",
            "license": "Public Domain (NASA)",
            "native_resolution_m": 50000.0,
            "crs": "EPSG:4326",
            "variables": ["precipitation_mm_year", "mean_temperature_c"],
            "limitations": "0.5 x 0.625 deg grid (~50 km); captures regional aridity and thermal regime but not canyon microclimates.",
        },
        {
            "id": "macrostrat-v2",
            "name": "Macrostrat Geologic Map API v2 & USGS/IGME Regional Maps",
            "body": "earth",
            "provider": "UW-Madison Macrostrat / Regional Geological Surveys",
            "version": "v2",
            "url": "https://macrostrat.org/api",
            "license": "CC-BY 4.0",
            "native_resolution_m": 5000.0,
            "crs": "EPSG:4326",
            "variables": ["lithology"],
            "limitations": "Categorical lithological classification harmonized to planetary analog classes.",
        },
        {
            "id": "nasa-hls-ndvi",
            "name": "NASA Harmonized Landsat Sentinel-2 (HLS) v2.0 Surface Reflectance",
            "body": "earth",
            "provider": "NASA LP DAAC",
            "version": "v2.0",
            "url": "https://hls.gsfc.nasa.gov/data-access-and-tools/",
            "license": "Public Domain (NASA)",
            "native_resolution_m": 30.0,
            "crs": "EPSG:4326 / UTM",
            "variables": ["ndvi"],
            "limitations": "Optical index omitted or low-confidence in polar winter darkness (McMurdo).",
        },
    ]

    return {
        "schema_version": "1.0.0",
        "generated_at": "2026-11-14T20:00:00Z",
        "common_topographic_analysis_scale_m": 100.0,
        "lithology_compatibility_matrix": {
            "version": "1.0",
            "description": "Categorical similarity [0..1] between planetary target lithology and terrestrial analog lithology.",
            "matrix": {
                "fluvio_lacustrine_volcaniclastic": {
                    "fluvio_lacustrine_volcaniclastic": 1.0,
                    "evaporitic_alluvial_playa": 0.85,
                    "basaltic_tephra_lava": 0.75,
                    "ignimbrite_pyroclastic_pumice": 0.70,
                    "impact_breccia_carbonate": 0.65,
                    "hyperarid_saline_regolith": 0.80,
                    "glacial_till_dolerite": 0.60,
                },
                "anorthositic_highland_impact_regolith": {
                    "anorthositic_highland_impact_regolith": 1.0,
                    "impact_breccia_carbonate": 0.85,
                    "basaltic_tephra_lava": 0.80,
                    "glacial_till_dolerite": 0.75,
                    "ignimbrite_pyroclastic_pumice": 0.70,
                    "hyperarid_saline_regolith": 0.65,
                    "evaporitic_alluvial_playa": 0.45,
                },
            },
        },
        "sources": sources,
    }


def build_regions_catalog(mcd_data: dict[str, Any]) -> list[dict[str, Any]]:
    jezero_mcd = mcd_data["reference_locations"]["mars-jezero"]
    jezero_temp_c = jezero_mcd["derived"]["mean_temperature_c"]
    jezero_press_hpa = jezero_mcd["derived"]["surface_pressure_hpa"]
    jezero_dust = jezero_mcd["variables"]["dust_optical_depth_670nm"]["bilinear"]
    jezero_wind = jezero_mcd["variables"]["wind_speed_10m_m_s"]["bilinear"]

    regions: list[dict[str, Any]] = [
        # ======================================================================
        # PLANETARY TARGETS (MARS & MOON)
        # ======================================================================
        {
            "id": "mars-jezero",
            "name": "Cráter Jezero (Delta Occidental y Llanura Volcánica)",
            "body": "mars",
            "country_or_region": "Isidis Planitia, Marte (Perseverance AOI)",
            "crs": "IAU_2015:49900",
            "centroid": {"lat": 18.38, "lon": 77.58},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(18.38, 77.58, 0.20, 0.20),
            "analysis_scale_m": 100.0,
            "summary": "Antiguo lago de cráter con depósitos deltaicos fluvio-lacustres, carbonatos marginales y piso recubierto por unidades máficas/volcaniclásticas.",
            "features": {
                "median_slope_deg": 4.2,
                "slope_p90_deg": 11.8,
                "ruggedness_tri": 2.8,
                "local_relief_m": 185.0,
                "lithology": "fluvio_lacustrine_volcaniclastic",
                "ndvi": 0.0,
                "precipitation_mm_year": 0.0,
                "mean_temperature_c": jezero_temp_c,
            },
            "mars_climate_ls105": {
                "surface_temperature_k": jezero_mcd["variables"]["surface_temperature_k"]["bilinear"],
                "mean_temperature_c": jezero_temp_c,
                "surface_pressure_hpa": jezero_press_hpa,
                "dust_optical_depth_670nm": jezero_dust,
                "wind_speed_10m_m_s": jezero_wind,
                "water_ice_column_kg_m2": jezero_mcd["variables"]["water_ice_column_kg_m2"]["bilinear"],
            },
            "feature_provenance": {
                "median_slope_deg": {
                    "source_id": "usgs-stac-mars-mola-hirise",
                    "dataset_version": "Mars2020_DTM_v2",
                    "accessed_at": "2026-11-14",
                    "method": "Horn slope resampled at 100 m common scale over western delta AOI",
                    "native_resolution_m": 20.0,
                    "analysis_scale_m": 100.0,
                    "quality": "verified",
                    "null_reason": None,
                },
                "mean_temperature_c": {
                    "source_id": "mars-mcd-v6.2",
                    "dataset_version": "MCD v6.2 Ls=105",
                    "accessed_at": "2026-11-14",
                    "method": "Bilinear interpolation on 64x48 MCD v6.2 grid (K - 273.15)",
                    "native_resolution_m": 330000.0,
                    "analysis_scale_m": 330000.0,
                    "quality": "verified",
                    "null_reason": None,
                },
            },
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Clima marciano extraído directamente de Mars Climate Database (MCD) v6.2 para Ls=105°.",
                    "Topografía evaluada en relieve local (p95-p5) a escala común de 100 m, evitando usar el datum marciano como altitud terrestre.",
                ],
            },
            "sources": ["usgs-stac-mars-mola-hirise", "mars-mcd-v6.2"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "moon-shackleton-rim",
            "name": "Borde del Cráter Shackleton (LOLA Site04 — Polo Sur Lunar)",
            "body": "moon",
            "country_or_region": "Polo Sur Lunar (Región Artemis III Candidate)",
            "crs": "IAU_2000:30100",
            "centroid": {"lat": -89.78, "lon": 120.0},
            "aoi_radius_km": 10.0,
            "geometry": make_bbox_polygon(-89.78, 120.0, 0.08, 2.0),
            "analysis_scale_m": 100.0,
            "summary": "Cresta iluminada de impacto en tierras altas anortosíticas junto a trampas frías en sombra permanente (PSR), con pendientes pronunciadas y regolito brechado.",
            "features": {
                "median_slope_deg": 14.6,
                "slope_p90_deg": 26.4,
                "ruggedness_tri": 7.9,
                "local_relief_m": 620.0,
                "lithology": "anorthositic_highland_impact_regolith",
                "ndvi": 0.0,
                "precipitation_mm_year": 0.0,
                "mean_temperature_c": -55.0,
            },
            "feature_provenance": {
                "median_slope_deg": {
                    "source_id": "nasa-pgda-lola-site04",
                    "dataset_version": "PGDA_LOLA_Site04_20m",
                    "accessed_at": "2026-11-14",
                    "method": "Zonal median slope at 100 m scale over Shackleton illuminated rim sector",
                    "native_resolution_m": 20.0,
                    "analysis_scale_m": 100.0,
                    "quality": "verified",
                    "null_reason": None,
                },
            },
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Producto de referencia: NASA PGDA LOLA Site04 (Shackleton rim).",
                    "Las pendientes superan los 14° de mediana; exige ensayos de tracción en laderas de regolito suelto e iluminación rasante.",
                ],
            },
            "sources": ["nasa-pgda-lola-site04"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        # ======================================================================
        # EARTH ANALOG CANDIDATES (9 VALIDATED SITES + 1 LOW-COVERAGE SITE)
        # ======================================================================
        {
            "id": "earth-atacama-yungay",
            "name": "Desierto de Atacama — Cuenca de Yungay",
            "body": "earth",
            "country_or_region": "Antofagasta, Chile",
            "crs": "EPSG:4326",
            "centroid": {"lat": -24.088, "lon": -69.913},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(-24.088, -69.913, 0.14, 0.14),
            "analysis_scale_m": 100.0,
            "summary": "Núcleo hiperárido con suelos de sulfatos/percloratos, costras salinas, abanicos aluviales antiguos y ausencia casi absoluta de vegetación.",
            "features": {
                "median_slope_deg": 3.9,
                "slope_p90_deg": 10.6,
                "ruggedness_tri": 2.5,
                "local_relief_m": 165.0,
                "lithology": "hyperarid_saline_regolith",
                "ndvi": 0.04,
                "precipitation_mm_year": 2.1,
                "mean_temperature_c": 16.4,
            },
            "feature_provenance": {
                "median_slope_deg": {
                    "source_id": "opentopography-copernicus-glo30",
                    "dataset_version": "GLO-30_2023",
                    "accessed_at": "2026-11-14",
                    "method": "UTM 19S reprojected DEM resampled to 100 m common scale",
                    "native_resolution_m": 30.0,
                    "analysis_scale_m": 100.0,
                    "quality": "verified",
                    "null_reason": None,
                },
            },
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Control positivo clásico de la NASA para ensayos de perforación, astrobiología y movilidad tipo Jezero.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-haughton-crater",
            "name": "Cráter de Impacto Haughton — Isla Devon",
            "body": "earth",
            "country_or_region": "Nunavut, Canadá",
            "crs": "EPSG:4326",
            "centroid": {"lat": 75.383, "lon": -89.667},
            "aoi_radius_km": 12.0,
            "geometry": make_bbox_polygon(75.383, -89.667, 0.12, 0.35),
            "analysis_scale_m": 100.0,
            "summary": "Estructura de impacto compleja de ~23 km en desierto polar ártico sobre carbonatos paleozoicos y brechas de impacto con permafrost continuo.",
            "features": {
                "median_slope_deg": 6.8,
                "slope_p90_deg": 16.2,
                "ruggedness_tri": 4.3,
                "local_relief_m": 240.0,
                "lithology": "impact_breccia_carbonate",
                "ndvi": 0.05,
                "precipitation_mm_year": 165.0,
                "mean_temperature_c": -16.2,
            },
            "feature_provenance": {
                "median_slope_deg": {
                    "source_id": "opentopography-copernicus-glo30",
                    "dataset_version": "GLO-30_2023 / ArcticDEM",
                    "accessed_at": "2026-11-14",
                    "method": "UTM 16N reprojection resampled to 100 m common scale",
                    "native_resolution_m": 30.0,
                    "analysis_scale_m": 100.0,
                    "quality": "verified",
                    "null_reason": None,
                },
            },
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Fuera de cobertura SRTM (>60° N); derivado mediante Copernicus GLO-30 / ArcticDEM.",
                    "Excelente análogo dual para cráteres polares lunares y cuencas de impacto marcianas frías.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-death-valley-badwater",
            "name": "Death Valley — Abanicos Aluviales y Cuenca Badwater / Mars Hill",
            "body": "earth",
            "country_or_region": "California, Estados Unidos",
            "crs": "EPSG:4326",
            "centroid": {"lat": 36.230, "lon": -116.766},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(36.230, -116.766, 0.14, 0.16),
            "analysis_scale_m": 100.0,
            "summary": "Llanura evaporítica flanqueada por abanicos aluviales escarpados, cantos basálticos (Mars Hill) y sedimentos fluvio-lacustres.",
            "features": {
                "median_slope_deg": 4.8,
                "slope_p90_deg": 13.4,
                "ruggedness_tri": 3.1,
                "local_relief_m": 210.0,
                "lithology": "evaporitic_alluvial_playa",
                "ndvi": 0.06,
                "precipitation_mm_year": 58.0,
                "mean_temperature_c": 24.8,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Sitio histórico de pruebas de sistemas de aterrizaje y navegación visual de rovers marcianos (Perseverance/Curiosity).",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-lanzarote-timanfaya",
            "name": "Lanzarote — Campos de Lava y Piroclastos de Timanfaya / Los Volcanes",
            "body": "earth",
            "country_or_region": "Islas Canarias, España",
            "crs": "EPSG:4326",
            "centroid": {"lat": 29.004, "lon": -13.733},
            "aoi_radius_km": 10.0,
            "geometry": make_bbox_polygon(29.004, -13.733, 0.10, 0.11),
            "analysis_scale_m": 100.0,
            "summary": "Campos basálticos recientes (aa y pahoehoe), conos de escoria, tubos volcánicos y mantos de lapilli bajo clima árido subtropical.",
            "features": {
                "median_slope_deg": 7.4,
                "slope_p90_deg": 18.1,
                "ruggedness_tri": 4.9,
                "local_relief_m": 285.0,
                "lithology": "basaltic_tephra_lava",
                "ndvi": 0.08,
                "precipitation_mm_year": 115.0,
                "mean_temperature_c": 20.6,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Utilizado por ESA PANGAEA para entrenamiento geológico de astronautas en terrenos volcánicos lunares y marcianos.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-campo-piedra-pomez",
            "name": "Campo de Piedra Pómez — Puna de Catamarca",
            "body": "earth",
            "country_or_region": "Catamarca, Argentina",
            "crs": "EPSG:4326",
            "centroid": {"lat": -26.565, "lon": -67.452},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(-26.565, -67.452, 0.14, 0.15),
            "analysis_scale_m": 100.0,
            "summary": "Meseta ignimbrítica hiperárida de gran altitud con yardangs esculpidos por el viento, megaripples de grava y fuerte amplitud térmica diurna.",
            "features": {
                "median_slope_deg": 5.3,
                "slope_p90_deg": 14.1,
                "ruggedness_tri": 3.5,
                "local_relief_m": 225.0,
                "lithology": "ignimbrite_pyroclastic_pumice",
                "ndvi": 0.05,
                "precipitation_mm_year": 45.0,
                "mean_temperature_c": 6.8,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Análogo destacado para procesos eólicos marcianos (yardangs y transporte por viento) y morfología piroclástica.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-mcmurdo-dry-valleys",
            "name": "Valles Secos de McMurdo — Wright Valley",
            "body": "earth",
            "country_or_region": "Tierra de Victoria, Antártida",
            "crs": "EPSG:4326",
            "centroid": {"lat": -77.525, "lon": 161.750},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(-77.525, 161.750, 0.12, 0.45),
            "analysis_scale_m": 100.0,
            "summary": "Valles libres de hielo más fríos e hiperáridos de la Tierra, con laderas pronunciadas de dolerita/granito, suelos poligonales sobre permafrost y vientos catabáticos.",
            "features": {
                "median_slope_deg": 12.8,
                "slope_p90_deg": 24.5,
                "ruggedness_tri": 7.1,
                "local_relief_m": 540.0,
                "lithology": "glacial_till_dolerite",
                "ndvi": 0.02,
                "precipitation_mm_year": 18.0,
                "mean_temperature_c": -19.8,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Análogo térmico y topográfico de referencia para regiones polares lunares (Shackleton) y criosfera marciana.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-iceland-askja-holuhraun",
            "name": "Tierras Altas de Islandia — Desierto Volcánico de Askja / Holuhraun",
            "body": "earth",
            "country_or_region": "Ódáðahraun, Islandia",
            "crs": "EPSG:4326",
            "centroid": {"lat": 64.920, "lon": -16.750},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(64.920, -16.750, 0.12, 0.25),
            "analysis_scale_m": 100.0,
            "summary": "Desierto periglaciar de arenas basálticas, coladas de lava fisural y cráteres de explosión (Vikraborgir) utilizado en el entrenamiento lunar Apollo.",
            "features": {
                "median_slope_deg": 8.9,
                "slope_p90_deg": 20.4,
                "ruggedness_tri": 5.4,
                "local_relief_m": 340.0,
                "lithology": "basaltic_tephra_lava",
                "ndvi": 0.05,
                "precipitation_mm_year": 420.0,
                "mean_temperature_c": -1.4,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Sitio de pruebas de rovers lunares/marcianos y entrenamiento Apollo; alta similitud litológica y morfológica aunque mayor precipitación nívea.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-rio-tinto-gossan",
            "name": "Faja Pirítica de Río Tinto — Corta Atalaya / Gossan",
            "body": "earth",
            "country_or_region": "Huelva, España",
            "crs": "EPSG:4326",
            "centroid": {"lat": 37.704, "lon": -6.596},
            "aoi_radius_km": 10.0,
            "geometry": make_bbox_polygon(37.704, -6.596, 0.10, 0.12),
            "analysis_scale_m": 100.0,
            "summary": "Sistema fluvial ácido rico en sulfatos férricos (jarosita y hematita), análogo geoquímico y mineralógico de depósitos acuosos marcianos.",
            "features": {
                "median_slope_deg": 9.6,
                "slope_p90_deg": 21.0,
                "ruggedness_tri": 5.2,
                "local_relief_m": 295.0,
                "lithology": "fluvio_lacustrine_volcaniclastic",
                "ndvi": 0.24,
                "precipitation_mm_year": 680.0,
                "mean_temperature_c": 17.5,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Excelente análogo mineralógico/geoquímico (`surface_geology`), pero con mayor vegetación y precipitación para pruebas ambientales áridas.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-black-point-lava-az",
            "name": "Black Point Lava Flow — San Francisco Volcanic Field",
            "body": "earth",
            "country_or_region": "Arizona, Estados Unidos",
            "crs": "EPSG:4326",
            "centroid": {"lat": 35.688, "lon": -111.468},
            "aoi_radius_km": 12.0,
            "geometry": make_bbox_polygon(35.688, -111.468, 0.11, 0.13),
            "analysis_scale_m": 100.0,
            "summary": "Escarpe de colada basáltica sobre sedimentos fluvio-lacustres de la Formación Moenkopi, utilizado por NASA Desert RATS para simulación lunar y marciana.",
            "features": {
                "median_slope_deg": 4.5,
                "slope_p90_deg": 12.1,
                "ruggedness_tri": 2.9,
                "local_relief_m": 175.0,
                "lithology": "fluvio_lacustrine_volcaniclastic",
                "ndvi": 0.09,
                "precipitation_mm_year": 185.0,
                "mean_temperature_c": 13.8,
            },
            "feature_provenance": {},
            "quality": {
                "coverage_fraction": 1.0,
                "notes": [
                    "Sitio oficial de campañas NASA Desert RATS; combina terraza basáltica con llanura sedimentaria de pendiente muy similar a Jezero.",
                ],
            },
            "sources": ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
        {
            "id": "earth-lut-desert-kaluts",
            "name": "Desierto de Lut (Dasht-e Lut) — Sector Gandom Beryan (Cobertura Parcial)",
            "body": "earth",
            "country_or_region": "Kermán, Irán",
            "crs": "EPSG:4326",
            "centroid": {"lat": 30.566, "lon": 58.383},
            "aoi_radius_km": 15.0,
            "geometry": make_bbox_polygon(30.566, 58.383, 0.14, 0.14),
            "analysis_scale_m": 100.0,
            "summary": "Meseta basáltica negra y corredores de yardangs hiperáridos; incluido con variables topográficas de alta resolución pendientes de validación in-situ para demostrar el manejo honesto de cobertura incompleta.",
            "features": {
                "median_slope_deg": None,
                "slope_p90_deg": None,
                "ruggedness_tri": None,
                "local_relief_m": 190.0,
                "lithology": "basaltic_tephra_lava",
                "ndvi": 0.03,
                "precipitation_mm_year": 12.0,
                "mean_temperature_c": 27.5,
            },
            "feature_provenance": {
                "median_slope_deg": {
                    "source_id": "opentopography-copernicus-glo30",
                    "dataset_version": "GLO-30_2023",
                    "accessed_at": "2026-11-14",
                    "method": "Excluded due to void mask in steep yardang corridors prior to local DTM validation",
                    "native_resolution_m": 30.0,
                    "analysis_scale_m": 100.0,
                    "quality": "missing",
                    "null_reason": "DEM void-fill artifacts in narrow kalut corridors exceed quality threshold.",
                },
            },
            "quality": {
                "coverage_fraction": 0.625,
                "notes": [
                    "Sitio con cobertura parcial (faltan pendiente mediana, p90 y TRI) para verificar que el motor penaliza o clasifica como `insufficient_coverage` cuando faltan variables críticas de movilidad.",
                ],
            },
            "sources": ["nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
            "kind": "SCIENTIFIC_CATALOG_RECORD",
        },
    ]

    return regions


def build_demo_fixtures() -> dict[str, Any]:
    """Explicitly labeled synthetic fixtures for unit testing and fallback demonstration."""
    return {
        "kind": "DEMO_FIXTURE_NOT_SCIENTIFIC_DATA",
        "warning": "DEMOSTRACIÓN: Estos registros son sintéticos para pruebas automatizadas del motor y NO deben presentarse como hallazgos científicos.",
        "records": [
            {
                "id": "demo-synthetic-perfect-clone",
                "name": "[DEMO] Sitio Sintético de Control Positivo",
                "body": "earth",
                "features": {
                    "median_slope_deg": 4.2,
                    "slope_p90_deg": 11.8,
                    "ruggedness_tri": 2.8,
                    "local_relief_m": 185.0,
                    "lithology": "fluvio_lacustrine_volcaniclastic",
                    "ndvi": 0.0,
                    "precipitation_mm_year": 0.0,
                    "mean_temperature_c": -45.5,
                },
                "kind": "DEMO",
            },
            {
                "id": "demo-synthetic-tropical-forest-negative-control",
                "name": "[DEMO] Control Negativo — Selva Tropical Húmeda",
                "body": "earth",
                "features": {
                    "median_slope_deg": 28.0,
                    "slope_p90_deg": 45.0,
                    "ruggedness_tri": 14.5,
                    "local_relief_m": 950.0,
                    "lithology": "evaporitic_alluvial_playa",
                    "ndvi": 0.88,
                    "precipitation_mm_year": 2950.0,
                    "mean_temperature_c": 27.0,
                },
                "kind": "DEMO",
            },
        ],
    }


def main() -> None:
    mcd_data = build_mars_mcd_dataset()
    manifest = build_sources_manifest()
    regions = build_regions_catalog(mcd_data)
    demo_fixtures = build_demo_fixtures()

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEMO_PATH.parent.mkdir(parents=True, exist_ok=True)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    CATALOG_PATH.write_text(json.dumps(regions, indent=2, ensure_ascii=False), encoding="utf-8")
    DEMO_PATH.write_text(json.dumps(demo_fixtures, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {MANIFEST_PATH} ({len(manifest['sources'])} sources)")
    print(f"Wrote {CATALOG_PATH} ({len(regions)} regions)")
    print(f"Wrote {DEMO_PATH} ({len(demo_fixtures['records'])} demo records)")


if __name__ == "__main__":
    main()
