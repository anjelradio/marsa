"use client";

import { useId, useState } from "react";
import { ExternalLink, Images } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import {
  pointImageUrl,
  type PointImagePlanet,
  type PointImageView,
} from "@/features/shared/domain/point-images";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/i18n/context";

const views: PointImageView[] = ["regional", "detail"];

/** Imagen orbital del punto elegido en dos escalas; mismo diseño que la galería de Marte. */
export function PointImagesPanel({ planet, point, className }: { planet: PointImagePlanet; point: GeoPoint; className?: string }) {
  const titleId = useId();
  const { dict } = useTranslation();
  const copy = dict[planet].images;
  const [view, setView] = useState<PointImageView>("regional");
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const url = pointImageUrl(planet, view, point);

  const theme =
    planet === "earth"
      ? {
          card: "bg-[#131a30]/55",
          icon: "text-sky-400",
          pressed: "aria-pressed:bg-white/15 aria-pressed:text-white shadow-none",
        }
      : {
          card: "bg-[#161a24]/55",
          icon: "text-slate-300",
          pressed: "aria-pressed:bg-white/15 aria-pressed:text-white shadow-none",
        };

  return (
    <aside aria-labelledby={titleId} className={cn("min-w-0 rounded-4xl", className ?? "max-sm:order-last sm:col-start-1 sm:row-start-1 lg:col-start-1")}>
      <Card className={`gap-3.5 rounded-4xl border-0 p-5 text-app-primary-foreground shadow-none ring-0 dark:ring-0 backdrop-blur-xl ${theme.card}`}>
        <div className="flex items-center gap-2.5 pb-2">
          <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/7">
            <Images aria-hidden="true" className={`size-4 shrink-0 ${theme.icon}`} />
          </span>
          <h2 id={titleId} className="font-headline text-base font-semibold text-white">
            {copy.title}
          </h2>
        </div>

        <div
          role="group"
          aria-label={copy.selectView}
          className="grid grid-cols-2 gap-1 rounded-2xl bg-white/7 backdrop-blur-md p-1"
        >
          {views.map((option) => (
            <Button
              key={option}
              type="button"
              variant="ghost"
              size="sm"
              aria-pressed={view === option}
              onClick={() => setView(option)}
              className={`h-auto min-h-8 rounded-xl px-2 py-1.5 text-center text-xs font-medium text-white/60 hover:text-white transition-colors ${theme.pressed}`}
            >
              {copy.views[option]}
            </Button>
          ))}
        </div>

        {failedUrl === url ? (
          <p role="status" className="text-sm text-white/80">{copy.error}</p>
        ) : (
          <a href={url} target="_blank" rel="noreferrer" className="group relative block overflow-hidden rounded-2xl bg-white/7">
            {/* eslint-disable-next-line @next/next/no-img-element -- imagen remota de un servicio público de la NASA */}
            <img
              src={url}
              alt={copy.title}
              referrerPolicy="no-referrer"
              loading="lazy"
              onError={() => setFailedUrl(url)}
              className="aspect-square w-full object-cover"
            />
            <ExternalLink
              aria-hidden="true"
              className="absolute top-2 right-2 size-6 rounded-full bg-black/60 p-1 text-white/80 opacity-0 transition-opacity group-hover:opacity-100"
            />
          </a>
        )}
        <p className="text-xs text-white/65">{copy.source}</p>
      </Card>
    </aside>
  );
}
