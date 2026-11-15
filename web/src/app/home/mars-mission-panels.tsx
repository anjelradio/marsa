"use client";

import { Card } from "@/components/ui/card";
import { useTranslation } from "@/i18n/context";
import { cn } from "@/lib/utils";

// True physical data for Mars from NASA NSSDC Planetary Fact Sheet
const semimajorAxis = 227.956; // million km (1.524 AU)
const eccentricity = 0.0935;

// Keplerian orbital profile: distance r(θ) across a full 360° revolution
const orbitDistances = Array.from({ length: 49 }, (_, index) => {
  const angle = (index / 48) * 2 * Math.PI;
  return (semimajorAxis * (1 - eccentricity ** 2)) / (1 + eccentricity * Math.cos(angle));
});

const orbitProfile = [
  "0 100%",
  ...orbitDistances.map((distance, index) =>
    `${(index / 48) * 100}% ${100 - ((distance - 200) / 60) * 100}%`,
  ),
  "100% 100%",
].join(", ");

// Orbital velocity calculated from distance using the vis-viva equation: v = sqrt(GM * (2/r - 1/a))
const orbitSpeeds = orbitDistances
  .filter((_, index) => index % 8 === 0)
  .map((distance) =>
    Math.sqrt(132_712 * (2 / distance - 1 / semimajorAxis)),
  );

interface MarsMissionPanelsProps {
  isExploring?: boolean;
}

export function MarsMissionPanels({ isExploring = false }: MarsMissionPanelsProps) {
  const { dict } = useTranslation();

  const measurements = [
    {
      label: dict.mars.panels.measurements.gravity,
      value: dict.mars.panels.measurements.gravityVal,
      unit: dict.mars.panels.measurements.gravityUnit,
      color: "#ae4685",
    },
    {
      label: dict.mars.panels.measurements.tilt,
      value: dict.mars.panels.measurements.tiltVal,
      unit: dict.mars.panels.measurements.tiltUnit,
      color: "#5f8bdb",
    },
    {
      label: dict.mars.panels.measurements.moons,
      value: dict.mars.panels.measurements.moonsVal,
      unit: dict.mars.panels.measurements.moonsUnit,
      color: "#b7b6ba",
    },
  ];

  return (
    <div
      className={cn(
        "order-4 grid gap-3 lg:contents",
        isExploring && "lg:pointer-events-none"
      )}
    >
      {/* 1. Heliocentric Distance & Keplerian Orbit Panel */}
      <figure
        className={cn(
          "relative min-w-0 rounded-3xl bg-app-primary/40 p-4 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[26%] lg:right-[20.7%] lg:z-0 lg:w-[30%] lg:p-2.5 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <figcaption className="mb-2 text-sm font-medium text-app-primary-foreground lg:ml-[45%]">
          {dict.mars.panels.distanceToSunTitle}
        </figcaption>
        <div className="relative h-28 overflow-hidden border-b border-white/20 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(25%_-_1px),#ffffff16_calc(25%_-_1px),#ffffff16_25%)] lg:h-[clamp(5.75rem,16svh,9rem)]">
          {/* Orbital distance profile polygon */}
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-linear-to-b from-[#b75d99] via-[#733460] to-[#31152e]"
            style={{ clipPath: `polygon(${orbitProfile})` }}
          />

          {/* Scientific Mean Distance reference line (227.9M km) */}
          <div
            aria-hidden="true"
            className="absolute inset-x-0 top-[53.5%] border-b border-white/30 border-dashed"
          />

          {/* Key astronomical markers: Aphelion (Peak) & Perihelion (Base) */}
          <span className="absolute top-1.5 left-2 rounded bg-black/70 px-1.5 py-0.5 text-[0.62rem] font-mono text-white/90">
            {dict.mars.panels.aphelion}
          </span>
          <span className="absolute bottom-1.5 left-2 rounded bg-black/70 px-1.5 py-0.5 text-[0.62rem] font-mono text-[#ffdb8a]">
            {dict.mars.panels.perihelion}
          </span>

          <p className="absolute right-2 top-1.5 rounded-md bg-black/70 px-2 py-0.5 text-[0.62rem] font-mono text-app-secondary">
            {dict.mars.panels.distanceRange}
          </p>
        </div>

        {/* Vis-viva orbital velocity section */}
        <div className="mt-3 flex items-end gap-2.5 lg:ml-[39%]">
          <div
            aria-hidden="true"
            className="flex h-13 flex-1 items-end justify-evenly gap-2 border-b border-white/15 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(33.33%_-_1px),#ffffff12_calc(33.33%_-_1px),#ffffff12_33.33%)] px-2 lg:h-[clamp(2.5rem,8svh,4.5rem)]"
          >
            {orbitSpeeds.map((speed, index) => (
              <span
                key={index}
                className="w-1 rounded-full bg-app-secondary/90"
                style={{ height: `${((speed - 21) / 6) * 100}%` }}
              />
            ))}
          </div>
          <p className="text-right text-[0.625rem] leading-tight text-app-secondary/80">
            {dict.mars.panels.orbitalSpeed}
            <span className="block font-mono font-medium">{dict.mars.panels.orbitalSpeedRange}</span>
          </p>
        </div>
      </figure>

      {/* 2. Curiosity Rover Landing Card */}
      <Card
        className={cn(
          "relative z-10 flex-row items-center gap-3 rounded-3xl bg-app-primary/65 p-1.5 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[65%] lg:right-[20.7%] lg:w-[31%] lg:gap-4 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <span className="grid min-h-16 shrink-0 place-items-center rounded-[1.15rem] bg-linear-to-br from-[#ffdb8a] to-[#f3824a] px-4 text-sm font-semibold text-[#39190d] shadow-[0_0_26px_#ffab5760] lg:min-h-[clamp(4rem,10svh,6rem)] lg:basis-[34%]">
          {dict.mars.panels.missionCuriosity}
        </span>
        <div className="min-w-0 py-2 pr-2">
          <p className="text-[clamp(1.4rem,3vw,2.6rem)] font-semibold leading-none tracking-tight font-mono">
            {dict.mars.panels.missionCuriosityCoord}
          </p>
          <p className="mt-1 text-xs text-app-secondary/70">
            {dict.mars.panels.missionCuriosityDesc}
          </p>
        </div>
      </Card>

      {/* 3. Physical Characteristics Circular Gauges */}
      <dl
        className={cn(
          "relative z-10 grid grid-cols-3 gap-1 rounded-3xl bg-app-primary/65 p-2 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[79.5%] lg:right-[20.7%] lg:w-[37%] lg:p-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        {measurements.map(({ label, value, unit, color }) => (
          <div key={label} className="relative flex min-w-0 flex-col items-center justify-center gap-0.5 py-3.5 text-center">
            <span
              aria-hidden="true"
              className="absolute inset-0 m-auto aspect-square w-full max-w-24 rounded-full border border-white/12 p-1"
            >
              <span
                className="block size-full rounded-full mask-[radial-gradient(closest-side,transparent_86%,black_89%,black_96%,transparent_99%)]"
                style={{ backgroundImage: `conic-gradient(${color} 65%, #bcbcbc17 0)` }}
              />
            </span>
            <dt className="order-2 text-[0.65rem] leading-none text-app-secondary/70">{label}</dt>
            <dd className="relative">
              <span className="block text-lg font-semibold leading-tight tracking-tight sm:text-xl font-mono">{value}</span>
              <span className="block text-[0.62rem] text-app-secondary/60">{unit}</span>
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
