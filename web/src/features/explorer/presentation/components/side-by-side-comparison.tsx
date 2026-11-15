"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  X,
  Layers,
  Sparkles,
  ExternalLink,
  MapPin,
  Thermometer,
  Wind,
  Compass,
  CheckCircle2,
  Box,
  Image as ImageIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MarsPlanet } from "@/features/mars/presentation/components/mars-planet";
import { MoonPlanet } from "@/features/moon/presentation/components/moon-planet";
import { EarthPlanet } from "@/features/earth/presentation/components/earth-planet";
import { cn } from "@/lib/utils";

export interface ComparisonSiteData {
  targetId: "mars-jezero" | "moon-shackleton-rim";
  targetName: string;
  targetBody: "Marte" | "Luna";
  targetCoords: string;
  targetTemp: string;
  targetPressure: string;
  targetDescription: string;
  targetImageUrl: string;
  earthSiteId: string;
  earthSiteName: string;
  earthLocation: string;
  earthCoords: string;
  earthTemp: string;
  earthPrecipitation: string;
  earthDescription: string;
  earthImageUrl: string;
  compatibilityScore: number;
  coverage: number;
  scientificRationale: string;
  fidelityFactors: { name: string; score: number; detail: string }[];
}

export const PRESET_COMPARISONS: Record<string, ComparisonSiteData> = {
  "jezero-atacama": {
    targetId: "mars-jezero",
    targetName: "Cráter Jezero",
    targetBody: "Marte",
    targetCoords: "18.38° N, 77.58° E",
    targetTemp: "140 K – 240 K (MCD v6.2 Ls=105°)",
    targetPressure: "6.1 mbar (CO₂)",
    targetDescription:
      "Antiguo lecho de lago y delta fluvial sedimentario con arcillas, carbonatos y sulfatos. Explorado por el rover Perseverance para detectar biofirmas microbianas fósiles.",
    targetImageUrl:
      "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=800&q=80",
    earthSiteId: "earth-atacama-desert",
    earthSiteName: "Desierto y Salar de Atacama",
    earthLocation: "Región de Antofagasta, Chile",
    earthCoords: "23.86° S, 69.13° W",
    earthTemp: "-5 °C a +35 °C",
    earthPrecipitation: "< 2 mm/año (Hiperárido)",
    earthDescription:
      "El desierto más árido no polar del planeta. Sus costras de halita, nitratos y regolito desecado son el laboratorio natural por excelencia de la NASA para probar sensores rover y límites biológicos.",
    earthImageUrl:
      "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80",
    compatibilityScore: 88.4,
    coverage: 100,
    scientificRationale:
      "Coincidencia sobresaliente en régimen de hiperaridez, índices de radiación UV y mineralogía de depósitos salinos evaporíticos. Excelente análogo para probar movilidad de ruedas en terreno arenoso/rocoso y espectrometría Raman/PIXL.",
    fidelityFactors: [
      { name: "Aridez y Humedad", score: 94, detail: "Evaporitas y régimen hídrico fósil casi idénticos" },
      { name: "Geomorfología", score: 86, detail: "Pendientes fluviales y costras salinas cuaternarias" },
      { name: "Radiación UV", score: 85, detail: "Altitud 2.400m con flujo UV-B análogo a superficie marciana" },
    ],
  },
  "shackleton-mcmurdo": {
    targetId: "moon-shackleton-rim",
    targetName: "Borde del Cráter Shackleton (LOLA Site04)",
    targetBody: "Luna",
    targetCoords: "89.90° S, 120.00° E",
    targetTemp: "40 K (-233 °C) en PSR a 220 K en borde (LRO Diviner)",
    targetPressure: "~3×10⁻¹⁵ bar (Vacío espacial)",
    targetDescription:
      "Cresta polar sur con picos de luz casi continua e interior en oscuridad permanente con depósitos volátiles de hielo de agua. Sitio candidato prioritario para el campamento base Artemis de la NASA.",
    targetImageUrl:
      "https://images.unsplash.com/photo-1532693322450-2cb5c511067d?auto=format&fit=crop&w=800&q=80",
    earthSiteId: "earth-mcmurdo-dry-valleys",
    earthSiteName: "Valles Secos de McMurdo",
    earthLocation: "Tierra de Victoria, Antártida",
    earthCoords: "77.50° S, 162.00° E",
    earthTemp: "-60 °C a -10 °C",
    earthPrecipitation: "< 10 mm/año (Desierto Polar Frío)",
    earthDescription:
      "Zona polar antártica libre de hielo protegida por vientos catabáticos. Presenta suelos regolíticos poligonales, permafrost seco y criósfera extrema utilizada para probar trajes EVA y perforadoras lunares.",
    earthImageUrl:
      "https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?auto=format&fit=crop&w=800&q=80",
    compatibilityScore: 84.7,
    coverage: 100,
    scientificRationale:
      "Principal análogo terrestre para procesos de criósfera polar, intemperismo físico por congelamiento y estabilidad de suelo bajo gradientes térmicos extremos. Ideal para pruebas de habitabilidad y movilidad sobre regolito congelado.",
    fidelityFactors: [
      { name: "Criósfera y Permafrost", score: 92, detail: "Regolito seco sobre permafrost a profundidades < 50 cm" },
      { name: "Aislamiento Operativo", score: 90, detail: "Logística y protocolos análogos a campamentos polares lunares" },
      { name: "Régimen Térmico", score: 72, detail: "Temperaturas terrestres bajo cero, aunque atenuadas por atmósfera" },
    ],
  },
  "jezero-rio-tinto": {
    targetId: "mars-jezero",
    targetName: "Cráter Jezero",
    targetBody: "Marte",
    targetCoords: "18.38° N, 77.58° E",
    targetTemp: "140 K – 240 K (MCD v6.2)",
    targetPressure: "6.1 mbar",
    targetDescription:
      "Depósitos sedimentarios ricos en minerales de alteración acuosa y sulfatos formados durante las etapas tempranas de Marte.",
    targetImageUrl:
      "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=800&q=80",
    earthSiteId: "earth-rio-tinto",
    earthSiteName: "Río Tinto y Faja Pirítica",
    earthLocation: "Huelva, Andalucía, España",
    earthCoords: "37.69° N, 6.55° W",
    earthTemp: "8 °C a 38 °C",
    earthPrecipitation: "650 mm/año",
    earthDescription:
      "Río de extrema acidez (pH ~2) enriquecido en hierro y sulfatos precipitados (jarosita, hematita y goethita), análogos directos de los minerales descubiertos por los rovers de la NASA.",
    earthImageUrl:
      "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
    compatibilityScore: 82.1,
    coverage: 100,
    scientificRationale:
      "Análogo geoquímico y astrobiológico de primer orden para estudiar la preservación de microfósiles y biofirmas en matrices ricas en hierro y jarosita.",
    fidelityFactors: [
      { name: "Mineralogía de Sulfatos", score: 96, detail: "Coprecipitación de jarosita y óxidos idéntica a Marte" },
      { name: "Quimiosíntesis Ácida", score: 88, detail: "Microorganismos extremófilos que subsisten sin materia orgánica" },
      { name: "Climatología Actual", score: 62, detail: "Clima mediterráneo atemperado, difiere del frío marciano" },
    ],
  },
};

interface SideBySideComparisonProps {
  initialKey?: string;
  onClose: () => void;
}

export function SideBySideComparison({
  initialKey = "jezero-atacama",
  onClose,
}: SideBySideComparisonProps) {
  const [activeKey, setActiveKey] = useState<string>(initialKey);
  const [viewMode, setViewMode] = useState<"visual" | "3d">("visual");

  const current = PRESET_COMPARISONS[activeKey] ?? PRESET_COMPARISONS["jezero-atacama"];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-xl animate-in fade-in duration-200">
      <div className="relative flex flex-col w-full max-w-6xl max-h-[92vh] overflow-hidden rounded-3xl border border-white/20 bg-[#0d131f]/95 text-white shadow-2xl">
        {/* Modal Header */}
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-5 py-4 bg-white/5">
          <div className="flex items-center gap-2">
            <span className="grid size-9 place-items-center rounded-2xl bg-white/10 text-[#ffab57]">
              <Sparkles className="size-4" />
            </span>
            <div>
              <h2 className="text-base sm:text-lg font-bold leading-tight flex items-center gap-2">
                Comparación Científica Lado a Lado
                <Badge variant="outline" className="text-xs border-[#ffab57]/50 text-[#ffab57] bg-[#ffab57]/10">
                  {current.targetBody} ↔ Tierra
                </Badge>
              </h2>
              <p className="text-xs text-white/60">
                Decision Support System · NASA Space Apps 2026
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle: Visual Card (Default) vs Dual 3D Globes */}
            <div className="flex items-center rounded-full border border-white/15 bg-black/40 p-1 text-xs">
              <button
                type="button"
                onClick={() => setViewMode("visual")}
                className={cn(
                  "flex items-center gap-1.5 rounded-full px-3 py-1 font-medium transition cursor-pointer",
                  viewMode === "visual"
                    ? "bg-white text-black shadow-md"
                    : "text-white/70 hover:text-white"
                )}
              >
                <ImageIcon className="size-3.5" />
                Ficha Visual + Texto
              </button>
              <button
                type="button"
                onClick={() => setViewMode("3d")}
                className={cn(
                  "flex items-center gap-1.5 rounded-full px-3 py-1 font-medium transition cursor-pointer",
                  viewMode === "3d"
                    ? "bg-[#ffab57] text-black shadow-md"
                    : "text-white/70 hover:text-white"
                )}
              >
                <Box className="size-3.5" />
                Vista 3D Dual
              </button>
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="rounded-full text-white/60 hover:text-white hover:bg-white/10 size-8"
            >
              <X className="size-4" />
            </Button>
          </div>
        </header>

        {/* Preset Selector Tabs */}
        <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-white/10 bg-black/20 text-xs">
          <span className="text-white/50 font-medium">Comparaciones Predefinidas:</span>
          <button
            type="button"
            onClick={() => setActiveKey("jezero-atacama")}
            className={cn(
              "rounded-full px-3 py-1 border transition cursor-pointer",
              activeKey === "jezero-atacama"
                ? "border-[#ffab57] bg-[#ffab57]/20 text-white font-semibold"
                : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
            )}
          >
            🔴 Marte (Jezero) ↔ Atacama (Chile)
          </button>
          <button
            type="button"
            onClick={() => setActiveKey("shackleton-mcmurdo")}
            className={cn(
              "rounded-full px-3 py-1 border transition cursor-pointer",
              activeKey === "shackleton-mcmurdo"
                ? "border-[#8de3ff] bg-[#8de3ff]/20 text-white font-semibold"
                : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
            )}
          >
            ⚪ Luna (Shackleton) ↔ McMurdo (Antártida)
          </button>
          <button
            type="button"
            onClick={() => setActiveKey("jezero-rio-tinto")}
            className={cn(
              "rounded-full px-3 py-1 border transition cursor-pointer",
              activeKey === "jezero-rio-tinto"
                ? "border-[#ffab57] bg-[#ffab57]/20 text-white font-semibold"
                : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
            )}
          >
            🔴 Marte (Jezero) ↔ Río Tinto (España)
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {viewMode === "3d" ? (
            /* Mode 2: Dual 3D Globes Side-by-Side */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Left: Planetary Target Globe */}
              <div className="relative flex flex-col items-center justify-center p-4 rounded-3xl border border-white/15 bg-black/40 min-h-[380px]">
                <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
                  <Badge className="bg-red-500/20 text-red-300 border-red-500/30">
                    {current.targetBody}: {current.targetName}
                  </Badge>
                </div>
                <div className="size-64 sm:size-72 relative">
                  {current.targetBody === "Marte" ? (
                    <MarsPlanet isExploring={true} showSurfaceOverlay={false} />
                  ) : (
                    <MoonPlanet isExploring={true} />
                  )}
                </div>
                <p className="mt-2 text-xs text-white/70 font-mono flex items-center gap-1">
                  <MapPin className="size-3 text-[#ffab57]" /> Coordenadas: {current.targetCoords}
                </p>
                <p className="text-[0.68rem] text-white/50 text-center mt-1 max-w-sm">
                  Arrastra el globo para rotarlo y examinar el terreno de inserción.
                </p>
              </div>

              {/* Right: Earth Globe */}
              <div className="relative flex flex-col items-center justify-center p-4 rounded-3xl border border-white/15 bg-black/40 min-h-[380px]">
                <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                    Tierra: {current.earthSiteName}
                  </Badge>
                </div>
                <div className="size-64 sm:size-72 relative">
                  <EarthPlanet isExploring={true} />
                </div>
                <p className="mt-2 text-xs text-white/70 font-mono flex items-center gap-1">
                  <MapPin className="size-3 text-cyan-400" /> Ubicación: {current.earthCoords}
                </p>
                <p className="text-[0.68rem] text-white/50 text-center mt-1 max-w-sm">
                  Arrastra el globo terrestre para localizar el laboratorio de campo.
                </p>
              </div>
            </div>
          ) : (
            /* Mode 1 (Default): Rich Visual Site Cards with Imagery & Detailed Text */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Target Planet Card */}
              <Card className="overflow-hidden rounded-3xl border-white/15 bg-white/5 p-0 text-white">
                <div className="relative h-48 w-full bg-black/50">
                  <Image
                    src={current.targetImageUrl}
                    alt={current.targetName}
                    fill
                    sizes="(max-width: 768px) 100vw, 50vw"
                    className="object-cover opacity-80"
                  />
                  <div className="absolute inset-0 bg-linear-to-t from-[#0d131f] via-transparent to-black/40" />
                  <div className="absolute bottom-3 left-4 right-4 flex items-end justify-between">
                    <div>
                      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-[#ffab57]">
                        Objetivo Planetario ({current.targetBody})
                      </span>
                      <h3 className="text-xl font-bold leading-tight">{current.targetName}</h3>
                    </div>
                    <Badge variant="secondary" className="font-mono text-xs bg-black/60 text-white/90">
                      {current.targetCoords}
                    </Badge>
                  </div>
                </div>

                <div className="p-4 space-y-3">
                  <p className="text-xs leading-relaxed text-white/80">
                    {current.targetDescription}
                  </p>
                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10 text-xs font-mono">
                    <div className="rounded-xl bg-white/5 p-2">
                      <span className="text-white/50 block text-[0.65rem]">Temperatura</span>
                      <span className="font-semibold text-white/90">{current.targetTemp}</span>
                    </div>
                    <div className="rounded-xl bg-white/5 p-2">
                      <span className="text-white/50 block text-[0.65rem]">Presión / Atmósfera</span>
                      <span className="font-semibold text-white/90">{current.targetPressure}</span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Earth Analog Card */}
              <Card className="overflow-hidden rounded-3xl border-white/15 bg-white/5 p-0 text-white">
                <div className="relative h-48 w-full bg-black/50">
                  <Image
                    src={current.earthImageUrl}
                    alt={current.earthSiteName}
                    fill
                    sizes="(max-width: 768px) 100vw, 50vw"
                    className="object-cover opacity-80"
                  />
                  <div className="absolute inset-0 bg-linear-to-t from-[#0d131f] via-transparent to-black/40" />
                  <div className="absolute bottom-3 left-4 right-4 flex items-end justify-between">
                    <div>
                      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-cyan-400">
                        Análogo Terrestre ({current.earthLocation})
                      </span>
                      <h3 className="text-xl font-bold leading-tight">{current.earthSiteName}</h3>
                    </div>
                    <Badge variant="secondary" className="font-mono text-xs bg-black/60 text-white/90">
                      {current.earthCoords}
                    </Badge>
                  </div>
                </div>

                <div className="p-4 space-y-3">
                  <p className="text-xs leading-relaxed text-white/80">
                    {current.earthDescription}
                  </p>
                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10 text-xs font-mono">
                    <div className="rounded-xl bg-white/5 p-2">
                      <span className="text-white/50 block text-[0.65rem]">Temperatura</span>
                      <span className="font-semibold text-white/90">{current.earthTemp}</span>
                    </div>
                    <div className="rounded-xl bg-white/5 p-2">
                      <span className="text-white/50 block text-[0.65rem]">Precipitación / Humedad</span>
                      <span className="font-semibold text-white/90">{current.earthPrecipitation}</span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Scientific Rationale & Compatibility Metrics */}
          <div className="rounded-3xl border border-white/15 bg-white/5 p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-semibold flex items-center gap-1.5 text-white">
                  <CheckCircle2 className="size-4 text-emerald-400" />
                  Dictamen de Compatibilidad Geocientífica
                </h4>
                <p className="text-xs text-white/60">
                  Calculado mediante el motor euclidiano ponderado y telemetría de satélites
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-[0.65rem] text-white/50 block uppercase">Puntaje de Similitud</span>
                  <span className="text-2xl font-bold font-mono text-emerald-400">
                    {current.compatibilityScore}%
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[0.65rem] text-white/50 block uppercase">Cobertura</span>
                  <span className="text-2xl font-bold font-mono text-cyan-400">
                    {current.coverage}%
                  </span>
                </div>
              </div>
            </div>

            <p className="text-xs leading-relaxed text-white/85 bg-black/30 p-3 rounded-2xl border border-white/10">
              💡 <strong className="text-white">Fundamento: </strong>
              {current.scientificRationale}
            </p>

            {/* Fidelity Factors Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              {current.fidelityFactors.map((factor) => (
                <div key={factor.name} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-semibold text-white">{factor.name}</span>
                    <span className="font-mono text-emerald-400">{factor.score}%</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-white/10 overflow-hidden">
                    <div
                      className="h-full bg-emerald-400 rounded-full"
                      style={{ width: `${factor.score}%` }}
                    />
                  </div>
                  <p className="mt-2 text-[0.65rem] text-white/60 leading-tight">
                    {factor.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 px-5 py-3.5 bg-black/40">
          <span className="text-xs text-white/50">
            Fuente científica: MCD v6.2 · NASA LRO LOLA/Diviner · Copernicus ERA5
          </span>
          <div className="flex items-center gap-2">
            <Button
              asChild
              size="sm"
              className="rounded-full bg-[#ffab57] text-black hover:bg-[#ffab57]/90 font-semibold text-xs"
            >
              <Link href="/explorer">
                Abrir en el Explorador Completo (DSS)
                <ExternalLink className="size-3.5 ml-1" />
              </Link>
            </Button>
          </div>
        </footer>
      </div>
    </div>
  );
}
