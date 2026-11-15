import { z } from "zod";
import { apiRequestData } from "@/features/shared/infrastructure/http/api-client";
import {
  Sitio,
  SitioSchema,
  CreateSitioInput,
  Medicion,
  MedicionSchema,
  ExtraerSatelitalInput,
  CuerpoCeleste,
  CuerpoCelesteSchema,
  Analogia,
  AnalogiaSchema,
} from "../domain/schemas";
import { ApiResult } from "@/features/shared/domain/types/api-results";

export class SatelitalService {
  /**
   * Obtiene la lista de cuerpos celestes (Tierra, Marte, Luna).
   */
  static async getCuerposCelestes(): Promise<ApiResult<CuerpoCeleste[]>> {
    return apiRequestData({
      url: "/api/v1/cuerpos-celestes/",
      method: "GET",
      withAuth: false,
      responseSchema: z.array(CuerpoCelesteSchema),
      fallbackMessage: "No se pudieron obtener los cuerpos celestes",
      mapData: (data) => data,
    });
  }

  /**
   * Obtiene los sitios registrados, opcionalmente filtrados por cuerpo celeste.
   */
  static async getSitios(cuerpoId?: number): Promise<ApiResult<Sitio[]>> {
    const query = cuerpoId ? `?cuerpo_id=${cuerpoId}` : "";
    return apiRequestData({
      url: `/api/v1/sitios/${query}`,
      method: "GET",
      withAuth: false,
      responseSchema: z.array(SitioSchema),
      fallbackMessage: "No se pudieron obtener los sitios",
      mapData: (data) => data,
    });
  }

  /**
   * Obtiene un sitio específico por su ID.
   */
  static async getSitioById(sitioId: number): Promise<ApiResult<Sitio>> {
    return apiRequestData({
      url: `/api/v1/sitios/${sitioId}`,
      method: "GET",
      withAuth: false,
      responseSchema: SitioSchema,
      fallbackMessage: "No se pudo obtener el sitio",
      mapData: (data) => data,
    });
  }

  /**
   * Registra un nuevo sitio con su geometría (punto o polígono GeoJSON).
   */
  static async createSitio(input: CreateSitioInput): Promise<ApiResult<Sitio>> {
    return apiRequestData({
      url: "/api/v1/sitios/",
      method: "POST",
      withAuth: false,
      body: input,
      responseSchema: SitioSchema,
      fallbackMessage: "No se pudo crear el sitio",
      mapData: (data) => data,
    });
  }

  /**
   * Obtiene las mediciones registradas para un sitio (temperatura, nubosidad, etc.).
   */
  static async getMediciones(sitioId?: number): Promise<ApiResult<Medicion[]>> {
    const query = sitioId ? `?sitio_id=${sitioId}` : "";
    return apiRequestData({
      url: `/api/v1/mediciones/${query}`,
      method: "GET",
      withAuth: false,
      responseSchema: z.array(MedicionSchema),
      fallbackMessage: "No se pudieron obtener las mediciones",
      mapData: (data) => data,
    });
  }

  /**
   * Dispara la extracción satelital en el backend (Copernicus para Tierra o USGS para Marte)
   * y guarda las mediciones resultantes en la base de datos.
   */
  static async extraerMedicionesSatelitales(
    input: ExtraerSatelitalInput
  ): Promise<ApiResult<Medicion[]>> {
    return apiRequestData({
      url: "/api/v1/mediciones/extraer-satelital",
      method: "POST",
      withAuth: false,
      body: input,
      responseSchema: z.array(MedicionSchema),
      fallbackMessage: "Error al extraer datos satelitales para el sitio",
      mapData: (data) => data,
    });
  }

  /**
   * Lista o calcula analogías entre la Tierra y un sitio de destino.
   */
  static async getAnalogias(): Promise<ApiResult<Analogia[]>> {
    return apiRequestData({
      url: "/api/v1/analogias/",
      method: "GET",
      withAuth: false,
      responseSchema: z.array(AnalogiaSchema),
      fallbackMessage: "No se pudieron obtener las analogías",
      mapData: (data) => data,
    });
  }
}

