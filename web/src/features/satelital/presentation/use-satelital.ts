"use client";

import { useEffect, useState, useTransition } from "react";
import { SatelitalService } from "../infrastructure/satelital-service";
import { Sitio, Medicion, CuerpoCeleste } from "../domain/schemas";

export function useSatelital(cuerpoId?: number) {
  const [cuerpos, setCuerpos] = useState<CuerpoCeleste[]>([]);
  const [sitios, setSitios] = useState<Sitio[]>([]);
  const [selectedSitio, setSelectedSitio] = useState<Sitio | null>(null);
  const [mediciones, setMediciones] = useState<Medicion[]>([]);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  // Cargar Cuerpos Celestes
  useEffect(() => {
    SatelitalService.getCuerposCelestes().then((res) => {
      if (res.ok) {
        setCuerpos(res.data);
      }
    });
  }, []);

  // Cargar Sitios según cuerpo celeste seleccionado
  const fetchSitios = (id?: number) => {
    startTransition(async () => {
      setError(null);
      const res = await SatelitalService.getSitios(id);
      if (res.ok) {
        setSitios(res.data);
      } else {
        setError(res.errors[0] || "Error al cargar los sitios");
      }
    });
  };

  useEffect(() => {
    fetchSitios(cuerpoId);
  }, [cuerpoId]);

  // Cargar Mediciones del sitio seleccionado
  const selectSitio = (sitio: Sitio) => {
    setSelectedSitio(sitio);
    startTransition(async () => {
      setError(null);
      const res = await SatelitalService.getMediciones(sitio.id);
      if (res.ok) {
        setMediciones(res.data);
      } else {
        setError(res.errors[0] || "Error al cargar las mediciones");
      }
    });
  };

  // Disparar extracción satelital en vivo
  const extraerDatosSatelitales = async (sitioId: number, datetimeRange?: string) => {
    startTransition(async () => {
      setError(null);
      const res = await SatelitalService.extraerMedicionesSatelitales({
        sitio_id: sitioId,
        datetime_range: datetimeRange,
      });

      if (res.ok) {
        setMediciones(res.data);
      } else {
        setError(res.errors[0] || "Error durante la extracción satelital");
      }
    });
  };

  return {
    cuerpos,
    sitios,
    selectedSitio,
    mediciones,
    isPending,
    error,
    selectSitio,
    fetchSitios,
    extraerDatosSatelitales,
  };
}
