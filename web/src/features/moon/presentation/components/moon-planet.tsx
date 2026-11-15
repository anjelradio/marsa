"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { createSurfaceSelection } from "@/features/shared/presentation/create-surface-selection";
import {
  latLonToVector3,
  type GeographicLandmark,
  type ProjectedLandmark,
} from "@/features/shared/domain/geographic-coordinates";

const radius = 0.96;
// Ver la nota equivalente en earth-planet.tsx: alinea marcadores y clics con la textura.
const TEXTURE_LON_OFFSET = Math.PI / 2;

export interface MoonPlanetProps {
  className?: string;
  isHovered?: boolean;
  isExploring?: boolean;
  rotationSpeed?: number;
  /** Sigue girando solo aunque esté en modo exploración (hasta que se arrastre). */
  autoRotate?: boolean;
  selectionLabel?: string;
  hasSelection?: boolean;
  onFocusGlobe?: () => void;
  /** Se llama con la coordenada seleccionada al hacer clic sobre el globo. */
  onSelect?: (point: { latitude: number; longitude: number }) => void;
  landmarks?: GeographicLandmark[];
  onProjectedLandmarksChange?: (landmarks: ProjectedLandmark[]) => void;
}

export function MoonPlanet({
  className,
  isHovered = false,
  isExploring = false,
  rotationSpeed = 0.008,
  autoRotate = false,
  selectionLabel,
  hasSelection = false,
  onFocusGlobe,
  onSelect,
  landmarks,
  onProjectedLandmarksChange,
}: MoonPlanetProps) {
  const mount = useRef<HTMLDivElement>(null);
  const isExploringRef = useRef(isExploring);
  const autoRotateRef = useRef(autoRotate);
  const onSelectRef = useRef(onSelect);
  const onFocusGlobeRef = useRef(onFocusGlobe);
  const clearSelectionRef = useRef<() => void>(null);
  const landmarksRef = useRef(landmarks);
  const onProjectedLandmarksChangeRef = useRef(onProjectedLandmarksChange);

  useEffect(() => {
    isExploringRef.current = isExploring;
  }, [isExploring]);

  useEffect(() => {
    autoRotateRef.current = autoRotate;
  }, [autoRotate]);

  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    onFocusGlobeRef.current = onFocusGlobe;
  }, [onFocusGlobe]);

  useEffect(() => {
    if (!hasSelection) clearSelectionRef.current?.();
  }, [hasSelection]);

  useEffect(() => {
    landmarksRef.current = landmarks;
  }, [landmarks]);

  useEffect(() => {
    onProjectedLandmarksChangeRef.current = onProjectedLandmarksChange;
  }, [onProjectedLandmarksChange]);

  useEffect(() => {
    const container = mount.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 2.8;

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2", {
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    if (!context) return;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      context,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.touchAction = "none";
    container.appendChild(renderer.domElement);

    const loader = new THREE.TextureLoader();
    let disposed = false;
    let ready = false;

    const texture = loader.load("/landing/moon.webp", () => {
      if (disposed) return;
      ready = true;
      syncMotion();
    });
    texture.colorSpace = THREE.SRGBColorSpace;

    const geometry = new THREE.SphereGeometry(radius, 80, 64);
    const material = new THREE.MeshPhongMaterial({
      map: texture,
      specular: 0x333842,
      shininess: 8,
    });

    // Lunar regolith scattering: sharp shadows, crater limb illumination
    material.onBeforeCompile = (shader) => {
      shader.fragmentShader = shader.fragmentShader.replace(
        "#include <opaque_fragment>",
        `
          vec3 sunDirection = directionalLights[0].direction;
          float daylight = dot(nonPerturbedNormal, sunDirection);
          float limb = pow(1.0 - max(nonPerturbedNormal.z, 0.0), 5.5);
          float scattering = smoothstep(-0.05, 0.65, daylight);
          outgoingLight += vec3(0.08, 0.10, 0.13) * scattering;
          float highSun = smoothstep(0.6, 1.0, daylight);
          outgoingLight += vec3(0.06, 0.08, 0.10) * highSun;
          outgoingLight += limb * mix(
            vec3(0.01, 0.015, 0.02),
            vec3(0.55, 0.72, 0.88),
            scattering
          );
          #include <opaque_fragment>
        `,
      );
    };

    const planet = new THREE.Mesh(geometry, material);
    planet.rotation.set(-0.02, -1.1, 0.03, "ZYX");
    scene.add(planet);
    const selection = createSurfaceSelection(planet, planet, radius);

    scene.add(new THREE.AmbientLight(0x406085, 0.12));
    const light = new THREE.DirectionalLight(0xffffff, 8.5);
    light.position.set(5.5, 1.8, 3.2);
    scene.add(light);

    // Update projected landmark 2D coordinates on current viewport
    const tempV = new THREE.Vector3();
    const updateLandmarkProjections = () => {
      const currentLandmarks = landmarksRef.current;
      const callback = onProjectedLandmarksChangeRef.current;
      if (!currentLandmarks || currentLandmarks.length === 0 || !callback) return;

      planet.updateMatrixWorld(true);
      const width = container.clientWidth;
      const height = container.clientHeight;
      if (!width || !height) return;

      const projected: ProjectedLandmark[] = currentLandmarks.map((lm) => {
        const localPos = latLonToVector3(lm.lat, lm.lon, radius, TEXTURE_LON_OFFSET);
        tempV.copy(localPos).applyMatrix4(planet.matrixWorld);
        const zWorld = tempV.z;
        const isFrontFacing = zWorld > 0.02;

        tempV.project(camera);
        const screenX = (tempV.x * 0.5 + 0.5) * width;
        const screenY = (-tempV.y * 0.5 + 0.5) * height;

        return {
          ...lm,
          screenX,
          screenY,
          visible: isFrontFacing,
          opacity: Math.max(0, Math.min(1, (zWorld - 0.02) / 0.18)),
        };
      });

      callback(projected);
    };

    // Drag Interaction
    let isDragging = false;
    let prevX = 0;
    let prevY = 0;

    const renderOnce = () => {
      renderer.render(scene, camera);
      updateLandmarkProjections();
    };

    // Click-to-select: raycast the globe and convert the hit to latitude/longitude.
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    let downX = 0;
    let downY = 0;
    let moved = false;

    const selectPoint = (clientX: number, clientY: number) => {
      const select = onSelectRef.current;
      if (!ready || !select) return;
      const bounds = renderer.domElement.getBoundingClientRect();
      if (!bounds.width || !bounds.height) return;
      pointer.set(
        (2 * (clientX - bounds.left)) / bounds.width - 1,
        1 - (2 * (clientY - bounds.top)) / bounds.height,
      );
      raycaster.setFromCamera(pointer, camera);
      const [hit] = raycaster.intersectObject(planet, false);
      if (!hit) return;
      if (!isExploringRef.current && onFocusGlobeRef.current) {
        onFocusGlobeRef.current();
        return;
      }
      const local = planet.worldToLocal(hit.point).normalize();
      const theta = THREE.MathUtils.radToDeg(Math.atan2(local.z, -local.x));
      selection.select(local, reducedMotion.matches);
      syncMotion();
      select({
        latitude: THREE.MathUtils.radToDeg(Math.asin(local.y)),
        longitude: THREE.MathUtils.euclideanModulo(theta, 360) - 180,
      });
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!isDragging) return;
      if (!moved && Math.hypot(e.clientX - downX, e.clientY - downY) < 5) return;
      moved = true;
      const dx = e.clientX - prevX;
      const dy = e.clientY - prevY;
      prevX = e.clientX;
      prevY = e.clientY;
      if (!isExploringRef.current || selection.active) return;

      planet.rotation.y += dx * 0.006;
      planet.rotation.x = Math.max(-0.65, Math.min(0.65, planet.rotation.x + dy * 0.004));

      renderOnce();
    };

    const onPointerUp = (e: PointerEvent) => {
      if (!isDragging) return;
      isDragging = false;
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);
      if (!moved && e.type === "pointerup") selectPoint(e.clientX, e.clientY);
    };

    const onPointerDown = (e: PointerEvent) => {
      if ((!isExploringRef.current && !onSelectRef.current) || e.button !== 0 || !e.isPrimary || isDragging) return;
      isDragging = true;
      moved = false;
      downX = e.clientX;
      downY = e.clientY;
      prevX = e.clientX;
      prevY = e.clientY;
      window.addEventListener("pointermove", onPointerMove, { passive: true });
      window.addEventListener("pointerup", onPointerUp, { passive: true });
      window.addEventListener("pointercancel", onPointerUp, { passive: true });
    };

    const domElement = renderer.domElement;
    const onKeyDown = (e: KeyboardEvent) => {
      if (!onSelectRef.current || (e.key !== "Enter" && e.key !== " ")) return;
      e.preventDefault();
      if (e.repeat) return;
      const bounds = domElement.getBoundingClientRect();
      selectPoint(bounds.left + bounds.width / 2, bounds.top + bounds.height / 2);
    };

    domElement.addEventListener("pointerdown", onPointerDown, { passive: true });
    container.addEventListener("keydown", onKeyDown);

    let lastWidth = 0;
    let lastHeight = 0;
    const resize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      if (!width || !height || (width === lastWidth && height === lastHeight)) return;
      lastWidth = width;
      lastHeight = height;
      renderer.setSize(width, height, false);
      renderOnce();
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);

    let animationFrameId: number;
    let lastTime = performance.now();
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    const animate = (time: number) => {
      const delta = Math.min(0.05, Math.max(0, (time - lastTime) / 1000));
      lastTime = time;

      if (selection.active) {
        selection.advance(reducedMotion.matches ? 0.5 : delta);
      } else if (!reducedMotion.matches && !isDragging && (!isExploringRef.current || autoRotateRef.current)) {
        planet.rotation.y += rotationSpeed * delta;
      }

      renderer.render(scene, camera);
      updateLandmarkProjections();
      if (!reducedMotion.matches && (!selection.active || selection.animating)) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    const syncMotion = () => {
      if (!ready || disposed) return;
      lastTime = performance.now();
      cancelAnimationFrame(animationFrameId);
      animationFrameId = requestAnimationFrame(animate);
    };

    clearSelectionRef.current = () => {
      if (!selection.active) return;
      selection.clear();
      syncMotion();
    };

    reducedMotion.addEventListener("change", syncMotion);
    resize();

    return () => {
      disposed = true;
      reducedMotion.removeEventListener("change", syncMotion);
      resizeObserver.disconnect();
      cancelAnimationFrame(animationFrameId);
      domElement.removeEventListener("pointerdown", onPointerDown);
      container.removeEventListener("keydown", onKeyDown);
      selection.clear();
      clearSelectionRef.current = null;
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);

      geometry.dispose();
      material.dispose();
      texture.dispose();
      renderer.dispose();
      if (domElement.parentNode === container) {
        container.removeChild(domElement);
      }
    };
  }, [rotationSpeed]);

  return (
    <div className={`relative ${className ?? "size-full"}`}>
      <div
        aria-hidden="true"
        className={`pointer-events-none absolute -inset-[22%] rounded-full bg-[radial-gradient(ellipse_at_50%_58%,#c4d9ff32,transparent_68%)] blur-2xl transition-[transform,opacity] duration-700 ease-out motion-reduce:transition-none ${isHovered ? "scale-[1.02] opacity-90" : "scale-100 opacity-70"}`}
      />
      <div
        aria-hidden="true"
        className={`pointer-events-none absolute inset-[2.5%] rounded-full shadow-[3px_-2px_10px_#d7e5ff75,9px_-5px_34px_#9bbcff4d] transition-[box-shadow] duration-700 ease-out motion-reduce:transition-none ${isHovered ? "shadow-[4px_-3px_15px_#e5eeff9c,12px_-7px_46px_#9bbcff70]" : ""}`}
      />
      <div
        ref={mount}
        role={onSelect ? "button" : undefined}
        tabIndex={onSelect ? 0 : undefined}
        aria-label={selectionLabel}
        className={`absolute inset-0 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-white/55 transition-transform duration-700 ease-out motion-reduce:transition-none ${isHovered && !isExploring ? "scale-[1.018]" : "scale-100"}`}
      />
    </div>
  );
}
