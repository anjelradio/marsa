import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";

const earthClimateSchema = z.object({
  coordinates: z.object({ latitude: z.number(), longitude: z.number() }),
  source: z.string(),
  values: z.object({
    surface_temperature_k: z.number(),
    surface_pressure_pa: z.number(),
    cloud_cover_pct: z.number(),
    aerosol_optical_depth: z.number(),
    wind_10m_m_s: z.number(),
  }),
});

export type EarthClimate = z.infer<typeof earthClimateSchema>;

export function requestEarthClimate(point: GeoPoint, signal: AbortSignal, fallbackMessage: string) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({
    lat: String(point.latitude),
    lon: String(point.longitude),
  });

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/cuerpo-celeste/tierra/clima?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema: earthClimateSchema,
    mapData: (data) => data,
  });
}
