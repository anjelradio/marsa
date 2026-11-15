"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import {
  CalendarDays,
  Clock3,
  Orbit,
  Sparkles,
  Thermometer,
  ArrowLeft,
  Wind,
  Mountain,
  Compass,
  RotateCcw,
  Atom,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { MarsPlanet } from "@/features/mars/presentation/components/mars-planet";
import type { MarsCoordinates } from "@/features/mars/infrastructure/mars-climate";
import { cn } from "@/lib/utils";
import { PlanetMissionPanels } from "./planet-mission-panels";
import { MarsClimatePanel } from "./mars-climate-panel";
import { MarsImageGallery } from "./mars-image-gallery";
import { AnalogsPanel } from "./analogs-panel";
import { earthLandmarks, GlobeMarkers, targetLandmarks } from "./analogs-globe";
import { PlanetExplorationPanels } from "./planet-exploration-panels";
import { PointGeologyPanel } from "./point-geology-panel";
import { EarthPlanet } from "@/features/earth/presentation/components/earth-planet";
import { MoonPlanet } from "@/features/moon/presentation/components/moon-planet";
import type { ProjectedLandmark } from "@/features/shared/domain/geographic-coordinates";
import { PlanetFilter, type HomePlanet } from "./planet-filter";
import type { AnalogDestination } from "@/features/analogs/infrastructure/analogs-ranking";
import { useAnalogRanking } from "@/features/analogs/presentation/use-analog-ranking";
import styles from "./mars-dashboard.module.css";
import stars from "./starfield.module.css";
import { useTranslation } from "@/i18n/context";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const { dict } = useTranslation();
  const [isExploring, setIsExploring] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState<MarsCoordinates | null>(null);
  const [explorationView, setExplorationView] = useState<"geology" | "climate">("geology");

  const selectPoint = useCallback((point: MarsCoordinates) => {
    setIsExploring(true);
    setSelectedPoint(point);
  }, []);

  const exitExploration = useCallback(() => {
    setIsExploring(false);
    setSelectedPoint(null);
  }, []);

  const [planet, setPlanet] = useState<HomePlanet>("mars");
  const [destination, setDestination] = useState<AnalogDestination>("marte");
  const [openSiteId, setOpenSiteId] = useState<number | null>(null);
  const { result: ranking, retry: retryRanking } = useAnalogRanking(destination, dict.analogs.error);
  const profile = dict[planet];
  const [markers, setMarkers] = useState<ProjectedLandmark[]>([]);
  const rankingList = ranking && ranking !== "error" ? ranking : null;
  const landmarks = useMemo(() => {
    if (!rankingList) return [];
    if (planet === "earth") return earthLandmarks(rankingList);
    if (planet === "moon") return targetLandmarks(rankingList);
    return [];
  }, [rankingList, planet]);

  const selectPlanet = useCallback((next: HomePlanet) => {
    setPlanet(next);
    setOpenSiteId(null);
    setIsExploring(false);
    setSelectedPoint(null);
    if (next === "mars") setDestination("marte");
    if (next === "moon") setDestination("luna");
  }, []);

  const changeDestination = useCallback((next: AnalogDestination) => {
    setDestination(next);
    setOpenSiteId(null);
    setPlanet((current) => (current === "earth" ? current : next === "marte" ? "mars" : "moon"));
  }, []);

  // Allow ESC key to seamlessly exit exploration mode
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !e.defaultPrevented && isExploring) {
        exitExploration();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isExploring, exitExploration]);

  const facts = useMemo(
    () => [
      {
        label: profile.facts.distanceToSun,
        value: profile.facts.distanceToSunVal,
        unit: profile.facts.distanceToSunUnit,
        icon: Orbit,
        color: "bg-app-primary/60",
      },
      {
        label: profile.facts.martianYear,
        value: profile.facts.martianYearVal,
        unit: profile.facts.martianYearUnit,
        icon: CalendarDays,
        color: "bg-[#290d24]/65",
      },
      {
        label: profile.facts.dayLength,
        value: profile.facts.dayLengthVal,
        unit: profile.facts.dayLengthUnit,
        icon: Clock3,
        color: "bg-[#131a30]/65",
      },
      {
        label: profile.facts.avgTemp,
        value: profile.facts.avgTempVal,
        unit: profile.facts.avgTempUnit,
        icon: Thermometer,
        color: "bg-[#2d1e14]/65",
      },
    ],
    [profile],
  );

  const surfaceCards = useMemo(
    () => [
      {
        ...profile.leftCards.atmosphere,
        icon: Wind,
        color: "bg-[#131a30]/65",
      },
      {
        ...profile.leftCards.topography,
        icon: Mountain,
        color: "bg-[#2d1e14]/65",
      },
      {
        ...profile.leftCards.composition,
        icon: Atom,
        color: "bg-[#291323]/65",
      },
    ],
    [profile],
  );

  return (
    <main className="relative isolate min-h-svh overflow-hidden bg-black text-app-secondary select-none">
      {/* Background Starfield */}
      <div aria-hidden="true" className="pointer-events-none absolute -inset-8 -z-10">
        <div className={cn(stars.nebula, "absolute inset-0")} />
        <div className={cn(stars.distantStars, "absolute inset-0")} />
        <div className={cn(stars.nearStars, "absolute inset-0")} />
        <div className={stars.comets} />
      </div>

      {/* Top right utility navigation */}
      <div className="absolute top-4 right-4 z-40 flex items-center gap-2">
        <LanguageSwitcher
          variant="outline"
          size="sm"
          className="border-white/15 bg-white/5 text-white hover:bg-white/15 hover:text-white backdrop-blur-md rounded-full"
        />
      </div>

      {!isExploring && (
        <div className="absolute top-16 left-1/2 z-50 -translate-x-1/2 sm:top-4">
          <PlanetFilter value={planet} onChange={selectPlanet} />
        </div>
      )}

      <section
        aria-labelledby="planet-title"
        className={cn(
          styles.dashboard,
          "relative mx-auto grid max-w-[1600px] gap-7 px-4 py-5 sm:px-7 lg:min-h-[max(680px,100svh)] lg:gap-0 lg:px-4",
          isExploring && "max-lg:pt-16",
        )}
      >
        {/* Header Branding */}
        <header className={cn(
          "text-app-primary-foreground lg:absolute lg:top-5 lg:left-4 z-30 motion-safe:transition-opacity motion-safe:duration-200",
          isExploring && "opacity-0 max-lg:hidden",
        )}>
          <div className="flex items-start gap-1 font-headline text-3xl font-semibold leading-none tracking-tight">
            {dict.common.appName} <Sparkles aria-hidden="true" className="size-3.5 fill-current text-[#ffab57]" />
          </div>
        </header>

        {/* Surface data cards stacked on the left side */}
        <aside
          aria-label={`${profile.title} · ${profile.leftCards.topography.label}`}
          inert={isExploring}
          className={cn(
            "order-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3 lg:absolute lg:top-20 lg:left-4 lg:z-20 lg:flex lg:w-52 lg:flex-col lg:gap-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
            isExploring ? "max-lg:hidden lg:-translate-x-72 lg:opacity-0 pointer-events-none" : "lg:translate-x-0 lg:opacity-100"
          )}
        >
          {surfaceCards.map(({ label, value, unit, detail, icon: Icon, color }, index) => (
            <Card
              key={label}
              className={cn(
                stars.dashboardCard,
                "group min-w-0 justify-between gap-1.5 rounded-3xl p-3.5 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,background-color,box-shadow] duration-300 hover:-translate-y-1 hover:ring-white/20 hover:shadow-[0_16px_36px_#00000045] motion-reduce:transition-none lg:min-h-32",
                color,
              )}
              style={{ animationDelay: `${120 + index * 90}ms` }}
            >
              <p className="flex items-center gap-2 text-xs leading-tight text-app-secondary/75">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7 transition-transform duration-300 group-hover:rotate-6 group-hover:scale-110 motion-reduce:transition-none">
                  <Icon aria-hidden="true" className="size-4 text-app-primary-foreground" />
                </span>
                {label}
              </p>
              <p className="pl-1 text-xl leading-none font-medium tracking-tight tabular-nums xl:text-2xl">
                {value}
                <span className="mt-1 block text-xs font-normal tracking-normal text-app-secondary/65">
                  {unit}
                </span>
              </p>
            </Card>
          ))}
        </aside>

        {/* 3D Planet Container: Implicit Interaction (pointer cursor, soft ambient glow, click to explore) */}
        <div
          className={cn(styles.planetStage, "relative z-10 order-1")}
          data-exploring={isExploring}
          data-selected={selectedPoint !== null}
        >
          <div
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className={cn(
              styles.planet,
              "pointer-events-auto relative mx-auto aspect-square w-full max-w-[580px]",
              isExploring ? "cursor-grab active:cursor-grabbing" : "cursor-pointer"
            )}
          >
            {planet === "mars" && (
              <MarsPlanet
                isHovered={isHovered && !isExploring}
                isExploring={isExploring}
                selectionLabel={profile.explore.selectCenter}
                onSelect={selectPoint}
              />
            )}
            {planet === "earth" && (
              <EarthPlanet
                isExploring={isExploring}
                onSelect={selectPoint}
                landmarks={landmarks}
                onProjectedLandmarksChange={setMarkers}
              />
            )}
            {planet === "moon" && (
              <MoonPlanet
                isExploring={isExploring}
                onSelect={selectPoint}
                landmarks={landmarks}
                onProjectedLandmarksChange={setMarkers}
              />
            )}
            {planet !== "mars" && (
              <GlobeMarkers
                points={markers}
                activeId={planet === "earth" && openSiteId !== null ? String(openSiteId) : null}
                onSelect={
                  planet === "earth"
                    ? (id) => setOpenSiteId(Number(id) === openSiteId ? null : Number(id))
                    : undefined
                }
              />
            )}
          </div>
        </div>

        {/* Mars Title & Subtitle */}
        <div
          inert={isExploring}
          className={cn(
            "relative z-20 order-2 -mt-[18%] pl-[5%] lg:absolute lg:top-[74.5%] lg:left-[14%] lg:mt-0 lg:pl-0 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
            isExploring ? "max-lg:hidden lg:translate-y-36 lg:opacity-0 pointer-events-none" : "lg:translate-y-0 lg:opacity-100"
          )}
        >
          <h1
            id="planet-title"
            className="text-[clamp(5.6rem,16vw,9rem)] font-black leading-[0.85] tracking-[-0.075em] text-white lg:origin-left lg:scale-x-[1.33] lg:text-[clamp(6.75rem,10.7vw,11rem)]"
          >
            {profile.title}
          </h1>
          <p className="mt-3 text-sm text-app-secondary/75 sm:text-base">
            {profile.subtitle}
          </p>
        </div>

        {/* 4 Top Fact Cards */}
        <dl
          inert={isExploring}
          className={cn(
            "order-3 grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:absolute lg:top-14 lg:right-[20.7%] lg:left-[22.7%] lg:z-0 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
            isExploring ? "max-lg:hidden lg:-translate-y-48 lg:opacity-0 pointer-events-none" : "lg:translate-y-0 lg:opacity-100"
          )}
        >
          {facts.map(({ label, value, unit, icon: Icon, color }, index) => (
            <Card
              key={label}
              className={cn(
                stars.dashboardCard,
                "min-w-0 gap-2 rounded-3xl px-3 py-3 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-[0_14px_32px_#00000040] motion-reduce:transition-none sm:px-4 lg:min-h-28 lg:gap-1 lg:py-2.5",
                color
              )}
              style={{ animationDelay: `${index * 70}ms` }}
            >
              <dt className="flex items-center gap-2 text-xs leading-tight text-app-secondary/75">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7">
                  <Icon aria-hidden="true" className="size-4 text-app-primary-foreground" />
                </span>
                {label}
              </dt>
              <dd className="pl-1 text-xl leading-none font-medium tracking-tight tabular-nums xl:text-2xl">
                {value}
                <span className="mt-1 block text-xs font-normal tracking-normal text-app-secondary/65">
                  {unit}
                </span>
              </dd>
            </Card>
          ))}
        </dl>

        {/* Right Side Panels: Distance to Sun graph, Curiosity, Measurements */}
        <PlanetMissionPanels planet={planet} isExploring={isExploring} />

        {isExploring && selectedPoint && (
          <div
            key={`${selectedPoint.latitude}:${selectedPoint.longitude}`}
            className={cn(styles.explorationPanels, "relative z-30 order-3 grid items-start gap-3 sm:grid-cols-2")}
          >
            {planet === "mars" ? (
              <>
                {explorationView === "geology" ? (
                  <PointGeologyPanel
                    cuerpo="Marte"
                    point={selectedPoint}
                    onClose={() => setSelectedPoint(null)}
                    viewMode="geology"
                    onToggleViewMode={setExplorationView}
                  />
                ) : (
                  <MarsClimatePanel
                    point={selectedPoint}
                    onClose={() => setSelectedPoint(null)}
                    onToggleViewMode={setExplorationView}
                  />
                )}
                <MarsImageGallery point={selectedPoint} />
              </>
            ) : (
              <PlanetExplorationPanels
                planet={planet}
                point={selectedPoint}
                onClose={() => setSelectedPoint(null)}
                explorationView={explorationView}
                onToggleViewMode={setExplorationView}
              />
            )}
          </div>
        )}

        {/* Exploration Mode Overlays: Return button & subtle drag hint */}
        {isExploring && (
          <div className={cn(styles.explorationControls, "absolute inset-x-4 top-5 z-40 flex items-center justify-between")}>
            <div className="flex items-center gap-3">
              <Button
                onClick={exitExploration}
                variant="outline"
                size="sm"
                className="rounded-full border-white/20 bg-black/60 px-4 text-white hover:bg-white/20 hover:text-white backdrop-blur-md shadow-xl gap-2 font-medium cursor-pointer"
              >
                <ArrowLeft className="size-4" />
                {profile.explore.exit}
              </Button>
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80 backdrop-blur-md">
                <Compass className="size-3.5 text-[#ffab57]" />
                {profile.explore.modeBadge}
              </span>
            </div>
          </div>
        )}
        {isExploring && (
          <div className="pointer-events-none z-20 order-2 mx-auto -mt-4 flex w-fit items-center gap-2 rounded-full border border-white/15 bg-black/60 px-4 py-1.5 text-center text-xs text-white/85 shadow-2xl backdrop-blur-md lg:absolute lg:bottom-6 lg:left-1/2 lg:mt-0 lg:-translate-x-1/2">
            <RotateCcw className="size-3.5 shrink-0 text-[#ffab57] animate-spin [animation-duration:8s] motion-reduce:animate-none" />
            {profile.explore.dragHint}
          </div>
        )}
      </section>

      <div inert={isExploring} className={cn(isExploring && "hidden")}>
        <AnalogsPanel
          destination={destination}
          onDestinationChange={changeDestination}
          result={ranking}
          onRetry={retryRanking}
          openId={openSiteId}
          onOpenChange={setOpenSiteId}
        />
      </div>
    </main>
  );
}
