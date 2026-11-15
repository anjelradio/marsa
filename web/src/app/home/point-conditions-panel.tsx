"use client";

import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { MapPin, Mountain, Thermometer, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import { useTranslation } from "@/i18n/context";

export interface ConditionMetric {
  label: string;
  display: string;
  icon: LucideIcon;
}

/** Panel de condiciones del punto elegido; mismo diseño que el clima de Marte. */
export function PointConditionsPanel({
  title,
  point,
  status,
  metrics,
  labels,
  footer,
  planet = "earth",
  onRetry,
  onClose,
  onToggleViewMode,
}: {
  title: string;
  point: GeoPoint;
  status: "loading" | "error" | "ready";
  metrics: ConditionMetric[] | null;
  labels: { latitude: string; longitude: string; loading: string; error: string; retry: string; close: string };
  footer?: ReactNode;
  planet?: "earth" | "moon";
  onRetry?: () => void;
  onClose: () => void;
  onToggleViewMode?: (mode: "geology" | "climate") => void;
}) {
  const { locale } = useTranslation();
  const format = (value: number) => value.toLocaleString(locale, { maximumFractionDigits: 2 });

  const theme =
    planet === "earth"
      ? {
          card: "bg-[#131a30]/55",
          accent: "text-sky-400",
          iconColor: "text-sky-400",
          buttonActive: "bg-white/15 text-white shadow-none",
        }
      : {
          card: "bg-[#161a24]/55",
          accent: "text-slate-300",
          iconColor: "text-slate-300",
          buttonActive: "bg-white/15 text-white shadow-none",
        };

  return (
    <aside
      aria-labelledby="point-conditions-title"
      className="min-w-0 rounded-4xl max-sm:order-first sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className={`gap-4 rounded-4xl border-0 p-5 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl ${theme.card}`}>
        {onToggleViewMode && (
          <div className="grid grid-cols-2 gap-1 rounded-2xl bg-white/7 backdrop-blur-md p-1 text-xs">
            <button
              type="button"
              onClick={() => onToggleViewMode("geology")}
              className="flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium text-white/60 hover:text-white transition-colors"
            >
              <Mountain className={`size-3.5 ${theme.accent}`} />
              <span>Rocas y Minerales</span>
            </button>
            <button
              type="button"
              onClick={() => onToggleViewMode("climate")}
              className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium transition-colors ${theme.buttonActive}`}
            >
              <Thermometer className="size-3.5 text-white" />
              <span>Clima y Atmósfera</span>
            </button>
          </div>
        )}
        <div className="flex items-start justify-between gap-2 pb-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2.5">
              <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7">
                <MapPin aria-hidden="true" className={`size-4 ${theme.accent}`} />
              </span>
              <h2 id="point-conditions-title" className="truncate font-headline text-base font-semibold text-white">
                {title}
              </h2>
            </div>
            <p className="mt-1 pl-10.5 font-mono text-xs text-white/60">
              <span className="whitespace-nowrap">{labels.latitude} {format(point.latitude)}°</span>
              {" · "}
              <span className="whitespace-nowrap">{labels.longitude} {format(point.longitude)}°</span>
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label={labels.close}
            onClick={onClose}
            className="shrink-0 rounded-full text-white/70 hover:bg-white/10 hover:text-white"
          >
            <X aria-hidden="true" className="size-4" />
          </Button>
        </div>

        <div aria-live="polite">
          {status === "loading" && <p className="text-sm text-white/75">{labels.loading}</p>}
          {status === "error" && (
            <div className="space-y-2 rounded-2xl bg-white/7 p-4 text-center">
              <p className="text-xs text-red-300">{labels.error}</p>
              {onRetry && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2 rounded-full border-0 bg-white/10 text-xs text-white hover:bg-white/20"
                  onClick={onRetry}
                >
                  {labels.retry}
                </Button>
              )}
            </div>
          )}
          {status === "ready" && metrics && (
            <>
              <dl className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {metrics.map(({ label, display, icon: Icon }) => (
                  <div key={label} className="flex flex-col justify-between gap-2 rounded-2xl bg-white/7 backdrop-blur-md p-3.5 min-h-[5.5rem]">
                    <dt className="flex items-center gap-1.5 text-xs text-app-secondary/75">
                      <span className="grid size-7 shrink-0 place-items-center rounded-lg bg-white/7">
                        <Icon aria-hidden="true" className={`size-3.5 ${theme.iconColor}`} />
                      </span>
                      <span className="truncate">{label}</span>
                    </dt>
                    <dd className="pl-1 font-mono text-base font-medium tracking-tight text-white">{display}</dd>
                  </div>
                ))}
              </dl>
              {footer && (
                <p className="mt-3 pt-2 text-xs leading-relaxed text-white/70">{footer}</p>
              )}
            </>
          )}
        </div>
      </Card>
    </aside>
  );
}
