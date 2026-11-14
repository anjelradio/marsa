import { Card } from "@/components/ui/card";

// Datos físicos de Marte publicados en la ficha planetaria de NASA NSSDC.
const measurements = [
  { label: "Gravedad", value: "3,73", unit: "m/s²", color: "#ae4685" },
  { label: "Inclinación", value: "25,2°", unit: "axial", color: "#5f8bdb" },
  { label: "Lunas", value: "2", unit: "naturales", color: "#b7b6ba" },
];

const semimajorAxis = 227.956;
const orbitDistances = Array.from({ length: 49 }, (_, index) => {
  const angle = (index / 48) * 2 * Math.PI;
  const eccentricity = 0.0935;
  return (semimajorAxis * (1 - eccentricity ** 2)) / (1 + eccentricity * Math.cos(angle));
});
const orbitProfile = [
  "0 100%",
  ...orbitDistances.map((distance, index) =>
    `${(index / 48) * 100}% ${100 - ((distance - 200) / 60) * 100}%`,
  ),
  "100% 100%",
].join(", ");

// La velocidad se calcula a partir de la distancia mediante la ecuación vis-viva.
const orbitSpeeds = orbitDistances
  .filter((_, index) => index % 8 === 0)
  .map((distance) =>
    Math.sqrt(132_712 * (2 / distance - 1 / semimajorAxis)),
  );

// Coloca el perfil orbital detrás del globo y el lugar de aterrizaje delante.
export function MarsMissionPanels() {
  return (
    <div className="order-4 grid gap-3 lg:contents">
      <figure className="relative min-w-0 rounded-3xl bg-app-primary/40 p-4 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[26%] lg:right-[20.7%] lg:z-0 lg:w-[30%] lg:p-2.5">
        <figcaption className="mb-2 text-sm font-medium text-app-primary-foreground lg:ml-[45%]">
          Distancia al Sol
        </figcaption>
        <div className="relative h-28 overflow-hidden border-b border-white/20 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(25%_-_1px),#ffffff16_calc(25%_-_1px),#ffffff16_25%)] lg:h-[clamp(5.75rem,16svh,9rem)]">
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-linear-to-b from-[#b75d99] via-[#733460] to-[#31152e]"
            style={{ clipPath: `polygon(${orbitProfile})` }}
          />
          <p className="absolute right-2 bottom-2 rounded-md bg-black/55 px-2 py-1 text-xs text-app-secondary">
            206,7–249,3 millones de km
          </p>
        </div>
        <div className="mt-3 flex items-end gap-2.5 lg:ml-[39%]">
          <div aria-hidden="true" className="flex h-13 flex-1 items-end justify-evenly gap-2 border-b border-white/15 bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_calc(33.33%_-_1px),#ffffff12_calc(33.33%_-_1px),#ffffff12_33.33%)] px-2 lg:h-[clamp(2.5rem,8svh,4.5rem)]">
            {orbitSpeeds.map((speed, index) => (
              <span
                key={index}
                className="w-1 rounded-full bg-app-secondary/90"
                style={{ height: `${((speed - 21) / 6) * 100}%` }}
              />
            ))}
          </div>
          <p className="text-right text-[0.625rem] leading-tight text-app-secondary/80">
            Velocidad orbital
            <span className="block">22–26,5 km/s</span>
          </p>
        </div>
      </figure>

      <Card className="relative z-10 flex-row items-center gap-3 rounded-3xl bg-app-primary/65 p-1.5 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[65%] lg:right-[20.7%] lg:w-[31%] lg:gap-4">
        <span className="grid min-h-16 shrink-0 place-items-center rounded-[1.15rem] bg-linear-to-br from-[#ffdb8a] to-[#f3824a] px-4 text-sm font-semibold text-[#39190d] shadow-[0_0_26px_#ffab5760] lg:min-h-[clamp(4rem,10svh,6rem)] lg:basis-[34%]">
          Curiosity
        </span>
        <div className="min-w-0 py-2 pr-2">
          <p className="text-[clamp(1.4rem,3vw,2.6rem)] font-semibold leading-none tracking-tight">137,4° E</p>
          <p className="mt-1 text-xs text-app-secondary/70">Aterrizaje en el cráter Gale</p>
        </div>
      </Card>

      <dl className="relative z-10 grid grid-cols-3 gap-1 rounded-3xl bg-app-primary/65 p-2 ring-1 ring-inset ring-white/10 backdrop-blur-md lg:absolute lg:top-[79.5%] lg:right-[20.7%] lg:w-[37%] lg:p-3">
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
              <span className="block text-lg font-semibold leading-tight tracking-tight sm:text-xl">{value}</span>
              <span className="block text-[0.62rem] text-app-secondary/60">{unit}</span>
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
