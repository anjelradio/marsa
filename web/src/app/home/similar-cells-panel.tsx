"use client";

import { Button } from "@/components/ui/button";
import { useTranslation } from "@/i18n/context";
import type { AnalogDestination } from "@/features/analogs/infrastructure/analogs-ranking";
import { useSimilarCells } from "@/features/analogs/presentation/use-similar-cells";

/** Las celdas de 10° del destino más parecidas a un sitio terrestre, con su estabilidad. */
export function SimilarCellsPanel({
  siteId,
  destination,
}: {
  siteId: number;
  destination: AnalogDestination;
}) {
  const { dict, locale } = useTranslation();
  const copy = dict.analogs;
  const cells = copy.cells;
  const { result, retry } = useSimilarCells(siteId, destination, cells.error);

  const pct = (value: number) => `${Math.round(value * 100)}%`;
  const group = (key: string) => (copy.groups as Record<string, string>)[key] ?? key;
  const degrees = (value: number) => value.toLocaleString(locale, { maximumFractionDigits: 0 });
  const bounds = (b: { lat_min: number; lat_max: number; lon_min: number; lon_max: number }) =>
    `${degrees(b.lat_min)}° / ${degrees(b.lat_max)}° · ${degrees(b.lon_min)}° / ${degrees(b.lon_max)}°`;

  let body;
  if (result === null) {
    body = <p className="text-white/70">{cells.loading}</p>;
  } else if (result === "error") {
    body = (
      <div className="space-y-2">
        <p className="text-white/85">{cells.error}</p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="rounded-full border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white"
          onClick={retry}
        >
          {cells.retry}
        </Button>
      </div>
    );
  } else if (result.evaluadas === 0) {
    body = <p className="text-white/70">{cells.empty}</p>;
  } else if (result.resultados.length === 0) {
    body = (
      <p className="text-white/70">
        {cells.noValid.replace("{min}", pct(result.cobertura_minima))}
      </p>
    );
  } else {
    const total = Object.values(result.pesos_grupo).reduce((a, b) => a + b, 0) || 1;
    const weights = Object.entries(result.pesos_grupo)
      .map(([key, weight]) => `${group(key)} ${pct(weight / total)}`)
      .join(" · ");
    body = (
      <>
        <p className="text-white/60">
          {cells.summary
            .replace("{valid}", String(result.validas))
            .replace("{total}", String(result.evaluadas))}
        </p>
        <ol className="space-y-1.5">
          {result.resultados.map((cell) => (
            <li key={cell.sitio_id} className="rounded-xl bg-white/5 px-2.5 py-2">
              <div className="flex items-baseline justify-between gap-3">
                <span className="font-mono text-white">
                  {cell.posicion}. {cell.codigo ?? cell.nombre}
                </span>
                <span className="font-mono text-base text-white">{pct(cell.similitud)}</span>
              </div>
              {cell.limites && (
                <p className="text-white/55">
                  {cells.cell} {bounds(cell.limites)}
                </p>
              )}
              <p className="text-white/75">
                {Object.entries(cell.por_grupo)
                  .map(([key, value]) => `${group(key)} ${pct(value)}`)
                  .join(" · ")}
                {" · "}
                {copy.coverage} {pct(cell.cobertura)}
              </p>
              <p className="text-white/60" title={cells.stabilityHint}>
                {cells.stability} {pct(cell.estabilidad)} · {cells.range}{" "}
                {pct(cell.similitud_min)}–{pct(cell.similitud_max)}
              </p>
            </li>
          ))}
        </ol>
        <p className="text-white/50">{cells.weights.replace("{weights}", weights)}</p>
      </>
    );
  }

  return (
    <section aria-label={cells.title} aria-live="polite" className="space-y-2">
      <h4 className="font-medium text-[#ffbd80]">{cells.title}</h4>
      {body}
    </section>
  );
}
