import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";

const coordinatesSchema = z.object({
  latitude: z.number(),
  longitude: z.number(),
});

const marsClimateSchema = z.object({
  coordinates: coordinatesSchema,
  grid_point: coordinatesSchema,
  solar_longitude_deg: z.number(),
  source: z.string(),
  values: z.object({
    surface_temperature_k: z.number(),
    surface_pressure_pa: z.number(),
    cloud_ice_kg_m2: z.number(),
    dust_optical_depth: z.number(),
    wind_10m_m_s: z.number(),
  }),
});

export type MarsCoordinates = z.infer<typeof coordinatesSchema>;
export type MarsClimate = z.infer<typeof marsClimateSchema>;

export function requestMarsClimate(
  point: MarsCoordinates,
  signal: AbortSignal,
  fallbackMessage: string,
) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({
    lat: String(point.latitude),
    lon: String(point.longitude),
  });

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/cuerpo-celeste/marte/clima?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema: marsClimateSchema,
    mapData: (data) => data,
  });
}
