"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import {
  CalendarDays,
  Clock3,
  Orbit,
  Sparkles,
  Thermometer,
  ArrowLeft,
  Wind,
  Mountain,
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
  const hasSelection = selectedPoint !== null;

  const focusGlobe = useCallback(() => setIsExploring(true), []);

  const clearSelection = useCallback(() => setSelectedPoint(null), []);

  const selectPoint = useCallback((point: MarsCoordinates) => {
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
  const globeLabel = isExploring ? profile.explore.selectCenter : profile.explore.focusGlobe;
  const [markers, setMarkers] = useState<ProjectedLandmark[]>([]);
  const rankingList = ranking && ranking !== "error" ? ranking : null;
  const landmarks = useMemo(() => {
    if (!rankingList || isExploring) return [];
    if (planet === "earth") return earthLandmarks(rankingList);
    if (planet === "moon") return targetLandmarks(rankingList);
    return [];
  }, [rankingList, planet, isExploring]);

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
        if (hasSelection) clearSelection();
        else exitExploration();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isExploring, hasSelection, clearSelection, exitExploration]);

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
    <main data-planet={planet} className={cn("relative isolate min-h-svh overflow-hidden bg-black text-app-secondary select-none", styles.planetTheme)}>
      {/* Background Starfield */}
      <div aria-hidden="true" className="pointer-events-none absolute -inset-8 -z-10">
        <div className={cn(stars.nebula, "absolute inset-0")} />
        <div className={cn(stars.distantStars, "absolute inset-0")} />
        <div className={cn(stars.nearStars, "absolute inset-0")} />
        <div className={stars.comets} />
      </div>

      {/* Top right utility navigation */}
      <div hidden={isExploring} className={cn("absolute top-4 right-4 z-40", !isExploring && "flex items-center gap-2")}>
        <LanguageSwitcher
          variant="outline"
          size="sm"
          className="border-white/15 bg-white/5 text-white hover:bg-white/15 hover:text-white backdrop-blur-md rounded-full"
        />
      </div>

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
            stars.leftCards,
            "order-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3 lg:absolute lg:top-20 lg:left-[14%] lg:z-20 lg:flex lg:w-52 lg:flex-col lg:gap-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
            isExploring ? "max-lg:hidden lg:-translate-x-72 lg:opacity-0 pointer-events-none" : "lg:translate-x-0 lg:opacity-100"
          )}
        >
          {surfaceCards.map(({ label, value, unit, icon: Icon, color }, index) => (
            <Card
              key={label}
              className={cn(
                stars.dashboardCard,
                "min-h-32 min-w-0 justify-between gap-1.5 rounded-4xl px-3.5 py-4 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl lg:min-h-34",
                color,
              )}
              style={{ animationDelay: `${120 + index * 90}ms` }}
            >
              <p className="flex items-center gap-2 text-xs leading-tight text-app-secondary/75">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7">
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
          data-selected={hasSelection}
        >
          <div
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className={cn(
              styles.planet,
              "pointer-events-auto relative mx-auto aspect-square w-full max-w-[580px]",
              isExploring && !hasSelection ? "cursor-grab active:cursor-grabbing" : "cursor-pointer"
            )}
          >
            {planet === "mars" && (
              <MarsPlanet
                isHovered={isHovered && !isExploring}
                isExploring={isExploring}
                selectionLabel={globeLabel}
                hasSelection={hasSelection}
                onFocusGlobe={focusGlobe}
                onSelect={selectPoint}
              />
            )}
            {planet === "earth" && (
              <EarthPlanet
                isHovered={isHovered && !isExploring}
                isExploring={isExploring}
                selectionLabel={globeLabel}
                hasSelection={hasSelection}
                onFocusGlobe={focusGlobe}
                autoRotate
                onSelect={selectPoint}
                landmarks={landmarks}
                onProjectedLandmarksChange={setMarkers}
              />
            )}
            {planet === "moon" && (
              <MoonPlanet
                isHovered={isHovered && !isExploring}
                isExploring={isExploring}
                selectionLabel={globeLabel}
                hasSelection={hasSelection}
                onFocusGlobe={focusGlobe}
                autoRotate
                onSelect={selectPoint}
                landmarks={landmarks}
                onProjectedLandmarksChange={setMarkers}
              />
            )}
            {!isExploring && planet !== "mars" && (
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
        {!isExploring && (
          <div className="relative z-20 order-0 flex justify-center lg:absolute lg:inset-y-0 lg:right-0 lg:z-20 lg:order-none lg:block">
            <PlanetFilter value={planet} onChange={selectPlanet} />
          </div>
        )}

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
            stars.centerCards,
            "order-3 grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:absolute lg:top-20 lg:right-[14%] lg:left-[29.4%] lg:z-0 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
            isExploring ? "max-lg:hidden lg:-translate-y-48 lg:opacity-0 pointer-events-none" : "lg:translate-y-0 lg:opacity-100"
          )}
        >
          {facts.map(({ label, value, unit, icon: Icon, color }, index) => (
            <Card
              key={label}
              className={cn(
                stars.dashboardCard,
                "min-h-28 min-w-0 gap-2 rounded-4xl px-3 py-4 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl sm:px-4 lg:min-h-30 lg:gap-1 lg:py-3.5",
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
            className={cn(styles.explorationPanels, "relative z-30 order-3 grid content-start gap-4")}
          >
            {planet === "mars" ? (
              <>
                {explorationView === "geology" ? (
                  <PointGeologyPanel
                    cuerpo="Marte"
                    point={selectedPoint}
                    onClose={clearSelection}
                    viewMode="geology"
                    onToggleViewMode={setExplorationView}
                  />
                ) : (
                  <MarsClimatePanel
                    point={selectedPoint}
                    onClose={clearSelection}
                    onToggleViewMode={setExplorationView}
                  />
                )}
                <MarsImageGallery point={selectedPoint} />
              </>
            ) : (
              <PlanetExplorationPanels
                planet={planet}
                point={selectedPoint}
                onClose={clearSelection}
                explorationView={explorationView}
                onToggleViewMode={setExplorationView}
              />
            )}
          </div>
        )}

        {isExploring && (
          <Button
            onClick={hasSelection ? clearSelection : exitExploration}
            variant="ghost"
            aria-label={hasSelection ? "Volver" : profile.explore.exit}
            className={cn(
              styles.explorationControls,
              "absolute top-4 left-4 z-40 inline-flex items-center gap-2 rounded-full border-0 bg-black/70 px-4 py-2 text-sm font-medium text-white/90 shadow-none ring-0 backdrop-blur-xl hover:bg-black/90 hover:text-white transition-all cursor-pointer",
            )}
          >
            <ArrowLeft aria-hidden="true" className="size-4" />
            <span>Volver</span>
          </Button>
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
