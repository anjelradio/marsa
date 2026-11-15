import {
  ClassificationStatus,
  DataSourceRecord,
  FeatureBreakdown,
  MissionProfile,
  MISSION_PROFILES,
  RegionFeatures,
  RegionProfile,
  SiteComparisonResult,
} from "./explorer-types";

export const SCIENTIFIC_SOURCES: DataSourceRecord[] = [
  {
    id: "mars-mcd-v6.2",
    name: "Mars Climate Database (MCD) v6.2 (Ls=105°)",
    body: "mars",
    provider: "LMD / OU / IAA / ESA / CNES",
    version: "v6.2 (climatology ave solar)",
    url: "https://www-mars.lmd.jussieu.fr/mars/access",
    license: "Public scientific attribution (LMD/OU/IAA/ESA/CNES)",
    native_resolution_m: 330000,
    crs: "IAU2000 Mars Equirectangular (64x48 grid)",
    variables: ["mean_temperature_c", "surface_pressure_hpa", "dust_optical_depth_670nm", "wind_speed_10m_m_s"],
    limitations: "Cuadrícula climática global 64x48; describe media diurna estacional en Ls=105°, no microclimas locales.",
  },
  {
    id: "usgs-stac-mars-mola-hirise",
    name: "USGS Astrogeology STAC API & NASA PDS MOLA/HiRISE",
    body: "mars",
    provider: "USGS Astrogeology / NASA PDS",
    version: "PDS4 Mars2020 DTM & MEGDR",
    url: "https://stac.astrogeology.usgs.gov/api",
    license: "Public Domain (NASA / USGS)",
    native_resolution_m: 20,
    crs: "IAU_2015:49900",
    variables: ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m", "lithology"],
    limitations: "Remuestreado a escala común de 100 m sobre el AOI del delta occidental de Jezero.",
  },
  {
    id: "nasa-pgda-lola-site04",
    name: "NASA PGDA LRO LOLA South Pole Site04 (Shackleton Rim)",
    body: "moon",
    provider: "NASA GSFC PGDA",
    version: "LOLA Site04 20m",
    url: "https://pgda.gsfc.nasa.gov/products/78",
    license: "Public Domain (NASA)",
    native_resolution_m: 20,
    crs: "IAU_2000:30100 South Polar Stereographic",
    variables: ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m", "lithology"],
    limitations: "Altimetría láser polar con interpolación entre trazas orbitales; sin atmósfera.",
  },
  {
    id: "opentopography-copernicus-glo30",
    name: "OpenTopography API — Copernicus DEM GLO-30 / SRTM",
    body: "earth",
    provider: "OpenTopography / ESA / NASA",
    version: "GLO-30 (2023)",
    url: "https://portal.opentopography.org/apidocs/",
    license: "Copernicus Open Access / Public Domain",
    native_resolution_m: 30,
    crs: "EPSG:4326 -> UTM métrico local (escala 100 m)",
    variables: ["median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m"],
    limitations: "Homogeneizado a 100 m de escala espacial para comparación defendible Tierra ↔ Marte/Luna.",
  },
  {
    id: "nasa-power-climatology",
    name: "NASA POWER Climatology API",
    body: "earth",
    provider: "NASA Langley Research Center (LaRC)",
    version: "POWER v2.4 (1991-2020)",
    url: "https://power.larc.nasa.gov/docs/services/api/temporal/climatology/",
    license: "Public Domain (NASA)",
    native_resolution_m: 50000,
    crs: "EPSG:4326",
    variables: ["precipitation_mm_year", "mean_temperature_c"],
    limitations: "Resolución ~50 km; representa aridez regional, no microclimas de cañón.",
  },
  {
    id: "macrostrat-v2",
    name: "Macrostrat Geologic API v2",
    body: "earth",
    provider: "UW-Madison Macrostrat",
    version: "v2",
    url: "https://macrostrat.org/api",
    license: "CC-BY 4.0",
    native_resolution_m: 5000,
    crs: "EPSG:4326",
    variables: ["lithology"],
    limitations: "Categorías litológicas armonizadas a clases de análogos planetarios.",
  },
  {
    id: "nasa-hls-ndvi",
    name: "NASA Harmonized Landsat Sentinel-2 (HLS)",
    body: "earth",
    provider: "NASA LP DAAC",
    version: "v2.0",
    url: "https://hls.gsfc.nasa.gov/data-access-and-tools/",
    license: "Public Domain (NASA)",
    native_resolution_m: 30,
    crs: "EPSG:4326",
    variables: ["ndvi"],
    limitations: "Índice óptico de vegetación terrestre para verificar exposición de suelo desnudo.",
  },
];

export const REGIONS_CATALOG: RegionProfile[] = [
  {
    id: "mars-jezero",
    name: "Cráter Jezero (Delta Occidental y Llanura Volcánica)",
    body: "mars",
    country_or_region: "Isidis Planitia, Marte (Perseverance AOI)",
    crs: "IAU_2015:49900",
    centroid: { lat: 18.38, lon: 77.58 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Antiguo lago de cráter con depósitos deltaicos fluvio-lacustres, carbonatos marginales y piso recubierto por unidades máficas/volcaniclásticas.",
    features: {
      median_slope_deg: 4.2,
      slope_p90_deg: 11.8,
      ruggedness_tri: 2.8,
      local_relief_m: 185,
      lithology: "fluvio_lacustrine_volcaniclastic",
      ndvi: 0,
      precipitation_mm_year: 0,
      mean_temperature_c: -45.5,
    },
    mars_climate_ls105: {
      surface_temperature_k: 227.65,
      mean_temperature_c: -45.5,
      surface_pressure_hpa: 6.451,
      dust_optical_depth_670nm: 0.252,
      wind_speed_10m_m_s: 6.36,
      water_ice_column_kg_m2: 0.00232,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: [
        "Clima marciano extraído de Mars Climate Database (MCD v6.2) en Ls=105° (227.65 K / -45.5 °C, 6.45 hPa, viento 6.36 m/s).",
        "Topografía calculada en relieve local (p95-p5) a escala común de 100 m.",
      ],
    },
    sources: ["usgs-stac-mars-mola-hirise", "mars-mcd-v6.2"],
  },
  {
    id: "moon-shackleton-rim",
    name: "Borde del Cráter Shackleton (LOLA Site04 — Polo Sur Lunar)",
    body: "moon",
    country_or_region: "Polo Sur Lunar (Región Candidata Artemis)",
    crs: "IAU_2000:30100",
    centroid: { lat: -89.78, lon: 120.0 },
    aoi_radius_km: 10,
    analysis_scale_m: 100,
    summary:
      "Cresta iluminada de impacto en tierras altas anortosíticas junto a trampas frías en sombra permanente (PSR), con pendientes pronunciadas y regolito brechado.",
    features: {
      median_slope_deg: 14.6,
      slope_p90_deg: 26.4,
      ruggedness_tri: 7.9,
      local_relief_m: 620,
      lithology: "anorthositic_highland_impact_regolith",
      ndvi: 0,
      precipitation_mm_year: 0,
      mean_temperature_c: -55.0,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: [
        "Referencia oficial NASA PGDA LOLA Site04 (Shackleton rim).",
        "Exige pruebas de tracción en laderas de >14° y navegación con iluminación solar rasante.",
      ],
    },
    sources: ["nasa-pgda-lola-site04"],
  },
  {
    id: "earth-atacama-yungay",
    name: "Desierto de Atacama — Cuenca de Yungay",
    body: "earth",
    country_or_region: "Antofagasta, Chile",
    crs: "EPSG:4326",
    centroid: { lat: -24.088, lon: -69.913 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Núcleo hiperárido con suelos de sulfatos/percloratos, costras salinas, abanicos aluviales antiguos y ausencia casi total de vegetación.",
    features: {
      median_slope_deg: 3.9,
      slope_p90_deg: 10.6,
      ruggedness_tri: 2.5,
      local_relief_m: 165,
      lithology: "hyperarid_saline_regolith",
      ndvi: 0.04,
      precipitation_mm_year: 2.1,
      mean_temperature_c: 16.4,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Control positivo clásico de NASA para ensayos de movilidad y perforación astrobiológica tipo Jezero."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-black-point-lava-az",
    name: "Black Point Lava Flow — San Francisco Volcanic Field",
    body: "earth",
    country_or_region: "Arizona, Estados Unidos",
    crs: "EPSG:4326",
    centroid: { lat: 35.688, lon: -111.468 },
    aoi_radius_km: 12,
    analysis_scale_m: 100,
    summary:
      "Escarpe de colada basáltica sobre sedimentos fluvio-lacustres de la Formación Moenkopi, utilizado por NASA Desert RATS para simulación lunar y marciana.",
    features: {
      median_slope_deg: 4.5,
      slope_p90_deg: 12.1,
      ruggedness_tri: 2.9,
      local_relief_m: 175,
      lithology: "fluvio_lacustrine_volcaniclastic",
      ndvi: 0.09,
      precipitation_mm_year: 185,
      mean_temperature_c: 13.8,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Sitio de campañas NASA Desert RATS; pendiente y contacto volcano-sedimentario muy cercanos a Jezero."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-death-valley-badwater",
    name: "Death Valley — Cuenca Badwater y Mars Hill",
    body: "earth",
    country_or_region: "California, Estados Unidos",
    crs: "EPSG:4326",
    centroid: { lat: 36.23, lon: -116.766 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Llanura evaporítica flanqueada por abanicos aluviales escarpados, cantos basálticos (Mars Hill) y sedimentos fluvio-lacustres.",
    features: {
      median_slope_deg: 4.8,
      slope_p90_deg: 13.4,
      ruggedness_tri: 3.1,
      local_relief_m: 210,
      lithology: "evaporitic_alluvial_playa",
      ndvi: 0.06,
      precipitation_mm_year: 58,
      mean_temperature_c: 24.8,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Sitio de calibración de sensores de aterrizaje y navegación de rovers marcianos."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-campo-piedra-pomez",
    name: "Campo de Piedra Pómez — Puna de Catamarca",
    body: "earth",
    country_or_region: "Catamarca, Argentina",
    crs: "EPSG:4326",
    centroid: { lat: -26.565, lon: -67.452 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Meseta ignimbrítica hiperárida de gran altitud con yardangs esculpidos por el viento, megaripples de grava y gran amplitud térmica.",
    features: {
      median_slope_deg: 5.3,
      slope_p90_deg: 14.1,
      ruggedness_tri: 3.5,
      local_relief_m: 225,
      lithology: "ignimbrite_pyroclastic_pumice",
      ndvi: 0.05,
      precipitation_mm_year: 45,
      mean_temperature_c: 6.8,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Análogo destacado para geomorfología eólica marciana y abrasión por polvo/viento."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-haughton-crater",
    name: "Cráter de Impacto Haughton — Isla Devon",
    body: "earth",
    country_or_region: "Nunavut, Canadá",
    crs: "EPSG:4326",
    centroid: { lat: 75.383, lon: -89.667 },
    aoi_radius_km: 12,
    analysis_scale_m: 100,
    summary:
      "Estructura de impacto compleja de ~23 km en desierto polar ártico sobre carbonatos y brechas de impacto con permafrost continuo.",
    features: {
      median_slope_deg: 6.8,
      slope_p90_deg: 16.2,
      ruggedness_tri: 4.3,
      local_relief_m: 240,
      lithology: "impact_breccia_carbonate",
      ndvi: 0.05,
      precipitation_mm_year: 165,
      mean_temperature_c: -16.2,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Fuera de cobertura SRTM (>60° N); procesado con Copernicus GLO-30. Análogo dual lunar/marciano polar."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-lanzarote-timanfaya",
    name: "Lanzarote — Campos de Lava y Piroclastos de Timanfaya",
    body: "earth",
    country_or_region: "Islas Canarias, España",
    crs: "EPSG:4326",
    centroid: { lat: 29.004, lon: -13.733 },
    aoi_radius_km: 10,
    analysis_scale_m: 100,
    summary:
      "Campos basálticos recientes, conos de escoria, tubos volcánicos y mantos de lapilli bajo clima árido subtropical.",
    features: {
      median_slope_deg: 7.4,
      slope_p90_deg: 18.1,
      ruggedness_tri: 4.9,
      local_relief_m: 285,
      lithology: "basaltic_tephra_lava",
      ndvi: 0.08,
      precipitation_mm_year: 115,
      mean_temperature_c: 20.6,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Sitio de entrenamiento geológico ESA PANGAEA para misiones lunares y marcianas."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-iceland-askja-holuhraun",
    name: "Tierras Altas de Islandia — Desierto Volcánico de Askja",
    body: "earth",
    country_or_region: "Ódáðahraun, Islandia",
    crs: "EPSG:4326",
    centroid: { lat: 64.92, lon: -16.75 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Desierto periglaciar de arenas basálticas, coladas de lava fisural y cráteres de explosión utilizado en el programa Apollo.",
    features: {
      median_slope_deg: 8.9,
      slope_p90_deg: 20.4,
      ruggedness_tri: 5.4,
      local_relief_m: 340,
      lithology: "basaltic_tephra_lava",
      ndvi: 0.05,
      precipitation_mm_year: 420,
      mean_temperature_c: -1.4,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Alta similitud litológica y morfológica para rovers lunares/marcianos; mayor precipitación nívea."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-rio-tinto-gossan",
    name: "Faja Pirítica de Río Tinto — Corta Atalaya / Gossan",
    body: "earth",
    country_or_region: "Huelva, España",
    crs: "EPSG:4326",
    centroid: { lat: 37.704, lon: -6.596 },
    aoi_radius_km: 10,
    analysis_scale_m: 100,
    summary:
      "Sistema rico en sulfatos férricos (jarosita y hematita), análogo mineralógico y astrobiológico de ambientes ácidos marcianos.",
    features: {
      median_slope_deg: 9.6,
      slope_p90_deg: 21.0,
      ruggedness_tri: 5.2,
      local_relief_m: 295,
      lithology: "fluvio_lacustrine_volcaniclastic",
      ndvi: 0.24,
      precipitation_mm_year: 680,
      mean_temperature_c: 17.5,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Análogo geoquímico clave, aunque con mayor cobertura vegetal y precipitación."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
  {
    id: "earth-mcmurdo-dry-valleys",
    name: "Valles Secos de McMurdo — Wright Valley",
    body: "earth",
    country_or_region: "Tierra de Victoria, Antártida",
    crs: "EPSG:4326",
    centroid: { lat: -77.525, lon: 161.75 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Valles libres de hielo más fríos e hiperáridos de la Tierra, con laderas pronunciadas de dolerita y permafrost continuo.",
    features: {
      median_slope_deg: 12.8,
      slope_p90_deg: 24.5,
      ruggedness_tri: 7.1,
      local_relief_m: 540,
      lithology: "glacial_till_dolerite",
      ndvi: 0.02,
      precipitation_mm_year: 18,
      mean_temperature_c: -19.8,
    },
    quality: {
      coverage_fraction: 1.0,
      notes: ["Principal análogo topográfico y térmico para el borde del Cráter Shackleton (Polo Sur Lunar) y criosfera marciana."],
    },
    sources: ["opentopography-copernicus-glo30", "nasa-power-climatology", "macrostrat-v2"],
  },
  {
    id: "earth-lut-desert-kaluts",
    name: "Desierto de Lut (Dasht-e Lut) — Sector Gandom Beryan (Cobertura Parcial)",
    body: "earth",
    country_or_region: "Kermán, Irán",
    crs: "EPSG:4326",
    centroid: { lat: 30.566, lon: 58.383 },
    aoi_radius_km: 15,
    analysis_scale_m: 100,
    summary:
      "Meseta basáltica y corredores de yardangs hiperáridos; pendiente mediana y TRI excluidas por vacíos de radar en corredores estrechos.",
    features: {
      median_slope_deg: null,
      slope_p90_deg: null,
      ruggedness_tri: null,
      local_relief_m: 190,
      lithology: "basaltic_tephra_lava",
      ndvi: 0.03,
      precipitation_mm_year: 12,
      mean_temperature_c: 27.5,
    },
    quality: {
      coverage_fraction: 0.625,
      notes: [
        "Demuestra manejo científico de datos faltantes: nunca convierte null en 0 y se clasifica como evidencia insuficiente cuando la cobertura cae bajo 70%.",
      ],
    },
    sources: ["nasa-power-climatology", "macrostrat-v2", "nasa-hls-ndvi"],
  },
];

const TOLERANCES: Record<keyof RegionFeatures, number> = {
  median_slope_deg: 12.0,
  slope_p90_deg: 20.0,
  ruggedness_tri: 6.5,
  local_relief_m: 450.0,
  lithology: 1.0,
  ndvi: 0.35,
  precipitation_mm_year: 500.0,
  mean_temperature_c: 65.0,
};

const LITHOLOGY_MATRIX: Record<string, Record<string, number>> = {
  fluvio_lacustrine_volcaniclastic: {
    fluvio_lacustrine_volcaniclastic: 1.0,
    evaporitic_alluvial_playa: 0.85,
    hyperarid_saline_regolith: 0.8,
    basaltic_tephra_lava: 0.75,
    ignimbrite_pyroclastic_pumice: 0.7,
    impact_breccia_carbonate: 0.65,
    glacial_till_dolerite: 0.6,
  },
  anorthositic_highland_impact_regolith: {
    anorthositic_highland_impact_regolith: 1.0,
    impact_breccia_carbonate: 0.85,
    basaltic_tephra_lava: 0.8,
    glacial_till_dolerite: 0.75,
    ignimbrite_pyroclastic_pumice: 0.7,
    hyperarid_saline_regolith: 0.65,
    evaporitic_alluvial_playa: 0.45,
  },
};

const UNITS: Record<keyof RegionFeatures, string> = {
  median_slope_deg: "°",
  slope_p90_deg: "°",
  ruggedness_tri: "TRI",
  local_relief_m: "m",
  lithology: "clase",
  ndvi: "0..1",
  precipitation_mm_year: "mm/año",
  mean_temperature_c: "°C",
};

export function evaluateAndRankLocal(
  target: RegionProfile,
  candidates: RegionProfile[],
  weights: Partial<Record<keyof RegionFeatures, number>>,
  minCoverage = 0.7,
): SiteComparisonResult[] {
  const activeEntries = Object.entries(weights).filter(([, w]) => (w ?? 0) > 0) as [
    keyof RegionFeatures,
    number,
  ][];
  const totalWeight = activeEntries.reduce((acc, [, w]) => acc + w, 0);

  const results: SiteComparisonResult[] = candidates
    .filter((c) => c.id !== target.id)
    .map((candidate) => {
      let validWeightSum = 0;
      let weightedSimSum = 0;
      const breakdown: FeatureBreakdown[] = [];
      const limitations = [...candidate.quality.notes];

      for (const [featureKey, rawWeight] of activeEntries) {
        const weight = rawWeight / totalWeight;
        const tVal = target.features[featureKey];
        const cVal = candidate.features[featureKey];
        const unit = UNITS[featureKey];

        if (tVal === null || cVal === null) {
          breakdown.push({
            feature: featureKey,
            unit,
            weight: Number(weight.toFixed(3)),
            target_value: tVal,
            candidate_value: cVal,
            similarity: null,
            weighted_contribution: null,
            status: cVal === null ? "missing_candidate" : "missing_target",
            note: "Variable ausente por control de calidad DEM; no se reemplaza con 0.",
          });
          if (cVal === null) {
            limitations.push(`Variable ${featureKey} no disponible en este sitio.`);
          }
          continue;
        }

        let sim = 0;
        if (featureKey === "lithology") {
          const tStr = String(tVal);
          const cStr = String(cVal);
          sim =
            tStr === cStr
              ? 1.0
              : LITHOLOGY_MATRIX[tStr]?.[cStr] ?? LITHOLOGY_MATRIX[cStr]?.[tStr] ?? 0.5;
        } else {
          const diff = Math.abs(Number(cVal) - Number(tVal));
          sim = Math.max(0, 1 - diff / TOLERANCES[featureKey]);
        }

        const roundedSim = Number(sim.toFixed(4));
        const contrib = Number((weight * roundedSim).toFixed(4));
        validWeightSum += weight;
        weightedSimSum += contrib;

        breakdown.push({
          feature: featureKey,
          unit,
          weight: Number(weight.toFixed(3)),
          target_value: tVal,
          candidate_value: cVal,
          similarity: roundedSim,
          weighted_contribution: contrib,
          status: "evaluated",
        });
      }

      const coverage = Number(validWeightSum.toFixed(3));
      let score: number | null = null;
      let classification: ClassificationStatus = "not_evaluated";

      if (validWeightSum > 0) {
        score = Number(((100 * weightedSimSum) / validWeightSum).toFixed(1));
        classification = coverage >= minCoverage ? "suitable" : "insufficient_coverage";
      }

      if (classification === "insufficient_coverage") {
        limitations.push(
          `Cobertura de datos (${Math.round(coverage * 100)}%) inferior al umbral mínimo requerido (${Math.round(minCoverage * 100)}%).`,
        );
      }

      return {
        site_id: candidate.id,
        site_name: candidate.name,
        body: candidate.body,
        country_or_region: candidate.country_or_region,
        centroid: candidate.centroid,
        score,
        coverage,
        classification,
        breakdown,
        limitations,
        sources: candidate.sources,
      };
    });

  const prio: Record<ClassificationStatus, number> = {
    suitable: 2,
    insufficient_coverage: 1,
    not_evaluated: 0,
  };

  return results.sort((a, b) => {
    if (prio[b.classification] !== prio[a.classification]) {
      return prio[b.classification] - prio[a.classification];
    }
    if (a.classification === "suitable") {
      return (b.score ?? -1) - (a.score ?? -1);
    }
    return b.coverage - a.coverage;
  });
}

export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function parseNaturalQueryClient(query: string): {
  body: "mars" | "moon";
  targetId: string;
  missionProfile: MissionProfile;
  weights: Partial<Record<keyof RegionFeatures, number>>;
  summary: string;
} {
  const q = query.toLowerCase();
  const isMoon =
    q.includes("luna") || q.includes("lunar") || q.includes("shackleton") || q.includes("polo sur");
  const body: "mars" | "moon" = isMoon ? "moon" : "mars";
  const targetId = isMoon ? "moon-shackleton-rim" : "mars-jezero";

  let missionProfile: MissionProfile = "rover_mobility";
  if (q.includes("geolog") || q.includes("volcán") || q.includes("volcan") || q.includes("litolog") || q.includes("mineral")) {
    missionProfile = "surface_geology";
  } else if (q.includes("ambiental") || q.includes("desierto") || q.includes("frío") || q.includes("frio") || q.includes("clima")) {
    missionProfile = "environmental_testing";
  }

  const weights: Partial<Record<keyof RegionFeatures, number>> = {
    ...MISSION_PROFILES[missionProfile].defaultWeights,
  };

  if (q.includes("pendientes suaves") || q.includes("pendiente suave") || q.includes("llano")) {
    weights.median_slope_deg = Number(((weights.median_slope_deg ?? 0.25) + 0.2).toFixed(2));
  }
  if (q.includes("seco") || q.includes("árido") || q.includes("arido") || q.includes("poca vegetación")) {
    weights.precipitation_mm_year = Number(((weights.precipitation_mm_year ?? 0.15) + 0.2).toFixed(2));
    weights.ndvi = Number(((weights.ndvi ?? 0.1) + 0.15).toFixed(2));
  }
  if (q.includes("frío") || q.includes("frio") || q.includes("polar")) {
    weights.mean_temperature_c = Number(((weights.mean_temperature_c ?? 0.15) + 0.2).toFixed(2));
  }

  return {
    body,
    targetId,
    missionProfile,
    weights,
    summary: `Objetivo: ${isMoon ? "Shackleton Rim (Luna)" : "Cráter Jezero (Marte)"} · Perfil: ${MISSION_PROFILES[missionProfile].title}`,
  };
}
