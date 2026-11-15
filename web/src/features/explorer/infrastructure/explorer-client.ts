import {
  CompareResponseSchema,
  CoordinateAnalyzeResponseSchema,
} from "./explorer-api-types";
import {
  evaluateAndRankLocal,
  haversineKm,
  parseNaturalQueryClient,
  REGIONS_CATALOG,
} from "../domain/explorer-catalog";
import {
  DirectionMode,
  MissionProfile,
  RegionFeatures,
  RegionProfile,
  SiteComparisonResult,
} from "../domain/explorer-types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function runComparisonRequest(params: {
  targetId: string;
  missionProfile: MissionProfile;
  direction: DirectionMode;
  weights: Partial<Record<keyof RegionFeatures, number>>;
  minCoverage?: number;
}): Promise<{
  results: SiteComparisonResult[];
  sourceMode: "backend-api" | "offline-catalog";
}> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        target_id: params.targetId,
        mission_profile: params.missionProfile,
        direction: params.direction,
        weights: params.weights,
        min_coverage: params.minCoverage ?? 0.7,
      }),
    });
    if (res.ok) {
      const data = (await res.json()) as CompareResponseSchema;
      return { results: data.results, sourceMode: "backend-api" };
    }
  } catch {
    // Fallback to deterministic local engine on identical catalog
  }

  const target =
    REGIONS_CATALOG.find((r) => r.id === params.targetId) ?? REGIONS_CATALOG[0];
  const candidates =
    params.direction === "planet_to_earth"
      ? REGIONS_CATALOG.filter((r) => r.body === "earth")
      : REGIONS_CATALOG.filter((r) => r.body === "mars" || r.body === "moon");

  return {
    results: evaluateAndRankLocal(
      target,
      candidates,
      params.weights,
      params.minCoverage ?? 0.7,
    ),
    sourceMode: "offline-catalog",
  };
}

export async function analyzeCoordinatesRequest(params: {
  lat: number;
  lon: number;
  radiusKm: number;
  missionProfile: MissionProfile;
}): Promise<CoordinateAnalyzeResponseSchema> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/earth-aoi/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        lat: params.lat,
        lon: params.lon,
        radius_km: params.radiusKm,
        mission_profile: params.missionProfile,
      }),
    });
    if (res.ok) {
      return (await res.json()) as CoordinateAnalyzeResponseSchema;
    }
  } catch {
    // Offline fallback using exact same haversine AOI validation logic
  }

  const earthSites = REGIONS_CATALOG.filter((r) => r.body === "earth");
  let closestSite: RegionProfile | null = null;
  let closestDist = Infinity;

  for (const site of earthSites) {
    const d = haversineKm(
      params.lat,
      params.lon,
      site.centroid.lat,
      site.centroid.lon,
    );
    if (d < closestDist) {
      closestDist = d;
      closestSite = site;
    }
  }

  if (!closestSite) {
    return {
      status: "out_of_coverage",
      message: "Sin datos procesados para esta área.",
      query: { lat: params.lat, lon: params.lon, radius_km: params.radiusKm },
      matched_region: null,
      distance_to_centroid_km: null,
      planetary_matches: [],
    };
  }

  const thresholdKm = closestSite.aoi_radius_km + params.radiusKm;
  if (closestDist > thresholdKm) {
    return {
      status: "out_of_coverage",
      message: `Sin datos procesados para esta área (${params.lat.toFixed(3)}°, ${params.lon.toFixed(3)}°). El sitio validado más cercano es '${closestSite.name}' a ${closestDist.toFixed(1)} km (fuera del radio AOI de ${thresholdKm.toFixed(0)} km).`,
      query: { lat: params.lat, lon: params.lon, radius_km: params.radiusKm },
      matched_region: null,
      distance_to_centroid_km: Number(closestDist.toFixed(1)),
      planetary_matches: [],
    };
  }

  const planetaryTargets = REGIONS_CATALOG.filter(
    (r) => r.body === "mars" || r.body === "moon",
  );
  const matches = evaluateAndRankLocal(closestSite, planetaryTargets, {
    median_slope_deg: 0.35,
    slope_p90_deg: 0.25,
    ruggedness_tri: 0.25,
    local_relief_m: 0.15,
  });

  return {
    status: "matched_aoi",
    message: `Coordenada dentro del AOI validada de '${closestSite.name}' (distancia al centroide: ${closestDist.toFixed(1)} km).`,
    query: { lat: params.lat, lon: params.lon, radius_km: params.radiusKm },
    matched_region: closestSite,
    distance_to_centroid_km: Number(closestDist.toFixed(1)),
    planetary_matches: matches,
  };
}

export { parseNaturalQueryClient };
