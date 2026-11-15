import {
  DirectionMode,
  MissionProfile,
  RegionProfile,
  SiteComparisonResult,
} from "../domain/explorer-types";

export interface CompareResponseSchema {
  target_id: string;
  target_name: string;
  target_body: string;
  mission_profile: MissionProfile;
  direction: DirectionMode;
  algorithm_version: string;
  analysis_scale_m: number | null;
  weights: Record<string, number>;
  results: SiteComparisonResult[];
}

export interface CoordinateAnalyzeResponseSchema {
  status: "matched_aoi" | "out_of_coverage";
  message: string;
  query: { lat: number; lon: number; radius_km: number };
  matched_region: RegionProfile | null;
  distance_to_centroid_km: number | null;
  planetary_matches: SiteComparisonResult[];
}
