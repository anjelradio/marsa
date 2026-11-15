"use client";

import { useEffect, useState } from "react";
import {
  Award,
  ChevronDown,
  ChevronUp,
  Database,
  FlaskConical,
  Gem,
  Layers,
  MapPin,
  Mountain,
  Orbit,
  RefreshCw,
  Sparkles,
  Thermometer,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import {
  requestPointGeology,
  type RespuestaGeologiaPunto,
} from "@/features/geology/infrastructure/geology-client";
import { useTranslation } from "@/i18n/context";
import { MarsAnalogComparison } from "./mars-analog-comparison";

type ActiveTab = "rocks" | "minerals" | "analogs";

export function PointGeologyPanel({
  cuerpo,
  point,
  onClose,
  viewMode = "geology",
  onToggleViewMode,
}: {
  cuerpo: "Tierra" | "Marte" | "Luna";
  point: GeoPoint;
  onClose: () => void;
  viewMode?: "geology" | "climate";
  onToggleViewMode?: (mode: "geology" | "climate") => void;
}) {
  const { dict, locale } = useTranslation();
  const [activeTab, setActiveTab] = useState<ActiveTab>(cuerpo === "Marte" ? "analogs" : "rocks");
  const [result, setResult] = useState<RespuestaGeologiaPunto | "error" | null>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const [showSources, setShowSources] = useState(false);

  const { latitude, longitude } = point;

  useEffect(() => {
    const controller = new AbortController();

    requestPointGeology(
      cuerpo,
      { latitude, longitude },
      controller.signal,
      "Error al obtener los datos geológicos en tiempo real"
    )
      .then((res) => {
        if (controller.signal.aborted) return;
        if (res.ok) {
          setResult(res.data);
        } else {
          setResult("error");
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setResult("error");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [cuerpo, latitude, longitude, attempt]);

  const fmt = (val: number, maxDigits = 2) =>
    val.toLocaleString(locale, { maximumFractionDigits: maxDigits });

  const data = result && result !== "error" ? result : null;
  const legacyAnalog = data?.mejor_analogo;
  const legacyMatch = legacyAnalog?.celda_analoga ?? legacyAnalog?.sitio_analogo_terrestre;
  const legacyScore = legacyMatch?.indice_similitud_algoritmo_pct
    ?? legacyAnalog?.sitio_analogo_terrestre?.similitud_pct;

  const theme =
    cuerpo === "Marte"
      ? {
          card: "bg-[#2d1e14]/55",
          accentText: "text-[#ffab57]",
          accentIcon: "text-[#ffab57]",
          accentBg: "bg-white/7 text-[#ffab57]",
          tabActive: "bg-white/15 text-white shadow-none",
          tagBg: "bg-white/7 text-white/90",
          mineralTag: "bg-white/7 text-white/90",
          progressBg: "bg-[#ffab57]",
          badge: "bg-white/7 text-[#ffab57]",
        }
      : cuerpo === "Luna"
      ? {
          card: "bg-[#161a24]/55",
          accentText: "text-slate-300",
          accentIcon: "text-slate-300",
          accentBg: "bg-white/7 text-slate-300",
          tabActive: "bg-white/15 text-white shadow-none",
          tagBg: "bg-white/7 text-slate-200",
          mineralTag: "bg-white/7 text-slate-200",
          progressBg: "bg-slate-300",
          badge: "bg-white/7 text-slate-300",
        }
      : {
          // Tierra
          card: "bg-[#131a30]/55",
          accentText: "text-sky-400",
          accentIcon: "text-sky-400",
          accentBg: "bg-white/7 text-sky-400",
          tabActive: "bg-white/15 text-white shadow-none",
          tagBg: "bg-white/7 text-sky-200",
          mineralTag: "bg-white/7 text-sky-200",
          progressBg: "bg-sky-400",
          badge: "bg-white/7 text-sky-300",
        };

  return (
    <aside
      aria-labelledby="point-geology-title"
      className="min-w-0 rounded-4xl max-sm:order-first sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className={`gap-3.5 rounded-4xl border-0 p-5 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl ${theme.card}`}>
        {/* Toggle Mode Switcher (Geología vs Clima) */}
        {onToggleViewMode && (
          <div className="grid grid-cols-2 gap-1 rounded-2xl bg-white/7 backdrop-blur-md p-1 text-xs">
            <button
              type="button"
              onClick={() => onToggleViewMode("geology")}
              className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
                viewMode === "geology"
                  ? theme.tabActive
                  : "text-white/60 hover:text-white"
              }`}
            >
              <Mountain className={`size-3.5 ${viewMode === "geology" ? theme.accentIcon : "text-white/50"}`} />
              <span>Rocas y Minerales</span>
            </button>
            <button
              type="button"
              onClick={() => onToggleViewMode("climate")}
              className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
                viewMode === "climate"
                  ? theme.tabActive
                  : "text-white/60 hover:text-white"
              }`}
            >
              <Thermometer className={`size-3.5 ${viewMode === "climate" ? "text-amber-400" : "text-white/50"}`} />
              <span>Clima y Atmósfera</span>
            </button>
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between gap-2 pb-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2.5">
              <span className={`grid size-8 shrink-0 place-items-center rounded-xl ${theme.accentBg}`}>
                <Mountain className="size-4" />
              </span>
              <h2
                id="point-geology-title"
                className="truncate font-headline text-base font-semibold text-white"
              >
                {data ? data.region_nombre : `Geología y Minerales · ${cuerpo}`}
              </h2>
            </div>
            <p className="mt-1 pl-10.5 font-mono text-xs text-white/60">
              <span className="inline-flex items-center gap-1">
                <MapPin className={`size-3 ${theme.accentIcon}`} />
                {fmt(latitude)}° Lat · {fmt(longitude)}° Lon
              </span>
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="Cerrar panel geológico"
            onClick={onClose}
            className="shrink-0 rounded-full text-white/70 hover:bg-white/10 hover:text-white"
          >
            <X className="size-4" />
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="grid grid-cols-3 gap-1 rounded-2xl bg-white/7 backdrop-blur-md p-1 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("rocks")}
            className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
              activeTab === "rocks"
                ? theme.tabActive
                : "text-white/60 hover:text-white"
            }`}
          >
            <Layers className="size-3.5" />
            <span>Rocas</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("minerals")}
            className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
              activeTab === "minerals"
                ? theme.tabActive
                : "text-white/60 hover:text-white"
            }`}
          >
            <Gem className="size-3.5" />
            <span>Minerales</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("analogs")}
            className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
              activeTab === "analogs"
                ? theme.tabActive
                : "text-white/60 hover:text-white"
            }`}
          >
            <Sparkles className="size-3.5" />
            <span>{cuerpo === "Marte" ? dict.marsAnalogComparison.tab : "Análogo"}</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="min-h-52">
          {loading && (
            <div className="flex flex-col items-center justify-center gap-3 py-10 text-white/70">
              <RefreshCw className={`size-6 animate-spin ${theme.accentIcon}`} />
              <p className="text-xs">
                Consultando geología y minerales en tiempo real...
              </p>
            </div>
          )}

          {result === "error" && !loading && (
            <div className="rounded-2xl border border-red-500/20 bg-red-950/20 p-4 text-center">
              <p className="text-xs text-red-300">
                No fue posible conectar con los servicios de geología para este punto.
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setLoading(true);
                  setResult(null);
                  setAttempt((a) => a + 1);
                }}
                className="mt-3 rounded-full border-white/20 bg-white/5 text-xs text-white hover:bg-white/10"
              >
                <RefreshCw className="mr-1.5 size-3" />
                Reintentar
              </Button>
            </div>
          )}

          {data?.cobertura_geologica === false && (
            <p role="status" className="rounded-2xl bg-white/5 p-3 text-sm text-white/80">
              {dict.marsAnalogComparison.noCoverage}
            </p>
          )}

          {data && !loading && data.cobertura_geologica !== false && (
            <>
              {/* TAB 1: ROCAS & LITOLOGÍA */}
              {activeTab === "rocks" && (
                <div className="space-y-2.5">
                  <div className="rounded-2xl bg-white/7 backdrop-blur-md p-3.5">
                    <span className={`text-[10px] font-semibold tracking-wider uppercase ${theme.accentText}`}>
                      Unidad Geológica
                    </span>
                    <h3 className="mt-0.5 text-sm font-medium text-white leading-snug">
                      {data.unidad_geologica}
                    </h3>
                    <p className="mt-1 text-xs text-white/60">
                      {data.tipo_terreno}
                    </p>
                  </div>

                  {/* Rocas Predominantes */}
                  <div>
                    <span className="flex items-center gap-1.5 text-[11px] font-medium text-white/70 uppercase tracking-wider">
                      <Layers className={`size-3.5 ${theme.accentIcon}`} />
                      Rocas Predominantes
                    </span>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {data.rocas_predominantes.map((roca, idx) => (
                        <span
                          key={idx}
                          className="rounded-xl bg-white/7 px-2.5 py-1 text-xs text-white/90"
                        >
                          {roca}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Distribución Litológica (% Área) */}
                  {Object.keys(data.distribucion_litologica).length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <span className="text-[11px] font-semibold text-white/70 uppercase tracking-wider">
                        Distribución de Área 10°×10°
                      </span>
                      <div className="space-y-1">
                        {Object.entries(data.distribucion_litologica).map(
                          ([cat, pct]) => (
                            <div
                              key={cat}
                              className="flex items-center justify-between text-xs"
                            >
                              <span className="capitalize text-white/70">
                                {cat.replace("_", " ")}
                              </span>
                              <div className="flex items-center gap-2">
                                <div className="h-1.5 w-20 overflow-hidden rounded-full bg-white/10">
                                  <div
                                    className={`h-full rounded-full ${theme.progressBg}`}
                                    style={{ width: `${Math.min(100, pct)}%` }}
                                  />
                                </div>
                                <span className="font-mono text-white/90 text-[11px]">
                                  {fmt(pct, 1)}%
                                </span>
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {/* Unidades Macrostrat en vivo (si existen) */}
                  {data.unidades_macrostrat.length > 0 && (
                    <div className="rounded-2xl bg-white/7 backdrop-blur-md p-3.5 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className={`text-[10px] font-semibold ${theme.accentText}`}>
                          Macrostrat Live Data
                        </span>
                        <span className="text-[10px] text-white/50">
                          {data.unidades_macrostrat.length} unidades encontradas
                        </span>
                      </div>
                      {data.unidades_macrostrat.slice(0, 2).map((u, i) => (
                        <div key={i} className="text-xs text-white/80">
                          <p className="font-medium text-white">{u.nombre}</p>
                          {u.descripcion && (
                            <p className="text-[11px] text-white/60 line-clamp-2">
                              {u.descripcion}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: MINERALES & MUESTRAS IN-SITU */}
              {activeTab === "minerals" && (
                <div className="space-y-2.5">
                  {/* Minerales Principales / Detectados por Espectrometría */}
                  <div>
                    <span className="flex items-center gap-1.5 text-[11px] font-medium text-white/70 uppercase tracking-wider">
                      <Gem className="size-3.5 text-teal-400" />
                      Minerales Detectados (Espectrometría Orbital)
                    </span>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {data.minerales_principales.map((mineral, idx) => (
                        <span
                          key={idx}
                          className="rounded-xl bg-white/7 px-2.5 py-1 text-xs text-white/90"
                        >
                          {mineral}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Muestras de Laboratorio In-Situ (CheMin XRD / Apolo) */}
                  {data.muestras_laboratorio_in_situ.length > 0 ? (
                    <div className="space-y-2 pt-1">
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-[11px] font-semibold text-white/90 uppercase tracking-wider">
                          <FlaskConical className={`size-3.5 ${theme.accentIcon}`} />
                          Muestras In-Situ Cuantitativas (% wt)
                        </span>
                        <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-medium text-emerald-300">
                          Laboratorio
                        </span>
                      </div>

                      {data.muestras_laboratorio_in_situ.slice(0, 2).map((m) => (
                        <div
                          key={m.muestra_id}
                          className="rounded-2xl bg-white/7 backdrop-blur-md p-3.5 space-y-1.5"
                        >
                          <div className="flex items-baseline justify-between">
                            <span className={`font-semibold text-xs ${theme.accentText}`}>
                              {m.muestra_id.replace(/_/g, " ")}
                            </span>
                            <span className="text-[10px] text-white/50">
                              {m.instrumento.split("-")[0]}
                            </span>
                          </div>
                          <p className="text-[11px] text-white/70">
                            {m.tipo_material}
                          </p>

                          {/* Mineral abundances */}
                          <div className="space-y-1 pt-1">
                            {m.minerales.map((min, mIdx) => (
                              <div
                                key={mIdx}
                                className="flex items-center justify-between text-[11px]"
                              >
                                <span className="text-white/80 truncate max-w-[55%]">
                                  {min.nombre}
                                </span>
                                <div className="flex items-center gap-2">
                                  <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/10">
                                    <div
                                      className={`h-full rounded-full ${theme.progressBg}`}
                                      style={{ width: `${Math.min(100, min.abundancia * 1.5)}%` }}
                                    />
                                  </div>
                                  <span className="font-mono text-white text-[10px] w-12 text-right">
                                    {fmt(min.abundancia, 1)} {min.unidad.split(" ")[0]}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-white/7 p-3.5 text-xs text-white/60">
                      Este punto cuenta con análisis espectral multiespectral y
                      litológico regional. Consulta la pestaña Análogo para
                      ver los sitios gemelos en Marte o la Luna con muestras CheMin y Apolo.
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: ANÁLOGO PLANETARIO */}
              {activeTab === "analogs" && data.ranking_terrestre && (
                <MarsAnalogComparison ranking={data.ranking_terrestre} point={point} />
              )}
              {activeTab === "analogs" && !data.ranking_terrestre && (
                <div className="space-y-2.5">
                  {legacyAnalog && legacyMatch ? (
                    <div className="space-y-2.5">
                      <div className="space-y-2 rounded-2xl bg-white/7 backdrop-blur-md p-3.5">
                        <div className="flex items-center justify-between">
                          <span className={`flex items-center gap-1.5 text-xs font-semibold ${theme.accentText}`}>
                            <Orbit className="size-3.5" />
                            Análogo en {legacyAnalog.cuerpo_destino}
                          </span>
                          {legacyScore != null && (
                            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-xs font-semibold text-emerald-300">
                              <Award className="size-3" />
                              {fmt(legacyScore, 1)}% similitud
                            </span>
                          )}
                        </div>
                        <h4 className="text-sm font-semibold text-white">{legacyMatch.region_referencia}</h4>
                        {legacyMatch.unidad_geologica && (
                          <p className="text-xs text-white/70">{legacyMatch.unidad_geologica}</p>
                        )}
                        {legacyMatch.rocas_principales.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {legacyMatch.rocas_principales.map((roca) => (
                              <span key={roca} className="rounded-lg bg-white/10 px-2 py-0.5 text-[10px] text-white/90">{roca}</span>
                            ))}
                          </div>
                        )}
                      </div>
                      <p className="rounded-2xl bg-white/7 p-3 text-xs leading-relaxed text-white/70">
                        Similitud coseno entre proporciones litológicas de las regiones catalogadas.
                      </p>
                    </div>
                  ) : (
                    <div className="text-xs text-white/60 p-4 text-center">
                      No hay datos de analogía disponibles para esta coordenada.
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer / Metadatos y Fuentes */}
        {data && data.atribuciones.length > 0 && (
          <div className="pt-2 text-[11px]">
            <button
              type="button"
              onClick={() => setShowSources(!showSources)}
              className="flex w-full items-center justify-between text-white/50 hover:text-white transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <Database className={`size-3 ${theme.accentIcon}`} />
                Fuentes oficiales y licencias ({data.atribuciones.length})
              </span>
              {showSources ? (
                <ChevronUp className="size-3.5" />
              ) : (
                <ChevronDown className="size-3.5" />
              )}
            </button>

            {showSources && (
              <div className="mt-2 space-y-1.5 rounded-2xl bg-white/7 p-3 text-[10px] text-white/70">
                {data.atribuciones.map((att, i) => (
                  <div key={i} className="border-b border-white/5 pb-1.5 last:border-0 last:pb-0">
                    <p className="font-semibold text-white/90">{att.fuente}</p>
                    <p className="text-white/60">{att.nota_metodologica}</p>
                    <p className="text-white/40">Licencia: {att.licencia} · Escala: {att.resolucion_o_escala}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>
    </aside>
  );
}
