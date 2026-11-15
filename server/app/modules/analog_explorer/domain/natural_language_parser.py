"""
Deterministic natural language query parser for Planetary Analog Explorer (Flow C).

Converts user text (Spanish or English) into typed, auditable filters without fabricating
scientific data or coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.modules.analog_explorer.domain.similarity_engine import (
    MISSION_PROFILE_DEFAULT_WEIGHTS,
    DirectionMode,
    MissionProfile,
)


@dataclass(frozen=True, slots=True)
class ParsedQueryResult:
    raw_query: str
    body: Literal["mars", "moon"]
    target_id: str
    mission_profile: MissionProfile
    direction: DirectionMode
    weights: dict[str, float]
    slope_preference: Literal["gentle", "steep", "default"]
    aridity_preference: Literal["hyperarid", "cold_dry", "default"]
    lithology_preference: str | None
    interpreted_summary: str
    ambiguities: list[str] = field(default_factory=list)


def parse_natural_language_query(query: str) -> ParsedQueryResult:
    q = query.strip().lower()
    ambiguities: list[str] = []

    # 1. Detect planetary body and target
    has_moon = any(tok in q for tok in ("luna", "lunar", "moon", "shackleton", "artemis", "polo sur"))
    has_mars = any(tok in q for tok in ("marte", "marciano", "marciana", "mars", "jezero", "perseverance"))

    if has_moon and not has_mars:
        body: Literal["mars", "moon"] = "moon"
        target_id = "moon-shackleton-rim"
    elif has_mars and not has_moon:
        body = "mars"
        target_id = "mars-jezero"
    else:
        body = "mars"
        target_id = "mars-jezero"
        if has_moon and has_mars:
            ambiguities.append("Se mencionan tanto Marte como la Luna; se seleccionó Cráter Jezero (Marte) por defecto.")
        else:
            ambiguities.append("No se especificó cuerpo planetario; se asumió Marte (Cráter Jezero) como referencia.")

    # 2. Detect search direction
    if any(tok in q for tok in ("qué objetivos", "que objetivos", "tengo un terreno", "en la tierra, ¿qué", "hacia marte")):
        direction: DirectionMode = "earth_to_planet"
    else:
        direction = "planet_to_earth"

    # 3. Detect mission profile
    if any(tok in q for tok in ("rover", "movilidad", "tracción", "traccion", "ruedas", "navegación", "pendiente")):
        mission_profile: MissionProfile = "rover_mobility"
    elif any(tok in q for tok in ("geología", "geologia", "mineral", "litología", "litologia", "volcánico", "volcanico", "roca", "basalto")):
        mission_profile = "surface_geology"
    elif any(tok in q for tok in ("ambiental", "clima", "desierto", "árido", "arido", "frío", "frio", "seco", "temperatura")):
        mission_profile = "environmental_testing"
    else:
        mission_profile = "rover_mobility"

    weights = dict(MISSION_PROFILE_DEFAULT_WEIGHTS[mission_profile])

    # 4. Detect modifier preferences and adjust weights deterministically
    slope_preference: Literal["gentle", "steep", "default"] = "default"
    if any(tok in q for tok in ("pendientes suaves", "pendiente suave", "llano", "plano", "flat", "gentle")):
        slope_preference = "gentle"
        weights["median_slope_deg"] = round(weights.get("median_slope_deg", 0.25) + 0.15, 2)
    elif any(tok in q for tok in ("escarpado", "pendiente pronunciada", "ladera", "borde", "steep")):
        slope_preference = "steep"
        weights["slope_p90_deg"] = round(weights.get("slope_p90_deg", 0.20) + 0.15, 2)

    aridity_preference: Literal["hyperarid", "cold_dry", "default"] = "default"
    if any(tok in q for tok in ("seco", "árido", "arido", "hiperárido", "desierto", "poca vegetación", "sin vegetación")):
        aridity_preference = "hyperarid"
        weights["precipitation_mm_year"] = round(weights.get("precipitation_mm_year", 0.15) + 0.20, 2)
        weights["ndvi"] = round(weights.get("ndvi", 0.10) + 0.15, 2)
    if any(tok in q for tok in ("frío", "frio", "polar", "hielo", "permafrost", "antártida", "ártico")):
        aridity_preference = "cold_dry"
        weights["mean_temperature_c"] = round(weights.get("mean_temperature_c", 0.15) + 0.20, 2)

    lithology_preference: str | None = None
    if any(tok in q for tok in ("volcánico", "volcanico", "basalto", "lava", "piroclasto")):
        lithology_preference = "basaltic_tephra_lava"
        weights["lithology"] = round(weights.get("lithology", 0.20) + 0.25, 2)
    elif any(tok in q for tok in ("impacto", "cráter", "crater", "brecha")):
        lithology_preference = "impact_breccia_carbonate"
    elif any(tok in q for tok in ("lago", "delta", "fluvial", "lacustre", "evaporita", "sal")):
        lithology_preference = "fluvio_lacustrine_volcaniclastic"

    # Normalize weights to sum to 1.0
    total_w = sum(weights.values())
    normalized_weights = {k: round(v / total_w, 3) for k, v in weights.items()}

    summary_parts = [
        f"Objetivo: {'Cráter Jezero (Marte)' if target_id == 'mars-jezero' else 'Borde del Cráter Shackleton (Luna)'}",
        f"Perfil: {mission_profile}",
        f"Dirección: {direction}",
    ]
    if slope_preference != "default":
        summary_parts.append(f"Preferencia topográfica: {slope_preference}")
    if aridity_preference != "default":
        summary_parts.append(f"Condición ambiental: {aridity_preference}")
    if lithology_preference:
        summary_parts.append(f"Afinidad litológica: {lithology_preference}")

    return ParsedQueryResult(
        raw_query=query.strip(),
        body=body,
        target_id=target_id,
        mission_profile=mission_profile,
        direction=direction,
        weights=normalized_weights,
        slope_preference=slope_preference,
        aridity_preference=aridity_preference,
        lithology_preference=lithology_preference,
        interpreted_summary=" · ".join(summary_parts),
        ambiguities=ambiguities,
    )
