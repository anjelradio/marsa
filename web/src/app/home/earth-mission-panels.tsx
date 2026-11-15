"use client";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// True physical data for Earth from NASA Planetary Fact Sheet
const semimajorAxis = 149.6; // million km (1.000 AU)
const eccentricity = 0.0167;

// Keplerian orbit profile Earth around Sun
const earthDistances = Array.from({ length: 49 }, (_, index) => {
  const angle = (index / 48) * 2 * Math.PI;
  return (semimajorAxis * (1 - eccentricity ** 2)) / (1 + eccentricity * Math.cos(angle));
});

const earthOrbitProfile = [
  "0 100%",
  ...earthDistances.map((distance, index) =>
    `${(index / 48) * 100}% ${100 - ((distance - 146) / 8) * 100}%`,
  ),
  "100% 100%",
].join(", ");

// Orbital velocity calculated from vis-viva equation: ~29.3 to 30.3 km/s
const earthSpeeds = earthDistances
  .filter((_, index) => index % 8 === 0)
  .map((distance) =>
    Math.sqrt(132_712 * (2 / distance - 1 / semimajorAxis)),
  );

export interface EarthMissionPanelsProps {
  isExploring?: boolean;
}

export function EarthMissionPanels({ isExploring = false }: EarthMissionPanelsProps) {
  const measurements = [
    {
      label: "Gravedad",
      value: "9,81",
      unit: "m/s²",
      detail: "1,00g estándar",
      color: "#38bdf8",
    },
    {
      label: "Inclinación",
      value: "23,44°",
      unit: "inclinación axial",
      detail: "Ciclo estacional",
      color: "#34d399",
    },
    {
      label: "Satélite",
      value: "1",
      unit: "Luna natural",
      detail: "Masa: 1/81 Tierra",
      color: "#94a3b8",
    },
  ];

  return (
    <div
      className={cn(
        "order-4 grid gap-3 lg:contents",
        isExploring && "lg:pointer-events-none"
      )}
    >
      {/* 1. Heliocentric Orbit & Distance to Sun Panel */}
      <figure
        className={cn(
          "relative min-w-0 rounded-3xl bg-[#0e2938]/40 p-4 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[26%] lg:right-[20.7%] lg:z-0 lg:w-[30%] lg:p-2.5 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <figcaption className="mb-2 text-sm font-medium text-white lg:ml-[45%]">
          Distancia al Sol (1 AU)
        </figcaption>
        <div className="relative h-28 overflow-hidden border-b border-white/20 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(25%_-_1px),#ffffff16_calc(25%_-_1px),#ffffff16_25%)] lg:h-[clamp(5.75rem,16svh,9rem)]">
          {/* Orbital distance profile polygon */}
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-linear-to-b from-[#2e749c] via-[#164e63] to-[#082f49]"
            style={{ clipPath: `polygon(${earthOrbitProfile})` }}
          />

          {/* Scientific Mean Distance reference line (149.6M km) */}
          <div
            aria-hidden="true"
            className="absolute inset-x-0 top-[50%] border-b border-white/30 border-dashed"
          />

          {/* Key astronomical markers: Aphelion & Perihelion */}
          <span className="absolute top-1.5 left-1/2 -translate-x-1/2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-white/90">
            Afelio: 152,1M km
          </span>
          <span className="absolute bottom-1.5 left-2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-[#38bdf8]">
            Perihelio: 147,1M km
          </span>

          <p className="absolute right-2 bottom-1.5 rounded-md bg-black/60 px-2 py-0.5 text-[0.65rem] font-mono text-white/80">
            147,1–152,1 millones de km
          </p>
        </div>

        {/* Vis-viva orbital velocity section */}
        <div className="mt-3 flex items-end gap-2.5 lg:ml-[39%]">
          <div
            aria-hidden="true"
            className="flex h-13 flex-1 items-end justify-evenly gap-2 border-b border-white/15 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(33.33%_-_1px),#ffffff12_calc(33.33%_-_1px),#ffffff12_33.33%)] px-2 lg:h-[clamp(2.5rem,8svh,4.5rem)]"
          >
            {earthSpeeds.map((speed, index) => (
              <span
                key={index}
                className="w-1 rounded-full bg-[#38bdf8]/90"
                style={{ height: `${Math.max(20, Math.min(100, ((speed - 28) / 3) * 100))}%` }}
              />
            ))}
          </div>
          <p className="text-right text-[0.625rem] leading-tight text-white/80">
            Velocidad orbital
            <span className="block font-mono font-medium">29,3–30,3 km/s</span>
          </p>
        </div>
      </figure>

      {/* 2. NASA Analog Testing Program Card */}
      <Card
        className={cn(
          "relative z-10 flex-row items-center gap-3 rounded-3xl bg-[#0e2938]/65 p-1.5 text-white shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[65%] lg:right-[20.7%] lg:w-[31%] lg:gap-4 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <span className="grid min-h-16 shrink-0 place-items-center rounded-[1.15rem] bg-linear-to-br from-[#38bdf8] to-[#0284c7] px-4 text-sm font-semibold text-[#082f49] shadow-[0_0_26px_#38bdf860] lg:min-h-[clamp(4rem,10svh,6rem)] lg:basis-[34%]">
          NASA DSS
        </span>
        <div className="min-w-0 py-2 pr-2">
          <p className="text-[clamp(1.4rem,3vw,2.6rem)] font-semibold leading-none tracking-tight font-mono">
            10 Sitios
          </p>
          <p className="mt-1 text-xs text-white/80">
            Red Global de Análogos Terrestres
          </p>
          <p className="text-[0.65rem] text-white/60">
            Atacama, McMurdo, Río Tinto, Devon y más
          </p>
        </div>
      </Card>

      {/* 3. Physical Gauges */}
      <aside
        aria-label="Mediciones Terrestres"
        className={cn(
          "order-5 grid grid-cols-1 gap-2.5 sm:grid-cols-3 lg:absolute lg:top-20 lg:right-4 lg:z-20 lg:flex lg:w-48 lg:flex-col lg:gap-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring ? "lg:translate-x-72 lg:opacity-0 pointer-events-none" : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        {measurements.map(({ label, value, unit, detail, color }, index) => (
          <Card
            key={label}
            className="group min-w-0 justify-between gap-1.5 rounded-3xl bg-[#0e2938]/60 p-3.5 text-white shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,background-color,box-shadow] duration-300 hover:-translate-y-1 hover:ring-white/20 hover:shadow-[0_16px_36px_#00000045] motion-reduce:transition-none lg:min-h-30"
            style={{ animationDelay: `${120 + index * 90}ms` }}
          >
            <p className="flex items-center gap-2 text-xs leading-tight text-white/75">
              <span
                className="size-2 rounded-full"
                style={{ backgroundColor: color }}
              />
              {label}
            </p>
            <p className="pl-1 text-xl leading-none font-medium tracking-tight tabular-nums xl:text-2xl">
              {value}
              <span className="mt-1 block text-xs font-normal tracking-normal text-white/65">
                {unit}
              </span>
              <span className="mt-1.5 block text-[0.62rem] font-normal tracking-normal text-white/50 font-mono">
                {detail}
              </span>
            </p>
          </Card>
        ))}
      </aside>
    </div>
  );
}
