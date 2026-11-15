import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";

export type AnalogDestination = "marte" | "luna";

const detailSchema = z.object({
  caracteristica: z.string(),
  unidad: z.string().nullable(),
  valor_tierra: z.number(),
  valor_destino: z.number(),
  similitud: z.number(),
});

const rankingItemSchema = z.object({
  posicion: z.number(),
  sitio_tierra_id: z.number(),
  sitio_tierra: z.string(),
  tipo: z.string().nullable(),
  geom: z.unknown().nullable(),
  sitio_destino_id: z.number(),
  sitio_destino: z.string(),
  similitud: z.number(),
  cobertura: z.number(),
  metodo: z.string(),
  coincide: z.string(),
  difiere: z.string(),
  detalle: z.array(detailSchema),
});

const rankingSchema = z.array(rankingItemSchema);

export type AnalogDetail = z.infer<typeof detailSchema>;
export type AnalogRankingItem = z.infer<typeof rankingItemSchema>;

export function requestAnalogRanking(
  destination: AnalogDestination,
  signal: AbortSignal,
  fallbackMessage: string,
) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({ destino: destination });

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/analogia/ranking?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema: rankingSchema,
    mapData: (data) => data,
  });
}
