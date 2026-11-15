"use client";

import { useMemo, useState } from "react";
import { EarthPlanet } from "@/features/earth/presentation/components/earth-planet";
import { MoonPlanet } from "@/features/moon/presentation/components/moon-planet";
import type { AnalogRankingState } from "@/features/analogs/presentation/use-analog-ranking";
import type { ProjectedLandmark } from "@/features/shared/domain/geographic-coordinates";
import { useTranslation } from "@/i18n/context";
import { earthLandmarks, GlobeMarkers, targetLandmarks } from "./analogs-globe";

export type StagePlanet = "moon" | "earth";

/** Planeta central de /home para Luna y Tierra, con los sitios del ranking como marcadores. */
export function AnalogsStage({
  planet,
  result,
  openId,
  onOpenChange,
}: {
  planet: StagePlanet;
  result: AnalogRankingState;
  openId: number | null;
  onOpenChange: (id: number | null) => void;
}) {
  const { dict } = useTranslation();
  const copy = dict.analogs.stage[planet];
  const [points, setPoints] = useState<ProjectedLandmark[]>([]);

  const ranking = result && result !== "error" ? result : null;
  const landmarks = useMemo(
    () => (ranking ? (planet === "earth" ? earthLandmarks(ranking) : targetLandmarks(ranking)) : []),
    [ranking, planet],
  );
  const markers = (
    <GlobeMarkers
      points={points}
      activeId={planet === "earth" && openId !== null ? String(openId) : null}
      onSelect={
        planet === "earth"
          ? (id) => onOpenChange(Number(id) === openId ? null : Number(id))
          : undefined
      }
    />
  );

  return (
    <section
      aria-labelledby="stage-title"
      className="relative z-10 mx-auto grid min-h-[max(680px,100svh)] max-w-[1600px] place-items-center px-4 pb-40 pt-28 sm:px-7"
    >
      <div className="relative aspect-square w-full max-w-[580px] cursor-grab active:cursor-grabbing">
        {planet === "earth" ? (
          <EarthPlanet isExploring autoRotate landmarks={landmarks} onProjectedLandmarksChange={setPoints} />
        ) : (
          <MoonPlanet isExploring autoRotate landmarks={landmarks} onProjectedLandmarksChange={setPoints} />
        )}
        {markers}
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-10 z-20 px-4 text-center">
        <h1
          id="stage-title"
          className="text-[clamp(4rem,12vw,8rem)] font-black leading-[0.85] tracking-[-0.06em] text-white"
        >
          {copy.title}
        </h1>
        <p className="mt-3 text-sm text-white/75 sm:text-base">{copy.subtitle}</p>
      </div>
    </section>
  );
}
