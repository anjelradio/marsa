"use client";

import { useState } from "react";
import { ExternalLink, Images } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import {
  pointImageUrl,
  type PointImagePlanet,
  type PointImageView,
} from "@/features/shared/domain/point-images";
import { useTranslation } from "@/i18n/context";

const views: PointImageView[] = ["regional", "detail"];

/** Imagen orbital del punto elegido en dos escalas; mismo diseño que la galería de Marte. */
export function PointImagesPanel({ planet, point }: { planet: PointImagePlanet; point: GeoPoint }) {
  const { dict } = useTranslation();
  const copy = dict[planet].images;
  const [view, setView] = useState<PointImageView>("regional");
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const url = pointImageUrl(planet, view, point);

  const theme =
    planet === "earth"
      ? {
          card: "border-sky-500/25 bg-linear-to-br from-[#0c1f36]/95 via-[#081525]/95 to-[#040a12]/95",
          icon: "text-sky-400",
          pressed: "aria-pressed:bg-sky-500/20 aria-pressed:text-sky-200",
        }
      : {
          card: "border-slate-400/25 bg-linear-to-br from-[#1c212a]/95 via-[#13161c]/95 to-[#0a0c0f]/95",
          icon: "text-slate-300",
          pressed: "aria-pressed:bg-slate-400/20 aria-pressed:text-slate-100",
        };

  return (
    <aside aria-labelledby="point-images-title" className="min-w-0 rounded-3xl max-sm:order-last sm:col-start-1 sm:row-start-1 lg:col-start-1">
      <Card className={`gap-3 rounded-3xl border p-4 text-white shadow-2xl backdrop-blur-md ${theme.card}`}>
        <h2 id="point-images-title" className="flex items-center gap-2 text-base font-medium text-white">
          <Images aria-hidden="true" className={`size-4 shrink-0 ${theme.icon}`} />
          {copy.title}
        </h2>

        <div
          role="group"
          aria-label={copy.selectView}
          className="grid grid-cols-2 gap-0.5 rounded-xl border border-white/10 bg-black/35 p-0.5"
        >
          {views.map((option) => (
            <Button
              key={option}
              type="button"
              variant="ghost"
              size="sm"
              aria-pressed={view === option}
              onClick={() => setView(option)}
              className={`h-auto min-h-8 rounded-[0.6rem] px-1.5 py-1.5 text-center text-xs whitespace-normal text-white/80 hover:bg-white/10 hover:text-white ${theme.pressed}`}
            >
              {copy.views[option]}
            </Button>
          ))}
        </div>

        {failedUrl === url ? (
          <p role="status" className="text-sm text-white/80">{copy.error}</p>
        ) : (
          <a href={url} target="_blank" rel="noreferrer" className="group relative block overflow-hidden rounded-2xl bg-black/40">
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
              className="absolute top-2 right-2 size-4 rounded bg-black/60 p-0.5 text-white/80 opacity-0 transition-opacity group-hover:opacity-100"
            />
          </a>
        )}
        <p className="text-xs text-white/65">{copy.source}</p>
      </Card>
    </aside>
  );
}
