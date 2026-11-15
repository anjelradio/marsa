import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";

export const mineralMuestraSchema = z.object({
  nombre: z.string(),
  formula: z.string().nullable().optional(),
  abundancia: z.number(),
  unidad: z.string().default("% peso (wt%)"),
});

export const muestraLaboratorioSchema = z.object({
  muestra_id: z.string(),
  cuerpo: z.string(),
  ubicacion: z.string(),
  coordenadas: z.record(z.string(), z.number()).nullable().optional(),
  tipo_material: z.string(),
  minerales: z.array(mineralMuestraSchema).default([]),
  fase_amorfa_pct: z.number().nullable().optional(),
  instrumento: z.string(),
  fuente_pds: z.string(),
});

export const metadatosFuenteSchema = z.object({
  fuente: z.string(),
  licencia: z.string(),
  resolucion_o_escala: z.string(),
  nota_metodologica: z.string(),
});

export const unidadMacrostratSchema = z.object({
  map_id: z.number().nullable().optional(),
  source_id: z.number().nullable().optional(),
  nombre: z.string().nullable().optional(),
  litologia: z.array(z.string()).default([]),
  descripcion: z.string().nullable().optional(),
  edad_superior_Ma: z.number().nullable().optional(),
  edad_inferior_Ma: z.number().nullable().optional(),
});

export const celdaAnalogicoSchema = z.object({
  celda_id: z.string(),
  region_referencia: z.string(),
  limites: z.record(z.string(), z.number()).nullable().optional(),
  categorias_area_pct: z.record(z.string(), z.number()).default({}),
  minerales_detectados: z.array(z.string()).default([]),
  rocas_principales: z.array(z.string()).default([]),
  unidad_geologica: z.string().nullable().optional(),
  cobertura_pct: z.number().nullable().optional(),
  indice_similitud_algoritmo_pct: z.number().nullable().optional(),
  nota_similitud: z.string().nullable().optional(),
});

const coordenadasCeldaSchema = z.object({ lat: z.number(), lng: z.number() });

const candidatoTerrestreSchema = z.object({
  celda_id: z.string(),
  region_referencia: z.string(),
  centro: coordenadasCeldaSchema,
  limites: z.object({
    lat_min: z.number(),
    lat_max: z.number(),
    lon_min: z.number(),
    lon_max: z.number(),
  }),
  similitud_pct: z.number(),
  cobertura_pct: z.number().nullable().optional(),
  comparacion_litologica: z.array(z.object({
    categoria: z.string(),
    marte_pct: z.number(),
    tierra_pct: z.number(),
  })),
});

const rankingTerrestreSchema = z.object({
  regiones_evaluadas: z.number(),
  candidatos: z.array(candidatoTerrestreSchema),
});

export type RankingTerrestre = z.infer<typeof rankingTerrestreSchema>;

export const respuestaGeologiaPuntoSchema = z.object({
  cuerpo: z.string(),
  coordenadas: z.object({ lat: z.number(), lng: z.number() }),
  celda_id: z.string(),
  region_nombre: z.string(),
  unidad_geologica: z.string(),
  tipo_terreno: z.string(),
  rocas_predominantes: z.array(z.string()).default([]),
  minerales_principales: z.array(z.string()).default([]),
  distribucion_litologica: z.record(z.string(), z.number()).default({}),
  unidades_macrostrat: z.array(unidadMacrostratSchema).default([]),
  muestras_laboratorio_in_situ: z.array(muestraLaboratorioSchema).default([]),
  cobertura_geologica: z.boolean().nullable().optional(),
  ranking_terrestre: rankingTerrestreSchema.nullable().optional(),
  mejor_analogo: z.object({
    cuerpo_destino: z.string(),
    celda_analoga: celdaAnalogicoSchema.nullish(),
    sitio_analogo_terrestre: celdaAnalogicoSchema.extend({ similitud_pct: z.number().optional() }).nullish(),
  }).nullish(),
  atribuciones: z.array(metadatosFuenteSchema).default([]),
});

export type MineralMuestra = z.infer<typeof mineralMuestraSchema>;
export type MuestraLaboratorio = z.infer<typeof muestraLaboratorioSchema>;
export type MetadatosFuente = z.infer<typeof metadatosFuenteSchema>;
export type UnidadMacrostrat = z.infer<typeof unidadMacrostratSchema>;
export type CeldaAnalogico = z.infer<typeof celdaAnalogicoSchema>;
export type RespuestaGeologiaPunto = z.infer<typeof respuestaGeologiaPuntoSchema>;

export function requestPointGeology(
  cuerpo: "Tierra" | "Marte" | "Luna",
  point: GeoPoint,
  signal: AbortSignal,
  fallbackMessage: string,
  destino?: "Marte" | "Luna" | "Tierra"
) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const params = new URLSearchParams({
    cuerpo,
    lat: point.latitude.toFixed(6),
    lng: point.longitude.toFixed(6),
  });
  if (destino) {
    params.set("destino", destino);
  }

  return apiRequestData({
    url: `${base.replace(/\/$/, "")}/api/analogia/geologia/punto?${params}`,
    method: "GET",
    withAuth: false,
    signal,
    fallbackMessage,
    responseSchema: respuestaGeologiaPuntoSchema,
    mapData: (data) => data,
  });
}
