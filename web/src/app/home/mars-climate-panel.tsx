"use client";

import { useEffect, useState } from "react";
import { Cloud, Gauge, MapPin, Mountain, Thermometer, Wind, X, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useTranslation } from "@/i18n/context";
import {
  requestMarsClimate,
  type MarsClimate,
  type MarsCoordinates,
} from "@/features/mars/infrastructure/mars-climate";

export function MarsClimatePanel({
  point,
  onClose,
  onToggleViewMode,
}: {
  point: MarsCoordinates;
  onClose: () => void;
  onToggleViewMode?: (mode: "geology" | "climate") => void;
}) {
  const { dict, locale } = useTranslation();
  const copy = dict.mars.climate;
  const [result, setResult] = useState<MarsClimate | "error" | null>(null);
  const [attempt, setAttempt] = useState(0);
  const { latitude, longitude } = point;

  useEffect(() => {
    const controller = new AbortController();
    void requestMarsClimate({ latitude, longitude }, controller.signal, copy.error).then((response) => {
      if (controller.signal.aborted) return;
      setResult(response.ok ? response.data : "error");
    });
    return () => controller.abort();
  }, [latitude, longitude, attempt, copy.error]);

  const format = (value: number, digits: number) => value.toLocaleString(locale, { maximumFractionDigits: digits });
  const values = result && result !== "error" ? result.values : null;
  const metrics = values && [
    { label: copy.temperature, value: values.surface_temperature_k - 273.15, unit: "°C", digits: 1, icon: Thermometer },
    { label: copy.pressure, value: values.surface_pressure_pa, unit: "Pa", digits: 1, icon: Gauge },
    { label: copy.wind, value: values.wind_10m_m_s, unit: "m/s", digits: 2, icon: Wind },
    { label: copy.clouds, value: values.cloud_ice_kg_m2 * 1000, unit: "g/m²", digits: 3, icon: Cloud },
    { label: copy.dust, value: values.dust_optical_depth, unit: "", digits: 3, icon: Sun },
  ];

  return (
    <aside
      aria-labelledby="mars-climate-title"
      className="min-w-0 rounded-4xl max-sm:order-first sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className="gap-4 rounded-4xl border-0 bg-[#2d1e14]/55 p-5 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl">
        {onToggleViewMode && (
          <div className="grid grid-cols-2 gap-1 rounded-2xl bg-white/7 backdrop-blur-md p-1 text-xs">
            <button
              type="button"
              onClick={() => onToggleViewMode("geology")}
              className="flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium text-white/60 hover:text-white transition-colors"
            >
              <Mountain className="size-3.5 text-[#ffab57]" />
              <span>Rocas y Minerales</span>
            </button>
            <button
              type="button"
              onClick={() => onToggleViewMode("climate")}
              className="flex items-center justify-center gap-1.5 rounded-xl bg-white/15 py-1.5 font-medium text-white shadow-none transition-colors"
            >
              <Thermometer className="size-3.5 text-amber-400" />
              <span>Clima y Atmósfera</span>
            </button>
          </div>
        )}
        <div className="flex items-start justify-between gap-2 pb-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2.5">
              <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7 text-[#ffab57]">
                <MapPin aria-hidden="true" className="size-4" />
              </span>
              <h2 id="mars-climate-title" className="truncate font-headline text-base font-semibold text-white">
                {copy.title}
              </h2>
            </div>
            <p className="mt-1 pl-10.5 font-mono text-xs text-white/60">
              <span className="whitespace-nowrap">{copy.latitude} {format(latitude, 2)}°</span>
              {" · "}
              <span className="whitespace-nowrap">{copy.longitude} {format(longitude, 2)}°</span>
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label={copy.close}
            onClick={onClose}
            className="shrink-0 rounded-full text-white/70 hover:bg-white/10 hover:text-white"
          >
            <X aria-hidden="true" className="size-4" />
          </Button>
        </div>

        <div aria-live="polite">
          {result === null && <p className="text-sm text-white/75">{copy.loading}</p>}
          {result === "error" && (
            <div className="space-y-2 rounded-2xl bg-white/7 p-4 text-center">
              <p className="text-xs text-red-300">{copy.error}</p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-2 rounded-full border-0 bg-white/10 text-xs text-white hover:bg-white/20"
                onClick={() => {
                  setResult(null);
                  setAttempt((previous) => previous + 1);
                }}
              >
                {copy.retry}
              </Button>
            </div>
          )}
          {metrics && result && result !== "error" && (
            <>
              <dl className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {metrics.map(({ label, value, unit, digits, icon: Icon }) => (
                  <div key={label} className="flex flex-col justify-between gap-2 rounded-2xl bg-white/7 backdrop-blur-md p-3.5 min-h-[5.5rem]">
                    <dt className="flex items-center gap-1.5 text-xs text-app-secondary/75">
                      <span className="grid size-7 shrink-0 place-items-center rounded-lg bg-white/7">
                        <Icon aria-hidden="true" className="size-3.5 text-[#ffab57]" />
                      </span>
                      <span className="truncate">{label}</span>
                    </dt>
                    <dd className="pl-1 font-mono text-base font-medium tracking-tight text-white tabular-nums">
                      {format(value, digits)}
                      {unit && <span className="ml-1 text-xs font-normal text-app-secondary/65">{unit}</span>}
                    </dd>
                  </div>
                ))}
              </dl>
              <p className="mt-3 pt-2 text-xs leading-relaxed text-white/70">
                {copy.model} · Ls {result.solar_longitude_deg}°<br />
                <a
                  href="https://www-mars.lmd.jussieu.fr/mars/info_web/index.html#quotes"
                  className="text-[#ffab57] underline underline-offset-2 hover:text-[#ffbe7a]"
                  target="_blank"
                  rel="noreferrer"
                >
                  {result.source}
                </a>
              </p>
            </>
          )}
        </div>
      </Card>
    </aside>
  );
}
