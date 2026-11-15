"""
Domain entities and pure scientific similarity engine for Planetary Analog Explorer.

Implements Section 6 of `PLAN_PLANETARY_ANALOG_EXPLORER_NASA_2026.md`:
- `sim_i = max(0.0, 1.0 - abs(x_i - y_i) / tolerance_i)` for numeric indicators.
- Categorical compatibility matrix lookup for `lithology`.
- `raw_score = 100 * sum(w_i * sim_i for valid i) / sum(w_i for valid i)`
- `coverage  = sum(w_i for valid i) / sum(w_i requested)`
- Never fills `null` with `0`.
- Classifies results with `coverage < min_coverage` (default `0.70`) as `insufficient_coverage`
  and ranks `suitable` (`apto`) above `insufficient_coverage`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Literal

MissionProfile = Literal["rover_mobility", "surface_geology", "environmental_testing"]
DirectionMode = Literal["planet_to_earth", "earth_to_planet"]
ClassificationStatus = Literal["suitable", "insufficient_coverage", "not_evaluated"]

MINIMUM_COVERAGE_THRESHOLD = 0.70

DEFAULT_TOLERANCES: dict[str, float] = {
    "median_slope_deg": 12.0,
    "slope_p90_deg": 20.0,
    "ruggedness_tri": 6.5,
    "local_relief_m": 450.0,
    "ndvi": 0.35,
    "precipitation_mm_year": 500.0,
    "mean_temperature_c": 65.0,
}

MISSION_PROFILE_DEFAULT_WEIGHTS: dict[MissionProfile, dict[str, float]] = {
    "rover_mobility": {
        "median_slope_deg": 0.35,
        "slope_p90_deg": 0.25,
        "ruggedness_tri": 0.25,
        "local_relief_m": 0.15,
    },
    "surface_geology": {
        "lithology": 0.40,
        "ruggedness_tri": 0.25,
        "local_relief_m": 0.20,
        "median_slope_deg": 0.15,
    },
    "environmental_testing": {
        "precipitation_mm_year": 0.35,
        "ndvi": 0.25,
        "mean_temperature_c": 0.20,
        "median_slope_deg": 0.20,
    },
}

FEATURE_UNITS: dict[str, str] = {
    "median_slope_deg": "deg",
    "slope_p90_deg": "deg",
    "ruggedness_tri": "TRI index",
    "local_relief_m": "m",
    "lithology": "category",
    "ndvi": "index [0..1]",
    "precipitation_mm_year": "mm/year",
    "mean_temperature_c": "°C",
}


@dataclass(frozen=True, slots=True)
class FeatureBreakdown:
    feature: str
    unit: str
    weight: float
    target_value: float | str | None
    candidate_value: float | str | None
    similarity: float | None
    weighted_contribution: float | None
    status: Literal["evaluated", "missing_target", "missing_candidate", "incompatible_scale", "unsupported_category"]
    note: str | None = None


@dataclass(frozen=True, slots=True)
class SiteComparisonResult:
    site_id: str
    site_name: str
    body: str
    country_or_region: str
    centroid: dict[str, float]
    score: float | None
    coverage: float
    classification: ClassificationStatus
    breakdown: list[FeatureBreakdown] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


def compute_numeric_similarity(candidate_val: float, target_val: float, tolerance: float) -> float:
    if tolerance <= 0:
        raise ValueError(f"Tolerance must be positive, got {tolerance}")
    diff = abs(candidate_val - target_val)
    return round(max(0.0, 1.0 - (diff / tolerance)), 4)


def compute_lithology_similarity(
    target_lith: str,
    candidate_lith: str,
    matrix: dict[str, dict[str, float]],
) -> float | None:
    if target_lith == candidate_lith:
        return 1.0
    if target_lith in matrix and candidate_lith in matrix[target_lith]:
        return round(float(matrix[target_lith][candidate_lith]), 4)
    if candidate_lith in matrix and target_lith in matrix[candidate_lith]:
        return round(float(matrix[candidate_lith][target_lith]), 4)
    return None


def evaluate_site_against_target(
    target: dict[str, Any],
    candidate: dict[str, Any],
    weights: dict[str, float],
    lithology_matrix: dict[str, dict[str, float]],
    tolerances: dict[str, float] | None = None,
    min_coverage: float = MINIMUM_COVERAGE_THRESHOLD,
) -> SiteComparisonResult:
    tol_map = {**DEFAULT_TOLERANCES, **(tolerances or {})}

    active_weights = {k: float(v) for k, v in weights.items() if float(v) > 0.0}
    total_requested_weight = sum(active_weights.values())
    if total_requested_weight <= 0.0:
        raise ValueError("Sum of requested weights must be strictly positive.")

    target_scale = target.get("analysis_scale_m")
    candidate_scale = candidate.get("analysis_scale_m")
    scale_mismatch = (
        target_scale is not None
        and candidate_scale is not None
        and not math.isclose(float(target_scale), float(candidate_scale), rel_tol=0.05)
    )

    target_features: dict[str, Any] = target.get("features", {})
    candidate_features: dict[str, Any] = candidate.get("features", {})

    breakdown: list[FeatureBreakdown] = []
    limitations: list[str] = list(candidate.get("quality", {}).get("notes", []))

    valid_weight_sum = 0.0
    weighted_sim_sum = 0.0

    topographic_keys = {"median_slope_deg", "slope_p90_deg", "ruggedness_tri", "local_relief_m"}

    for feature_key, weight in active_weights.items():
        unit = FEATURE_UNITS.get(feature_key, "")
        t_val = target_features.get(feature_key)
        c_val = candidate_features.get(feature_key)

        if feature_key in topographic_keys and scale_mismatch:
            breakdown.append(
                FeatureBreakdown(
                    feature=feature_key,
                    unit=unit,
                    weight=round(weight, 4),
                    target_value=t_val,
                    candidate_value=c_val,
                    similarity=None,
                    weighted_contribution=None,
                    status="incompatible_scale",
                    note=f"Escalas espaciales incompatibles ({target_scale} m vs {candidate_scale} m).",
                )
            )
            limitations.append(f"Indicador {feature_key} excluido por diferencia de escala espacial.")
            continue

        if t_val is None:
            breakdown.append(
                FeatureBreakdown(
                    feature=feature_key,
                    unit=unit,
                    weight=round(weight, 4),
                    target_value=None,
                    candidate_value=c_val,
                    similarity=None,
                    weighted_contribution=None,
                    status="missing_target",
                    note="Sin dato disponible en la región objetivo.",
                )
            )
            continue

        if c_val is None:
            null_reason = (
                candidate.get("feature_provenance", {})
                .get(feature_key, {})
                .get("null_reason")
                or "Dato no disponible en el sitio candidato."
            )
            breakdown.append(
                FeatureBreakdown(
                    feature=feature_key,
                    unit=unit,
                    weight=round(weight, 4),
                    target_value=t_val,
                    candidate_value=None,
                    similarity=None,
                    weighted_contribution=None,
                    status="missing_candidate",
                    note=null_reason,
                )
            )
            limitations.append(f"Falta `{feature_key}`: {null_reason}")
            continue

        if feature_key == "lithology":
            sim = compute_lithology_similarity(str(t_val), str(c_val), lithology_matrix)
            if sim is None:
                breakdown.append(
                    FeatureBreakdown(
                        feature=feature_key,
                        unit=unit,
                        weight=round(weight, 4),
                        target_value=str(t_val),
                        candidate_value=str(c_val),
                        similarity=None,
                        weighted_contribution=None,
                        status="unsupported_category",
                        note="Categoría litológica sin equivalencia validada en la matriz.",
                    )
                )
                continue
        else:
            sim = compute_numeric_similarity(float(c_val), float(t_val), tol_map[feature_key])

        valid_weight_sum += weight
        contrib = weight * sim
        weighted_sim_sum += contrib

        breakdown.append(
            FeatureBreakdown(
                feature=feature_key,
                unit=unit,
                weight=round(weight, 4),
                target_value=t_val,
                candidate_value=c_val,
                similarity=sim,
                weighted_contribution=round(contrib, 4),
                status="evaluated",
            )
        )

    coverage = round(valid_weight_sum / total_requested_weight, 4)

    if valid_weight_sum <= 0.0:
        raw_score = None
        classification: ClassificationStatus = "not_evaluated"
        limitations.append("Ninguna variable solicitada pudo evaluarse con datos válidos.")
    else:
        raw_score = round(100.0 * (weighted_sim_sum / valid_weight_sum), 2)
        if coverage < min_coverage:
            classification = "insufficient_coverage"
            limitations.append(
                f"Cobertura de datos ({coverage * 100:.1f}%) inferior al umbral mínimo ({min_coverage * 100:.0f}%)."
            )
        else:
            classification = "suitable"

    if target.get("body") in ("mars", "moon") and candidate.get("body") == "earth":
        limitations.append(
            "Límite físico planetario: la gravedad, presión atmosférica y radiación marciana/lunar difieren de la Tierra."
        )

    return SiteComparisonResult(
        site_id=candidate["id"],
        site_name=candidate["name"],
        body=candidate["body"],
        country_or_region=candidate.get("country_or_region", ""),
        centroid=candidate["centroid"],
        score=raw_score,
        coverage=coverage,
        classification=classification,
        breakdown=breakdown,
        limitations=limitations,
        sources=list(candidate.get("sources", [])),
    )


def rank_candidates(results: list[SiteComparisonResult]) -> list[SiteComparisonResult]:
    """
    Stable scientific ranking:
    1. `suitable` (apto) before `insufficient_coverage`, and `not_evaluated` last.
    2. Within `suitable`: order by `(score, coverage)` descending.
    3. Within `insufficient_coverage`: order by `(coverage, score)` descending so low-coverage sites never lead.
    """
    priority_map: dict[ClassificationStatus, int] = {
        "suitable": 2,
        "insufficient_coverage": 1,
        "not_evaluated": 0,
    }

    def sort_key(item: SiteComparisonResult) -> tuple[int, float, float, str]:
        prio = priority_map[item.classification]
        score_val = item.score if item.score is not None else -1.0
        if item.classification == "suitable":
            return (prio, score_val, item.coverage, item.site_id)
        return (prio, item.coverage, score_val, item.site_id)

    return sorted(results, key=sort_key, reverse=True)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometers on Earth (mean radius = 6371.0 km)."""
    r_earth = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r_earth * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
