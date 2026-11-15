"""Schemas Pydantic para los endpoints de geología, rocas, minerales y análogos planetarios."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MineralMuestra(BaseModel):
    nombre: str
    formula: Optional[str] = None
    abundancia: float
    unidad: str = "% peso (wt%)"


class MuestraLaboratorio(BaseModel):
    muestra_id: str
    cuerpo: str
    ubicacion: str
    coordenadas: Optional[Dict[str, float]] = None
    tipo_material: str
    minerales: List[MineralMuestra] = Field(default_factory=list)
    fase_amorfa_pct: Optional[float] = 0.0
    instrumento: str
    fuente_pds: str


class MetadatosFuente(BaseModel):
    fuente: str
    licencia: str
    resolucion_o_escala: str
    nota_metodologica: str


class UnidadMacrostrat(BaseModel):
    map_id: Optional[int] = None
    source_id: Optional[int] = None
    nombre: Optional[str] = None
    litologia: List[str] = Field(default_factory=list)
    descripcion: Optional[str] = None
    edad_superior_Ma: Optional[float] = None
    edad_inferior_Ma: Optional[float] = None


class RespuestaMacrostratPuntual(BaseModel):
    coordenadas: Dict[str, float]
    total_unidades: int
    unidades: List[UnidadMacrostrat] = Field(default_factory=list)
    atribucion: MetadatosFuente


class CeldaAnalogico(BaseModel):
    celda_id: str
    region_referencia: str
    limites: Optional[Dict[str, float]] = None
    categorias_area_pct: Dict[str, float] = Field(default_factory=dict)
    minerales_detectados: List[str] = Field(default_factory=list)
    rocas_principales: List[str] = Field(default_factory=list)
    unidad_geologica: Optional[str] = None
    cobertura_pct: Optional[float] = 100.0
    indice_similitud_algoritmo_pct: Optional[float] = None
    nota_similitud: Optional[str] = None


class RespuestaComparacion(BaseModel):
    cuerpo_origen: str = "Tierra"
    cuerpo_destino: str = "Marte"
    coordenadas_origen: Dict[str, float]
    celda_origen_id: str
    geologia_puntual_macrostrat: List[UnidadMacrostrat] = Field(default_factory=list)
    distribucion_litologica_celda: Dict[str, float] = Field(default_factory=dict)
    celda_analoga_mas_similar: Optional[CeldaAnalogico] = None
    muestras_minerales_relacionadas: List[MuestraLaboratorio] = Field(default_factory=list)
    atribuciones: List[MetadatosFuente] = Field(default_factory=list)


class LimitesCelda(BaseModel):
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


class CoordenadasCelda(BaseModel):
    lat: float
    lng: float


class ComparacionLitologica(BaseModel):
    categoria: str
    marte_pct: float
    tierra_pct: float


class CandidatoTerrestre(BaseModel):
    celda_id: str
    region_referencia: str
    centro: CoordenadasCelda
    limites: LimitesCelda
    similitud_pct: float
    cobertura_pct: Optional[float] = None
    rocas_principales: List[str] = Field(default_factory=list)
    comparacion_litologica: List[ComparacionLitologica] = Field(default_factory=list)


class RankingTerrestrePunto(BaseModel):
    regiones_evaluadas: int = 0
    candidatos: List[CandidatoTerrestre] = Field(default_factory=list)


class RespuestaGeologiaPunto(BaseModel):
    cuerpo: str
    coordenadas: Dict[str, float]
    celda_id: str
    region_nombre: str
    unidad_geologica: str
    tipo_terreno: str
    rocas_predominantes: List[str] = Field(default_factory=list)
    minerales_principales: List[str] = Field(default_factory=list)
    distribucion_litologica: Dict[str, float] = Field(default_factory=dict)
    unidades_macrostrat: List[UnidadMacrostrat] = Field(default_factory=list)
    muestras_laboratorio_in_situ: List[MuestraLaboratorio] = Field(default_factory=list)
    cobertura_geologica: Optional[bool] = None
    ranking_terrestre: Optional[RankingTerrestrePunto] = None
    mejor_analogo: Optional[Dict[str, Any]] = None
    atribuciones: List[MetadatosFuente] = Field(default_factory=list)
