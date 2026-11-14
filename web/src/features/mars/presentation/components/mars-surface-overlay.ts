import {
  BufferGeometry,
  DoubleSide,
  Float32BufferAttribute,
  Group,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshBasicMaterial,
  WireframeGeometry,
} from "three";

// Coordenadas del trazado decorativo en el disco visible, de 0 a 100.
const points = [
  [23, 11], [28, 6], [34, 8], [36, 5], [40, 3], [48, 3], [50, 5],
  [46, 8], [50, 14], [39, 16], [44, 18], [43, 22],
  [27, 32], [34, 24], [50, 28], [48, 36], [39, 40],
  [29, 44], [24, 50], [19, 52], [30, 64], [49, 54],
  [45, 61], [51, 68], [49, 81],
];

const faces = [
  0, 1, 2, 1, 3, 2, 2, 3, 4, 2, 4, 7, 4, 5, 7, 5, 6, 7,
  2, 7, 9, 7, 8, 9, 9, 10, 11, 9, 11, 13, 12, 13, 11,
  12, 11, 14, 12, 14, 15, 12, 15, 16, 12, 16, 17,
  17, 16, 21, 17, 18, 21, 18, 19, 21, 19, 20, 21,
  20, 21, 22, 20, 22, 23, 20, 23, 24, 22, 23, 24,
];

// Proyecta la malla sobre la cara visible para que siga el encuadre del planeta.
export function createMarsSurfaceOverlay(radius: number) {
  const geometry = new BufferGeometry();
  const positions = points.flatMap(([u, v]) => [
    radius * (u / 50 - 1),
    radius * (1 - v / 50),
    radius,
  ]);
  geometry.setAttribute("position", new Float32BufferAttribute(positions, 3));
  geometry.setIndex(faces);

  const fill = new MeshBasicMaterial({
    color: 0xffd4b4,
    opacity: 0.12,
    transparent: true,
    depthWrite: false,
    depthTest: false,
    side: DoubleSide,
  });
  const wireframe = new WireframeGeometry(geometry);
  const stroke = new LineBasicMaterial({
    color: 0xffd8bd,
    opacity: 0.48,
    transparent: true,
    depthWrite: false,
    depthTest: false,
  });

  const mesh = new Mesh(geometry, fill);
  mesh.renderOrder = 1;
  const lines = new LineSegments(wireframe, stroke);
  lines.renderOrder = 2;
  const group = new Group();
  group.add(mesh, lines);

  return {
    group,
    dispose() {
      geometry.dispose();
      wireframe.dispose();
      fill.dispose();
      stroke.dispose();
    },
  };
}
