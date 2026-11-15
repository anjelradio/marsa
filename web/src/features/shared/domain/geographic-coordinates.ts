import * as THREE from "three";

/**
 * Converts geographic latitude and longitude (in degrees) to a 3D Cartesian Vector3
 * on a sphere of a given radius, calibrated for standard equirectangular planet maps.
 *
 * @param lat Latitude in degrees (-90 to +90)
 * @param lon Longitude in degrees (-180 to +180 or 0 to 360)
 * @param radius Sphere radius
 * @param lonOffsetRad Optional texture meridian calibration offset in radians
 */
export function latLonToVector3(
  lat: number,
  lon: number,
  radius: number,
  lonOffsetRad = 0,
): THREE.Vector3 {
  // Normalize longitude to [-180, 180]
  let normLon = lon;
  while (normLon > 180) normLon -= 360;
  while (normLon < -180) normLon += 360;

  const phi = (90 - lat) * (Math.PI / 180);
  const theta = normLon * (Math.PI / 180) + Math.PI / 2 + lonOffsetRad;

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const y = radius * Math.cos(phi);
  const z = radius * Math.sin(phi) * Math.sin(theta);

  return new THREE.Vector3(x, y, z);
}

export interface GeographicLandmark {
  id: string;
  name: string;
  lat: number;
  lon: number;
  type: string;
  coord: string;
  desc: string;
  comparisonKey?: string | null;
}

export interface ProjectedLandmark {
  id: string;
  name: string;
  type: string;
  coord: string;
  desc: string;
  screenX: number;
  screenY: number;
  visible: boolean;
  opacity: number;
  comparisonKey?: string | null;
}
