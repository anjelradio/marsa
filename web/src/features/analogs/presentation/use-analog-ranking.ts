"use client";

import { useEffect, useState } from "react";
import {
  requestAnalogRanking,
  type AnalogDestination,
  type AnalogRankingItem,
} from "@/features/analogs/infrastructure/analogs-ranking";

export type AnalogRankingState = AnalogRankingItem[] | "error" | null;

/** Pide el ranking del destino; devuelve null mientras carga o cambia de destino. */
export function useAnalogRanking(destination: AnalogDestination, errorMessage: string) {
  const [attempt, setAttempt] = useState(0);
  const [loaded, setLoaded] = useState<{
    destination: AnalogDestination;
    attempt: number;
    value: AnalogRankingItem[] | "error";
  } | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void requestAnalogRanking(destination, controller.signal, errorMessage).then((response) => {
      if (controller.signal.aborted) return;
      setLoaded({ destination, attempt, value: response.ok ? response.data : "error" });
    });
    return () => controller.abort();
  }, [destination, attempt, errorMessage]);

  const result: AnalogRankingState =
    loaded && loaded.destination === destination && loaded.attempt === attempt
      ? loaded.value
      : null;

  return { result, retry: () => setAttempt((previous) => previous + 1) };
}
