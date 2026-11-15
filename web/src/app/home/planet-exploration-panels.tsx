"use client";

import { useEffect, useState } from "react";
import { Cloud, Gauge, Radiation, Snowflake, Sun, Thermometer, Wind, Weight } from "lucide-react";
import {
  requestEarthClimate,
  type EarthClimate,
} from "@/features/earth/infrastructure/earth-climate";
import {
  MOON_GRAVITY_M_S2,
  MOON_RADIATION_MSV_PER_DAY,
  moonConditions,
} from "@/features/moon/infrastructure/moon-conditions";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import { useTranslation } from "@/i18n/context";
import { PointConditionsPanel, type ConditionMetric } from "./point-conditions-panel";
import { PointImagesPanel } from "./point-images-panel";

function EarthClimatePanel({ point, onClose }: { point: GeoPoint; onClose: () => void }) {
  const { dict, locale } = useTranslation();
  const copy = dict.earth.climate;
  const [result, setResult] = useState<EarthClimate | "error" | null>(null);
  const [attempt, setAttempt] = useState(0);
  const { latitude, longitude } = point;

  useEffect(() => {
    const controller = new AbortController();
    void requestEarthClimate({ latitude, longitude }, controller.signal, copy.error).then((response) => {
      if (controller.signal.aborted) return;
      setResult(response.ok ? response.data : "error");
    });
    return () => controller.abort();
  }, [latitude, longitude, attempt, copy.error]);

  const fmt = (value: number, digits: number) => value.toLocaleString(locale, { maximumFractionDigits: digits });
  const values = result && result !== "error" ? result.values : null;
  const metrics: ConditionMetric[] | null = values && [
    { label: copy.temperature, display: `${fmt(values.surface_temperature_k - 273.15, 1)} °C`, icon: Thermometer },
    { label: copy.pressure, display: `${fmt(values.surface_pressure_pa / 100, 1)} hPa`, icon: Gauge },
    { label: copy.wind, display: `${fmt(values.wind_10m_m_s, 2)} m/s`, icon: Wind },
    { label: copy.clouds, display: `${fmt(values.cloud_cover_pct, 1)} %`, icon: Cloud },
    { label: copy.aerosols, display: fmt(values.aerosol_optical_depth, 3), icon: Sun },
  ];

  return (
    <PointConditionsPanel
      title={copy.title}
      point={point}
      status={result === null ? "loading" : result === "error" ? "error" : "ready"}
      metrics={metrics}
      labels={copy}
      onRetry={() => {
        setResult(null);
        setAttempt((previous) => previous + 1);
      }}
      onClose={onClose}
      footer={
        result && result !== "error" ? (
          <a
            href="https://power.larc.nasa.gov/"
            className="text-[#ffbd80] underline underline-offset-2"
            target="_blank"
            rel="noreferrer"
          >
            {result.source}
          </a>
        ) : null
      }
    />
  );
}

function MoonConditionsPanel({ point, onClose }: { point: GeoPoint; onClose: () => void }) {
  const { dict, locale } = useTranslation();
  const copy = dict.moon.climate;
  const { noonK, nightK } = moonConditions(point);
  const fmt = (value: number, digits: number) => value.toLocaleString(locale, { maximumFractionDigits: digits });
  const metrics: ConditionMetric[] = [
    { label: copy.noon, display: `${fmt(noonK - 273.15, 0)} °C`, icon: Thermometer },
    { label: copy.night, display: `${fmt(nightK - 273.15, 0)} °C`, icon: Snowflake },
    { label: copy.pressure, display: "≈ 3×10⁻¹⁰ Pa", icon: Gauge },
    { label: copy.gravity, display: `${fmt(MOON_GRAVITY_M_S2, 2)} m/s²`, icon: Weight },
    { label: copy.radiation, display: `${fmt(MOON_RADIATION_MSV_PER_DAY, 2)} mSv/${copy.day}`, icon: Radiation },
  ];

  return (
    <PointConditionsPanel
      title={copy.title}
      point={point}
      status="ready"
      metrics={metrics}
      labels={copy}
      onClose={onClose}
      footer={copy.model}
    />
  );
}

/** Paneles de clima/condiciones e imágenes del punto elegido en la Tierra o la Luna. */
export function PlanetExplorationPanels({
  planet,
  point,
  onClose,
}: {
  planet: "earth" | "moon";
  point: GeoPoint;
  onClose: () => void;
}) {
  return (
    <>
      {planet === "earth" ? (
        <EarthClimatePanel point={point} onClose={onClose} />
      ) : (
        <MoonConditionsPanel point={point} onClose={onClose} />
      )}
      <PointImagesPanel planet={planet} point={point} />
    </>
  );
}
