import { z } from "zod";

// ==============================================================================
// ESQUEMAS DE SITIO
// ==============================================================================
export const SitioSchema = z.object({
  id: z.number(),
  cuerpo_id: z.number(),
  nombre: z.string(),
  tipo: z.string().nullable().optional(),
  geom: z.record(z.string(), z.any()).nullable().optional(),
});

export const CreateSitioInputSchema = z.object({
  cuerpo_id: z.number().int().positive(),
  nombre: z.string().min(1).max(100),
  tipo: z.string().max(50).nullable().optional(),
  geom: z.record(z.string(), z.any()).nullable().optional(),
});

// ==============================================================================
// ESQUEMAS DE MEDICIÓN
// ==============================================================================
export const MedicionSchema = z.object({
  id: z.number(),
  sitio_id: z.number(),
  caracteristica_id: z.number(),
  dataset_id: z.number(),
  valor: z.number(),
  resolucion: z.number().nullable().optional(),
  valor_normalizado: z.number().nullable().optional(),
});

export const ExtraerSatelitalInputSchema = z.object({
  sitio_id: z.number().int().positive(),
  datetime_range: z.string().optional(),
});

// ==============================================================================
// ESQUEMAS DE CUERPO CELESTE & ANÁLOGÍA
// ==============================================================================
export const CuerpoCelesteSchema = z.object({
  id: z.number(),
  nombre: z.string(),
  tipo: z.string().nullable().optional(),
  radio_km: z.number().nullable().optional(),
});

export const AnalogiaSchema = z.object({
  id: z.number().optional(),
  sitio_tierra_id: z.number(),
  sitio_destino_id: z.number(),
  similitud: z.number().nullable().optional(),
  cobertura: z.number().nullable().optional(),
  metodo: z.string().nullable().optional(),
  coincide: z.string().nullable().optional(),
  difiere: z.string().nullable().optional(),
});

// ==============================================================================
// TIPOS INFERIDOS
// ==============================================================================
export type Sitio = z.infer<typeof SitioSchema>;
export type CreateSitioInput = z.infer<typeof CreateSitioInputSchema>;
export type Medicion = z.infer<typeof MedicionSchema>;
export type ExtraerSatelitalInput = z.infer<typeof ExtraerSatelitalInputSchema>;
export type CuerpoCeleste = z.infer<typeof CuerpoCelesteSchema>;
export type Analogia = z.infer<typeof AnalogiaSchema>;

