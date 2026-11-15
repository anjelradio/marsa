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
          card: "border-sky-500/25 bg-linear-to-br from-[#0c1f36]/95 via-[#081525]/95 to-[#040a12]/95",
          accent: "text-sky-400",
          iconColor: "text-sky-400",
          buttonActive: "bg-sky-600/80 text-white",
        }
      : {
          card: "border-slate-400/25 bg-linear-to-br from-[#1c212a]/95 via-[#13161c]/95 to-[#0a0c0f]/95",
          accent: "text-slate-300",
          iconColor: "text-slate-300",
          buttonActive: "bg-slate-600/80 text-white",
        };

  return (
    <aside
      aria-labelledby="point-conditions-title"
      className="min-w-0 rounded-3xl max-sm:order-first sm:col-start-2 sm:row-start-1 lg:col-start-3"
    >
      <Card className={`gap-4 rounded-3xl border p-4 text-white shadow-2xl backdrop-blur-md ${theme.card}`}>
        {onToggleViewMode && (
          <div className="grid grid-cols-2 gap-1 rounded-2xl border border-white/10 bg-black/50 p-1 text-xs">
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
              className={`flex items-center justify-center gap-1.5 rounded-xl py-1.5 font-medium shadow transition-colors ${theme.buttonActive}`}
            >
              <Thermometer className="size-3.5 text-white" />
              <span>Clima y Atmósfera</span>
            </button>
          </div>
        )}
        <div className="flex items-start justify-between gap-2">
          <div>
            <h2 id="point-conditions-title" className="flex items-center gap-2 font-headline text-base font-medium text-white">
              <MapPin aria-hidden="true" className={`size-4 shrink-0 ${theme.accent}`} />
              {title}
            </h2>
            <p className="mt-1 font-mono text-xs text-white/75">
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
            className="shrink-0 rounded-full text-white/80 hover:bg-white/10 hover:text-white"
          >
            <X aria-hidden="true" />
          </Button>
        </div>

        <div aria-live="polite">
          {status === "loading" && <p className="text-sm text-white/75">{labels.loading}</p>}
          {status === "error" && (
            <div className="space-y-2">
              <p className="text-sm text-white/85">{labels.error}</p>
              {onRetry && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="rounded-full border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white"
                  onClick={onRetry}
                >
                  {labels.retry}
                </Button>
              )}
            </div>
          )}
          {status === "ready" && metrics && (
            <>
              <dl className="space-y-1">
                {metrics.map(({ label, display, icon: Icon }) => (
                  <div key={label} className="flex items-center justify-between gap-2 rounded-xl bg-white/5 px-2.5 py-2 text-xs">
                    <dt className="flex items-center gap-2 text-white/75">
                      <Icon aria-hidden="true" className={`size-3.5 shrink-0 ${theme.iconColor}`} />
                      {label}
                    </dt>
                    <dd className="shrink-0 font-mono text-white">{display}</dd>
                  </div>
                ))}
              </dl>
              {footer && (
                <p className="mt-3 border-t border-white/10 pt-2 text-xs leading-relaxed text-white/70">{footer}</p>
              )}
            </>
          )}
        </div>
      </Card>
    </aside>
  );
}
