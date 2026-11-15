import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Globe2, Info, Moon, Orbit, Rocket, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LandingScenes } from "@/features/landing/presentation/components/landing-scenes";
import { cn } from "@/lib/utils";
import stars from "./home/starfield.module.css";
import styles from "./landing.module.css";

export const metadata: Metadata = {
  title: "AstroPlus | Explora el sistema solar",
  description: "Observa la Tierra y la Luna en 3D y explora Marte con AstroPlus.",
};

const topics = [
  { id: "tierra", title: "La Tierra", description: "Reconoce los océanos y continentes de nuestro planeta en la escena 3D.", icon: Globe2 },
  { id: "luna", title: "La Luna", description: "Observa cómo nuestro satélite acompaña a la Tierra en su órbita.", icon: Moon },
  { id: "orbita", title: "Órbitas", description: "Consulta en el atlas la distancia de Marte al Sol y cómo varía su velocidad orbital.", icon: Orbit },
  { id: "planeta-marte", title: "Marte", description: "Explora su relieve y ubica el lugar donde aterrizó el rover Curiosity.", icon: Sun },
];

const iconLink =
  cn(styles.glassButton, "size-10 rounded-2xl p-0 sm:size-11 [&_svg]:size-[1.125rem]");

export default function LandingPage() {
  return (
    <main lang="es" className={cn(styles.landing, "relative isolate overflow-hidden bg-[#050505] text-zinc-300")}>
      <div aria-hidden="true" className={styles.sky}>
        <div className={cn(stars.distantStars, "absolute -inset-8 opacity-30")} />
        <div className={cn(stars.nearStars, "absolute -inset-8 opacity-40")} />
        <div className={styles.skyOrbit} />
        <div className={cn(stars.comets, styles.earthComets, "absolute inset-0")} />
      </div>
      <LandingScenes
        earthBackdropClass={styles.scene}
        earthFallback={<div className={styles.fallback} />}
        marsContent={<MarsLandingContent />}
        marsBackdrop={
          <div className={cn(styles.marsSky, "absolute inset-0 overflow-hidden")}>
            <div className={cn(stars.distantStars, styles.marsFarStars, "absolute -inset-[16%]")} />
            <div className={cn(stars.nearStars, styles.marsNearStars, "absolute -inset-[16%]")} />
            <div className={cn(stars.comets, styles.marsComets, "absolute inset-0")} />
          </div>
        }
      >
        <section aria-labelledby="landing-title" className={cn(styles.hero, "relative z-10 flex flex-col items-center px-5 text-center sm:px-8")}>
          <h1 id="landing-title" className="relative font-headline text-[clamp(3rem,7.75vw,7rem)] font-bold leading-none tracking-[-0.055em] text-white">
            <span aria-hidden="true" className={styles.titleOrbit} />
            Astro<span className={styles.plus}>Plus</span>
          </h1>
          <p className="mt-2 max-w-[26rem] text-sm leading-snug text-slate-200/90">
            Observa la Tierra y la Luna en 3D y explora la superficie y la órbita de Marte en el atlas interactivo.
          </p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-3 sm:gap-5">
            <Button asChild variant="ghost" className={cn(styles.glassButton, styles.exploreButton, "h-10 rounded-full px-5 sm:px-6")}>
              <a href="#marte"><Rocket aria-hidden="true" /> Explorar Marte <ArrowRight aria-hidden="true" /></a>
            </Button>
            <div className="flex gap-2 sm:gap-3">
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#tierra" aria-label="Sobre la Tierra"><Globe2 aria-hidden="true" /></a>
              </Button>
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#luna" aria-label="Sobre la Luna"><Moon aria-hidden="true" /></a>
              </Button>
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#explorar" aria-label="Ver guía de exploración"><Info aria-hidden="true" /></a>
              </Button>
            </div>
          </div>
        </section>

        <section id="explorar" aria-label="Guía de exploración" className="relative z-10 scroll-mt-6 px-5 pt-12 pb-20 sm:px-8">
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-linear-to-b from-transparent via-[#050505] via-65% to-[#050505]" />
          <div className="relative mx-auto grid max-w-6xl grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
            {topics.map(({ id, title, description, icon: Icon }) => (
              <Card key={id} id={id} className={cn(styles.glassCard, "relative flex min-h-40 scroll-mt-8 flex-col justify-end gap-2 rounded-3xl px-3 py-4 ring-0 dark:ring-0 motion-safe:transition-transform motion-safe:hover:-translate-y-1 sm:min-h-52 sm:px-5 sm:py-5 lg:aspect-[3/4]")}>
                <Icon aria-hidden="true" className="pointer-events-none absolute top-4 right-3 size-10 text-white/20 sm:top-5 sm:right-5 sm:size-14 lg:size-16" />
                <h2 className="font-headline text-lg font-semibold text-white sm:text-2xl">{title}</h2>
                <p className="text-xs leading-relaxed text-zinc-400 sm:text-sm">{description}</p>
              </Card>
            ))}
          </div>
        </section>
      </LandingScenes>
    </main>
  );
}

// Presenta el planeta y enlaza con los datos de la vista de Marte.
function MarsLandingContent() {
  return (
    <div className="relative z-10 mx-auto w-full max-w-xl md:mx-0">
      <h2 id="mars-landing-title" className="font-headline text-[clamp(4.5rem,10vw,8rem)] font-semibold leading-[0.9] tracking-[-0.075em] text-white">
        Marte
      </h2>
      <p className="mt-5 max-w-md text-sm leading-relaxed text-zinc-300 sm:text-base">
        Acércate al planeta rojo. Recorre su relieve, descubre cómo cambia su distancia al Sol y ubica el cráter Gale, donde aterrizó Curiosity.
      </p>
      <Button asChild variant="ghost" className={cn(styles.glassButton, "mt-8 h-12 rounded-full px-6")}>
        <Link href="/home">Abrir atlas de Marte <ArrowRight aria-hidden="true" /></Link>
      </Button>
    </div>
  );
}
