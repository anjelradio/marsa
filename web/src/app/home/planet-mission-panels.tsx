"use client";

import { Card } from "@/components/ui/card";
import { useTranslation } from "@/i18n/context";
import { cn } from "@/lib/utils";

export type MissionPlanet = "mars" | "earth" | "moon";

interface OrbitProfile {
  /** Semieje mayor en millones de km (Sol) o miles de km (Luna alrededor de la Tierra). */
  semimajorAxis: number;
  eccentricity: number;
  /** GM del astro central en km³/s² por unidad de distancia (vis-viva). */
  gm: number;
  distanceMin: number;
  distanceSpan: number;
  speedMin: number;
  speedSpan: number;
}

// Datos físicos de las fichas planetarias de NASA NSSDC.
const ORBITS: Record<MissionPlanet, OrbitProfile> = {
  mars: { semimajorAxis: 227.956, eccentricity: 0.0935, gm: 132_712, distanceMin: 200, distanceSpan: 60, speedMin: 21, speedSpan: 6 },
  earth: { semimajorAxis: 149.598, eccentricity: 0.0167, gm: 132_712, distanceMin: 146, distanceSpan: 8, speedMin: 29, speedSpan: 1.5 },
  moon: { semimajorAxis: 384.4, eccentricity: 0.0549, gm: 398.6, distanceMin: 355, distanceSpan: 60, speedMin: 0.9, speedSpan: 0.25 },
};

function buildOrbit({ semimajorAxis, eccentricity, gm, distanceMin, distanceSpan, speedMin, speedSpan }: OrbitProfile) {
  // Perfil kepleriano: distancia r(θ) a lo largo de una revolución completa.
  const distances = Array.from({ length: 49 }, (_, index) => {
    const angle = (index / 48) * 2 * Math.PI;
    return (semimajorAxis * (1 - eccentricity ** 2)) / (1 + eccentricity * Math.cos(angle));
  });
  const profile = [
    "0 100%",
    ...distances.map(
      (distance, index) => `${(index / 48) * 100}% ${100 - ((distance - distanceMin) / distanceSpan) * 100}%`,
    ),
    "100% 100%",
  ].join(", ");
  // Velocidad orbital con la ecuación vis-viva: v = sqrt(GM · (2/r − 1/a)).
  const speeds = distances
    .filter((_, index) => index % 8 === 0)
    .map((distance) => Math.sqrt(gm * (2 / distance - 1 / semimajorAxis)));
  return {
    profile,
    speedHeights: speeds.map((speed) => ((speed - speedMin) / speedSpan) * 100),
    meanTop: (1 - (semimajorAxis - distanceMin) / distanceSpan) * 100,
  };
}

const ORBIT_SHAPES = {
  mars: buildOrbit(ORBITS.mars),
  earth: buildOrbit(ORBITS.earth),
  moon: buildOrbit(ORBITS.moon),
};

interface PlanetMissionPanelsProps {
  planet?: MissionPlanet;
  isExploring?: boolean;
}

export function PlanetMissionPanels({ planet = "mars", isExploring = false }: PlanetMissionPanelsProps) {
  const { dict } = useTranslation();
  const p = dict[planet].panels;
  const { profile, speedHeights, meanTop } = ORBIT_SHAPES[planet];

  const measurements = [
    { label: p.measurements.gravity, value: p.measurements.gravityVal, unit: p.measurements.gravityUnit, color: "#ae4685" },
    { label: p.measurements.tilt, value: p.measurements.tiltVal, unit: p.measurements.tiltUnit, color: "#5f8bdb" },
    { label: p.measurements.moons, value: p.measurements.moonsVal, unit: p.measurements.moonsUnit, color: "#b7b6ba" },
  ];

  return (
    <div
      inert={isExploring}
      className={cn(
        "order-4 grid gap-3 lg:contents",
        isExploring && "max-lg:hidden lg:pointer-events-none"
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
          {p.distanceToSunTitle}
        </figcaption>
        <div className="relative h-28 overflow-hidden border-b border-white/20 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(25%_-_1px),#ffffff16_calc(25%_-_1px),#ffffff16_25%)] lg:h-[clamp(5.75rem,16svh,9rem)]">
          {/* Orbital distance profile polygon */}
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-linear-to-b from-[#b75d99] via-[#733460] to-[#31152e]"
            style={{ clipPath: `polygon(${profile})` }}
          />

          {/* Mean distance reference line */}
          <div
            aria-hidden="true"
            className="absolute inset-x-0 border-b border-white/30 border-dashed"
            style={{ top: `${meanTop}%` }}
          />

          {/* Key astronomical markers: far point (peak) & near point (base) */}
          <span className="absolute top-1.5 left-1/2 -translate-x-1/2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-white/90">
            {p.aphelion}
          </span>
          <span className="absolute bottom-1.5 left-2 rounded bg-black/60 px-1.5 py-0.5 text-[0.62rem] font-mono text-[#ffdb8a]">
            {p.perihelion}
          </span>

          <p className="absolute right-2 bottom-1.5 rounded-md bg-black/60 px-2 py-0.5 text-[0.65rem] font-mono text-app-secondary">
            {p.distanceRange}
          </p>
        </div>

        {/* Vis-viva orbital velocity section */}
        <div className="mt-3 flex items-end gap-2.5 lg:ml-[39%]">
          <div
            aria-hidden="true"
            className="flex h-13 flex-1 items-end justify-evenly gap-2 border-b border-white/15 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(33.33%_-_1px),#ffffff12_calc(33.33%_-_1px),#ffffff12_33.33%)] px-2 lg:h-[clamp(2.5rem,8svh,4.5rem)]"
          >
            {speedHeights.map((height, index) => (
              <span
                key={index}
                className="w-1 rounded-full bg-app-secondary/90"
                style={{ height: `${height}%` }}
              />
            ))}
          </div>
          <p className="text-right text-[0.625rem] leading-tight text-app-secondary/80">
            {p.orbitalSpeed}
            <span className="block font-mono font-medium">{p.orbitalSpeedRange}</span>
          </p>
        </div>
      </figure>

      {/* 2. Reference mission card */}
      <Card
        className={cn(
          "relative z-10 flex-row items-center gap-3 rounded-3xl bg-app-primary/65 p-1.5 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[65%] lg:right-[20.7%] lg:w-[31%] lg:gap-4 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
          isExploring
            ? "lg:translate-x-[160%] lg:opacity-0 pointer-events-none"
            : "lg:translate-x-0 lg:opacity-100"
        )}
      >
        <span className="grid min-h-16 shrink-0 place-items-center rounded-[1.15rem] bg-linear-to-br from-[#ffdb8a] to-[#f3824a] px-4 text-sm font-semibold text-[#39190d] shadow-[0_0_26px_#ffab5760] lg:min-h-[clamp(4rem,10svh,6rem)] lg:basis-[34%]">
          {p.missionCuriosity}
        </span>
        <div className="min-w-0 py-2 pr-2">
          <p className="text-[clamp(1.4rem,3vw,2.6rem)] font-semibold leading-none tracking-tight font-mono">
            {p.missionCuriosityCoord}
          </p>
          <p className="mt-1 text-xs text-app-secondary/70">{p.missionCuriosityDesc}</p>
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
