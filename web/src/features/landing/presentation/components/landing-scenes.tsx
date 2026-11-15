"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { cn } from "@/lib/utils";

import { EarthScene } from "./earth-scene";

const MarsPlanet = dynamic(
  () => import("@/features/mars/presentation/components/mars-planet").then((module) => module.MarsPlanet),
  { ssr: false },
);

type LandingScenesProps = {
  earthBackdropClass: string;
  earthFallback: ReactNode;
  children: ReactNode;
  marsContent: ReactNode;
  marsBackdrop: ReactNode;
};

type PlanetScene = "earth" | "mars";

const fadeDuration = 650;
const sceneFade = "data-[shown=false]:opacity-0 motion-safe:transition-opacity motion-safe:ease-in-out motion-safe:duration-(--scene-fade)";

// Conserva el canvas saliente mientras termina el fundido, luego libera su contexto.
export function LandingScenes({
  earthBackdropClass,
  earthFallback,
  children,
  marsContent,
  marsBackdrop,
}: LandingScenesProps) {
  const earthSection = useRef<HTMLDivElement>(null);
  const marsSection = useRef<HTMLElement>(null);
  const [activeScene, setActiveScene] = useState<PlanetScene | null | undefined>(undefined);
  const [mountedScenes, setMountedScenes] = useState({ earth: false, mars: false });

  useEffect(() => {
    const earth = earthSection.current;
    const mars = marsSection.current;
    if (!earth || !mars) return;

    const visibleThreshold = 0.12;
    const visible = { earth: false, mars: false };
    const releaseTimers: Partial<Record<PlanetScene, number>> = {};
    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let currentScene: PlanetScene | null | undefined;

    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        const scene = entry.target === earth ? "earth" : "mars";
        visible[scene] = entry.intersectionRatio >= visibleThreshold;
      }

      const nextScene = visible.mars ? "mars" : visible.earth ? "earth" : null;
      if (nextScene === currentScene) return;

      const leavingScene = currentScene;
      currentScene = nextScene;
      setActiveScene(nextScene);

      if (nextScene) {
        window.clearTimeout(releaseTimers[nextScene]);
        setMountedScenes((previous) => ({ ...previous, [nextScene]: true }));
      }

      if (leavingScene) {
        releaseTimers[leavingScene] = window.setTimeout(() => {
          setMountedScenes((previous) => ({ ...previous, [leavingScene]: false }));
        }, motion.matches ? 0 : fadeDuration + 70);
      }
    }, { threshold: visibleThreshold });

    observer.observe(earth);
    observer.observe(mars);
    return () => {
      observer.disconnect();
      Object.values(releaseTimers).forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

  const fadeStyle = { "--scene-fade": `${fadeDuration}ms` } as CSSProperties;

  return (
    <>
      <div className="relative isolate overflow-hidden">
        <div
          ref={earthSection}
          aria-hidden="true"
          className={cn(earthBackdropClass, sceneFade)}
          data-landing-scene="earth"
          data-shown={activeScene === undefined || activeScene === "earth"}
          style={fadeStyle}
        >
          {earthFallback}
          {mountedScenes.earth && <EarthScene />}
        </div>
        {children}
      </div>

      <section
        ref={marsSection}
        id="marte"
        aria-labelledby="mars-landing-title"
        className="relative isolate mx-auto grid min-h-[90svh] max-w-[1600px] items-center gap-5 px-5 pt-14 pb-20 sm:px-8 md:grid-cols-[1.2fr_1fr] md:gap-7 md:py-16 lg:gap-16 lg:px-12"
      >
        <div
          aria-hidden="true"
          className={cn("pointer-events-none absolute inset-y-0 left-1/2 -z-10 w-dvw -translate-x-1/2 overflow-hidden", sceneFade)}
          data-shown={activeScene === "mars"}
          style={fadeStyle}
        >
          {mountedScenes.mars && marsBackdrop}
        </div>
        <div
          aria-hidden="true"
          data-landing-scene="mars"
          data-shown={activeScene === "mars"}
          style={fadeStyle}
          className={cn(
            "relative mx-auto aspect-square w-full max-w-[31rem] md:-ml-[11%] md:w-[111%] md:max-w-[min(62vw,80svh)]",
            "motion-safe:[&_canvas]:opacity-0 motion-safe:[&_canvas]:transition-opacity motion-safe:[&_canvas]:duration-500 motion-safe:[&_canvas[data-rendered]]:opacity-100",
            sceneFade,
          )}
        >
          {mountedScenes.mars && <MarsPlanet showSurfaceOverlay={false} rotationSpeed={0.055} />}
        </div>
        {marsContent}
      </section>
    </>
  );
}
