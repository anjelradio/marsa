import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";
import type { AnalogDestination } from "@/features/analogs/infrastructure/analogs-ranking";

const detailSchema = z.object({
  caracteristica: z.string(),
  unidad: z.string().nullable(),
  valor_tierra: z.number(),
  valor_destino: z.number(),
  similitud: z.number(),
  grupo: z.string().default("fisico"),
});

const cellSchema = z.object({
  posicion: z.number(),
  sitio_id: z.number(),
  codigo: z.string().nullable(),
  nombre: z.string(),
  limites: z
    .object({ lat_min: z.number(), lat_max: z.number(), lon_min: z.number(), lon_max: z.number() })
    .nullable(),
  similitud: z.number(),
  por_grupo: z.record(z.string(), z.number()),
  cobertura: z.number(),
  estabilidad: z.number(),
  similitud_min: z.number(),
  similitud_max: z.number(),
  coincide: z.string(),
  difiere: z.string(),
  detalle: z.array(detailSchema),
});

const responseSchema = z.object({
  origen: z.object({
    sitio_id: z.number(),
    nombre: z.string(),
    codigo: z.string().nullable(),
    tipo: z.string().nullable(),
  }),
  destino: z.string(),
  metodo: z.string(),
  pesos_grupo: z.record(z.string(), z.number()),
  cobertura_minima: z.number(),
  evaluadas: z.number(),
  validas: z.number(),
  descartadas_por_cobertura: z.number(),
  resultados: z.array(cellSchema),
});

export type SimilarCell = z.infer<typeof cellSchema>;
export type SimilarCellsResponse = z.infer<typeof responseSchema>;

/** Las celdas de 10° del destino más parecidas a un sitio terrestre del ranking. */
export function requestSimilarCells(
  siteId: number,
  destination: AnalogDestination,
  signal: AbortSignal,
  fallbackMessage: string,
  limit = 5,
) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({
    sitio_id: String(siteId),
    destino: destination,
    limite: String(limit),
  });

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/analogia/celdas-similares?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema,
    mapData: (data) => data,
  });
}
