"""
Unit and HTTP contract tests for Planetary Analog Explorer (`server/tests/test_analog_explorer.py`).

Verifies all Definition of Done criteria from Section 12 of `PLAN_PLANETARY_ANALOG_EXPLORER_NASA_2026.md`:
- Deterministic similarity calculation (same inputs -> identical ranking).
- Missing values (`None`) never become `0` by accident.
- Sites with insufficient coverage (`< 0.70`) are classified as `insufficient_coverage` and never lead the ranking.
- Negative weights, zero-sum weights, and out-of-range coordinates are rejected (`422`).
- Positive and negative synthetic controls (`data/demo/demo_fixtures.json`) behave as expected.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException
from pydantic import ValidationError

from app.main import health_check
from app.modules.analog_explorer.domain.natural_language_parser import (
    parse_natural_language_query,
)
from app.modules.analog_explorer.domain.similarity_engine import (
    MISSION_PROFILE_DEFAULT_WEIGHTS,
    evaluate_site_against_target,
    rank_candidates,
)
from app.modules.analog_explorer.infrastructure.api.routers.explorer_router import (
    analyze_earth_coordinates,
    compare_regions,
    get_mars_climate_data,
    get_region_detail,
    get_sources_manifest,
    list_sites,
    list_targets,
    parse_query_endpoint,
)
from app.modules.analog_explorer.infrastructure.api.schemas.explorer_schemas import (
    CompareRequestSchema,
    CoordinateAnalyzeRequestSchema,
    ParseQueryRequestSchema,
)
from app.modules.analog_explorer.infrastructure.persistence.catalog_repository import (
    CatalogRepository,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
DEMO_FIXTURES_PATH = ROOT_DIR / "data" / "demo" / "demo_fixtures.json"


def test_health_endpoints() -> None:
    data = health_check()
    assert isinstance(data, dict)
    assert data["status"] == "ok"


def test_targets_and_sites_catalog() -> None:
    targets_payload = list_targets(body=None)
    assert targets_payload["count"] == 2
    target_ids = {t["id"] for t in targets_payload["items"]}
    assert target_ids == {"mars-jezero", "moon-shackleton-rim"}

    mars_payload = list_targets(body="mars")
    assert mars_payload["count"] == 1
    assert mars_payload["items"][0]["id"] == "mars-jezero"

    sites_payload = list_sites(body="earth")
    assert sites_payload["count"] >= 9

    jezero_detail = get_region_detail("mars-jezero")
    assert jezero_detail["id"] == "mars-jezero"
    assert "mars_climate_ls105" in jezero_detail

    mcd = get_mars_climate_data()
    assert mcd["dataset_id"] == "mars-mcd-v6.2-ls105"

    sources = get_sources_manifest()
    assert len(sources["sources"]) == 7


def test_deterministic_ranking_and_low_coverage_handling() -> None:
    req = CompareRequestSchema(
        target_id="mars-jezero",
        mission_profile="rover_mobility",
        direction="planet_to_earth",
    )
    resp1 = compare_regions(req)
    resp2 = compare_regions(req)
    assert resp1 == resp2, "Same dataset and weights must yield identical results"

    results = resp1["results"]
    assert len(results) >= 9

    top_ids = [r["site_id"] for r in results[:3]]
    assert "earth-atacama-yungay" in top_ids
    assert "earth-black-point-lava-az" in top_ids

    lut_entry = next(r for r in results if r["site_id"] == "earth-lut-desert-kaluts")
    assert lut_entry["classification"] == "insufficient_coverage"
    assert lut_entry["coverage"] < 0.70

    suitable_indices = [i for i, r in enumerate(results) if r["classification"] == "suitable"]
    lut_index = next(i for i, r in enumerate(results) if r["site_id"] == "earth-lut-desert-kaluts")
    assert lut_index > max(suitable_indices)


def test_missing_values_never_become_zero() -> None:
    repo = CatalogRepository()
    jezero = repo.get_region_by_id("mars-jezero")
    lut = repo.get_region_by_id("earth-lut-desert-kaluts")
    manifest = repo.get_manifest()
    assert jezero is not None and lut is not None

    res = evaluate_site_against_target(
        target=jezero,
        candidate=lut,
        weights=MISSION_PROFILE_DEFAULT_WEIGHTS["rover_mobility"],
        lithology_matrix=manifest["lithology_compatibility_matrix"]["matrix"],
    )
    slope_bd = next(b for b in res.breakdown if b.feature == "median_slope_deg")
    assert slope_bd.candidate_value is None
    assert slope_bd.similarity is None
    assert slope_bd.status == "missing_candidate"


def test_positive_and_negative_controls() -> None:
    repo = CatalogRepository()
    jezero = repo.get_region_by_id("mars-jezero")
    manifest = repo.get_manifest()
    demo_data = json.loads(DEMO_FIXTURES_PATH.read_text(encoding="utf-8"))
    pos_ctrl = demo_data["records"][0]
    neg_ctrl = demo_data["records"][1]
    assert jezero is not None

    pos_res = evaluate_site_against_target(
        target=jezero,
        candidate={**pos_ctrl, "centroid": {"lat": 0.0, "lon": 0.0}, "analysis_scale_m": 100.0},
        weights=MISSION_PROFILE_DEFAULT_WEIGHTS["rover_mobility"],
        lithology_matrix=manifest["lithology_compatibility_matrix"]["matrix"],
    )
    neg_res = evaluate_site_against_target(
        target=jezero,
        candidate={**neg_ctrl, "centroid": {"lat": 0.0, "lon": 0.0}, "analysis_scale_m": 100.0},
        weights=MISSION_PROFILE_DEFAULT_WEIGHTS["rover_mobility"],
        lithology_matrix=manifest["lithology_compatibility_matrix"]["matrix"],
    )
    assert pos_res.score == 100.0
    assert neg_res.score is not None and neg_res.score < 15.0
    ranked = rank_candidates([neg_res, pos_res])
    assert ranked[0].site_id == pos_ctrl["id"]


def test_invalid_weights_and_coordinates_rejected() -> None:
    # Negative weight
    try:
        CompareRequestSchema(
            target_id="mars-jezero",
            mission_profile="rover_mobility",
            weights={"median_slope_deg": -0.5, "ruggedness_tri": 1.0},
        )
        raise AssertionError("Expected ValidationError for negative weight")
    except ValidationError:
        pass

    # Sum of weights == 0
    try:
        CompareRequestSchema(
            target_id="mars-jezero",
            mission_profile="rover_mobility",
            weights={"median_slope_deg": 0.0, "ruggedness_tri": 0.0},
        )
        raise AssertionError("Expected ValidationError for zero weight sum")
    except ValidationError:
        pass

    # Invalid coordinates (> 90 deg latitude)
    try:
        CoordinateAnalyzeRequestSchema(lat=105.0, lon=-69.9, radius_km=15.0)
        raise AssertionError("Expected ValidationError for out-of-bounds latitude")
    except ValidationError:
        pass

    # Unknown region returns 404 HTTPException
    try:
        get_region_detail("non-existent-region-id")
        raise AssertionError("Expected HTTPException 404")
    except HTTPException as exc:
        assert exc.status_code == 404


def test_coordinate_analysis_in_and_out_of_coverage() -> None:
    data_in = analyze_earth_coordinates(
        CoordinateAnalyzeRequestSchema(
            lat=-24.10, lon=-69.90, radius_km=15.0, mission_profile="rover_mobility"
        )
    )
    assert data_in["status"] == "matched_aoi"
    assert data_in["matched_region"]["id"] == "earth-atacama-yungay"
    assert len(data_in["planetary_matches"]) == 2

    data_out = analyze_earth_coordinates(
        CoordinateAnalyzeRequestSchema(lat=0.0, lon=-140.0, radius_km=15.0)
    )
    assert data_out["status"] == "out_of_coverage"
    assert "Sin datos procesados para esta área" in data_out["message"]
    assert data_out["matched_region"] is None


def test_natural_language_parser() -> None:
    parsed = parse_query_endpoint(
        ParseQueryRequestSchema(
            query="Muéstrame zonas terrestres parecidas a Jezero para probar un rover, con pendientes suaves y terreno seco"
        )
    )
    assert parsed["body"] == "mars"
    assert parsed["target_id"] == "mars-jezero"
    assert parsed["mission_profile"] == "rover_mobility"
    assert parsed["slope_preference"] == "gentle"
    assert parsed["aridity_preference"] == "hyperarid"
    assert abs(sum(parsed["weights"].values()) - 1.0) < 0.01

