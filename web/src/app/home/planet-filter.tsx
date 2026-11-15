"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/i18n/context";

export type HomePlanet = "mars" | "moon" | "earth";

const PLANETS: HomePlanet[] = ["mars", "moon", "earth"];

/** Filtro superior para elegir el planeta que ocupa el centro de /home. */
export function PlanetFilter({
  value,
  onChange,
}: {
  value: HomePlanet;
  onChange: (planet: HomePlanet) => void;
}) {
  const { dict } = useTranslation();
  const copy = dict.analogs;

  return (
    <div
      role="group"
      aria-label={copy.planetFilter}
      className="flex gap-1 rounded-full border border-white/15 bg-black/50 p-1 backdrop-blur-md"
    >
      {PLANETS.map((planet) => (
        <Button
          key={planet}
          type="button"
          size="sm"
          variant="ghost"
          aria-pressed={value === planet}
          onClick={() => onChange(planet)}
          className={cn(
            "rounded-full px-4 text-white/80 hover:bg-white/10 hover:text-white",
            value === planet && "bg-[#ffab57] text-black hover:bg-[#ffab57] hover:text-black",
          )}
        >
          {copy.planets[planet]}
        </Button>
      ))}
    </div>
  );
}
