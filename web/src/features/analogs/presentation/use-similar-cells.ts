"use client";

import { useEffect, useState } from "react";
import type { AnalogDestination } from "@/features/analogs/infrastructure/analogs-ranking";
import {
  requestSimilarCells,
  type SimilarCellsResponse,
} from "@/features/analogs/infrastructure/similar-cells";

export type SimilarCellsState = SimilarCellsResponse | "error" | null;

/** Busca las celdas parecidas al sitio; devuelve null mientras carga o cambia el sitio o destino. */
export function useSimilarCells(
  siteId: number,
  destination: AnalogDestination,
  errorMessage: string,
) {
  const [attempt, setAttempt] = useState(0);
  const [loaded, setLoaded] = useState<{
    siteId: number;
    destination: AnalogDestination;
    attempt: number;
    value: SimilarCellsResponse | "error";
  } | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void requestSimilarCells(siteId, destination, controller.signal, errorMessage).then(
      (response) => {
        if (controller.signal.aborted) return;
        setLoaded({ siteId, destination, attempt, value: response.ok ? response.data : "error" });
      },
    );
    return () => controller.abort();
  }, [siteId, destination, attempt, errorMessage]);

  const result: SimilarCellsState =
    loaded &&
    loaded.siteId === siteId &&
    loaded.destination === destination &&
    loaded.attempt === attempt
      ? loaded.value
      : null;

  return { result, retry: () => setAttempt((previous) => previous + 1) };
}
