"""Servicio de geología planetaria, consulta en tiempo real a Macrostrat y comparación litológica/mineralógica."""

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from app.modules.analogia.infrastructure.api.schemas.geology_schemas import (
    CandidatoTerrestre,
    CeldaAnalogico,
    ComparacionLitologica,
    CoordenadasCelda,
    LimitesCelda,
    MetadatosFuente,
    MuestraLaboratorio,
    RankingTerrestrePunto,
    RespuestaComparacion,
    RespuestaGeologiaPunto,
    UnidadMacrostrat,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


def cargar_json_seguro(nombre_archivo: str, respaldo: Any) -> Any:
    ruta = DATA_DIR / nombre_archivo
    if ruta.exists():
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Error leyendo %s: %s", nombre_archivo, exc)
    return respaldo


def obtener_id_celda_10x10(lat: float, lng: float, prefijo: str = "T") -> str:
    """Calcula el identificador estándar de celda 10° x 10° a partir de lat/lng."""
    lat_base = math.floor(lat / 10.0) * 10
    lon_base = math.floor(lng / 10.0) * 10
    hem_lat = "N" if lat_base >= 0 else "S"
    hem_lon = "E" if lon_base >= 0 else "W"
    return f"{prefijo}_{hem_lat}{abs(lat_base):02d}_{hem_lon}{abs(lon_base):03d}"


def calcular_similitud_coseno(cat_origen: Dict[str, float], cat_destino: Dict[str, float]) -> float:
    """
    Calcula el índice de similitud (0 a 100%) entre las proporciones de área
    geológica o litológica de dos celdas planetarias.
    Mapea sinónimos comunes (por ejemplo, basalto_mar <-> volcanico, anortosita <-> sedimentario/magmático).
    """
    # Mapeo semántico de categorías entre cuerpos
    mapa_alias = {
        "basalto_mar": "volcanico",
        "anortosita_tierras_altas": "plutonico",
        "brecha_tierras_altas": "sedimentario",
        "brecha_impacto": "sedimentario",
        "hielo_volatiles_trampa": "evaporitas",
    }
    
    norm_origen: Dict[str, float] = {}
    for k, v in cat_origen.items():
        clave = mapa_alias.get(k, k)
        norm_origen[clave] = norm_origen.get(clave, 0.0) + v
        
    norm_destino: Dict[str, float] = {}
    for k, v in cat_destino.items():
        clave = mapa_alias.get(k, k)
        norm_destino[clave] = norm_destino.get(clave, 0.0) + v

    todas_categorias = set(norm_origen.keys()).union(set(norm_destino.keys()))
    producto_punto = sum(norm_origen.get(c, 0.0) * norm_destino.get(c, 0.0) for c in todas_categorias)
    norma_a = math.sqrt(sum(v ** 2 for v in norm_origen.values()))
    norma_b = math.sqrt(sum(v ** 2 for v in norm_destino.values()))

    if norma_a == 0 or norma_b == 0:
        return 0.0
    return round((producto_punto / (norma_a * norma_b)) * 100.0, 2)


async def consultar_macrostrat(lat: float, lng: float, scale: Optional[str] = None) -> List[UnidadMacrostrat]:
    """
    Consulta la API pública de Macrostrat en tiempo real.
    Si la API no responde o hay bloqueo de red, proporciona una respuesta limpia sin fallar.
    """
    url = "https://macrostrat.org/api/v2/geologic_units/map"
    params = {"lat": lat, "lng": lng, "format": "json"}
    if scale in {"small", "medium", "large"}:
        params["scale"] = scale

    headers = {
        "User-Agent": "naseando/1.0 (Planetary Analogs Explorer; contact: naseando@astroplus.space)",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                payload = resp.json()
                unidades_raw = payload.get("success", {}).get("data", [])
                unidades_limpias = []
                for u in unidades_raw:
                    lith_raw = u.get("lith", [])
                    lith_list = lith_raw if isinstance(lith_raw, list) else [str(lith_raw)] if lith_raw else []
                    unidades_limpias.append(
                        UnidadMacrostrat(
                            map_id=u.get("map_id"),
                            source_id=u.get("source_id"),
                            nombre=u.get("name") or "Unidad geológica regional sin nombre específico",
                            litologia=lith_list,
                            descripcion=u.get("descrip"),
                            edad_superior_Ma=u.get("t_age"),
                            edad_inferior_Ma=u.get("b_age"),
                        )
                    )
                return unidades_limpias
    except Exception as exc:
        logger.info("Macrostrat live query fallback para lat=%.2f, lng=%.2f: %s", lat, lng, exc)

    return []


def buscar_celda_mas_cercana(lat: float, lng: float, celdas_dict_o_lista: Any) -> Dict[str, Any]:
    """Busca la celda más cercana en el conjunto por distancia euclidiana o identificador."""
    if isinstance(celdas_dict_o_lista, dict):
        celda_id = obtener_id_celda_10x10(lat, lng, "T")
        if celda_id in celdas_dict_o_lista:
            res = dict(celdas_dict_o_lista[celda_id])
            res["celda_id"] = celda_id
            return res
        # Si no está exacta, buscar la más cercana
        mejor = None
        menor_dist = float("inf")
        for cid, data in celdas_dict_o_lista.items():
            lim = data.get("limites", {})
            c_lat = (lim.get("lat_min", 0) + lim.get("lat_max", 0)) / 2.0
            c_lon = (lim.get("lon_min", 0) + lim.get("lon_max", 0)) / 2.0
            dist = math.hypot(lat - c_lat, lng - c_lon)
            if dist < menor_dist:
                menor_dist = dist
                mejor = {**data, "celda_id": cid}
        return mejor or {
            "celda_id": celda_id,
            "categorias_area_pct": {"volcanico": 45.0, "sedimentario": 40.0, "evaporitas": 15.0},
            "minerales_detectados": ["Cuarzo", "Feldespato", "Piroxeno"],
            "rocas_principales": ["Basalto", "Arenisca"],
            "cobertura_pct": 90.0,
        }
    elif isinstance(celdas_dict_o_lista, list):
        mejor = None
        menor_dist = float("inf")
        for item in celdas_dict_o_lista:
            lim = item.get("limites", {})
            c_lat = (lim.get("lat_min", 0) + lim.get("lat_max", 0)) / 2.0
            c_lon = (lim.get("lon_min", 0) + lim.get("lon_max", 0)) / 2.0
            dist = math.hypot(lat - c_lat, lng - c_lon)
            if dist < menor_dist:
                menor_dist = dist
                mejor = item
        return mejor or celdas_dict_o_lista[0]
    return {}


async def comparar_analogo_tierra(
    lat: float,
    lng: float,
    destino: str = "marte",
) -> RespuestaComparacion:
    """
    Realiza la comparación en tiempo real entre un punto terrestre y Marte o la Luna:
    1. Consulta Macrostrat para obtener unidades geológicas puntuales en vivo.
    2. Cruza con la celda 10°x10° de la Tierra (GLiM).
    3. Calcula similitud coseno contra celdas de Marte (USGS SIM 3292 / OMEGA) o Luna (USGS Lunar / Kaguya).
    4. Adjunta fichas de muestras in-situ de referencia (CheMin para Marte, Apolo para Luna).
    """
    destino_norm = destino.lower().strip()
    es_luna = "luna" in destino_norm or "moon" in destino_norm

    unidades_macrostrat = await consultar_macrostrat(lat, lng)

    celdas_tierra = cargar_json_seguro("celdas_glim_10x10.json", {})
    datos_celda_tierra = buscar_celda_mas_cercana(lat, lng, celdas_tierra)
    cat_tierra = datos_celda_tierra.get("categorias_area_pct", {"volcanico": 50.0, "sedimentario": 50.0})

    if es_luna:
        celdas_destino = cargar_json_seguro("celdas_luna_10x10.json", [])
        cuerpo_nombre = "Luna"
        fuente_mapa = "USGS Unified Geologic Map of the Moon (Fortezzo et al.)"
        licencia_mapa = "Public Domain / USGS"
    else:
        celdas_destino = cargar_json_seguro("celdas_marte_10x10.json", [])
        cuerpo_nombre = "Marte"
        fuente_mapa = "USGS SIM 3292 Geologic Map of Mars (Tanaka et al.)"
        licencia_mapa = "Public Domain / USGS"

    mejor_celda: Optional[CeldaAnalogico] = None
    mayor_similitud = -1.0

    for cd in celdas_destino:
        cats_dest = cd.get("categorias_area_pct", {})
        score = calcular_similitud_coseno(cat_tierra, cats_dest)
        if score > mayor_similitud:
            mayor_similitud = score
            min_detectados = cd.get("minerales_omega_detectados") or cd.get("minerales_kaguya_detectados") or []
            mejor_celda = CeldaAnalogico(
                celda_id=cd["celda_id"],
                region_referencia=cd["region_referencia"],
                limites=cd.get("limites"),
                categorias_area_pct=cats_dest,
                minerales_detectados=min_detectados,
                rocas_principales=cd.get("rocas_principales", []),
                unidad_geologica=cd.get("unidad_geologica_usgs"),
                cobertura_pct=cd.get("cobertura_pct", 100.0),
                indice_similitud_algoritmo_pct=score,
                nota_similitud=f"Calculado por similitud coseno basada en proporciones litológicas 10°x10° con {cuerpo_nombre}.",
            )

    # Filtrar muestras minerales correspondientes
    todas_muestras = cargar_json_seguro("muestras_minerales.json", [])
    muestras_filtradas = [
        MuestraLaboratorio(**m)
        for m in todas_muestras
        if m.get("cuerpo", "").lower() == cuerpo_nombre.lower()
    ]

    atribuciones = [
        MetadatosFuente(
            fuente="Macrostrat API (macrostrat.org)",
            licencia="CC BY 4.0",
            resolucion_o_escala="Variable / Continental a Local (1:250k - 1:5M)",
            nota_metodologica="Consulta en tiempo real al punto geográfico seleccionado en el mapa.",
        ),
        MetadatosFuente(
            fuente="GLiM (Global Lithological Map - Hartmann & Moosdorf 2012)",
            licencia="CC BY 3.0",
            resolucion_o_escala="0.5° agregada a celdas globales 10° x 10°",
            nota_metodologica="Distribución porcentual de área de litologías superficiales terrestres.",
        ),
        MetadatosFuente(
            fuente=fuente_mapa,
            licencia=licencia_mapa,
            resolucion_o_escala="1:20.000.000 (SIM 3292 / Lunar Map)",
            nota_metodologica="Clasificación de unidades estratigráficas y litológicas planetarias.",
        ),
        MetadatosFuente(
            fuente="NASA Planetary Data System (PDS) - Curiosity CheMin / Apollo Sample Catalog",
            licencia="Public Domain / NASA",
            resolucion_o_escala="Muestras in-situ directas de laboratorio (difracción de rayos X y espectrometría)",
            nota_metodologica="Composición cuantitativa en porcentaje de peso (% wt) de minerales cristalinos y amorfos.",
        ),
    ]

    return RespuestaComparacion(
        cuerpo_origen="Tierra",
        cuerpo_destino=cuerpo_nombre,
        coordenadas_origen={"lat": lat, "lng": lng},
        celda_origen_id=datos_celda_tierra.get("celda_id", obtener_id_celda_10x10(lat, lng)),
        geologia_puntual_macrostrat=unidades_macrostrat,
        distribucion_litologica_celda=cat_tierra,
        celda_analoga_mas_similar=mejor_celda,
        muestras_minerales_relacionadas=muestras_filtradas,
        atribuciones=atribuciones,
    )


def _contiene_coordenadas(limites: LimitesCelda, lat: float, lng: float) -> bool:
    # El antimeridiano tiene dos representaciones válidas en los catálogos.
    lng = -180.0 if lng == 180.0 else lng
    en_latitud = limites.lat_min <= lat < limites.lat_max or lat == limites.lat_max == 90
    en_longitud = limites.lon_min <= lng < limites.lon_max or (
        lng == -180.0 and limites.lon_max == 180.0
    )
    return en_latitud and en_longitud


def _ranking_terrestre(categorias_marte: Dict[str, float]) -> RankingTerrestrePunto:
    if not any(v > 0 for v in categorias_marte.values()):
        return RankingTerrestrePunto()

    evaluadas = 0
    candidatos = []
    celdas_tierra = cargar_json_seguro("celdas_glim_10x10.json", {})
    for celda_id, datos in celdas_tierra.items():
        limites = LimitesCelda(**datos["limites"])
        categorias_tierra = datos["categorias_area_pct"]
        if not any(v > 0 for v in categorias_tierra.values()):
            continue

        evaluadas += 1
        similitud = calcular_similitud_coseno(categorias_marte, categorias_tierra)
        if similitud <= 0:
            continue

        categorias = categorias_marte.keys() | categorias_tierra.keys()
        comparacion = [
            ComparacionLitologica(
                categoria=categoria,
                marte_pct=categorias_marte.get(categoria, 0.0),
                tierra_pct=categorias_tierra.get(categoria, 0.0),
            )
            for categoria in sorted(categorias)
            if categorias_marte.get(categoria, 0.0) > 0 or categorias_tierra.get(categoria, 0.0) > 0
        ]
        candidatos.append(CandidatoTerrestre(
            celda_id=celda_id,
            region_referencia=datos["nombre_region"],
            centro=CoordenadasCelda(
                lat=(limites.lat_min + limites.lat_max) / 2,
                lng=(limites.lon_min + limites.lon_max) / 2,
            ),
            limites=limites,
            similitud_pct=similitud,
            cobertura_pct=datos.get("cobertura_pct"),
            rocas_principales=datos.get("litologias_dominantes", []),
            comparacion_litologica=comparacion,
        ))

    candidatos.sort(key=lambda candidato: (-candidato.similitud_pct, candidato.celda_id))
    return RankingTerrestrePunto(regiones_evaluadas=evaluadas, candidatos=candidatos[:3])


async def analizar_geologia_punto(
    cuerpo: str,
    lat: float,
    lng: float,
    destino: Optional[str] = None,
) -> RespuestaGeologiaPunto:
    """
    Analiza en tiempo real las rocas y minerales presentes en cualquier coordenada
    de la Tierra, Marte o la Luna, con analogías geológicas cruzadas.
    """
    cuerpo_norm = cuerpo.lower().strip()
    muestras_todas = cargar_json_seguro("muestras_minerales.json", [])

    if "tierra" in cuerpo_norm or "earth" in cuerpo_norm:
        dest = destino or "Marte"
        comp = await comparar_analogo_tierra(lat, lng, dest)
        celdas_tierra = cargar_json_seguro("celdas_glim_10x10.json", {})
        info_tierra = buscar_celda_mas_cercana(lat, lng, celdas_tierra)

        rocas = info_tierra.get("rocas_principales", ["Basalto", "Andesita", "Arenisca", "Granito"])
        minerales = info_tierra.get("minerales_detectados", ["Cuarzo", "Plagioclasa", "Feldespato potásico", "Piroxeno"])
        unidad_geo = "Unidad superficial Terrestre (GLiM)"
        if comp.geologia_puntual_macrostrat:
            u0 = comp.geologia_puntual_macrostrat[0]
            if u0.nombre:
                unidad_geo = u0.nombre
            if u0.litologia:
                rocas = u0.litologia + [r for r in rocas if r not in u0.litologia]

        return RespuestaGeologiaPunto(
            cuerpo="Tierra",
            coordenadas={"lat": lat, "lng": lng},
            celda_id=comp.celda_origen_id,
            region_nombre=info_tierra.get("region_referencia", f"Coordenadas terrestres ({lat:.2f}°, {lng:.2f}°)"),
            unidad_geologica=unidad_geo,
            tipo_terreno="Terreno Mixto Continental / Volcánico / Sedimentario",
            rocas_predominantes=rocas,
            minerales_principales=minerales,
            distribucion_litologica=comp.distribucion_litologica_celda,
            unidades_macrostrat=comp.geologia_puntual_macrostrat,
            muestras_laboratorio_in_situ=[],
            mejor_analogo={
                "cuerpo_destino": comp.cuerpo_destino,
                "celda_analoga": comp.celda_analoga_mas_similar.model_dump() if comp.celda_analoga_mas_similar else None,
            },
            atribuciones=comp.atribuciones,
        )

    elif "marte" in cuerpo_norm or "mars" in cuerpo_norm:
        celdas_marte = cargar_json_seguro("celdas_marte_10x10.json", [])
        cm = next((
            celda for celda in celdas_marte
            if _contiene_coordenadas(LimitesCelda(**celda["limites"]), lat, lng)
        ), None)
        if cm is None:
            return RespuestaGeologiaPunto(
                cuerpo="Marte",
                coordenadas={"lat": lat, "lng": lng},
                celda_id=obtener_id_celda_10x10(lat, lng, "M"),
                region_nombre="Marte",
                unidad_geologica="",
                tipo_terreno="",
                cobertura_geologica=False,
                ranking_terrestre=RankingTerrestrePunto(),
            )

        limites_marte = LimitesCelda(**cm["limites"])
        muestras_marte = [
            MuestraLaboratorio(**m) for m in muestras_todas
            if m.get("cuerpo", "").lower() == "marte"
            and (coordenadas := m.get("coordenadas"))
            and _contiene_coordenadas(limites_marte, coordenadas["lat"], coordenadas["lon"])
        ]

        ranking = _ranking_terrestre(cm.get("categorias_area_pct", {}))
        mejor_tierra = ranking.candidatos[0] if ranking.candidatos else None

        atribuciones = [
            MetadatosFuente(
                fuente="USGS SIM 3292 Geologic Map of Mars (Tanaka et al. 2014)",
                licencia="Public Domain / USGS",
                resolucion_o_escala="1:20.000.000 global",
                nota_metodologica="Unidades estratigráficas de las eras Noeica, Hespérica y Amazónica.",
            ),
            MetadatosFuente(
                fuente="ESA Mars Express OMEGA / NASA CRISM Spectral Mineralogy",
                licencia="ESA / NASA Open Data",
                resolucion_o_escala="1 a 5 km por píxel espectral",
                nota_metodologica="Detección de absorciones de infrarrojo cercano para minerales hidratados, olivino y piroxeno.",
            ),
            MetadatosFuente(
                fuente="NASA MSL Curiosity CheMin Instrument (PDS Geosciences)",
                licencia="Public Domain / NASA",
                resolucion_o_escala="Difracción de Rayos X (XRD) in-situ en el Cráter Gale",
                nota_metodologica="Porcentajes cuantitativos de peso (% wt) de cada fase mineral.",
            ),
            MetadatosFuente(
                fuente="GLiM (Global Lithological Map - Hartmann & Moosdorf 2012)",
                licencia="CC BY 3.0",
                resolucion_o_escala="Celdas de 10° x 10° del catálogo terrestre",
                nota_metodologica="El ranking compara las proporciones de área por categoría litológica.",
            ),
        ]

        return RespuestaGeologiaPunto(
            cuerpo="Marte",
            coordenadas={"lat": lat, "lng": lng},
            celda_id=cm["celda_id"],
            region_nombre=cm.get("region_referencia", f"Región Marciana ({lat:.2f}°, {lng:.2f}°)"),
            unidad_geologica=cm.get("unidad_geologica_usgs", "Unidad Noeica / Hespérica sin diferenciar"),
            tipo_terreno="",
            rocas_predominantes=cm.get("rocas_principales", ["Basalto toleítico", "Lutita lacustre", "Arenisca sulfatada"]),
            minerales_principales=cm.get("minerales_omega_detectados", ["Olivino", "Piroxeno", "Óxidos férricos", "Sulfatos hidratados"]),
            distribucion_litologica=cm.get("categorias_area_pct", {}),
            unidades_macrostrat=[],
            muestras_laboratorio_in_situ=muestras_marte,
            cobertura_geologica=True,
            ranking_terrestre=ranking,
            mejor_analogo={
                "cuerpo_destino": "Tierra",
                "sitio_analogo_terrestre": {
                    **mejor_tierra.model_dump(),
                    "minerales_detectados": [],
                },
            } if mejor_tierra else None,
            atribuciones=atribuciones,
        )

    else:
        # Luna
        celdas_luna = cargar_json_seguro("celdas_luna_10x10.json", [])
        cl = buscar_celda_mas_cercana(lat, lng, celdas_luna)
        celda_id = cl.get("celda_id", obtener_id_celda_10x10(lat, lng, "L"))

        muestras_luna = [
            MuestraLaboratorio(**m) for m in muestras_todas if m.get("cuerpo", "").lower() == "luna"
        ]

        # Comparar con la Tierra
        celdas_tierra = cargar_json_seguro("celdas_glim_10x10.json", {})
        mejor_tierra = None
        mejor_score = -1.0
        for tid, tdata in celdas_tierra.items():
            sc = calcular_similitud_coseno(cl.get("categorias_area_pct", {}), tdata.get("categorias_area_pct", {}))
            if sc > mejor_score:
                mejor_score = sc
                mejor_tierra = {
                    "celda_id": tid,
                    "region_referencia": tdata.get("region_referencia", tid),
                    "similitud_pct": sc,
                    "rocas_principales": tdata.get("rocas_principales", []),
                    "minerales_detectados": tdata.get("minerales_detectados", []),
                }

        atribuciones = [
            MetadatosFuente(
                fuente="USGS Unified Geologic Map of the Moon (Fortezzo et al. 2020)",
                licencia="Public Domain / USGS & NASA",
                resolucion_o_escala="1:5.000.000 unificada global",
                nota_metodologica="Cartografía geológica que une los seis cuadrantes de las misiones Apolo y mapas satelitales.",
            ),
            MetadatosFuente(
                fuente="JAXA SELENE (Kaguya) Multiband Imager & NASA Moon Mineralogy Mapper (M³)",
                licencia="JAXA / NASA Open Access",
                resolucion_o_escala="20 m a 100 m por píxel",
                nota_metodologica="Identificación espectral de ilmenita en mares y anortita pura en tierras altas.",
            ),
            MetadatosFuente(
                fuente="NASA Lunar Sample Compendium (Apollo Missions)",
                licencia="Public Domain / NASA Astromaterials Curation",
                resolucion_o_escala="Análisis petrográfico de laboratorio de 382 kg de rocas lunares retornadas",
                nota_metodologica="Composición modal cuantitativa y difracción de rayos X.",
            ),
        ]

        return RespuestaGeologiaPunto(
            cuerpo="Luna",
            coordenadas={"lat": lat, "lng": lng},
            celda_id=celda_id,
            region_nombre=cl.get("region_referencia", f"Superficie Lunar ({lat:.2f}°, {lng:.2f}°)"),
            unidad_geologica=cl.get("unidad_geologica_usgs", "Basalto de Mar Lunar / Anortosita de Tierras Altas"),
            tipo_terreno="Terreno de Mar Lunar (basáltico) o Tierras Altas (anortosítico)",
            rocas_predominantes=cl.get("rocas_principales", ["Basalto rico en titanio", "Anortosita ferroana", "Brecha de impacto"]),
            minerales_principales=cl.get("minerales_kaguya_detectados", ["Plagioclasa anortita", "Clinopiroxeno", "Ilmenita", "Olivino"]),
            distribucion_litologica=cl.get("categorias_area_pct", {}),
            unidades_macrostrat=[],
            muestras_laboratorio_in_situ=muestras_luna,
            mejor_analogo={
                "cuerpo_destino": "Tierra",
                "sitio_analogo_terrestre": mejor_tierra,
            },
            atribuciones=atribuciones,
        )
