import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Globe2, Info, Moon, Orbit, Rocket, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LandingScenes } from "@/features/landing/presentation/components/landing-scenes";
import { cn } from "@/lib/utils";
import stars from "./home/starfield.module.css";
import styles from "./landing.module.css";

export const metadata: Metadata = {
  title: "AstroPlus | Explore the Solar System",
  description: "View Earth and the Moon in 3D and explore Mars with AstroPlus.",
};

const topics = [
  { id: "tierra", title: "Earth", description: "Explore the oceans and continents of our home planet in the interactive 3D scene.", icon: Globe2 },
  { id: "luna", title: "The Moon", description: "Observe Earth's natural satellite accompanying our planet in its orbit.", icon: Moon },
  { id: "orbita", title: "Orbits", description: "Check Mars' distance to the Sun and examine how its orbital velocity varies.", icon: Orbit },
  { id: "planeta-marte", title: "Mars", description: "Explore Martian topography and locate the landing site of the Curiosity rover.", icon: Sun },
];

const iconLink =
  cn(styles.glassButton, "size-10 rounded-2xl p-0 sm:size-11 [&_svg]:size-[1.125rem]");

export default function LandingPage() {
  return (
    <main lang="en" className={cn(styles.landing, "relative isolate overflow-hidden bg-[#050505] text-zinc-300")}>
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
          <h1 id="landing-title" className="relative flex justify-center">
            <span className="sr-only">MARSA - Earth Analog Explorer</span>
            <Image
              src="/landing/marsa-terra.png"
              alt="MARSA - Earth Analog Explorer"
              width={2103}
              height={748}
              priority
              className="h-auto w-full max-w-[340px] sm:max-w-[460px] md:max-w-[560px] drop-shadow-[0_0_35px_rgba(59,149,255,0.35)] object-contain"
            />
          </h1>
          <p className="mt-4 max-w-[26rem] text-sm leading-snug text-slate-200/90">
            View Earth and the Moon in 3D and explore the surface and orbit of Mars in the interactive atlas.
          </p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-3 sm:gap-5">
            <Button asChild variant="ghost" className={cn(styles.glassButton, styles.exploreButton, "h-10 rounded-full px-5 sm:px-6")}>
              <a href="#marte"><Rocket aria-hidden="true" /> Explore Mars <ArrowRight aria-hidden="true" /></a>
            </Button>
            <div className="flex gap-2 sm:gap-3">
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#tierra" aria-label="About Earth"><Globe2 aria-hidden="true" /></a>
              </Button>
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#luna" aria-label="About the Moon"><Moon aria-hidden="true" /></a>
              </Button>
              <Button asChild variant="ghost" className={iconLink}>
                <a href="#explorar" aria-label="View exploration guide"><Info aria-hidden="true" /></a>
              </Button>
            </div>
          </div>
        </section>

        <section id="explorar" aria-label="Exploration guide" className="relative z-10 scroll-mt-6 px-5 pt-12 pb-20 sm:px-8">
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
        Mars
      </h2>
      <p className="mt-5 max-w-md text-sm leading-relaxed text-zinc-300 sm:text-base">
        Get closer to the Red Planet. Explore its terrain, discover how its distance to the Sun changes, and locate Gale Crater, where Curiosity landed.
      </p>
      <Button asChild variant="ghost" className={cn(styles.glassButton, "mt-8 h-12 rounded-full px-6")}>
        <Link href="/home">Launch Mars Atlas <ArrowRight aria-hidden="true" /></Link>
      </Button>
    </div>
  );
}
