import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";

/** Dosis de radiación en superficie medida por Chang'E-4 LND (≈1.37 mSv/día). */
export const MOON_RADIATION_MSV_PER_DAY = 1.37;
export const MOON_GRAVITY_M_S2 = 1.62;
export interface MoonConditions {
  noonK: number;
  nightK: number;
}

/**
 * Modelo radiativo simplificado (sin atmósfera): la temperatura del mediodía
 * cae con cos(lat)^¼ y la nocturna baja de ~95 K en el ecuador a ~60 K en los polos.
 * Reproduce el orden de magnitud de las medidas de LRO Diviner; no son datos medidos.
 */
export function moonConditions({ latitude }: GeoPoint): MoonConditions {
  const lat = (latitude * Math.PI) / 180;
  const noonK = Math.max(160, 394 * Math.pow(Math.max(Math.cos(lat), 0), 0.25));
  const nightK = 95 - 35 * Math.abs(Math.sin(lat));
  return { noonK, nightK };
}
