"""
Domain types and embedded offline-first scientific catalog for Planetary Analog Explorer.
Mirrors the FastAPI contracts (`/api/targets`, `/api/sites`, `/api/compare`, `/api/sources`).
"""

export type PlanetaryBody = "mars" | "moon" | "earth";
export type MissionProfile = "rover_mobility" | "surface_geology" | "environmental_testing";
export type DirectionMode = "planet_to_earth" | "earth_to_planet";
export type ClassificationStatus = "suitable" | "insufficient_coverage" | "not_evaluated";

export interface RegionFeatures {
  median_slope_deg: number | null;
  slope_p90_deg: number | null;
  ruggedness_tri: number | null;
  local_relief_m: number | null;
  lithology: string | null;
  ndvi: number | null;
  precipitation_mm_year: number | null;
  mean_temperature_c: number | null;
}

export interface MarsClimateLs105 {
  surface_temperature_k: number;
  mean_temperature_c: number;
  surface_pressure_hpa: number;
  dust_optical_depth_670nm: number;
  wind_speed_10m_m_s: number;
  water_ice_column_kg_m2: number;
}

export interface RegionProfile {
  id: string;
  name: string;
  body: PlanetaryBody;
  country_or_region: string;
  crs: string;
  centroid: { lat: number; lon: number };
  aoi_radius_km: number;
  analysis_scale_m: number;
  summary: string;
  features: RegionFeatures;
  mars_climate_ls105?: MarsClimateLs105;
  quality: {
    coverage_fraction: number;
    notes: string[];
  };
  sources: string[];
}

export interface FeatureBreakdown {
  feature: keyof RegionFeatures;
  unit: string;
  weight: number;
  target_value: number | string | null;
  candidate_value: number | string | null;
  similarity: number | null;
  weighted_contribution: number | null;
  status: string;
  note?: string | null;
}

export interface SiteComparisonResult {
  site_id: string;
  site_name: string;
  body: PlanetaryBody;
  country_or_region: string;
  centroid: { lat: number; lon: number };
  score: number | null;
  coverage: number;
  classification: ClassificationStatus;
  breakdown: FeatureBreakdown[];
  limitations: string[];
  sources: string[];
}

export interface DataSourceRecord {
  id: string;
  name: string;
  body: PlanetaryBody;
  provider: string;
  version: string;
  url: string;
  license: string;
  native_resolution_m: number;
  crs: string;
  variables: string[];
  limitations: string;
}

export const FEATURE_LABELS: Record<keyof RegionFeatures, { label: string; unit: string; badge: string }> = {
  median_slope_deg: { label: "Pendiente mediana", unit: "°", badge: "DEM 100m" },
  slope_p90_deg: { label: "Pendiente p90 (riesgo)", unit: "°", badge: "DEM 100m" },
  ruggedness_tri: { label: "Rugosidad (TRI)", unit: "índice", badge: "DEM 100m" },
  local_relief_m: { label: "Relieve local (p95-p5)", unit: "m", badge: "DEM 100m" },
  lithology: { label: "Litología / Material", unit: "clase", badge: "Macrostrat / USGS" },
  ndvi: { label: "Cobertura vegetal (NDVI)", unit: "0..1", badge: "NASA HLS" },
  precipitation_mm_year: { label: "Precipitación anual", unit: "mm/año", badge: "NASA POWER" },
  mean_temperature_c: { label: "Temperatura media", unit: "°C", badge: "MCD v6.2 / POWER" },
};

export const LITHOLOGY_LABELS: Record<string, string> = {
  fluvio_lacustrine_volcaniclastic: "Fluvio-lacustre / Volcaniclástico",
  anorthositic_highland_impact_regolith: "Anortosita / Regolito de impacto polar",
  hyperarid_saline_regolith: "Regolito salino hiperárido (sulfatos/percloratos)",
  impact_breccia_carbonate: "Brecha de impacto / Carbonatos",
  evaporitic_alluvial_playa: "Playa evaporítica / Abanico aluvial",
  basaltic_tephra_lava: "Coladas basálticas / Tefra y piroclastos",
  ignimbrite_pyroclastic_pumice: "Ignimbrita / Pómez piroclástica eólica",
  glacial_till_dolerite: "Till glaciar hiperárido / Dolerita",
};

export const MISSION_PROFILES: Record<
  MissionProfile,
  { title: string; subtitle: string; defaultWeights: Partial<Record<keyof RegionFeatures, number>> }
> = {
  rover_mobility: {
    title: "Movilidad de Rover",
    subtitle: "Prioriza tracción, pendiente mediana/p90, rugosidad TRI y relieve local a escala de 100 m.",
    defaultWeights: {
      median_slope_deg: 0.35,
      slope_p90_deg: 0.25,
      ruggedness_tri: 0.25,
      local_relief_m: 0.15,
    },
  },
  surface_geology: {
    title: "Geología de Superficie",
    subtitle: "Prioriza compatibilidad litológica, morfología de cráter/abanico y rugosidad superficial.",
    defaultWeights: {
      lithology: 0.4,
      ruggedness_tri: 0.25,
      local_relief_m: 0.2,
      median_slope_deg: 0.15,
    },
  },
  environmental_testing: {
    title: "Pruebas Ambientales",
    subtitle: "Evalúa hiperaridez, ausencia de vegetación (NDVI) y régimen térmico extremo para ensayos de instrumentos.",
    defaultWeights: {
      precipitation_mm_year: 0.35,
      ndvi: 0.25,
      mean_temperature_c: 0.2,
      median_slope_deg: 0.2,
    },
  },
};
