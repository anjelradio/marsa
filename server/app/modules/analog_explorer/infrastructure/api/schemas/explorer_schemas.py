"""
Pydantic v2 HTTP request/response schemas for Planetary Analog Explorer API.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.analog_explorer.domain.similarity_engine import (
    ClassificationStatus,
    DirectionMode,
    MissionProfile,
)


class CompareRequestSchema(BaseModel):
    target_id: str = Field(..., min_length=2, description="Target region ID (e.g., 'mars-jezero' or an Earth site ID in reverse mode)")
    mission_profile: MissionProfile = Field(default="rover_mobility")
    direction: DirectionMode = Field(default="planet_to_earth")
    weights: dict[str, float] | None = Field(
        default=None,
        description="Optional custom indicator weights. Each weight must be >= 0 and their sum must be > 0.",
    )
    min_coverage: float = Field(default=0.70, ge=0.1, le=1.0)

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        if value is None:
            return None
        allowed_keys = {
            "median_slope_deg",
            "slope_p90_deg",
            "ruggedness_tri",
            "local_relief_m",
            "lithology",
            "ndvi",
            "precipitation_mm_year",
            "mean_temperature_c",
        }
        for k, v in value.items():
            if k not in allowed_keys:
                raise ValueError(f"Unsupported indicator key: '{k}'")
            if v < 0.0:
                raise ValueError(f"Weight for '{k}' cannot be negative ({v}).")
        if sum(value.values()) <= 0.0:
            raise ValueError("The sum of indicator weights must be strictly greater than 0.")
        return value


class FeatureBreakdownSchema(BaseModel):
    feature: str
    unit: str
    weight: float
    target_value: float | str | None
    candidate_value: float | str | None
    similarity: float | None
    weighted_contribution: float | None
    status: str
    note: str | None = None


class SiteComparisonResultSchema(BaseModel):
    site_id: str
    site_name: str
    body: str
    country_or_region: str
    centroid: dict[str, float]
    score: float | None
    coverage: float
    classification: ClassificationStatus
    breakdown: list[FeatureBreakdownSchema]
    limitations: list[str]
    sources: list[str]


class CompareResponseSchema(BaseModel):
    target_id: str
    target_name: str
    target_body: str
    mission_profile: MissionProfile
    direction: DirectionMode
    algorithm_version: str
    analysis_scale_m: float | None
    weights: dict[str, float]
    results: list[SiteComparisonResultSchema]


class ParseQueryRequestSchema(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


class ParseQueryResponseSchema(BaseModel):
    raw_query: str
    body: Literal["mars", "moon"]
    target_id: str
    mission_profile: MissionProfile
    direction: DirectionMode
    weights: dict[str, float]
    slope_preference: str
    aridity_preference: str
    lithology_preference: str | None
    interpreted_summary: str
    ambiguities: list[str]


class CoordinateAnalyzeRequestSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(default=15.0, ge=1.0, le=50.0)
    mission_profile: MissionProfile = Field(default="rover_mobility")

    @model_validator(mode="after")
    def check_finite(self) -> "CoordinateAnalyzeRequestSchema":
        return self


class CoordinateAnalyzeResponseSchema(BaseModel):
    status: Literal["matched_aoi", "out_of_coverage"]
    message: str
    query: dict[str, float]
    matched_region: dict[str, Any] | None = None
    distance_to_centroid_km: float | None = None
    planetary_matches: list[SiteComparisonResultSchema] = Field(default_factory=list)
