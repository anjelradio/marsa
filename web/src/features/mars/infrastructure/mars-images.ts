import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";
import type { MarsCoordinates } from "./mars-climate";

const marsImagesSchema = z.array(z.object({
  id: z.string(),
  source: z.enum(["HiRISE", "Viking"]),
  preview_url: z.url({ protocol: /^https$/ }),
}));

export type MarsImage = z.infer<typeof marsImagesSchema>[number];
export type MarsImageView = "regional" | "detail";

export function requestMarsImages(
  point: MarsCoordinates,
  view: MarsImageView,
  signal: AbortSignal,
  fallbackMessage: string,
) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({
    lat: String(point.latitude),
    lon: String(point.longitude),
    view,
  });

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/cuerpo-celeste/marte/imagenes?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema: marsImagesSchema,
    mapData: (data) => data,
  });
}
