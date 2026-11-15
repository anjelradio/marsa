"""
FastAPI router for Planetary Analog Explorer (`/api/...`).

Implements all required P0 and P1 endpoints:
- `GET /api/targets`
- `GET /api/sites`
- `GET /api/regions/{region_id}`
- `POST /api/compare`
- `GET /api/sources`
- `GET /api/mars-climate`
- `POST /api/parse-query`
- `POST /api/earth-aoi/analyze`
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.analog_explorer.domain.natural_language_parser import (
    parse_natural_language_query,
)
from app.modules.analog_explorer.domain.similarity_engine import (
    MISSION_PROFILE_DEFAULT_WEIGHTS,
    evaluate_site_against_target,
    haversine_distance_km,
    rank_candidates,
)
from app.modules.analog_explorer.infrastructure.api.schemas.explorer_schemas import (
    CompareRequestSchema,
    CompareResponseSchema,
    CoordinateAnalyzeRequestSchema,
    CoordinateAnalyzeResponseSchema,
    ParseQueryRequestSchema,
    ParseQueryResponseSchema,
)
from app.modules.analog_explorer.infrastructure.persistence.catalog_repository import (
    CatalogRepository,
)

router = APIRouter()
repo = CatalogRepository()


@router.get("/targets", summary="List documented planetary reference targets (Mars & Moon)")
def list_targets(
    body: str | None = Query(default=None, description="Filter by planetary body: mars | moon"),
) -> dict[str, Any]:
    if body and body.lower() not in ("mars", "moon"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Parameter 'body' for /api/targets must be 'mars' or 'moon'.",
        )
    targets = repo.get_targets(body=body)
    return {"count": len(targets), "items": targets}


@router.get("/sites", summary="List terrestrial analog candidate sites with known data coverage")
def list_sites(
    body: str = Query(default="earth", description="Filter by body (default: earth)"),
) -> dict[str, Any]:
    sites = repo.get_sites(body=body)
    return {"count": len(sites), "items": sites}


@router.get("/regions/{region_id}", summary="Retrieve full RegionProfile, AOI geometry, features, and provenance")
def get_region_detail(region_id: str) -> dict[str, Any]:
    region = repo.get_region_by_id(region_id)
    if region is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region '{region_id}' not found in validated catalog.",
        )
    return region


@router.get("/sources", summary="Catalog of scientific datasets, resolutions, CRS, and licenses")
def get_sources_manifest() -> dict[str, Any]:
    return repo.get_manifest()


@router.get("/mars-climate", summary="Processed Mars Climate Database (MCD v6.2, Ls=105) layers & reference points")
def get_mars_climate_data() -> dict[str, Any]:
    return repo.get_mars_mcd_summary()


@router.post("/compare", response_model=CompareResponseSchema, summary="Run deterministic multi-criteria similarity comparison")
def compare_regions(payload: CompareRequestSchema) -> dict[str, Any]:
    target = repo.get_region_by_id(payload.target_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target region '{payload.target_id}' not found in catalog.",
        )

    manifest = repo.get_manifest()
    lithology_matrix: dict[str, dict[str, float]] = manifest["lithology_compatibility_matrix"]["matrix"]

    weights = payload.weights or dict(MISSION_PROFILE_DEFAULT_WEIGHTS[payload.mission_profile])
    total_w = sum(weights.values())
    normalized_weights = {k: round(v / total_w, 4) for k, v in weights.items() if v > 0}

    if payload.direction == "planet_to_earth":
        candidates = repo.get_sites(body="earth")
    else:
        candidates = repo.get_targets()

    evaluated = [
        evaluate_site_against_target(
            target=target,
            candidate=cand,
            weights=normalized_weights,
            lithology_matrix=lithology_matrix,
            min_coverage=payload.min_coverage,
        )
        for cand in candidates
        if cand["id"] != target["id"]
    ]
    ranked = rank_candidates(evaluated)

    return {
        "target_id": target["id"],
        "target_name": target["name"],
        "target_body": target["body"],
        "mission_profile": payload.mission_profile,
        "direction": payload.direction,
        "algorithm_version": "baseline-v1",
        "analysis_scale_m": target.get("analysis_scale_m"),
        "weights": normalized_weights,
        "results": [asdict(r) for r in ranked],
    }


@router.post("/parse-query", response_model=ParseQueryResponseSchema, summary="Parse natural language query into typed scientific filters")
def parse_query_endpoint(payload: ParseQueryRequestSchema) -> dict[str, Any]:
    parsed = parse_natural_language_query(payload.query)
    return asdict(parsed)


@router.post(
    "/earth-aoi/analyze",
    response_model=CoordinateAnalyzeResponseSchema,
    summary="Validate terrestrial coordinates against precomputed AOIs and compute reverse planetary matches",
)
def analyze_earth_coordinates(payload: CoordinateAnalyzeRequestSchema) -> dict[str, Any]:
    earth_sites = repo.get_sites(body="earth")

    closest_site: dict[str, Any] | None = None
    closest_dist_km: float = float("inf")

    for site in earth_sites:
        c_lat = float(site["centroid"]["lat"])
        c_lon = float(site["centroid"]["lon"])
        dist = haversine_distance_km(payload.lat, payload.lon, c_lat, c_lon)
        if dist < closest_dist_km:
            closest_dist_km = dist
            closest_site = site

    if closest_site is None:
        return {
            "status": "out_of_coverage",
            "message": "Sin datos procesados para esta área.",
            "query": {"lat": payload.lat, "lon": payload.lon, "radius_km": payload.radius_km},
            "matched_region": None,
            "distance_to_centroid_km": None,
            "planetary_matches": [],
        }

    site_radius = float(closest_site.get("aoi_radius_km", 15.0))
    effective_threshold_km = site_radius + payload.radius_km

    if closest_dist_km > effective_threshold_km:
        return {
            "status": "out_of_coverage",
            "message": (
                f"Sin datos procesados para esta área ({payload.lat:.3f}°, {payload.lon:.3f}°). "
                f"El sitio validado más cercano es '{closest_site['name']}' a {closest_dist_km:.1f} km "
                f"(fuera del radio AOI de {effective_threshold_km:.0f} km)."
            ),
            "query": {"lat": payload.lat, "lon": payload.lon, "radius_km": payload.radius_km},
            "matched_region": None,
            "distance_to_centroid_km": round(closest_dist_km, 2),
            "planetary_matches": [],
        }

    manifest = repo.get_manifest()
    lithology_matrix: dict[str, dict[str, float]] = manifest["lithology_compatibility_matrix"]["matrix"]
    weights = dict(MISSION_PROFILE_DEFAULT_WEIGHTS[payload.mission_profile])

    planetary_targets = repo.get_targets()
    evaluated = [
        evaluate_site_against_target(
            target=closest_site,
            candidate=ptarget,
            weights=weights,
            lithology_matrix=lithology_matrix,
        )
        for ptarget in planetary_targets
    ]
    ranked = rank_candidates(evaluated)

    return {
        "status": "matched_aoi",
        "message": f"Coordenada dentro del AOI validada de '{closest_site['name']}' (distancia al centroide: {closest_dist_km:.1f} km).",
        "query": {"lat": payload.lat, "lon": payload.lon, "radius_km": payload.radius_km},
        "matched_region": closest_site,
        "distance_to_centroid_km": round(closest_dist_km, 2),
        "planetary_matches": [asdict(r) for r in ranked],
    }
