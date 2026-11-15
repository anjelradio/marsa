"use client";

import { useEffect, useState } from "react";
import {
  Award,
  ChevronDown,
  ChevronUp,
  Database,
  ExternalLink,
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
  const { locale } = useTranslation();
  const [activeTab, setActiveTab] = useState<ActiveTab>("rocks");
  const [result, setResult] = useState<RespuestaGeologiaPunto | "error" | null>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const [showSources, setShowSources] = useState(false);

  const { latitude, longitude } = point;

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setResult(null);

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

  const theme =
    cuerpo === "Marte"
      ? {
          card: "border-[#ffab57]/30 bg-linear-to-br from-[#281810]/95 via-[#1a110a]/95 to-[#100b07]/95",
          accentText: "text-[#ffab57]",
          accentIcon: "text-[#ffab57]",
          accentBg: "bg-[#ffab57]/20 text-[#ffab57]",
          tabActive: "bg-orange-600/80 text-white shadow",
          tagBg: "bg-amber-950/60 border-amber-500/30 text-amber-200",
          mineralTag: "bg-orange-950/60 border-orange-500/30 text-orange-200",
          progressBg: "bg-[#ffab57]",
          badge: "bg-amber-950/60 text-amber-300 border-amber-800/40",
        }
      : cuerpo === "Luna"
      ? {
          card: "border-slate-400/30 bg-linear-to-br from-[#1c212a]/95 via-[#13161c]/95 to-[#0b0d10]/95",
          accentText: "text-slate-300",
          accentIcon: "text-slate-300",
          accentBg: "bg-slate-400/20 text-slate-300",
          tabActive: "bg-slate-600/80 text-white shadow",
          tagBg: "bg-slate-900/80 border-slate-500/30 text-slate-200",
          mineralTag: "bg-indigo-950/60 border-indigo-500/30 text-indigo-200",
          progressBg: "bg-slate-300",
          badge: "bg-slate-900/60 text-slate-300 border-slate-700/40",
        }
      : {
          // Tierra
          card: "border-sky-500/30 bg-linear-to-br from-[#0c1f36]/95 via-[#081525]/95 to-[#040a12]/95",
          accentText: "text-sky-400",
          accentIcon: "text-sky-400",
          accentBg: "bg-sky-500/20 text-sky-400",
          tabActive: "bg-sky-600/80 text-white shadow",
          tagBg: "bg-sky-950/80 border-sky-500/30 text-sky-200",
          mineralTag: "bg-teal-950/60 border-teal-500/30 text-teal-200",
          progressBg: "bg-sky-400",
          badge: "bg-sky-950/60 text-sky-300 border-sky-800/40",
        };

  return (
    <aside
      aria-labelledby="point-geology-title"
      className="min-w-0 rounded-3xl max-sm:order-first sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className={`gap-3 rounded-3xl border p-4 text-white shadow-2xl backdrop-blur-md ${theme.card}`}>
        {/* Toggle Mode Switcher (Geología vs Clima) */}
        {onToggleViewMode && (
          <div className="grid grid-cols-2 gap-1 rounded-2xl border border-white/10 bg-black/50 p-1 text-xs">
            <button
              type="button"
              onClick={() => onToggleViewMode("geology")}
              className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
                viewMode === "geology"
                  ? theme.tabActive
                  : "text-white/60 hover:text-white"
              }`}
            >
              <Mountain className={`size-3.5 ${viewMode === "geology" ? "text-white" : theme.accentIcon}`} />
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
              <Thermometer className={`size-3.5 ${viewMode === "climate" ? "text-white" : "text-amber-400"}`} />
              <span>Clima y Atmósfera</span>
            </button>
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between gap-2 border-b border-white/10 pb-2.5">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className={`flex size-7 shrink-0 items-center justify-center rounded-xl ${theme.accentBg}`}>
                <Mountain className="size-4" />
              </span>
              <h2
                id="point-geology-title"
                className="truncate font-headline text-base font-semibold text-white"
              >
                {data ? data.region_nombre : `Geología y Minerales · ${cuerpo}`}
              </h2>
            </div>
            <p className="mt-1 font-mono text-xs text-white/60">
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
        <div className="grid grid-cols-3 gap-1 rounded-2xl bg-black/40 p-1 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("rocks")}
            className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${
              activeTab === "rocks"
                ? theme.tabActive
                : "text-white/65 hover:text-white hover:bg-white/5"
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
                : "text-white/65 hover:text-white hover:bg-white/5"
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
                : "text-white/65 hover:text-white hover:bg-white/5"
            }`}
          >
            <Sparkles className="size-3.5" />
            <span>Análogo</span>
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
                onClick={() => setAttempt((a) => a + 1)}
                className="mt-3 rounded-full border-white/20 bg-white/5 text-xs text-white hover:bg-white/10"
              >
                <RefreshCw className="mr-1.5 size-3" />
                Reintentar
              </Button>
            </div>
          )}

          {data && !loading && (
            <>
              {/* TAB 1: ROCAS & LITOLOGÍA */}
              {activeTab === "rocks" && (
                <div className="space-y-2.5">
                  <div className="rounded-2xl bg-white/5 p-2.5 border border-white/5">
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
                          className="rounded-lg bg-white/7 border border-white/10 px-2.5 py-1 text-xs text-white/90"
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
                    <div className="rounded-xl border border-white/10 bg-black/30 p-2.5 space-y-1">
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
                          className="rounded-lg bg-white/7 border border-white/10 px-2.5 py-1 text-xs text-white/90"
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
                        <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-medium text-emerald-300">
                          Laboratorio
                        </span>
                      </div>

                      {data.muestras_laboratorio_in_situ.slice(0, 2).map((m) => (
                        <div
                          key={m.muestra_id}
                          className="rounded-2xl border border-white/10 bg-black/30 p-2.5 space-y-1.5"
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
                    <div className="rounded-xl bg-white/5 p-3 text-xs text-white/60">
                      Este punto cuenta con análisis espectral multiespectral y
                      litológico regional. Consulta la pestaña Análogo para
                      ver los sitios gemelos en Marte o la Luna con muestras CheMin y Apolo.
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: ANÁLOGO PLANETARIO */}
              {activeTab === "analogs" && (
                <div className="space-y-2.5">
                  {data.mejor_analogo ? (
                    <div className="space-y-2.5">
                      {/* Analogue Match Card */}
                      <div className="rounded-2xl border border-white/10 bg-black/40 p-3 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className={`flex items-center gap-1.5 text-xs font-semibold ${theme.accentText}`}>
                            <Orbit className="size-3.5" />
                            Análogo en {data.mejor_analogo.cuerpo_destino as string || "Planeta Destino"}
                          </span>
                          {/* Score Badge */}
                          {(() => {
                            const match = (data.mejor_analogo.celda_analoga as any) || (data.mejor_analogo.sitio_analogo_terrestre as any);
                            const score = match?.indice_similitud_algoritmo_pct ?? match?.similitud_pct;
                            return score !== undefined ? (
                              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-bold text-emerald-300 border border-emerald-500/30">
                                <Award className="size-3" />
                                {fmt(score, 1)}% similitud
                              </span>
                            ) : null;
                          })()}
                        </div>

                        {/* Matching Region */}
                        {(() => {
                          const match = (data.mejor_analogo.celda_analoga as any) || (data.mejor_analogo.sitio_analogo_terrestre as any);
                          if (!match) return null;
                          return (
                            <div className="space-y-1">
                              <h4 className="text-sm font-semibold text-white">
                                {match.region_referencia || match.celda_id}
                              </h4>
                              {match.unidad_geologica && (
                                <p className="text-xs text-white/70">
                                  {match.unidad_geologica}
                                </p>
                              )}
                              {match.rocas_principales && match.rocas_principales.length > 0 && (
                                <div className="mt-1 flex flex-wrap gap-1">
                                  {match.rocas_principales.map((r: string, idx: number) => (
                                    <span
                                      key={idx}
                                      className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] text-white/80"
                                    >
                                      {r}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>

                      <div className="rounded-xl bg-white/5 p-2.5 text-xs text-white/70 leading-relaxed">
                        El algoritmo de AstroPlus analiza la distribución litológica y mineralógica
                        calculando la similitud coseno entre las celdas globales 10°×10°.
                      </div>
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
          <div className="border-t border-white/10 pt-2 text-[11px]">
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
              <div className="mt-2 space-y-1.5 rounded-xl bg-black/40 p-2.5 text-[10px] text-white/70">
                {data.atribuciones.map((att, i) => (
                  <div key={i} className="border-b border-white/5 pb-1 last:border-0 last:pb-0">
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
