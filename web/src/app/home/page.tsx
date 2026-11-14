import { CalendarDays, Clock3, Globe2, Orbit, Sparkles, Thermometer } from "lucide-react";
import { Card } from "@/components/ui/card";
import { MarsPlanet } from "@/features/mars/presentation/components/mars-planet";
import { cn } from "@/lib/utils";
import { MarsMissionPanels } from "./mars-mission-panels";
import stars from "./starfield.module.css";

const facts = [
  { label: "Distancia al Sol", value: "227,9", unit: "millones de km", icon: Orbit, color: "bg-app-primary/60" },
  { label: "Año marciano", value: "687", unit: "días terrestres", icon: CalendarDays, color: "bg-[#290d24]/65" },
  { label: "Duración del día", value: "24 h 37 min", unit: "tiempo terrestre", icon: Clock3, color: "bg-[#131a30]/65" },
  { label: "Temperatura media", value: "−63 °C", unit: "en la superficie", icon: Thermometer, color: "bg-[#2d1e14]/65" },
];

export default function HomePage() {
  return (
    <main className="relative isolate min-h-svh overflow-hidden bg-black text-app-secondary">
      <div aria-hidden="true" className="pointer-events-none absolute -inset-8 -z-10">
        <div className={cn(stars.distantStars, "absolute inset-0")} />
        <div className={cn(stars.nearStars, "absolute inset-0")} />
        <div className={stars.comets} />
      </div>

      <section aria-labelledby="mars-title" className="relative mx-auto grid max-w-[1600px] gap-7 px-4 py-5 sm:px-7 lg:min-h-[max(680px,100svh)] lg:gap-0 lg:px-4">
        <header className="text-app-primary-foreground lg:absolute lg:top-5 lg:left-4">
          <div className="flex items-start gap-1 font-headline text-3xl font-semibold leading-none tracking-tight">
            AstroPlus <Sparkles aria-hidden="true" className="size-3.5 fill-current" />
          </div>
          <p className="mt-4 flex w-fit items-center gap-2 rounded-full bg-[#381331] px-4 py-2 text-sm lg:mt-22">
            <Globe2 aria-hidden="true" className="size-4" /> Planetas
          </p>
        </header>

        <div className="relative order-1 mx-auto aspect-square w-full max-w-[580px] lg:pointer-events-none lg:absolute lg:top-[50.3%] lg:left-[38.4%] lg:z-10 lg:w-[min(50%,71svh)] lg:max-w-none lg:-translate-1/2">
          <MarsPlanet />
        </div>

        <div className="relative z-20 order-2 -mt-[18%] pl-[5%] lg:absolute lg:top-[74.5%] lg:left-[14%] lg:mt-0 lg:pl-0">
          <h1 id="mars-title" className="text-[clamp(5.6rem,16vw,9rem)] font-black leading-[0.85] tracking-[-0.075em] text-white lg:origin-left lg:scale-x-[1.33] lg:text-[clamp(6.75rem,10.7vw,11rem)]">
            Mars
          </h1>
          <p className="mt-3 text-sm text-app-secondary/75 sm:text-base">
            El cuarto planeta del sistema solar
          </p>
        </div>

        <dl className="order-3 grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:absolute lg:inset-x-4 lg:top-11 lg:left-[22.7%] lg:z-0">
          {facts.map(({ label, value, unit, icon: Icon, color }) => (
            <Card key={label} className={cn("min-w-0 gap-2 rounded-3xl px-3 py-3 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md sm:px-4 lg:min-h-30 lg:gap-1 lg:py-2.5", color)}>
              <dt className="flex items-center gap-2 text-xs leading-tight text-app-secondary/75">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7">
                  <Icon aria-hidden="true" className="size-4 text-app-primary-foreground" />
                </span>
                {label}
              </dt>
              <dd className="pl-1 text-xl leading-none font-medium tracking-tight tabular-nums xl:text-2xl">
                {value}
                <span className="mt-1 block text-xs font-normal tracking-normal text-app-secondary/65">{unit}</span>
              </dd>
            </Card>
          ))}
        </dl>

        <MarsMissionPanels />
      </section>
    </main>
  );
}
