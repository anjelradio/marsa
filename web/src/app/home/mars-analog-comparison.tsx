"use client";

import { useRef, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { RankingTerrestre } from "@/features/geology/infrastructure/geology-client";
import type { GeoPoint } from "@/features/shared/domain/geographic-coordinates";
import { AppDialog } from "@/features/shared/presentation/components/dialogs/app-dialog";
import { useTranslation } from "@/i18n/context";
import { MarsImageGallery } from "./mars-image-gallery";
import { PointImagesPanel } from "./point-images-panel";

// Muestra los candidatos de la región seleccionada y abre su comparación orbital.
export function MarsAnalogComparison({ ranking, point }: { ranking: RankingTerrestre; point: GeoPoint }) {
  const { dict, locale } = useTranslation();
  const copy = dict.marsAnalogComparison;
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const candidate = ranking.candidatos.find((item) => item.celda_id === selectedId);
  const percent = new Intl.NumberFormat(locale, { style: "percent", maximumFractionDigits: 1 });
  const degrees = new Intl.NumberFormat(locale, { maximumFractionDigits: 2 });

  return (
    <div className="space-y-3">
      <p className="text-xs leading-relaxed text-white/70">{copy.scope}</p>
      {ranking.candidatos.length ? (
        <>
          <p className="text-xs font-medium text-white/80">
            {copy.count.replace("{shown}", String(ranking.candidatos.length)).replace("{total}", String(ranking.regiones_evaluadas))}
          </p>
          <ol className="space-y-2">
            {ranking.candidatos.map((item) => (
              <li key={item.celda_id}>
                <Button
                  variant="outline"
                  type="button"
                  aria-haspopup="dialog"
                  aria-label={`${copy.compare} · ${item.region_referencia}`}
                  className="h-auto w-full justify-between gap-3 rounded-2xl border-0 bg-white/7 p-3.5 text-left whitespace-normal text-white hover:bg-white/12 transition-all shadow-none ring-0 dark:ring-0"
                  onClick={(event) => {
                    trigger.current = event.currentTarget;
                    setSelectedId(item.celda_id);
                  }}
                >
                  <span className="min-w-0 text-xs leading-snug">{item.region_referencia}</span>
                  <span className="inline-flex shrink-0 items-center gap-1.5 font-mono text-xs text-amber-200">
                    {percent.format(item.similitud_pct / 100)} <ArrowUpRight aria-hidden="true" className="size-3" />
                  </span>
                </Button>
              </li>
            ))}
          </ol>
        </>
      ) : (
        <p className="text-sm text-white/75">{copy.noMatches}</p>
      )}

      <AppDialog
        open={Boolean(candidate)}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedId(null);
            requestAnimationFrame(() => trigger.current?.focus());
          }
        }}
        title={candidate?.region_referencia ?? copy.compare}
        description={copy.scope}
        showCloseButton
        size="full"
        className="max-h-[90dvh] overflow-y-auto"
        bodyClassName="space-y-4 p-4 sm:p-6"
      >
        {candidate && (
          <>
            <p className="text-sm text-muted-foreground">
              {copy.center} {degrees.format(candidate.centro.lat)}° / {degrees.format(candidate.centro.lng)}°
              {candidate.cobertura_pct != null && ` · ${copy.coverage} ${percent.format(candidate.cobertura_pct / 100)}`}
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <MarsImageGallery point={point} className="self-start" />
              <PointImagesPanel
                key={candidate.celda_id}
                planet="earth"
                point={{ latitude: candidate.centro.lat, longitude: candidate.centro.lng }}
                className="self-start"
              />
            </div>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b">
                  <th scope="col" className="py-2">{copy.material}</th>
                  <th scope="col" className="py-2 text-right">{copy.mars}</th>
                  <th scope="col" className="py-2 text-right">{copy.earth}</th>
                </tr>
              </thead>
              <tbody>
                {candidate.comparacion_litologica.map(({ categoria, marte_pct, tierra_pct }) => (
                  <tr key={categoria} className="border-b">
                    <th scope="row" className="py-2 font-normal">
                      {copy.classes[categoria as keyof typeof copy.classes] ?? categoria.replaceAll("_", " ")}
                    </th>
                    <td className="py-2 text-right tabular-nums">{percent.format(marte_pct / 100)}</td>
                    <td className="py-2 text-right tabular-nums">{percent.format(tierra_pct / 100)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </AppDialog>
    </div>
  );
}
