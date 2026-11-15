"use client";

import { useId } from "react";
import { Globe2, Moon, Orbit } from "lucide-react";
import { useTranslation } from "@/i18n/context";
import styles from "./planet-filter.module.css";

export type HomePlanet = "mars" | "moon" | "earth";

const PLANETS = [
  { id: "earth", icon: Globe2 },
  { id: "mars", icon: Orbit },
  { id: "moon", icon: Moon },
] as const;
const positions = ["center", "below", "above"] as const;

export function PlanetFilter({
  value,
  onChange,
}: {
  value: HomePlanet;
  onChange: (planet: HomePlanet) => void;
}) {
  const { dict } = useTranslation();
  const copy = dict.analogs;
  const groupName = useId();
  const selectedIndex = PLANETS.findIndex(({ id }) => id === value);

  return (
    <fieldset className={styles.wheel}>
      <legend className="sr-only">{copy.planetFilter}</legend>
      {PLANETS.map(({ id, icon: Icon }, index) => {
        const position = positions[(index - selectedIndex + PLANETS.length) % PLANETS.length];
        return (
          <label key={id} className={styles.option} data-position={position}>
            <input
              className="sr-only"
              type="radio"
              name={groupName}
              value={id}
              checked={id === value}
              onChange={() => onChange(id)}
            />
            <span aria-hidden="true" className={styles.icon}><Icon size={22} strokeWidth={1.5} /></span>
            <span className={styles.label}>{copy.planets[id]}</span>
          </label>
        );
      })}
    </fieldset>
  );
}
