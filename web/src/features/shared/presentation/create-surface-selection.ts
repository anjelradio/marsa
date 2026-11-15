import * as THREE from "three";

const detailDirection = new THREE.Vector3(0.58, 0, 0.815).normalize();
const patchAngle = THREE.MathUtils.degToRad(9);

/** Projects a hexagonal patch onto the sphere and brings it into view. */
export function createSurfaceSelection(surface: THREE.Object3D, pivot: THREE.Object3D, radius: number) {
  const target = new THREE.Quaternion();
  const start = new THREE.Quaternion();
  let patch: THREE.Group | null = null;
  let progress = 1;

  function clear() {
    if (!patch) return;
    for (const part of patch.children as (THREE.Mesh | THREE.LineSegments)[]) {
      part.geometry.dispose();
      (part.material as THREE.Material).dispose();
    }
    patch.removeFromParent();
    patch = null;
    progress = 1;
  }

  function select(normal: THREE.Vector3, reducedMotion: boolean) {
    clear();
    const axis = Math.abs(normal.y) > 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
    const tangent = axis.cross(normal).normalize();
    const bitangent = new THREE.Vector3().crossVectors(normal, tangent);
    const edge = Array.from({ length: 6 }, (_, index) => {
      const angle = index * Math.PI / 3;
      return normal.clone().multiplyScalar(Math.cos(patchAngle))
        .addScaledVector(tangent, Math.sin(patchAngle) * Math.cos(angle))
        .addScaledVector(bitangent, Math.sin(patchAngle) * Math.sin(angle));
    });

    const center = normal.clone().multiplyScalar(radius * 1.019);
    const triangles: number[] = [];
    const outlines: number[] = [];
    const spokes: number[] = [];
    for (const [index, corner] of edge.entries()) {
      const next = edge[(index + 1) % edge.length];
      const vertex = corner.clone().multiplyScalar(radius * 1.019);
      spokes.push(...center.toArray(), ...vertex.toArray());
      // Subdivide the rim so it follows the curvature of the globe.
      for (let step = 0; step < 4; step++) {
        const a = corner.clone().lerp(next, step / 4).setLength(radius * 1.019);
        const b = corner.clone().lerp(next, (step + 1) / 4).setLength(radius * 1.019);
        triangles.push(...center.toArray(), ...a.toArray(), ...b.toArray());
        outlines.push(...a.toArray(), ...b.toArray());
      }
    }

    const geometry = (positions: number[]) => new THREE.BufferGeometry()
      .setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    patch = new THREE.Group();
    patch.add(
      new THREE.Mesh(geometry(triangles), new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.15, depthWrite: false,
      })),
      new THREE.LineSegments(geometry(outlines), new THREE.LineBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.93, depthWrite: false,
      })),
      new THREE.LineSegments(geometry(spokes), new THREE.LineBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.42, depthWrite: false,
      })),
    );
    // Draw above the translucent atmosphere, while respecting the globe's depth.
    patch.children.forEach((part, index) => { part.renderOrder = 4 + index; });
    surface.add(patch);

    const worldNormal = normal.clone().applyQuaternion(surface.getWorldQuaternion(new THREE.Quaternion()));
    start.copy(pivot.quaternion);
    target.setFromUnitVectors(worldNormal, detailDirection).multiply(start);
    progress = reducedMotion ? 1 : 0;
    if (reducedMotion) pivot.quaternion.copy(target);
  }

  return {
    get active() { return patch !== null; },
    get animating() { return progress < 1; },
    select,
    clear,
    advance(seconds: number) {
      if (progress === 1) return;
      progress = Math.min(1, progress + seconds / 0.5);
      pivot.quaternion.slerpQuaternions(start, target, 1 - (1 - progress) ** 3);
    },
  };
}
