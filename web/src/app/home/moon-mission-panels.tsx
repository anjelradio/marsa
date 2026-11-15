"use client";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// True physical data for Moon from NASA Planetary Fact Sheet
const semimajorAxis = 384.4; // thousand km
const eccentricity = 0.0549;

// Keplerian orbit profile Earth-Moon: r(θ) across a full 360° revolution
const moonDistances = Array.from({ length: 49 }, (_, index) => {
  const angle = (index / 48) * 2 * Math.PI;
  return (semimajorAxis * (1 - eccentricity ** 2)) / (1 + eccentricity * Math.cos(angle));
});

const moonOrbitProfile = [
  "0 100%",
  ...moonDistances.map((distance, index) =>
    `${(index / 48) * 100}% ${100 - ((distance - 355) / 58) * 100}%`,
  ),
  "100% 100%",
].join(", ");

// Orbital velocity calculated using the vis-viva equation: v = sqrt(GM * (2/r - 1/a))
const moonSpeeds = moonDistances
  .filter((_, index) => index % 8 === 0)
  .map((distance) =>
    Math.sqrt(398_600 * (2 / (distance * 1000) - 1 / (semimajorAxis * 1000))) / 1000,
  );

export interface MoonMissionPanelsProps {
  isExploring?: boolean;
}

export function MoonMissionPanels({ isExploring = false }: MoonMissionPanelsProps) {
  const measurements = [
    {
      label: "Gravedad",
      value: "1,62",
      unit: "m/s²",
      detail: "16,6% de la Tierra",
      color: "#5fa8db",
    },
    {
      label: "Inclinación",
      value: "1,54°",
      unit: "inclinación axial",
      detail: "Picos de luz eterna",
      color: "#79c2d0",
    },
    {
      label: "Albedo",
      value: "0,12",
      unit: "reflectividad",
      detail: "Regolito anortosítico",
      color: "#d0d9e0",
    },
  ];

  return (
    <div
      className={cn(
        "order-4 grid gap-3 lg:contents",
        isExploring && "lg:pointer-events-none"
      )}
    >
      {/* 1. Earth-Moon Distance & Keplerian Orbit Panel */}
      <figure
        className={cn(
          "relative min-w-0 rounded-3xl bg-[#132338]/40 p-4 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[26%] lg:right-[20.7%] lg:z-0 lg:w-[30%] lg:p-2.5 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <figcaption className="mb-2 text-sm font-medium text-white lg:ml-[45%]">
          Distancia a la Tierra
        </figcaption>
        <div className="relative h-28 overflow-hidden border-b border-white/20 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(25%_-_1px),#ffffff16_calc(25%_-_1px),#ffffff16_25%)] lg:h-[clamp(5.75rem,16svh,9rem)]">
          {/* Orbital distance profile polygon */}
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-linear-to-b from-[#4a85b5] via-[#244c70] to-[#0c1f33]"
            style={{ clipPath: `polygon(${moonOrbitProfile})` }}
          />

          {/* Scientific Mean Distance reference line (384.4k km) */}
          <div
            aria-hidden="true"
            className="absolute inset-x-0 top-[50%] border-b border-white/30 border-dashed"
          />

          {/* Key astronomical markers: Apogee (Peak) & Perigee (Base) */}
          <span className="absolute top-1.5 left-1/2 -translate-x-1/2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-white/90">
            Apogeo: 405,5k km
          </span>
          <span className="absolute bottom-1.5 left-2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-[#8de3ff]">
            Perigeo: 363,3k km
          </span>

          <p className="absolute right-2 bottom-1.5 rounded-md bg-black/60 px-2 py-0.5 text-[0.65rem] font-mono text-white/80">
            363,3–405,5 mil km
          </p>
        </div>

        {/* Vis-viva orbital velocity section */}
        <div className="mt-3 flex items-end gap-2.5 lg:ml-[39%]">
          <div
            aria-hidden="true"
            className="flex h-13 flex-1 items-end justify-evenly gap-2 border-b border-white/15 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(33.33%_-_1px),#ffffff12_calc(33.33%_-_1px),#ffffff12_33.33%)] px-2 lg:h-[clamp(2.5rem,8svh,4.5rem)]"
          >
            {moonSpeeds.map((speed, index) => (
              <span
                key={index}
                className="w-1 rounded-full bg-[#8de3ff]/90"
                style={{ height: `${Math.max(20, Math.min(100, (speed / 1.1) * 100))}%` }}
              />
            ))}
          </div>
          <p className="text-right text-[0.625rem] leading-tight text-white/80">
            Velocidad orbital
            <span className="block font-mono font-medium">0,97–1,08 km/s</span>
          </p>
        </div>
      </figure>

      {/* 2. Artemis III Landing Site Card */}
      <Card
        className={cn(
          "relative z-10 flex-row items-center gap-3 rounded-3xl bg-[#132338]/65 p-1.5 text-white shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[65%] lg:right-[20.7%] lg:w-[31%] lg:gap-4 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <span className="grid min-h-16 shrink-0 place-items-center rounded-[1.15rem] bg-linear-to-br from-[#8de3ff] to-[#2563eb] px-4 text-sm font-semibold text-[#0a192f] shadow-[0_0_26px_#8de3ff60] lg:min-h-[clamp(4rem,10svh,6rem)] lg:basis-[34%]">
          Artemis III
        </span>
        <div className="min-w-0 py-2 pr-2">
          <p className="text-[clamp(1.4rem,3vw,2.6rem)] font-semibold leading-none tracking-tight font-mono">
            89,9° S
          </p>
          <p className="mt-1 text-xs text-white/80">
            Borde Shackleton · Sitio LOLA 04
          </p>
          <p className="text-[0.65rem] text-white/60">
            Base permanente y trampas frías de hielo
          </p>
        </div>
      </Card>

      {/* 3. Physical Gauges */}
      <aside
        aria-label="Mediciones Lunares"
        className={cn(
          "order-5 grid grid-cols-1 gap-2.5 sm:grid-cols-3 lg:absolute lg:top-20 lg:right-4 lg:z-20 lg:flex lg:w-48 lg:flex-col lg:gap-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring ? "lg:translate-x-72 lg:opacity-0 pointer-events-none" : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        {measurements.map(({ label, value, unit, detail, color }, index) => (
          <Card
            key={label}
            className="group min-w-0 justify-between gap-1.5 rounded-3xl bg-[#132338]/60 p-3.5 text-white shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,background-color,box-shadow] duration-300 hover:-translate-y-1 hover:ring-white/20 hover:shadow-[0_16px_36px_#00000045] motion-reduce:transition-none lg:min-h-30"
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
