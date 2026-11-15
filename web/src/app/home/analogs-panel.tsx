"use client";

import { AlertTriangle, ChevronDown, Globe2, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/i18n/context";
import type { AnalogDestination } from "@/features/analogs/infrastructure/analogs-ranking";
import type { AnalogRankingState } from "@/features/analogs/presentation/use-analog-ranking";

const DESTINATIONS: AnalogDestination[] = ["marte", "luna"];

export function AnalogsPanel({
  destination,
  onDestinationChange,
  result,
  onRetry,
  openId,
  onOpenChange,
}: {
  destination: AnalogDestination;
  onDestinationChange: (destination: AnalogDestination) => void;
  result: AnalogRankingState;
  onRetry: () => void;
  openId: number | null;
  onOpenChange: (id: number | null) => void;
}) {
  const { dict, locale } = useTranslation();
  const copy = dict.analogs;

  const pct = (value: number) => `${Math.round(value * 100)}%`;
  const name = (key: string) => (copy.features as Record<string, string>)[key] ?? key;
  const list = (value: string) =>
    value ? value.split(", ").map(name).join(", ") : copy.none;
  const number = (value: number) => value.toLocaleString(locale, { maximumFractionDigits: 2 });

  return (
    <section
      aria-labelledby="analogs-title"
      className="relative z-30 mx-auto w-full max-w-[1100px] px-4 pb-16 pt-8 sm:px-7"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 id="analogs-title" className="flex items-center gap-2 font-headline text-2xl font-semibold text-white">
            <Globe2 aria-hidden="true" className="size-5 text-[#ffab57]" />
            {copy.title}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-white/70">{copy.subtitle}</p>
        </div>
        <div role="group" aria-label={copy.selectDestination} className="flex gap-1 rounded-full border border-white/15 bg-white/5 p-1">
          {DESTINATIONS.map((value) => (
            <Button
              key={value}
              type="button"
              size="sm"
              variant="ghost"
              aria-pressed={destination === value}
              onClick={() => {
                onOpenChange(null);
                onDestinationChange(value);
              }}
              className={cn(
                "rounded-full px-4 text-white/80 hover:bg-white/10 hover:text-white",
                destination === value && "bg-[#ffab57] text-black hover:bg-[#ffab57] hover:text-black",
              )}
            >
              {copy.destinations[value]}
            </Button>
          ))}
        </div>
      </div>

      <div aria-live="polite" className="mt-5">
        {result === null && <p className="text-sm text-white/75">{copy.loading}</p>}
        {result === "error" && (
          <div className="space-y-2">
            <p className="text-sm text-white/85">{copy.error}</p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="rounded-full border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white"
              onClick={onRetry}
            >
              {copy.retry}
            </Button>
          </div>
        )}
        {result && result !== "error" && (
          <ol className="space-y-2.5">
            {result.map((item) => {
              const isOpen = openId === item.sitio_tierra_id;
              return (
                <li key={item.sitio_tierra_id}>
                  <Card className="gap-0 rounded-3xl ring-0 dark:ring-0 bg-white/5 p-0 text-white shadow-none backdrop-blur-xl">
                    <button
                      type="button"
                      aria-expanded={isOpen}
                      onClick={() => onOpenChange(isOpen ? null : item.sitio_tierra_id)}
                      className="flex w-full items-center gap-3 rounded-3xl px-4 py-3 text-left"
                    >
                      <span className="grid size-8 shrink-0 place-items-center rounded-full bg-[#ffab57]/20 font-mono text-sm text-[#ffbd80]">
                        {item.posicion}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="flex items-center gap-1.5 truncate text-sm font-medium">
                          <MapPin aria-hidden="true" className="size-3.5 shrink-0 text-[#ffab57]" />
                          {item.sitio_tierra}
                        </span>
                        <span className="block truncate text-xs text-white/60">
                          {item.tipo} · {copy.bestMatch}: {item.sitio_destino}
                        </span>
                        <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-white/10">
                          <span
                            className="block h-full rounded-full bg-[#ffab57]"
                            style={{ width: pct(item.similitud) }}
                          />
                        </span>
                      </span>
                      <span className="shrink-0 text-right">
                        <span className="block font-mono text-lg">{pct(item.similitud)}</span>
                        <span className="block text-[0.65rem] text-white/55">
                          {copy.coverage} {pct(item.cobertura)}
                        </span>
                      </span>
                      <ChevronDown
                        aria-hidden="true"
                        className={cn("size-4 shrink-0 text-white/60 transition-transform", isOpen && "rotate-180")}
                      />
                    </button>

                    {isOpen && (
                      <div className="space-y-3 border-t border-white/10 px-4 py-3 text-xs">
                        {(copy.uses as Record<string, string>)[item.sitio_tierra] && (
                          <p className="rounded-xl bg-[#ffab57]/10 px-2.5 py-2 leading-relaxed text-white/85">
                            <span className="text-[#ffbd80]">{copy.usesTitle}:</span>{" "}
                            {(copy.uses as Record<string, string>)[item.sitio_tierra]}
                          </p>
                        )}
                        <p>
                          <span className="text-[#9be29b]">{copy.matches}:</span>{" "}
                          <span className="text-white/80">{list(item.coincide)}</span>
                        </p>
                        <p>
                          <span className="text-[#ff9b8a]">{copy.differs}:</span>{" "}
                          <span className="text-white/80">{list(item.difiere)}</span>
                        </p>
                        <dl className="space-y-1">
                          {item.detalle.map((d) => (
                            <div key={d.caracteristica} className="grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1 rounded-xl bg-white/5 px-2.5 py-2 sm:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_5rem]">
                              <dt className="text-white/80">{name(d.caracteristica)}</dt>
                              <dd className="text-right font-mono text-white sm:text-left">
                                {copy.earth} {number(d.valor_tierra)} · {copy.target} {number(d.valor_destino)}
                                {d.unidad && d.unidad !== "tau" ? ` ${d.unidad}` : ""}
                              </dd>
                              <dd className="col-span-2 font-mono text-white/70 sm:col-span-1 sm:text-right">
                                {pct(d.similitud)}
                              </dd>
                            </div>
                          ))}
                        </dl>
                        <p className="text-white/50">
                          {copy.method}: {item.metodo}
                        </p>
                      </div>
                    )}
                  </Card>
                </li>
              );
            })}
          </ol>
        )}
      </div>

      <div className="mt-6 rounded-3xl border border-[#ffab57]/25 bg-[#ffab57]/5 p-4 text-sm text-white/80">
        <h3 className="flex items-center gap-2 font-medium text-[#ffbd80]">
          <AlertTriangle aria-hidden="true" className="size-4" />
          {copy.limitsTitle}
        </h3>
        <p className="mt-1.5 leading-relaxed">{copy.limitsBody}</p>
        <p className="mt-2 text-xs text-white/55">{copy.dataNote}</p>
      </div>
    </section>
  );
}
