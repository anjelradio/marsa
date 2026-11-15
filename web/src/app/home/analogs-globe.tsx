"use client";

import { cn } from "@/lib/utils";
import type { AnalogRankingItem } from "@/features/analogs/infrastructure/analogs-ranking";
import type {
  GeographicLandmark,
  ProjectedLandmark,
} from "@/features/shared/domain/geographic-coordinates";

function pointOf(geom: unknown): { lat: number; lon: number } | null {
  const g = geom as { type?: string; coordinates?: unknown } | null;
  if (!g || g.type !== "Point" || !Array.isArray(g.coordinates)) return null;
  const [lon, lat] = g.coordinates as number[];
  return Number.isFinite(lat) && Number.isFinite(lon) ? { lat, lon } : null;
}

/** Las celdas de 10° llegan como polígono: se marcan por su centro. */
function centerOf(limits: AnalogRankingItem["limites_destino"]): { lat: number; lon: number } | null {
  if (!limits) return null;
  return {
    lat: (limits.lat_min + limits.lat_max) / 2,
    lon: (limits.lon_min + limits.lon_max) / 2,
  };
}

function formatCoord(lat: number, lon: number) {
  return `${Math.abs(lat).toFixed(2)}° ${lat < 0 ? "S" : "N"} · ${Math.abs(lon).toFixed(2)}° ${lon < 0 ? "W" : "E"}`;
}

/** Sitios terrestres del ranking como marcadores del globo de la Tierra. */
export function earthLandmarks(ranking: AnalogRankingItem[]): GeographicLandmark[] {
  return ranking.flatMap((item) => {
    const p = pointOf(item.geom);
    return p
      ? [{
          id: String(item.sitio_tierra_id),
          name: item.sitio_tierra,
          type: item.tipo ?? "",
          coord: formatCoord(p.lat, p.lon),
          desc: "",
          ...p,
        }]
      : [];
  });
}

/** Sitios de destino sin repetir, como marcadores del globo lunar. */
export function targetLandmarks(ranking: AnalogRankingItem[]): GeographicLandmark[] {
  const seen = new Map<number, GeographicLandmark>();
  for (const item of ranking) {
    const p = pointOf(item.geom_destino) ?? centerOf(item.limites_destino);
    if (p && !seen.has(item.sitio_destino_id)) {
      seen.set(item.sitio_destino_id, {
        id: String(item.sitio_destino_id),
        name: item.sitio_destino,
        type: "",
        coord: formatCoord(p.lat, p.lon),
        desc: "",
        ...p,
      });
    }
  }
  return [...seen.values()];
}

/** Marcadores proyectados sobre el canvas del globo; clicables si hay onSelect. */
export function GlobeMarkers({
  points,
  activeId,
  onSelect,
}: {
  points: ProjectedLandmark[];
  activeId: string | null;
  onSelect?: (id: string) => void;
}) {
  return (
    <div className="pointer-events-none absolute inset-0 z-10">
      {points.map((poi) => {
        if (!poi.visible || poi.opacity <= 0.05) return null;
        const active = activeId === poi.id;
        return (
          <button
            key={poi.id}
            type="button"
            disabled={!onSelect}
            onClick={() => onSelect?.(poi.id)}
            aria-label={poi.name}
            className={cn(
              "absolute flex -translate-x-1/2 -translate-y-1/2 items-center gap-1.5 rounded-full border px-2.5 py-1 text-[0.68rem] font-semibold backdrop-blur-md transition-colors",
              onSelect ? "pointer-events-auto cursor-pointer" : "pointer-events-none",
              active
                ? "border-[#ffab57] bg-[#39190d]/95 text-white shadow-[0_0_14px_#ffab57a0]"
                : "border-white/20 bg-black/70 text-white/90",
            )}
            style={{ left: poi.screenX, top: poi.screenY, opacity: poi.opacity }}
          >
            <span className="size-1.5 rounded-full bg-[#ffab57]" />
            <span className="max-w-32 truncate">{poi.name}</span>
          </button>
        );
      })}
    </div>
  );
}
