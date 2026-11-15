"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import L from "leaflet";
import {
  Globe2,
  MapPin,
  Minus,
  Plus,
  RotateCcw,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { RegionProfile, SiteComparisonResult } from "../../domain/explorer-types";
import { cn } from "@/lib/utils";

export interface InteractiveAnalogMapProps {
  sites: RegionProfile[];
  ranking: SiteComparisonResult[];
  selectedSiteId: string;
  secondarySiteId?: string;
  queriedCoord?: { lat: number; lon: number; radiusKm: number } | null;
  activeBody?: "earth" | "mars" | "moon";
  onSelectSite: (siteId: string) => void;
  onMapCoordinateClick?: (lat: number, lon: number) => void;
  className?: string;
}

// Planetary landmark reference targets for 2D maps
const MARS_2D_LANDMARKS = [
  { id: "mars-jezero", name: "Cráter Jezero (Perseverance)", lat: 18.38, lon: 77.58, type: "Delta Lacustre" },
  { id: "mars-gale", name: "Cráter Gale (Curiosity)", lat: -4.6, lon: 137.4, type: "Monte Sharp" },
  { id: "mars-olympus", name: "Monte Olimpo", lat: 18.65, lon: -133.8, type: "Volcán Escudo" },
  { id: "mars-valles", name: "Valles Marineris", lat: -13.9, lon: -59.2, type: "Cañón Tectónico" },
];

const MOON_2D_LANDMARKS = [
  { id: "moon-shackleton", name: "Cráter Shackleton (LOLA Site04)", lat: -89.9, lon: 120.0, type: "Polo Sur / PSR" },
  { id: "moon-tranquillitatis", name: "Mare Tranquillitatis (Apollo 11)", lat: 0.67, lon: 23.47, type: "Mar Basáltico" },
  { id: "moon-tycho", name: "Cráter Tycho", lat: -43.3, lon: -11.4, type: "Impacto con Rayos" },
  { id: "moon-aitken", name: "Cuenca Polo Sur-Aitken", lat: -53.0, lon: -169.0, type: "Cuenca Gigante" },
];

export function InteractiveAnalogMap({
  sites,
  ranking,
  selectedSiteId,
  secondarySiteId,
  queriedCoord,
  activeBody = "earth",
  onSelectSite,
  onMapCoordinateClick,
  className,
}: InteractiveAnalogMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);
  const imageOverlayRef = useRef<L.ImageOverlay | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);

  const [currentBody, setCurrentBody] = useState<"earth" | "mars" | "moon">(activeBody);
  const [cursorCoord, setCursorCoord] = useState<{ lat: number; lon: number } | null>(null);
  const [selectedSiteDetail, setSelectedSiteDetail] = useState<RegionProfile | null>(null);

  useEffect(() => {
    setCurrentBody(activeBody);
  }, [activeBody]);

  const rankMap = useMemo(() => {
    const map = new Map<string, { rank: number; result: SiteComparisonResult }>();
    ranking.forEach((r, idx) => {
      map.set(r.site_id, { rank: idx + 1, result: r });
    });
    return map;
  }, [ranking]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20, 0],
      zoom: 2,
      minZoom: 1.5,
      maxZoom: 9,
      maxBounds: L.latLngBounds([-90, -210], [90, 210]),
      maxBoundsViscosity: 0.85,
      zoomControl: false,
      attributionControl: false,
    });

    mapInstanceRef.current = map;
    const layers = L.layerGroup().addTo(map);
    layerGroupRef.current = layers;

    // Cursor coordinates tracking
    map.on("mousemove", (e: L.LeafletMouseEvent) => {
      const lat = Number(e.latlng.lat.toFixed(2));
      const lon = Number(e.latlng.lng.toFixed(2));
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        setCursorCoord({ lat, lon });
      }
    });

    map.on("mouseout", () => setCursorCoord(null));

    // Coordinate click handler
    map.on("click", (e: L.LeafletMouseEvent) => {
      const lat = Number(e.latlng.lat.toFixed(4));
      const lon = Number(e.latlng.lng.toFixed(4));
      if (onMapCoordinateClick) {
        onMapCoordinateClick(lat, lon);
      }
    });

    // Invalidate size after layout settles
    const timeout = setTimeout(() => {
      map.invalidateSize();
    }, 150);

    return () => {
      clearTimeout(timeout);
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Basemap according to current celestial body
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove existing basemaps
    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
      tileLayerRef.current = null;
    }
    if (imageOverlayRef.current) {
      map.removeLayer(imageOverlayRef.current);
      imageOverlayRef.current = null;
    }

    const bounds: L.LatLngBoundsExpression = [[-90, -180], [90, 180]];

    if (currentBody === "earth") {
      // 1. Dark CartoDB basemap with high visual fidelity
      const tileLayer = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          subdomains: "abcd",
          maxZoom: 19,
          noWrap: true,
        }
      );

      // Offline fallback: if tiles fail (e.g. offline environment), fallback to local /landing/earth.webp
      tileLayer.on("tileerror", () => {
        if (!imageOverlayRef.current) {
          const fallbackOverlay = L.imageOverlay("/landing/earth.webp", bounds, {
            opacity: 0.85,
          }).addTo(map);
          imageOverlayRef.current = fallbackOverlay;
        }
      });

      tileLayer.addTo(map);
      tileLayerRef.current = tileLayer;
    } else if (currentBody === "mars") {
      // Mars 2D Equirectangular map
      const marsOverlay = L.imageOverlay("/mars/marsmap.jpg", bounds, {
        opacity: 0.95,
      }).addTo(map);
      imageOverlayRef.current = marsOverlay;
    } else if (currentBody === "moon") {
      // Moon 2D Equirectangular map
      const moonOverlay = L.imageOverlay("/landing/moon.webp", bounds, {
        opacity: 0.95,
      }).addTo(map);
      imageOverlayRef.current = moonOverlay;
    }
  }, [currentBody]);

  // Update Markers when sites, ranking, or body changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    if (currentBody === "earth") {
      // Render Earth Analog Sites
      sites.forEach((site) => {
        const isPrimary = site.id === selectedSiteId;
        const isSecondary = site.id === secondarySiteId;
        const rankInfo = rankMap.get(site.id);
        const rankNumber = rankInfo?.rank ?? "";
        const score = rankInfo?.result.score;
        const isLowCoverage = rankInfo?.result.classification === "insufficient_coverage";

        let markerColor = "#10b981"; // Emerald suitable
        if (isPrimary) markerColor = "#f59e0b"; // Amber primary
        else if (isSecondary) markerColor = "#06b6d4"; // Cyan secondary
        else if (isLowCoverage) markerColor = "#f43f5e"; // Rose insufficient

        const iconHtml = `
          <div class="relative group cursor-pointer flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
            <span class="absolute -inset-1.5 rounded-full animate-ping opacity-30" style="background-color: ${markerColor};"></span>
            <div class="relative flex items-center gap-1.5 rounded-full border border-white/30 px-2 py-0.5 shadow-lg backdrop-blur-md transition-transform duration-200 group-hover:scale-110" style="background-color: ${isPrimary ? '#39190d' : '#0b1329'};">
              <span class="size-2 rounded-full" style="background-color: ${markerColor};"></span>
              <span class="text-[10px] font-mono font-bold text-white tracking-tight">
                ${rankNumber ? `#${rankNumber}` : ""} ${score !== null && score !== undefined ? `${score}%` : ""}
              </span>
            </div>
            <div class="pointer-events-none absolute -bottom-5 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-black/80 px-1.5 py-0.5 text-[9px] font-medium text-white/90 opacity-0 shadow transition-opacity duration-150 group-hover:opacity-100">
              ${site.name}
            </div>
          </div>
        `;

        const customIcon = L.divIcon({
          className: "custom-pin",
          html: iconHtml,
          iconSize: [40, 20],
          iconAnchor: [20, 10],
        });

        const marker = L.marker([site.centroid.lat, site.centroid.lon], { icon: customIcon });

        marker.on("click", (e) => {
          L.DomEvent.stopPropagation(e);
          onSelectSite(site.id);
          setSelectedSiteDetail(site);
        });

        marker.addTo(layerGroup);
      });

      // Render queried coordinate circle if present
      if (queriedCoord) {
        L.circle([queriedCoord.lat, queriedCoord.lon], {
          radius: (queriedCoord.radiusKm || 15) * 1000,
          color: "#f43f5e",
          fillColor: "#f43f5e",
          fillOpacity: 0.2,
          weight: 1.5,
          dashArray: "4, 4",
        }).addTo(layerGroup);

        L.circleMarker([queriedCoord.lat, queriedCoord.lon], {
          radius: 4,
          color: "#ffffff",
          fillColor: "#f43f5e",
          fillOpacity: 1,
          weight: 2,
        }).addTo(layerGroup);
      }
    } else if (currentBody === "mars") {
      // Render Mars reference landmarks
      MARS_2D_LANDMARKS.forEach((m) => {
        const iconHtml = `
          <div class="relative group cursor-pointer flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
            <span class="absolute -inset-1.5 rounded-full animate-ping opacity-35 bg-[#ffab57]"></span>
            <div class="relative flex items-center gap-1 rounded-full border border-[#ffab57]/50 bg-[#29130d]/90 px-2 py-0.5 shadow-lg backdrop-blur-md transition-transform duration-200 group-hover:scale-110">
              <span class="size-1.5 rounded-full bg-[#ffab57]"></span>
              <span class="text-[10px] font-mono font-bold text-white tracking-tight">${m.name}</span>
            </div>
          </div>
        `;

        const customIcon = L.divIcon({
          className: "custom-mars-pin",
          html: iconHtml,
          iconSize: [40, 20],
          iconAnchor: [20, 10],
        });

        const marker = L.marker([m.lat, m.lon], { icon: customIcon });
        marker.addTo(layerGroup);
      });
    } else if (currentBody === "moon") {
      // Render Moon reference landmarks
      MOON_2D_LANDMARKS.forEach((m) => {
        const iconHtml = `
          <div class="relative group cursor-pointer flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
            <span class="absolute -inset-1.5 rounded-full animate-ping opacity-35 bg-[#8de3ff]"></span>
            <div class="relative flex items-center gap-1 rounded-full border border-[#8de3ff]/50 bg-[#0c1e33]/90 px-2 py-0.5 shadow-lg backdrop-blur-md transition-transform duration-200 group-hover:scale-110">
              <span class="size-1.5 rounded-full bg-[#8de3ff]"></span>
              <span class="text-[10px] font-mono font-bold text-white tracking-tight">${m.name}</span>
            </div>
          </div>
        `;

        const customIcon = L.divIcon({
          className: "custom-moon-pin",
          html: iconHtml,
          iconSize: [40, 20],
          iconAnchor: [20, 10],
        });

        const marker = L.marker([m.lat, m.lon], { icon: customIcon });
        marker.addTo(layerGroup);
      });
    }
  }, [sites, ranking, selectedSiteId, secondarySiteId, queriedCoord, currentBody, rankMap, onSelectSite]);

  // Selected site detail card sync
  useEffect(() => {
    const current = sites.find((s) => s.id === selectedSiteId);
    if (current) setSelectedSiteDetail(current);
  }, [selectedSiteId, sites]);

  const handleZoomIn = () => mapInstanceRef.current?.zoomIn();
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut();
  const handleResetView = () => mapInstanceRef.current?.setView([20, 0], 2);

  return (
    <div
      className={cn(
        "relative flex flex-col overflow-hidden rounded-3xl border border-white/20 bg-[#070b16] shadow-2xl backdrop-blur-xl",
        className ?? "h-[540px] w-full"
      )}
    >
      {/* Top Map Header & Controls */}
      <header className="relative z-10 flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-black/60 px-4 py-3 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="grid size-7 place-items-center rounded-xl bg-white/10 text-emerald-400">
            <Globe2 className="size-4" />
          </span>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Visor Cartográfico 2D de Análogos Geológicos
            </h3>
            <p className="text-[10px] text-white/60 font-mono">
              Proyección Equirectangular WGS84 · EPSG:4326 · Resolución 100 m
            </p>
          </div>
        </div>

        {/* Celestial Body Toggle inside Map */}
        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-full border border-white/15 bg-black/40 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setCurrentBody("earth")}
              className={cn(
                "rounded-full px-2.5 py-0.5 font-medium transition cursor-pointer",
                currentBody === "earth" ? "bg-[#38bdf8] text-black font-semibold shadow" : "text-white/70 hover:text-white"
              )}
            >
              Tierra
            </button>
            <button
              type="button"
              onClick={() => setCurrentBody("mars")}
              className={cn(
                "rounded-full px-2.5 py-0.5 font-medium transition cursor-pointer",
                currentBody === "mars" ? "bg-[#ffab57] text-black font-semibold shadow" : "text-white/70 hover:text-white"
              )}
            >
              Marte
            </button>
            <button
              type="button"
              onClick={() => setCurrentBody("moon")}
              className={cn(
                "rounded-full px-2.5 py-0.5 font-medium transition cursor-pointer",
                currentBody === "moon" ? "bg-[#8de3ff] text-black font-semibold shadow" : "text-white/70 hover:text-white"
              )}
            >
              Luna
            </button>
          </div>
        </div>
      </header>

      {/* Main Map Container */}
      <div className="relative flex-1 w-full h-full overflow-hidden">
        <div ref={mapContainerRef} className="size-full z-0 cursor-crosshair" />

        {/* Floating Zoom & Reset Tools (Top-Left) */}
        <div className="absolute top-3 left-3 z-10 flex flex-col gap-1.5">
          <button
            type="button"
            onClick={handleZoomIn}
            aria-label="Acercar mapa"
            className="grid size-8 place-items-center rounded-xl border border-white/20 bg-black/70 text-white shadow-lg backdrop-blur-md transition hover:bg-white/20 hover:scale-105 active:scale-95"
          >
            <Plus className="size-4" />
          </button>
          <button
            type="button"
            onClick={handleZoomOut}
            aria-label="Alejar mapa"
            className="grid size-8 place-items-center rounded-xl border border-white/20 bg-black/70 text-white shadow-lg backdrop-blur-md transition hover:bg-white/20 hover:scale-105 active:scale-95"
          >
            <Minus className="size-4" />
          </button>
          <button
            type="button"
            onClick={handleResetView}
            aria-label="Restablecer vista centrada"
            className="grid size-8 place-items-center rounded-xl border border-white/20 bg-black/70 text-white shadow-lg backdrop-blur-md transition hover:bg-white/20 hover:scale-105 active:scale-95"
          >
            <RotateCcw className="size-3.5" />
          </button>
        </div>

        {/* Floating Selected Site Mini-Card (Bottom-Left) */}
        {selectedSiteDetail && currentBody === "earth" && (
          <div className="absolute bottom-3 left-3 z-10 w-72 rounded-2xl border border-white/20 bg-[#091122]/90 p-3 shadow-2xl backdrop-blur-xl animate-in fade-in duration-200">
            <div className="flex items-start justify-between gap-1">
              <div>
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                  Sitio Seleccionado
                </span>
                <h4 className="text-xs font-bold text-white leading-tight">
                  {selectedSiteDetail.name}
                </h4>
                <p className="text-[10px] text-white/60 font-mono">
                  {selectedSiteDetail.country_or_region}
                </p>
              </div>
              {rankMap.get(selectedSiteDetail.id)?.result.score && (
                <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 text-[10px] font-mono">
                  {rankMap.get(selectedSiteDetail.id)?.result.score}%
                </Badge>
              )}
            </div>
            <div className="mt-2 grid grid-cols-2 gap-1.5 border-t border-white/10 pt-2 text-[10px] font-mono text-white/70">
              <div>Lat: {selectedSiteDetail.centroid.lat}°</div>
              <div>Lon: {selectedSiteDetail.centroid.lon}°</div>
            </div>
            <p className="mt-1.5 text-[10px] text-white/80 line-clamp-2">
              {selectedSiteDetail.summary}
            </p>
          </div>
        )}

        {/* Live Coordinate Cursor HUD (Bottom-Right) */}
        <div className="absolute bottom-3 right-3 z-10 flex items-center gap-2 rounded-full border border-white/15 bg-black/70 px-3 py-1 text-[10px] font-mono text-white/80 backdrop-blur-md shadow-lg pointer-events-none">
          <MapPin className="size-3 text-cyan-400" />
          {cursorCoord ? (
            <span>
              Lat: {cursorCoord.lat >= 0 ? `+${cursorCoord.lat}` : cursorCoord.lat}° · Lon:{" "}
              {cursorCoord.lon >= 0 ? `+${cursorCoord.lon}` : cursorCoord.lon}°
            </span>
          ) : (
            <span>Mueve el puntero o haz clic para consultar coordenadas</span>
          )}
        </div>
      </div>

      {/* Map Legend Footer */}
      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-black/60 px-4 py-2 text-[10px] text-white/70">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-amber-400" /> Primario
          </span>
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-cyan-400" /> Comparador B
          </span>
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-emerald-400" /> Cobertura Apta (≥ 70%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-rose-400" /> Cobertura Parcial (&lt; 70%)
          </span>
        </div>
        <span className="font-mono text-white/50">
          Scroll para zoom · Arrastra para navegar
        </span>
      </footer>
    </div>
  );
}
