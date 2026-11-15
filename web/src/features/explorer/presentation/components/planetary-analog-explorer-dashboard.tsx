"use client";

import { useEffect, useId, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Compass,
  Database,
  ExternalLink,
  Globe2,
  Layers,
  MapPin,
  RotateCcw,
  Scale,
  Search,
  SlidersHorizontal,
  Sparkles,
  Thermometer,
  Wind,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { MarsPlanet } from "@/features/mars/presentation/components/mars-planet";
import {
  REGIONS_CATALOG,
  SCIENTIFIC_SOURCES,
} from "../../domain/explorer-catalog";
import {
  FEATURE_LABELS,
  LITHOLOGY_LABELS,
  MISSION_PROFILES,
  MissionProfile,
  RegionFeatures,
  SiteComparisonResult,
} from "../../domain/explorer-types";
import {
  analyzeCoordinatesRequest,
  parseNaturalQueryClient,
  runComparisonRequest,
} from "../../infrastructure/explorer-client";
import { CoordinateAnalyzeResponseSchema } from "../../infrastructure/explorer-api-types";
import { InteractiveAnalogMap } from "./interactive-analog-map";

const WEIGHT_KEYS: (keyof RegionFeatures)[] = [
  "median_slope_deg",
  "slope_p90_deg",
  "ruggedness_tri",
  "local_relief_m",
  "lithology",
  "ndvi",
  "precipitation_mm_year",
  "mean_temperature_c",
];

function formatValue(key: keyof RegionFeatures, val: number | string | null | undefined): string {
  if (val === null || val === undefined) return "Sin dato (null)";
  if (key === "lithology") return LITHOLOGY_LABELS[String(val)] ?? String(val);
  return `${val} ${FEATURE_LABELS[key].unit}`;
}

export function PlanetaryAnalogExplorerDashboard() {
  const tableCaptionId = useId();
  const [selectedBody, setSelectedBody] = useState<"mars" | "moon">("mars");
  const [targetId, setTargetId] = useState<string>("mars-jezero");
  const [missionProfile, setMissionProfile] = useState<MissionProfile>("rover_mobility");
  const [weights, setWeights] = useState<Partial<Record<keyof RegionFeatures, number>>>(
    MISSION_PROFILES.rover_mobility.defaultWeights,
  );
  const [results, setResults] = useState<SiteComparisonResult[]>([]);
  const [sourceMode, setSourceMode] = useState<"backend-api" | "offline-catalog">("offline-catalog");

  const [selectedSiteId, setSelectedSiteId] = useState<string>("earth-atacama-yungay");
  const [secondarySiteId, setSecondarySiteId] = useState<string>("earth-black-point-lava-az");

  // Natural language query state (Flow C)
  const [nlQuery, setNlQuery] = useState<string>(
    "Muéstrame zonas terrestres parecidas a Jezero para probar un rover, con pendientes suaves y terreno seco",
  );
  const [nlSummary, setNlSummary] = useState<string | null>(null);

  // Coordinate query state (Flow B)
  const [coordLat, setCoordLat] = useState<string>("-24.088");
  const [coordLon, setCoordLon] = useState<string>("-69.913");
  const [coordRadius, setCoordRadius] = useState<string>("15");
  const [coordResponse, setCoordResponse] = useState<CoordinateAnalyzeResponseSchema | null>(null);

  const planetaryTargets = useMemo(
    () => REGIONS_CATALOG.filter((r) => r.body === "mars" || r.body === "moon"),
    [],
  );
  const earthSites = useMemo(
    () => REGIONS_CATALOG.filter((r) => r.body === "earth"),
    [],
  );

  const activeTarget = useMemo(
    () => planetaryTargets.find((t) => t.id === targetId) ?? planetaryTargets[0],
    [planetaryTargets, targetId],
  );

  const primarySite = useMemo(
    () => earthSites.find((s) => s.id === selectedSiteId) ?? earthSites[0],
    [earthSites, selectedSiteId],
  );
  const secondarySite = useMemo(
    () => earthSites.find((s) => s.id === secondarySiteId) ?? earthSites[1],
    [earthSites, secondarySiteId],
  );

  const primaryComparison = useMemo(
    () => results.find((r) => r.site_id === selectedSiteId) ?? results[0],
    [results, selectedSiteId],
  );

  useEffect(() => {
    let cancelled = false;
    runComparisonRequest({
      targetId,
      missionProfile,
      direction: "planet_to_earth",
      weights,
    }).then((res) => {
      if (cancelled) return;
      setResults(res.results);
      setSourceMode(res.sourceMode);
      if (res.results.length >= 2) {
        setSelectedSiteId((prev) =>
          res.results.some((r) => r.site_id === prev) ? prev : res.results[0].site_id,
        );
      }
    });
    return () => {
      cancelled = true;
    };
  }, [targetId, missionProfile, weights]);

  const handleSelectBody = (body: "mars" | "moon") => {
    setSelectedBody(body);
    setTargetId(body === "mars" ? "mars-jezero" : "moon-shackleton-rim");
  };

  const handleSelectProfile = (profile: MissionProfile) => {
    setMissionProfile(profile);
    setWeights({ ...MISSION_PROFILES[profile].defaultWeights });
  };

  const handleWeightChange = (key: keyof RegionFeatures, val: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const handleApplyNaturalQuery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlQuery.trim()) return;
    const parsed = parseNaturalQueryClient(nlQuery);
    setSelectedBody(parsed.body);
    setTargetId(parsed.targetId);
    setMissionProfile(parsed.missionProfile);
    setWeights(parsed.weights);
    setNlSummary(parsed.summary);
  };

  const handleAnalyzeCoordinates = async (latNum: number, lonNum: number) => {
    setCoordLat(String(latNum));
    setCoordLon(String(lonNum));
    const rad = Math.max(1, Math.min(50, Number(coordRadius) || 15));
    const resp = await analyzeCoordinatesRequest({
      lat: latNum,
      lon: lonNum,
      radiusKm: rad,
      missionProfile,
    });
    setCoordResponse(resp);
    if (resp.status === "matched_aoi" && resp.matched_region) {
      setSelectedSiteId(resp.matched_region.id);
    }
  };

  return (
    <div className="min-h-svh bg-[#050811] text-slate-100">
      {/* Top Header */}
      <header className="sticky top-0 z-30 border-b border-white/10 bg-[#050811]/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 text-slate-950 shadow-lg shadow-orange-500/20">
              <Globe2 className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-white sm:text-lg">
                  Planetary Analog Explorer
                </span>
                <span className="rounded-full border border-orange-400/30 bg-orange-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-orange-300">
                  NASA Space Apps 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Sistema de Soporte a la Decisión (DSS) · Marte y Luna → Análogos Terrestres Trazables
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 text-xs">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-emerald-300">
              <Database className="size-3.5" />
              Motor: {sourceMode === "backend-api" ? "FastAPI Conectado" : "Catálogo Versionado Offline (P0)"}
            </span>
            <Link
              href="/home"
              className="inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/5 px-3.5 py-1.5 font-medium text-white transition hover:bg-white/10"
            >
              <Sparkles className="size-3.5 text-amber-400" />
              Atlas 3D (Marte · Luna · Tierra)
            </Link>
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/5 px-3.5 py-1.5 font-medium text-white transition hover:bg-white/10"
            >
              <Globe2 className="size-3.5 text-cyan-400" />
              Landing
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1600px] space-y-6 px-4 py-6 sm:px-6">
        {/* Flow C: Natural Language Search Bar */}
        <section
          aria-label="Búsqueda semántica auditable"
          className="rounded-2xl border border-white/10 bg-[#0b1222]/90 p-4 shadow-lg"
        >
          <form onSubmit={handleApplyNaturalQuery} className="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-300">
              <Search className="size-4 shrink-0" />
              Consulta Semántica (P1)
            </div>
            <input
              type="text"
              value={nlQuery}
              onChange={(e) => setNlQuery(e.target.value)}
              placeholder="Ej: Busco análogos lunares en desiertos fríos con poca vegetación..."
              className="flex-1 rounded-xl border border-white/15 bg-black/50 px-3.5 py-2 text-sm text-white placeholder:text-slate-500 focus:border-amber-400 focus:outline-none"
            />
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="submit"
                className="rounded-xl bg-amber-500 px-4 py-2 text-xs font-semibold text-slate-950 transition hover:bg-amber-400"
              >
                Interpretar a Filtros
              </button>
              <button
                type="button"
                onClick={() => {
                  setNlQuery("Busco análogos lunares en desiertos fríos con poca vegetación");
                }}
                className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 hover:bg-white/10"
              >
                Ejemplo Lunar Polar
              </button>
            </div>
          </form>
          {nlSummary && (
            <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-amber-400/25 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-200">
              <span>
                <strong>Filtros extraídos (auditables):</strong> {nlSummary}
              </span>
              <span className="text-[11px] text-amber-300/80">
                El ranking siempre se calcula con el motor determinista multicriterio, nunca por LLM.
              </span>
            </div>
          )}
        </section>

        {/* Main 3-Column Grid: Left (Target & Weights) | Center (Map + 3D Target Preview) | Right (Ranked Analog Candidates) */}
        <div className="grid gap-6 lg:grid-cols-12">
          {/* LEFT COLUMN: Planetary Target, Mission Profile & Weight Sliders */}
          <aside className="space-y-5 lg:col-span-3">
            {/* Step 1: Planetary Body & Reference Target */}
            <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white">1. Destino Espacial de Referencia</h2>
                <span className="rounded bg-white/10 px-2 py-0.5 text-[10px] font-medium text-slate-300">
                  Flujo A (P0)
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleSelectBody("mars")}
                  className={`rounded-xl border px-3 py-2.5 text-left transition ${
                    selectedBody === "mars"
                      ? "border-orange-400 bg-orange-500/20 text-white"
                      : "border-white/10 bg-white/5 text-slate-400 hover:bg-white/10"
                  }`}
                >
                  <div className="text-xs font-bold">Marte</div>
                  <div className="text-[11px] opacity-80">Cráter Jezero</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectBody("moon")}
                  className={`rounded-xl border px-3 py-2.5 text-left transition ${
                    selectedBody === "moon"
                      ? "border-cyan-400 bg-cyan-500/20 text-white"
                      : "border-white/10 bg-white/5 text-slate-400 hover:bg-white/10"
                  }`}
                >
                  <div className="text-xs font-bold">Luna</div>
                  <div className="text-[11px] opacity-80">Borde Shackleton</div>
                </button>
              </div>

              {/* 3D Globe / Target Preview Card */}
              <div className="relative overflow-hidden rounded-xl border border-white/10 bg-black p-3">
                {selectedBody === "mars" ? (
                  <div className="relative mx-auto aspect-square w-36">
                    <MarsPlanet />
                  </div>
                ) : (
                  <div className="mx-auto grid aspect-square w-36 place-items-center rounded-full bg-[radial-gradient(circle_at_35%_30%,#e2e8f0,#475569_65%,#0f172a_100%)] shadow-[0_0_35px_rgba(148,163,184,0.3)]">
                    <span className="rounded-full bg-black/60 px-2.5 py-1 text-[10px] font-semibold text-cyan-200">
                      LOLA Site04 · 89.78° S
                    </span>
                  </div>
                )}

                <div className="mt-2 space-y-1 text-xs">
                  <div className="font-semibold text-white">{activeTarget.name}</div>
                  <p className="text-[11px] leading-relaxed text-slate-400">{activeTarget.summary}</p>
                  <div className="flex flex-wrap gap-1.5 pt-1 text-[10px]">
                    <span className="rounded bg-white/10 px-2 py-0.5 text-slate-300">
                      CRS: {activeTarget.crs}
                    </span>
                    <span className="rounded bg-white/10 px-2 py-0.5 text-slate-300">
                      Escala: {activeTarget.analysis_scale_m} m
                    </span>
                  </div>
                </div>

                {/* MCD v6.2 Mars Climate Telemetry Box */}
                {activeTarget.mars_climate_ls105 && (
                  <div className="mt-3 rounded-lg border border-orange-400/25 bg-orange-950/30 p-2.5 text-[11px]">
                    <div className="mb-1.5 flex items-center justify-between font-semibold text-orange-300">
                      <span>Clima MCD v6.2 (Ls = 105°)</span>
                      <span className="text-[10px] opacity-80">Dato LMD/ESA</span>
                    </div>
                    <div className="grid grid-cols-2 gap-1.5 text-slate-200">
                      <div className="flex items-center gap-1">
                        <Thermometer className="size-3 text-orange-400" />
                        <span>
                          {activeTarget.mars_climate_ls105.mean_temperature_c} °C (
                          {activeTarget.mars_climate_ls105.surface_temperature_k.toFixed(1)} K)
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Wind className="size-3 text-orange-400" />
                        <span>Viento 10m: {activeTarget.mars_climate_ls105.wind_speed_10m_m_s} m/s</span>
                      </div>
                      <div>Presión: {activeTarget.mars_climate_ls105.surface_pressure_hpa} hPa</div>
                      <div>Polvo τ670: {activeTarget.mars_climate_ls105.dust_optical_depth_670nm}</div>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            {/* Step 2: Mission Profile & Weights */}
            <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-1.5 text-sm font-semibold text-white">
                  <SlidersHorizontal className="size-4 text-amber-400" />
                  2. Perfil de Ensayo y Pesos
                </h2>
                <button
                  type="button"
                  onClick={() => handleSelectProfile(missionProfile)}
                  className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-white"
                >
                  <RotateCcw className="size-3" /> Reset
                </button>
              </div>

              <div className="space-y-1.5">
                {(Object.keys(MISSION_PROFILES) as MissionProfile[]).map((profKey) => {
                  const prof = MISSION_PROFILES[profKey];
                  const active = missionProfile === profKey;
                  return (
                    <button
                      key={profKey}
                      type="button"
                      onClick={() => handleSelectProfile(profKey)}
                      className={`w-full rounded-xl border p-2.5 text-left transition ${
                        active
                          ? "border-amber-400/70 bg-amber-500/15 text-white"
                          : "border-white/10 bg-white/[0.03] text-slate-300 hover:bg-white/[0.07]"
                      }`}
                    >
                      <div className="text-xs font-semibold">{prof.title}</div>
                      <div className="mt-0.5 text-[11px] text-slate-400">{prof.subtitle}</div>
                    </button>
                  );
                })}
              </div>

              <div className="space-y-2.5 pt-2">
                <div className="text-xs font-medium text-slate-300">
                  Ajuste fino de pesos ($w_i$):
                </div>
                {WEIGHT_KEYS.map((k) => {
                  const val = weights[k] ?? 0;
                  return (
                    <div key={k} className="space-y-1">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-300">{FEATURE_LABELS[k].label}</span>
                        <span className="font-mono text-amber-300">{(val * 100).toFixed(0)}%</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={val}
                        aria-label={FEATURE_LABELS[k].label}
                        onChange={(e) => handleWeightChange(k, parseFloat(e.target.value))}
                        className="h-1.5 w-full cursor-pointer accent-amber-400"
                      />
                    </div>
                  );
                })}
              </div>
            </Card>
          </aside>

          {/* CENTER COLUMN: Interactive Map + Coordinate AOI Checker + Side-by-Side Comparator */}
          <div className="space-y-5 lg:col-span-6">
            <InteractiveAnalogMap
              sites={earthSites}
              ranking={results}
              selectedSiteId={selectedSiteId}
              secondarySiteId={secondarySiteId}
              queriedCoord={
                coordResponse
                  ? {
                      lat: coordResponse.query.lat,
                      lon: coordResponse.query.lon,
                      radiusKm: coordResponse.query.radius_km,
                    }
                  : null
              }
              onSelectSite={(id) => setSelectedSiteId(id)}
              onMapCoordinateClick={(lat, lon) => handleAnalyzeCoordinates(lat, lon)}
            />

            {/* Flow B: Coordinate & AOI Validator */}
            <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                  <Compass className="size-4 text-cyan-400" />
                  Verificador de Coordenadas Terrestres y Cobertura AOI (Flujo B)
                </h2>
                <span className="text-[11px] text-slate-400">
                  No inventa perfiles fuera de polígonos validados
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
                <div>
                  <label className="block text-[11px] text-slate-400">Latitud (°N)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={coordLat}
                    onChange={(e) => setCoordLat(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-white/15 bg-black/50 px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400">Longitud (°E)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={coordLon}
                    onChange={(e) => setCoordLon(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-white/15 bg-black/50 px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400">Radio AOI (km)</label>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={coordRadius}
                    onChange={(e) => setCoordRadius(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-white/15 bg-black/50 px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div className="flex items-end gap-1.5">
                  <button
                    type="button"
                    onClick={() =>
                      handleAnalyzeCoordinates(
                        parseFloat(coordLat) || 0,
                        parseFloat(coordLon) || 0,
                      )
                    }
                    className="w-full rounded-lg bg-cyan-500 px-3 py-1.5 text-xs font-semibold text-slate-950 transition hover:bg-cyan-400"
                  >
                    Verificar AOI
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => handleAnalyzeCoordinates(-24.088, -69.913)}
                  className="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-slate-300 hover:bg-white/10"
                >
                  Probar Atacama (-24.09, -69.91)
                </button>
                <button
                  type="button"
                  onClick={() => handleAnalyzeCoordinates(-77.525, 161.75)}
                  className="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-slate-300 hover:bg-white/10"
                >
                  Probar McMurdo (-77.53, 161.75)
                </button>
                <button
                  type="button"
                  onClick={() => handleAnalyzeCoordinates(0.0, -140.0)}
                  className="rounded-md border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-rose-300 hover:bg-rose-500/20"
                >
                  Probar Punto Sin Cobertura (Océano Pacífico 0°, -140°)
                </button>
              </div>

              {coordResponse && (
                <div
                  className={`rounded-xl border p-3 text-xs ${
                    coordResponse.status === "matched_aoi"
                      ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                      : "border-rose-500/40 bg-rose-500/10 text-rose-200"
                  }`}
                >
                  <div className="font-semibold">{coordResponse.message}</div>
                  {coordResponse.planetary_matches.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-3 text-[11px]">
                      {coordResponse.planetary_matches.map((pm) => (
                        <span key={pm.site_id} className="rounded bg-black/40 px-2 py-0.5">
                          Compatibilidad con <strong>{pm.site_name}</strong>: {pm.score}% (Cobertura{" "}
                          {Math.round(pm.coverage * 100)}%)
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Card>

            {/* Side-by-Side Scientific Comparator Table (following `responsive-table` modern web guidance) */}
            <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                  <Scale className="size-4 text-amber-400" />
                  Comparador Geocientífico Lado a Lado (Objetivo vs. 2 Sitios Terrestres)
                </h2>
                <div className="flex items-center gap-2 text-xs">
                  <label htmlFor="secondary-site-select" className="text-slate-400">
                    Comparar contra B:
                  </label>
                  <select
                    id="secondary-site-select"
                    value={secondarySiteId}
                    onChange={(e) => setSecondarySiteId(e.target.value)}
                    className="rounded-lg border border-white/15 bg-black/60 px-2.5 py-1 text-xs text-cyan-300"
                  >
                    {earthSites.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div
                tabIndex={0}
                role="region"
                aria-labelledby={tableCaptionId}
                className="max-w-full overflow-auto rounded-xl border border-white/10 [container-type:inline-size]"
              >
                <table className="w-full border-separate border-spacing-0 text-left text-xs">
                  <caption id={tableCaptionId} className="sr-only">
                    Comparación de indicadores topográficos, geológicos y ambientales a escala de 100 metros
                  </caption>
                  <thead className="sticky inset-block-start-0 z-10 bg-[#111c35] text-[11px] uppercase text-slate-300">
                    <tr>
                      <th className="sticky inset-inline-start-0 bg-[#111c35] px-3 py-2.5">
                        Indicador (Escala 100 m)
                      </th>
                      <th className="px-3 py-2.5 text-orange-300">
                        Objetivo: {activeTarget.name.split("(")[0]}
                      </th>
                      <th className="px-3 py-2.5 text-amber-300">
                        Sitio A: {primarySite.name.split("—")[0]}
                      </th>
                      <th className="px-3 py-2.5 text-cyan-300">
                        Sitio B: {secondarySite.name.split("—")[0]}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {WEIGHT_KEYS.map((key) => {
                      const meta = FEATURE_LABELS[key];
                      return (
                        <tr key={key} className="hover:bg-white/[0.03]">
                          <th
                            scope="row"
                            className="sticky inset-inline-start-0 bg-[#0b1222] px-3 py-2 font-medium text-white"
                          >
                            <div>{meta.label}</div>
                            <span className="text-[10px] font-normal text-slate-400">
                              Fuente: {meta.badge}
                            </span>
                          </th>
                          <td className="px-3 py-2 font-mono text-orange-200">
                            {formatValue(key, activeTarget.features[key])}
                          </td>
                          <td className="px-3 py-2 font-mono text-amber-200">
                            {formatValue(key, primarySite.features[key])}
                          </td>
                          <td className="px-3 py-2 font-mono text-cyan-200">
                            {formatValue(key, secondarySite.features[key])}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* RIGHT COLUMN: Ranked Terrestrial Analog Results & Scientific Breakdown Sheet */}
          <aside className="space-y-5 lg:col-span-3">
            <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white">
                  3. Ranking de Análogos Terrestres
                </h2>
                <span className="text-[11px] text-slate-400">
                  Umbral cobertura ≥ 70%
                </span>
              </div>

              <div className="max-h-[360px] space-y-2 overflow-y-auto pr-1">
                {results.map((item, idx) => {
                  const isSelected = item.site_id === selectedSiteId;
                  const isLowCov = item.classification === "insufficient_coverage";
                  return (
                    <button
                      key={item.site_id}
                      type="button"
                      onClick={() => setSelectedSiteId(item.site_id)}
                      className={`w-full rounded-xl border p-3 text-left transition ${
                        isSelected
                          ? "border-amber-400 bg-amber-500/15"
                          : "border-white/10 bg-white/[0.03] hover:bg-white/[0.07]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-[10px] font-bold text-amber-300">
                              #{idx + 1}
                            </span>
                            <span className="text-xs font-semibold text-white">
                              {item.site_name}
                            </span>
                          </div>
                          <div className="mt-0.5 flex items-center gap-1 text-[11px] text-slate-400">
                            <MapPin className="size-3" />
                            {item.country_or_region}
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="font-mono text-sm font-bold text-white">
                            {item.score !== null ? `${item.score.toFixed(1)}%` : "N/E"}
                          </div>
                          <div
                            className={`text-[10px] font-medium ${
                              isLowCov ? "text-rose-400" : "text-emerald-400"
                            }`}
                          >
                            Cob: {Math.round(item.coverage * 100)}%
                          </div>
                        </div>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[10px]">
                        <span
                          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-medium ${
                            isLowCov
                              ? "bg-rose-500/20 text-rose-300"
                              : "bg-emerald-500/20 text-emerald-300"
                          }`}
                        >
                          {isLowCov ? (
                            <>
                              <AlertTriangle className="size-3" /> Evidencia insuficiente
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="size-3" /> Candidato apto
                            </>
                          )}
                        </span>
                        <span className="text-slate-400">
                          {item.centroid.lat.toFixed(2)}°, {item.centroid.lon.toFixed(2)}°
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </Card>

            {/* Detailed Scientific Breakdown of Selected Site */}
            {primaryComparison && (
              <Card className="gap-3 rounded-2xl border-white/10 bg-[#0b1222] p-4 text-slate-100">
                <div className="flex items-center justify-between border-b border-white/10 pb-2">
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-amber-400">
                      Ficha Científica Auditada
                    </span>
                    <h3 className="text-sm font-bold text-white">
                      {primaryComparison.site_name}
                    </h3>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-lg font-black text-amber-400">
                      {primaryComparison.score !== null
                        ? `${primaryComparison.score.toFixed(1)}%`
                        : "N/E"}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Cobertura: {Math.round(primaryComparison.coverage * 100)}%
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="font-semibold text-slate-300">
                    Desglose por indicador ($\text{"sim"}_i$):
                  </div>
                  {primaryComparison.breakdown.map((b) => (
                    <div
                      key={b.feature}
                      className="rounded-lg border border-white/10 bg-black/40 p-2"
                    >
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-medium text-white">
                          {FEATURE_LABELS[b.feature]?.label ?? b.feature}
                        </span>
                        <span className="font-mono text-amber-300">
                          {b.similarity !== null
                            ? `sim = ${(b.similarity * 100).toFixed(0)}% (peso ${(b.weight * 100).toFixed(0)}%)`
                            : "Dato faltante (null)"}
                        </span>
                      </div>
                      <div className="mt-1 flex justify-between text-[10px] text-slate-400">
                        <span>Objetivo: {String(b.target_value ?? "null")}</span>
                        <span>Sitio: {String(b.candidate_value ?? "null")}</span>
                      </div>
                      {b. similarity !== null && (
                        <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-amber-500 to-emerald-400"
                            style={{ width: `${Math.round(b.similarity * 100)}%` }}
                          />
                        </div>
                      )}
                      {b.note && (
                        <div className="mt-1 text-[10px] text-rose-300">{b.note}</div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Limitations & Uncertainties */}
                <div className="rounded-xl border border-amber-500/25 bg-amber-500/10 p-2.5 text-[11px] text-amber-100">
                  <div className="mb-1 flex items-center gap-1.5 font-semibold text-amber-300">
                    <AlertTriangle className="size-3.5" />
                    Límites Científicos y Notas de Calidad
                  </div>
                  <ul className="list-disc space-y-1 pl-4 text-amber-200/90">
                    {primaryComparison.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              </Card>
            )}
          </aside>
        </div>

        {/* Scientific Sources & Provenance Footer Section */}
        <section
          aria-label="Catálogo de fuentes científicas y licencias"
          className="rounded-2xl border border-white/10 bg-[#0b1222] p-5"
        >
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                <Layers className="size-4 text-emerald-400" />
                Trazabilidad de Fuentes Científicas, Resoluciones y Licencias (`data/manifest.json`)
              </h2>
              <p className="text-xs text-slate-400">
                Todos los indicadores distinguen entre Dato NASA/USGS/ESA, Cálculo propio a escala común (100 m) y limitaciones de resolución.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {SCIENTIFIC_SOURCES.map((src) => (
              <div
                key={src.id}
                className="flex flex-col justify-between rounded-xl border border-white/10 bg-black/40 p-3 text-xs"
              >
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="rounded bg-white/10 px-2 py-0.5 text-[10px] font-semibold uppercase text-amber-300">
                      {src.body}
                    </span>
                    <span className="font-mono text-[10px] text-slate-400">
                      Res: {src.native_resolution_m} m
                    </span>
                  </div>
                  <div className="mt-1.5 font-semibold text-white">{src.name}</div>
                  <div className="mt-0.5 text-[11px] text-slate-400">{src.provider}</div>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-slate-300">
                    {src.limitations}
                  </p>
                </div>

                <div className="mt-3 flex items-center justify-between border-t border-white/10 pt-2 text-[10px] text-slate-400">
                  <span>{src.license.slice(0, 28)}</span>
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-medium text-cyan-300 hover:underline"
                  >
                    Fuente <ExternalLink className="size-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
