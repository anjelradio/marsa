"use client";

import { useEffect, useState } from "react";
import { Cloud, Gauge, MapPin, Thermometer, Wind, X, Sun } from "lucide-react";
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
}: {
  point: MarsCoordinates;
  onClose: () => void;
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
      className="min-w-0 rounded-3xl sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className="gap-4 rounded-3xl border border-white/15 bg-linear-to-br from-[#281810]/95 to-[#120d0b]/95 p-4 text-white shadow-2xl backdrop-blur-md">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h2 id="mars-climate-title" className="flex items-center gap-2 font-headline text-base font-medium text-white">
              <MapPin aria-hidden="true" className="size-4 shrink-0 text-[#ffab57]" />
              {copy.title}
            </h2>
            <p className="mt-1 font-mono text-xs text-white/75">
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
            className="shrink-0 rounded-full text-white/80 hover:bg-white/10 hover:text-white"
          >
            <X aria-hidden="true" />
          </Button>
        </div>

        <div aria-live="polite">
          {result === null && <p className="text-sm text-white/75">{copy.loading}</p>}
          {result === "error" && (
            <div className="space-y-2">
              <p className="text-sm text-white/85">{copy.error}</p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="rounded-full border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white"
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
              <dl className="space-y-1">
                {metrics.map(({ label, value, unit, digits, icon: Icon }) => (
                  <div key={label} className="flex items-center justify-between gap-2 rounded-xl bg-white/5 px-2.5 py-2 text-xs">
                    <dt className="flex items-center gap-2 text-white/75">
                      <Icon aria-hidden="true" className="size-3.5 shrink-0 text-[#ffab57]" />
                      {label}
                    </dt>
                    <dd className="shrink-0 font-mono text-white">{format(value, digits)}{unit && ` ${unit}`}</dd>
                  </div>
                ))}
              </dl>
              <p className="mt-3 border-t border-white/10 pt-2 text-xs leading-relaxed text-white/70">
                {copy.model} · Ls {result.solar_longitude_deg}°<br />
                <a
                  href="https://www-mars.lmd.jussieu.fr/mars/info_web/index.html#quotes"
                  className="text-[#ffbd80] underline underline-offset-2"
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
