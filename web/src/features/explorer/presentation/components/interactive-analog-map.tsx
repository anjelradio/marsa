"use client";

import { RegionProfile, SiteComparisonResult } from "../../domain/explorer-types";

interface InteractiveAnalogMapProps {
  sites: RegionProfile[];
  ranking: SiteComparisonResult[];
  selectedSiteId: string;
  secondarySiteId: string;
  queriedCoord: { lat: number; lon: number; radiusKm: number } | null;
  onSelectSite: (siteId: string) => void;
  onMapCoordinateClick: (lat: number, lon: number) => void;
}

function projectEquirectangular(lat: number, lon: number, width = 900, height = 450) {
  const x = ((lon + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return { x, y };
}

export function InteractiveAnalogMap({
  sites,
  ranking,
  selectedSiteId,
  secondarySiteId,
  queriedCoord,
  onSelectSite,
  onMapCoordinateClick,
}: InteractiveAnalogMapProps) {
  const rankMap = new Map<string, { rank: number; result: SiteComparisonResult }>();
  ranking.forEach((r, idx) => {
    rankMap.set(r.site_id, { rank: idx + 1, result: r });
  });

  const handleSvgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const relX = (e.clientX - rect.left) / rect.width;
    const relY = (e.clientY - rect.top) / rect.height;
    const lon = Number((relX * 360 - 180).toFixed(3));
    const lat = Number((90 - relY * 180).toFixed(3));
    onMapCoordinateClick(lat, lon);
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/15 bg-[#080d1a] shadow-inner">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 bg-white/[0.03] px-4 py-2.5 text-xs text-slate-300">
        <div className="flex items-center gap-2 font-medium text-white">
          <span className="inline-block size-2 rounded-full bg-emerald-400" />
          Mapa Terrestre de Regiones Candidatas (WGS84 · EPSG:4326 · Escala de análisis 100 m)
        </div>
        <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-300">
          <span className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full bg-amber-400 ring-2 ring-amber-400/40" />
            Seleccionado (Primario)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full bg-cyan-400 ring-2 ring-cyan-400/40" />
            Comparador B
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full bg-emerald-400" />
            Apto (Cobertura ≥ 70%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full bg-rose-400" />
            Evidencia insuficiente (&lt; 70%)
          </span>
        </div>
      </div>

      <svg
        viewBox="0 0 900 450"
        role="img"
        aria-label="Mapa mundial equirectangular con polígonos AOI de análogos terrestres validados. Haz clic en un marcador para ver su ficha o en cualquier punto para consultar coordenadas."
        onClick={handleSvgClick}
        className="h-auto w-full cursor-crosshair select-none bg-[radial-gradient(circle_at_50%_40%,#111e38_0%,#060b16_100%)]"
      >
        {/* Graticule grid lines every 30 degrees */}
        {[-60, -30, 0, 30, 60].map((lat) => {
          const { y } = projectEquirectangular(lat, 0);
          return (
            <g key={`lat-${lat}`}>
              <line
                x1={0}
                y1={y}
                x2={900}
                y2={y}
                stroke={lat === 0 ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.06)"}
                strokeDasharray={lat === 0 ? undefined : "4 4"}
              />
              <text x={8} y={y - 4} fill="rgba(255,255,255,0.35)" fontSize="9">
                {lat}°
              </text>
            </g>
          );
        })}
        {[-120, -60, 0, 60, 120].map((lon) => {
          const { x } = projectEquirectangular(0, lon);
          return (
            <g key={`lon-${lon}`}>
              <line
                x1={x}
                y1={0}
                x2={x}
                y2={450}
                stroke={lon === 0 ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.06)"}
                strokeDasharray={lon === 0 ? undefined : "4 4"}
              />
              <text x={x + 4} y={14} fill="rgba(255,255,255,0.35)" fontSize="9">
                {lon}°
              </text>
            </g>
          );
        })}

        {/* Stylized continental landmasses for spatial orientation */}
        <g fill="rgba(148, 163, 184, 0.12)" stroke="rgba(148, 163, 184, 0.28)" strokeWidth="1">
          {/* North America */}
          <polygon points="85,60 245,45 290,95 250,175 195,205 140,165 95,115" />
          {/* South America */}
          <polygon points="235,220 315,245 305,345 265,405 245,350 225,265" />
          {/* Europe */}
          <polygon points="415,65 515,55 535,115 470,135 415,125" />
          {/* Africa */}
          <polygon points="410,145 520,150 560,225 515,335 465,335 445,235 405,195" />
          {/* Asia */}
          <polygon points="525,60 765,65 795,165 705,215 605,195 540,140" />
          {/* Australia */}
          <polygon points="710,285 810,285 815,355 725,360" />
          {/* Antarctica */}
          <polygon points="60,415 840,412 860,445 45,445" />
        </g>

        {/* Queried coordinate circle if user clicked map or entered lat/lon */}
        {queriedCoord && (() => {
          const { x, y } = projectEquirectangular(queriedCoord.lat, queriedCoord.lon);
          return (
            <g>
              <circle
                cx={x}
                cy={y}
                r={Math.max(10, queriedCoord.radiusKm * 0.6)}
                fill="rgba(244, 63, 94, 0.15)"
                stroke="#fb7185"
                strokeWidth="1.5"
                strokeDasharray="3 3"
              />
              <circle cx={x} cy={y} r={3.5} fill="#fb7185" />
            </g>
          );
        })()}

        {/* Validated Earth Analog AOIs */}
        {sites.map((site) => {
          const { x, y } = projectEquirectangular(site.centroid.lat, site.centroid.lon);
          const info = rankMap.get(site.id);
          const isPrimary = site.id === selectedSiteId;
          const isSecondary = site.id === secondarySiteId;
          const isLowCoverage = info?.result.classification === "insufficient_coverage";

          const fillColor = isPrimary
            ? "#fbbf24"
            : isSecondary
              ? "#22d3ee"
              : isLowCoverage
                ? "#fb7185"
                : "#34d399";

          return (
            <g
              key={site.id}
              onClick={(e) => {
                e.stopPropagation();
                onSelectSite(site.id);
              }}
              className="cursor-pointer transition-transform"
            >
              {/* AOI footprint ring */}
              <circle
                cx={x}
                cy={y}
                r={isPrimary || isSecondary ? 15 : 10}
                fill={fillColor}
                fillOpacity={isPrimary || isSecondary ? 0.24 : 0.14}
                stroke={fillColor}
                strokeWidth={isPrimary || isSecondary ? 2 : 1}
              />
              {/* Centroid pin */}
              <circle
                cx={x}
                cy={y}
                r={isPrimary || isSecondary ? 5.5 : 4}
                fill={fillColor}
                stroke="#090d16"
                strokeWidth="1.5"
              />
              {/* Rank & Score pill */}
              <g transform={`translate(${x + 8}, ${y - 8})`}>
                <rect
                  x={0}
                  y={-10}
                  width={info?.result.score !== null && info?.result.score !== undefined ? 64 : 46}
                  height={16}
                  rx={4}
                  fill="rgba(9, 13, 22, 0.88)"
                  stroke={fillColor}
                  strokeWidth="0.9"
                />
                <text x={5} y={1} fill="#f8fafc" fontSize="9.5" fontWeight="600">
                  #{info?.rank ?? "-"} ·{" "}
                  {info?.result.score !== null && info?.result.score !== undefined
                    ? `${info.result.score.toFixed(0)} pts`
                    : "N/E"}
                </text>
              </g>
            </g>
          );
        })}
      </svg>

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-black/40 px-4 py-2 text-[11px] text-slate-400">
        <span>
          Haz clic en un pin para abrir su ficha geocientífica o en cualquier punto del mapa para validar cobertura AOI.
        </span>
        <span>Atribución de datos: NASA PDS · USGS Astrogeology · OpenTopography GLO-30 · MCD v6.2</span>
      </div>
    </div>
  );
}
