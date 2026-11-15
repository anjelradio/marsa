"use client";

import { useState, useEffect, useMemo } from "react";
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
  X,
  MapPin,
  RotateCcw,
  Atom,
  Globe2,
  Moon,
  Sun,
  Scale,
  ExternalLink,
  Map as MapIcon,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MarsPlanet } from "@/features/mars/presentation/components/mars-planet";
import { MoonPlanet } from "@/features/moon/presentation/components/moon-planet";
import { EarthPlanet } from "@/features/earth/presentation/components/earth-planet";
import { MarsMissionPanels } from "./mars-mission-panels";
import { MoonMissionPanels } from "./moon-mission-panels";
import { EarthMissionPanels } from "./earth-mission-panels";
import { SideBySideComparison } from "@/features/explorer/presentation/components/side-by-side-comparison";
import { InteractiveAnalogMap } from "@/features/explorer/presentation/components/interactive-analog-map";
import { FALLBACK_CATALOG_REGIONS, FALLBACK_DEFAULT_RANKINGS } from "@/features/explorer/domain/explorer-catalog";
import type { RegionProfile } from "@/features/explorer/domain/explorer-types";
import { MOON_LANDMARKS } from "@/features/moon/domain/moon-data";
import { EARTH_LANDMARKS } from "@/features/earth/domain/earth-data";
import styles from "./mars-dashboard.module.css";
import stars from "./starfield.module.css";
import { useTranslation } from "@/i18n/context";
import { LanguageSwitcher } from "@/features/shared/presentation/components/language-switcher";
import { cn } from "@/lib/utils";

type CelestialBody = "mars" | "moon" | "earth";
type ViewMode = "3d" | "2d";

export default function HomePage() {
  const { dict } = useTranslation();
  const [activeBody, setActiveBody] = useState<CelestialBody>("mars");
  const [viewMode, setViewMode] = useState<ViewMode>("3d");
  const [isExploring, setIsExploring] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [activeLandmark, setActiveLandmark] = useState<string | null>(null);

  // Side-by-side comparison modal state
  const [comparisonKey, setComparisonKey] = useState<string | null>(null);

  // Allow ESC key to exit exploration mode or close active landmark
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (activeLandmark) {
          setActiveLandmark(null);
        } else if (isExploring) {
          setIsExploring(false);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isExploring, activeLandmark]);

  // Facts for Mars, Moon, and Earth
  const facts = useMemo(() => {
    if (activeBody === "moon") {
      return [
        {
          label: "Distancia a la Tierra",
          value: "384.400",
          unit: "km (media orbital)",
          icon: Orbit,
          color: "bg-[#132338]/65",
        },
        {
          label: "Período Sinódico",
          value: "29,5",
          unit: "días terrestres",
          icon: CalendarDays,
          color: "bg-[#192b42]/65",
        },
        {
          label: "Día Lunar (1 Día)",
          value: "708h 44m",
          unit: "día solar completo",
          icon: Clock3,
          color: "bg-[#122133]/65",
        },
        {
          label: "Rango Térmico Polar",
          value: "40 a 220",
          unit: "Kelvin (-233 a -53 °C)",
          icon: Thermometer,
          color: "bg-[#1d314c]/65",
        },
      ];
    }
    if (activeBody === "earth") {
      return [
        {
          label: "Distancia al Sol (1 AU)",
          value: "149,6",
          unit: "millones de km",
          icon: Orbit,
          color: "bg-[#0e2938]/65",
        },
        {
          label: "Año Solar",
          value: "365,25",
          unit: "días solares",
          icon: CalendarDays,
          color: "bg-[#13374b]/65",
        },
        {
          label: "Rotación Diurna",
          value: "24h 00m",
          unit: "período de rotación",
          icon: Clock3,
          color: "bg-[#0b2230]/65",
        },
        {
          label: "Temperatura Media",
          value: "+15 °C",
          unit: "superficie global",
          icon: Thermometer,
          color: "bg-[#174158]/65",
        },
      ];
    }
    // Mars (default)
    return [
      {
        label: dict.mars.facts.distanceToSun,
        value: dict.mars.facts.distanceToSunVal,
        unit: dict.mars.facts.distanceToSunUnit,
        icon: Orbit,
        color: "bg-app-primary/60",
      },
      {
        label: dict.mars.facts.martianYear,
        value: dict.mars.facts.martianYearVal,
        unit: dict.mars.facts.martianYearUnit,
        icon: CalendarDays,
        color: "bg-[#290d24]/65",
      },
      {
        label: dict.mars.facts.dayLength,
        value: dict.mars.facts.dayLengthVal,
        unit: dict.mars.facts.dayLengthUnit,
        icon: Clock3,
        color: "bg-[#131a30]/65",
      },
      {
        label: dict.mars.facts.avgTemp,
        value: dict.mars.facts.avgTempVal,
        unit: dict.mars.facts.avgTempUnit,
        icon: Thermometer,
        color: "bg-[#2d1e14]/65",
      },
    ];
  }, [activeBody, dict]);

  // Surface characteristics stacked on the left
  const surfaceCards = useMemo(() => {
    if (activeBody === "moon") {
      return [
        {
          label: "Atmósfera",
          value: "< 10⁻¹² mbar",
          unit: "exosfera / vacío",
          detail: "Helio, Neón e Hidrógeno",
          icon: Wind,
          color: "bg-[#132338]/65",
        },
        {
          label: "Topografía Polar",
          value: "Polo Sur-Aitken",
          unit: "cuenca de 2.500 km",
          detail: "> 8 km de profundidad",
          icon: Mountain,
          color: "bg-[#192b42]/65",
        },
        {
          label: "Composición",
          value: "Regolito y Hielo",
          unit: "trampas frías (PSR)",
          detail: "Anortosita e ilmenita",
          icon: Atom,
          color: "bg-[#122133]/65",
        },
      ];
    }
    if (activeBody === "earth") {
      return [
        {
          label: "Atmósfera",
          value: "1.013 mbar",
          unit: "presión al nivel del mar",
          detail: "78% N₂ · 21% O₂ · 1% Ar",
          icon: Wind,
          color: "bg-[#0e2938]/65",
        },
        {
          label: "Topografía",
          value: "Monte Everest",
          unit: "8.848 m sobre el nivel del mar",
          detail: "Fosa de las Marianas: -10.994 m",
          icon: Mountain,
          color: "bg-[#13374b]/65",
        },
        {
          label: "Hidrosfera",
          value: "71%",
          unit: "cobertura oceánica",
          detail: "Agua líquida en superficie",
          icon: Atom,
          color: "bg-[#0b2230]/65",
        },
      ];
    }
    // Mars
    return [
      {
        ...dict.mars.leftCards.atmosphere,
        icon: Wind,
        color: "bg-[#131a30]/65",
      },
      {
        ...dict.mars.leftCards.topography,
        icon: Mountain,
        color: "bg-[#2d1e14]/65",
      },
      {
        ...dict.mars.leftCards.composition,
        icon: Atom,
        color: "bg-[#291323]/65",
      },
    ];
  }, [activeBody, dict]);

  // Interactive POIs per body
  const currentLandmarks = useMemo(() => {
    if (activeBody === "moon") {
      return MOON_LANDMARKS.map((m) => ({
        id: m.id,
        name: m.name,
        type: m.type,
        coord: m.coord,
        desc: m.desc,
        positionClass: m.positionClass,
        comparisonKey: "shackleton-mcmurdo",
      }));
    }
    if (activeBody === "earth") {
      return EARTH_LANDMARKS.map((e) => ({
        id: e.id,
        name: e.name,
        type: e.type,
        coord: e.coord,
        desc: e.desc,
        positionClass: e.positionClass,
        comparisonKey: e.comparedWithTargetId === "mars-jezero" ? "jezero-atacama" : "shackleton-mcmurdo",
      }));
    }
    // Mars
    return [
      {
        id: "olympus",
        name: dict.mars.landmarks.olympus.name,
        type: dict.mars.landmarks.olympus.type,
        coord: dict.mars.landmarks.olympus.altitude,
        desc: dict.mars.landmarks.olympus.desc,
        positionClass: "top-[32%] left-[26%]",
        comparisonKey: null,
      },
      {
        id: "valles",
        name: dict.mars.landmarks.valles.name,
        type: dict.mars.landmarks.valles.type,
        coord: dict.mars.landmarks.valles.altitude,
        desc: dict.mars.landmarks.valles.desc,
        positionClass: "top-[54%] left-[64%]",
        comparisonKey: null,
      },
      {
        id: "curiosity",
        name: dict.mars.landmarks.curiosity.name,
        type: dict.mars.landmarks.curiosity.type,
        coord: dict.mars.landmarks.curiosity.altitude,
        desc: dict.mars.landmarks.curiosity.desc,
        positionClass: "top-[62%] left-[34%]",
        comparisonKey: "jezero-atacama",
      },
      {
        id: "perseverance",
        name: dict.mars.landmarks.perseverance.name,
        type: dict.mars.landmarks.perseverance.type,
        coord: dict.mars.landmarks.perseverance.altitude,
        desc: dict.mars.landmarks.perseverance.desc,
        positionClass: "top-[38%] left-[72%]",
        comparisonKey: "jezero-atacama",
      },
    ];
  }, [activeBody, dict]);

  const bodyTitles = {
    mars: { title: dict.mars.title, subtitle: dict.mars.subtitle, color: "text-[#ffab57]" },
    moon: { title: "Luna", subtitle: "Satélite natural de la Tierra · Artemis Base Camp", color: "text-[#8de3ff]" },
    earth: { title: "Tierra", subtitle: "Planeta hogar y red global de análogos geológicos", color: "text-[#38bdf8]" },
  };

  const earthSites = useMemo(() => FALLBACK_CATALOG_REGIONS.filter((r: RegionProfile) => r.body === "earth"), []);

  return (
    <main className="relative isolate min-h-svh overflow-hidden bg-black text-app-secondary select-none">
      {/* Background Starfield */}
      <div aria-hidden="true" className="pointer-events-none absolute -inset-8 -z-10">
        <div className={cn(stars.nebula, "absolute inset-0")} />
        <div className={cn(stars.distantStars, "absolute inset-0")} />
        <div className={cn(stars.nearStars, "absolute inset-0")} />
        <div className={stars.comets} />
      </div>

      {/* Top utility navigation */}
      <div className="absolute top-4 right-4 z-40 flex flex-wrap items-center gap-2">
        {/* Celestial Body Segmented Control */}
        <div className="flex items-center rounded-full border border-white/15 bg-black/60 p-1 text-xs backdrop-blur-md shadow-xl">
          <button
            type="button"
            onClick={() => {
              setActiveBody("mars");
              setActiveLandmark(null);
            }}
            className={cn(
              "flex items-center gap-1.5 rounded-full px-3 py-1 font-medium transition cursor-pointer",
              activeBody === "mars"
                ? "bg-[#ffab57] text-black shadow-md font-semibold"
                : "text-white/70 hover:text-white"
            )}
          >
            <Sun className="size-3.5" />
            Marte
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveBody("moon");
              setActiveLandmark(null);
            }}
            className={cn(
              "flex items-center gap-1.5 rounded-full px-3 py-1 font-medium transition cursor-pointer",
              activeBody === "moon"
                ? "bg-[#8de3ff] text-black shadow-md font-semibold"
                : "text-white/70 hover:text-white"
            )}
          >
            <Moon className="size-3.5" />
            Luna
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveBody("earth");
              setActiveLandmark(null);
            }}
            className={cn(
              "flex items-center gap-1.5 rounded-full px-3 py-1 font-medium transition cursor-pointer",
              activeBody === "earth"
                ? "bg-[#38bdf8] text-black shadow-md font-semibold"
                : "text-white/70 hover:text-white"
            )}
          >
            <Globe2 className="size-3.5" />
            Tierra
          </button>
        </div>

        {/* View Mode Toggle: 3D Globe vs 2D Map */}
        <div className="flex items-center rounded-full border border-white/15 bg-black/60 p-1 text-xs backdrop-blur-md shadow-xl">
          <button
            type="button"
            onClick={() => setViewMode("3d")}
            className={cn(
              "flex items-center gap-1 rounded-full px-2.5 py-1 font-medium transition cursor-pointer",
              viewMode === "3d" ? "bg-white text-black font-semibold" : "text-white/70 hover:text-white"
            )}
          >
            <Globe2 className="size-3.5" />
            3D
          </button>
          <button
            type="button"
            onClick={() => setViewMode("2d")}
            className={cn(
              "flex items-center gap-1 rounded-full px-2.5 py-1 font-medium transition cursor-pointer",
              viewMode === "2d" ? "bg-white text-black font-semibold" : "text-white/70 hover:text-white"
            )}
          >
            <MapIcon className="size-3.5" />
            Mapa 2D
          </button>
        </div>

        {/* Compare Side-by-Side Action Button */}
        <Button
          onClick={() => setComparisonKey("jezero-atacama")}
          size="sm"
          className="rounded-full bg-linear-to-r from-[#ffab57] to-[#8de3ff] text-black font-semibold shadow-lg hover:opacity-90 gap-1.5 text-xs"
        >
          <Scale className="size-3.5" />
          Comparar Lado a Lado
        </Button>

        {/* Link to Dedicated DSS Explorer */}
        <Button
          asChild
          variant="outline"
          size="sm"
          className="border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white backdrop-blur-md rounded-full text-xs"
        >
          <Link href="/explorer">
            DSS Análogos
            <ExternalLink className="size-3 ml-1" />
          </Link>
        </Button>

        <Button
          asChild
          variant="ghost"
          size="sm"
          className="text-white/80 hover:text-white hover:bg-white/10 rounded-full"
        >
          <Link href="/">
            <ArrowLeft className="size-4 mr-1.5" />
            Landing
          </Link>
        </Button>
        <LanguageSwitcher
          variant="outline"
          size="sm"
          className="border-white/15 bg-white/5 text-white hover:bg-white/15 hover:text-white backdrop-blur-md rounded-full"
        />
      </div>

      {/* Main Dashboard Section */}
      <section
        aria-labelledby="dashboard-title"
        className="relative mx-auto grid max-w-[1600px] gap-7 px-4 py-5 sm:px-7 lg:min-h-[max(680px,100svh)] lg:gap-0 lg:px-4"
      >
        {/* Header Branding */}
        <header
          className={cn(
            "text-app-primary-foreground lg:absolute lg:top-5 lg:left-4 z-30 motion-safe:transition-opacity motion-safe:duration-200",
            isExploring && "opacity-0"
          )}
        >
          <div className="flex items-start gap-1 font-headline text-3xl font-semibold leading-none tracking-tight">
            {dict.common.appName}{" "}
            <Sparkles aria-hidden="true" className={cn("size-3.5 fill-current", bodyTitles[activeBody].color)} />
          </div>
          <p className="mt-1 text-xs text-white/60">
            Atlas 3D Interactivo y Explorador de Análogos
          </p>
        </header>

        {/* 2D Map View or 3D Globe View */}
        {viewMode === "2d" ? (
          <div className="relative z-20 order-1 mx-auto w-full max-w-5xl pt-20 pb-10">
            <InteractiveAnalogMap
              sites={earthSites}
              ranking={FALLBACK_DEFAULT_RANKINGS}
              selectedSiteId="earth-atacama-desert"
              secondarySiteId="earth-mcmurdo-dry-valleys"
              queriedCoord={null}
              onSelectSite={(id) => {
                const presetKey = id.includes("mcmurdo") ? "shackleton-mcmurdo" : "jezero-atacama";
                setComparisonKey(presetKey);
              }}
              onMapCoordinateClick={() => {}}
            />
            <div className="mt-4 flex items-center justify-between text-xs text-white/60">
              <span>Haz clic en un sitio análogo terrestre para abrir la comparación con Marte / Luna.</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setViewMode("3d")}
                className="rounded-full border-white/20 text-white"
              >
                Volver a Globo 3D
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* Surface data cards stacked on the left side */}
            <aside
              aria-label="Características Superficiales"
              className={cn(
                "order-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3 lg:absolute lg:top-20 lg:left-4 lg:z-20 lg:flex lg:w-52 lg:flex-col lg:gap-3 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
                isExploring ? "lg:-translate-x-72 lg:opacity-0 pointer-events-none" : "lg:translate-x-0 lg:opacity-100"
              )}
            >
              {surfaceCards.map(({ label, value, unit, detail, icon: Icon, color }, index) => (
                <Card
                  key={label}
                  className={cn(
                    stars.dashboardCard,
                    "group min-w-0 justify-between gap-1.5 rounded-3xl p-3.5 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,background-color,box-shadow] duration-300 hover:-translate-y-1 hover:ring-white/20 hover:shadow-[0_16px_36px_#00000045] motion-reduce:transition-none lg:min-h-32",
                    color
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
                    <span className="mt-1.5 block text-[0.62rem] font-normal tracking-normal text-app-secondary/50 font-mono">
                      {detail}
                    </span>
                  </p>
                </Card>
              ))}
            </aside>

            {/* 3D Planet Stage */}
            <div className={cn(styles.planetStage, "relative z-10 order-1")} data-exploring={isExploring}>
              <div
                role="button"
                tabIndex={0}
                aria-label={bodyTitles[activeBody].title}
                onClick={() => {
                  if (!isExploring) setIsExploring(true);
                }}
                onKeyDown={(e) => {
                  if ((e.key === "Enter" || e.key === " ") && !isExploring) {
                    e.preventDefault();
                    setIsExploring(true);
                  }
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                className={cn(
                  styles.planet,
                  "pointer-events-auto relative mx-auto aspect-square w-full max-w-[580px] outline-none focus-visible:ring-2 focus-visible:ring-[#ffab57]/80 focus-visible:ring-offset-4 focus-visible:ring-offset-black",
                  isExploring ? "cursor-grab active:cursor-grabbing" : "cursor-pointer"
                )}
              >
                {/* Dynamically active 3D planet */}
                {activeBody === "mars" && (
                  <MarsPlanet isHovered={isHovered && !isExploring} isExploring={isExploring} />
                )}
                {activeBody === "moon" && (
                  <MoonPlanet isHovered={isHovered && !isExploring} isExploring={isExploring} />
                )}
                {activeBody === "earth" && (
                  <EarthPlanet isHovered={isHovered && !isExploring} isExploring={isExploring} />
                )}

                {/* Exploration Mode: Interactive Surface Landmarks / POIs */}
                {isExploring && (
                  <div className="pointer-events-none absolute inset-0 z-30 animate-in fade-in fill-mode-both duration-240 lg:[animation-delay:120ms] motion-reduce:animate-none">
                    {currentLandmarks.map((poi) => {
                      const isActive = activeLandmark === poi.id;
                      return (
                        <div
                          key={poi.id}
                          className={cn(
                            "absolute -translate-x-1/2 -translate-y-1/2 transition-[transform,opacity] duration-300 motion-reduce:transition-none",
                            poi.positionClass
                          )}
                        >
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveLandmark(isActive ? null : poi.id);
                            }}
                            className={cn(
                              "group pointer-events-auto flex items-center gap-1.5 rounded-full border px-2.5 py-1 backdrop-blur-md text-[0.68rem] font-semibold transition-[color,background-color,border-color,transform,box-shadow] duration-300 shadow-lg cursor-pointer motion-reduce:transition-none",
                              isActive
                                ? "border-[#ffab57] bg-[#39190d]/90 text-white scale-110 shadow-[0_0_20px_#ffab57a0]"
                                : "border-white/20 bg-black/60 text-white/90 hover:border-white/40 hover:bg-black/80 hover:scale-105"
                            )}
                          >
                            <span className="relative flex size-2">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ffab57] opacity-75 motion-reduce:animate-none" />
                              <span className="relative inline-flex rounded-full size-2 bg-[#ffab57]" />
                            </span>
                            <span>{poi.name}</span>
                          </button>

                          {/* Popover detail card for active landmark */}
                          {isActive && (
                            <div
                              onClick={(e) => e.stopPropagation()}
                              className="pointer-events-auto absolute top-8 left-1/2 -translate-x-1/2 z-40 w-72 rounded-2xl border border-white/20 bg-[#160b1e]/95 p-3.5 shadow-2xl backdrop-blur-xl animate-in zoom-in-95 duration-200 motion-reduce:animate-none"
                            >
                              <div className="flex items-start justify-between gap-1">
                                <div>
                                  <p className="text-xs font-bold text-white flex items-center gap-1">
                                    <MapPin className="size-3 text-[#ffab57]" /> {poi.name}
                                  </p>
                                  <p className="text-[0.62rem] text-[#ffab57] font-medium">{poi.type}</p>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => setActiveLandmark(null)}
                                  className="rounded-full p-0.5 text-white/60 hover:text-white hover:bg-white/10"
                                >
                                  <X className="size-3.5" />
                                </button>
                              </div>
                              <p className="mt-1.5 text-[0.68rem] leading-relaxed text-app-secondary/85">
                                {poi.desc}
                              </p>
                              <p className="mt-2 text-[0.62rem] font-mono text-white/60 border-t border-white/10 pt-1">
                                📍 {poi.coord}
                              </p>

                              {/* Button to open side-by-side analog comparison */}
                              {poi.comparisonKey && (
                                <div className="mt-3 pt-2 border-t border-white/10">
                                  <Button
                                    onClick={() => setComparisonKey(poi.comparisonKey)}
                                    size="sm"
                                    className="w-full rounded-xl bg-linear-to-r from-[#ffab57] to-[#8de3ff] text-black font-semibold text-xs h-7 gap-1"
                                  >
                                    <Scale className="size-3" />
                                    Comparar con Análogos Terrestres
                                  </Button>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Title & Subtitle */}
            <div
              className={cn(
                "relative z-20 order-2 -mt-[18%] pl-[5%] lg:absolute lg:top-[74.5%] lg:left-[14%] lg:mt-0 lg:pl-0 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
                isExploring ? "lg:translate-y-36 lg:opacity-0 pointer-events-none" : "lg:translate-y-0 lg:opacity-100"
              )}
            >
              <h1
                id="dashboard-title"
                className="text-[clamp(5.6rem,16vw,9rem)] font-black leading-[0.85] tracking-[-0.075em] text-white lg:origin-left lg:scale-x-[1.33] lg:text-[clamp(6.75rem,10.7vw,11rem)]"
              >
                {bodyTitles[activeBody].title}
              </h1>
              <p className="mt-3 text-sm text-app-secondary/75 sm:text-base">
                {bodyTitles[activeBody].subtitle}
              </p>
            </div>

            {/* 4 Top Fact Cards */}
            <dl
              className={cn(
                "order-3 grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:absolute lg:inset-x-4 lg:top-11 lg:left-[22.7%] lg:z-0 transform-gpu transition-[translate,opacity] duration-400 [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] motion-reduce:transition-none",
                isExploring ? "lg:-translate-y-48 lg:opacity-0 pointer-events-none" : "lg:translate-y-0 lg:opacity-100"
              )}
            >
              {facts.map(({ label, value, unit, icon: Icon, color }, index) => (
                <Card
                  key={label}
                  className={cn(
                    stars.dashboardCard,
                    "min-w-0 gap-2 rounded-3xl px-3 py-3 text-app-primary-foreground shadow-none ring-1 ring-inset ring-white/10 backdrop-blur-md transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-[0_14px_32px_#00000040] motion-reduce:transition-none sm:px-4 lg:min-h-30 lg:gap-1 lg:py-2.5",
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

            {/* Right Side Mission Panels */}
            {activeBody === "mars" && <MarsMissionPanels isExploring={isExploring} />}
            {activeBody === "moon" && <MoonMissionPanels isExploring={isExploring} />}
            {activeBody === "earth" && <EarthMissionPanels isExploring={isExploring} />}

            {/* Exploration Mode Overlays */}
            {isExploring && (
              <div
                className={cn(
                  styles.explorationControls,
                  "absolute inset-x-4 top-5 z-40 flex items-center justify-between"
                )}
              >
                <div className="flex items-center gap-3">
                  <Button
                    onClick={() => {
                      setIsExploring(false);
                      setActiveLandmark(null);
                    }}
                    variant="outline"
                    size="sm"
                    className="rounded-full border-white/20 bg-black/60 px-4 text-white hover:bg-white/20 hover:text-white backdrop-blur-md shadow-xl gap-2 font-medium cursor-pointer"
                  >
                    <ArrowLeft className="size-4" />
                    {dict.mars.explore.exit}
                  </Button>
                  <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80 backdrop-blur-md">
                    <Compass className="size-3.5 text-[#ffab57]" />
                    Modo Exploración 3D · {bodyTitles[activeBody].title}
                  </span>
                </div>

                {/* Drag hint pill at bottom */}
                <div className="pointer-events-none fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 rounded-full border border-white/15 bg-black/60 px-4 py-1.5 text-xs text-white/85 backdrop-blur-md shadow-2xl">
                  <RotateCcw className="size-3.5 text-[#ffab57] animate-spin [animation-duration:8s] motion-reduce:animate-none" />
                  Arrastra para girar el globo 3D · Clic en los puntos para ver detalles
                </div>
              </div>
            )}
          </>
        )}
      </section>

      {/* Side-by-Side Comparison Dialog Modal */}
      {comparisonKey && (
        <SideBySideComparison
          initialKey={comparisonKey}
          onClose={() => setComparisonKey(null)}
        />
      )}
    </main>
  );
}
