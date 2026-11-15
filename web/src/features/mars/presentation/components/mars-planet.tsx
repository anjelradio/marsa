"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { MarsCoordinates } from "@/features/mars/infrastructure/mars-climate";
import { createSurfaceSelection } from "@/features/shared/presentation/create-surface-selection";
import { createMarsSurfaceOverlay } from "./mars-surface-overlay";

const radius = 0.96;
const dragThreshold = 5;

// Superficie y atmósfera adaptadas de Aditya-567/3D-Planets (Apache-2.0).
export function MarsPlanet({
  className,
  isHovered = false,
  isExploring = false,
  showSurfaceOverlay = true,
  rotationSpeed = 0.012,
  selectionLabel,
  hasSelection = false,
  onFocusGlobe,
  onSelect,
}: {
  className?: string;
  isHovered?: boolean;
  isExploring?: boolean;
  showSurfaceOverlay?: boolean;
  rotationSpeed?: number;
  selectionLabel?: string;
  hasSelection?: boolean;
  onFocusGlobe?: () => void;
  onSelect?: (point: MarsCoordinates) => void;
}) {
  const mount = useRef<HTMLDivElement>(null);
  const isExploringRef = useRef(isExploring);
  const onSelectRef = useRef(onSelect);
  const onFocusGlobeRef = useRef(onFocusGlobe);
  const clearSelectionRef = useRef<() => void>(null);
  const syncOverlayRef = useRef<() => void>(null);

  useEffect(() => {
    isExploringRef.current = isExploring;
    syncOverlayRef.current?.();
  }, [isExploring]);

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
    const container = mount.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 2.8;

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2", { alpha: true, antialias: true, powerPreference: "high-performance" });
    if (!context) return;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      context,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    // A 1.75 DPR cap keeps the globe crisp without doubling the fragment cost
    // on high-density displays.
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.touchAction = "none";
    container.appendChild(renderer.domElement);

    const loader = new THREE.TextureLoader();
    let disposed = false;
    let ready = false;
    const texture = loader.load("/mars/marsmap.jpg", () => {
      if (disposed) return;
      ready = true;
      syncMotion();
    });
    texture.colorSpace = THREE.SRGBColorSpace;
    const bump = loader.load("/mars/marsbump.jpg", () => {
      if (!disposed && ready && !document.hidden) renderer.render(scene, camera);
    });
    const geometry = new THREE.SphereGeometry(radius, 80, 64);
    const material = new THREE.MeshPhongMaterial({
      map: texture,
      bumpMap: bump,
      bumpScale: 0.022,
      specular: 0x2b190f,
      shininess: 12,
    });

    // Warm daylight scattering on sunlit side and limb glow
    material.onBeforeCompile = (shader) => {
      shader.fragmentShader = shader.fragmentShader.replace(
        "#include <opaque_fragment>",
        `
          vec3 sunDirection = directionalLights[0].direction;
          float daylight = dot(nonPerturbedNormal, sunDirection);
          float limb = pow(1.0 - max(nonPerturbedNormal.z, 0.0), 6.0);
          float scattering = smoothstep(-0.12, 0.75, daylight);
          outgoingLight += vec3(0.36, 0.105, 0.067) * scattering;
          float highSun = smoothstep(0.55, 1.0, daylight);
          outgoingLight += vec3(0.08, 0.04, 0.084) * highSun;
          outgoingLight += limb * mix(
            vec3(0.021, 0.002, 0.001),
            vec3(0.86, 0.37, 0.18),
            scattering
          );
          #include <opaque_fragment>
        `,
      );
    };

    const planet = new THREE.Mesh(geometry, material);
    planet.rotation.set(-0.08, -2.12, 0.22, "ZYX");
    scene.add(planet);

    const surfaceOverlay = showSurfaceOverlay ? createMarsSurfaceOverlay(radius) : null;
    if (surfaceOverlay) scene.add(surfaceOverlay.group);
    const selection = createSurfaceSelection(planet, planet, radius);

    scene.add(new THREE.AmbientLight(0xff411b, 0.09));
    const light = new THREE.DirectionalLight(0xffefe7, 10.5);
    light.position.set(6, 2.2, 3.6);
    scene.add(light);

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const domElement = renderer.domElement;
    let gesture: { id: number; x: number; y: number; moved: boolean } | null = null;

    const renderOnce = () => renderer.render(scene, camera);

    const selectPoint = (clientX: number, clientY: number) => {
      if (!ready || !onSelectRef.current) return;
      const bounds = domElement.getBoundingClientRect();
      if (!bounds.width || !bounds.height) return;
      pointer.set(
        2 * (clientX - bounds.left) / bounds.width - 1,
        1 - 2 * (clientY - bounds.top) / bounds.height,
      );
      raycaster.setFromCamera(pointer, camera);
      const [hit] = raycaster.intersectObject(planet, false);
      if (!hit) return;
      if (!isExploringRef.current && onFocusGlobeRef.current) {
        onFocusGlobeRef.current();
        return;
      }

      // The texture begins at 0° east. Convert in mesh space so drag and tilt
      // affect which surface point is visible without changing its coordinates.
      const local = planet.worldToLocal(hit.point).normalize();
      const east = THREE.MathUtils.radToDeg(Math.atan2(local.z, -local.x));
      const latitude = THREE.MathUtils.radToDeg(Math.asin(local.y));
      const longitude = THREE.MathUtils.euclideanModulo(east + 180, 360) - 180;
      selection.select(local, reducedMotion.matches);
      syncMotion();
      onSelectRef.current({ latitude, longitude });
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!gesture || e.pointerId !== gesture.id) return;
      const dx = e.clientX - gesture.x;
      const dy = e.clientY - gesture.y;
      if (!gesture.moved && Math.hypot(dx, dy) < dragThreshold) return;
      gesture.moved = true;
      gesture.x = e.clientX;
      gesture.y = e.clientY;
      if (!isExploringRef.current || selection.active) return;

      planet.rotation.y += dx * 0.006;
      planet.rotation.x = Math.max(-0.65, Math.min(0.65, planet.rotation.x + dy * 0.004));

      if (reducedMotion.matches) renderOnce();
    };

    const clearGesture = () => {
      gesture = null;
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerCancel);
      window.removeEventListener("blur", clearGesture);
    };

    const onPointerUp = (e: PointerEvent) => {
      if (!gesture || e.pointerId !== gesture.id) return;
      const isClick = !gesture.moved
        && Math.hypot(e.clientX - gesture.x, e.clientY - gesture.y) < dragThreshold;
      clearGesture();
      if (isClick) selectPoint(e.clientX, e.clientY);
    };

    const onPointerCancel = (e: PointerEvent) => {
      if (e.pointerId === gesture?.id) clearGesture();
    };

    const onPointerDown = (e: PointerEvent) => {
      if ((!isExploringRef.current && !onSelectRef.current) || e.button !== 0 || !e.isPrimary || gesture) return;
      gesture = { id: e.pointerId, x: e.clientX, y: e.clientY, moved: false };
      window.addEventListener("pointermove", onPointerMove, { passive: true });
      window.addEventListener("pointerup", onPointerUp, { passive: true });
      window.addEventListener("pointercancel", onPointerCancel, { passive: true });
      window.addEventListener("blur", clearGesture);
    };

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
      camera.left = -width / height;
      camera.right = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
      if (ready && !document.hidden) renderer.render(scene, camera);
    };

    const observer = new ResizeObserver(resize);
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    function syncMotion() {
      renderer.setAnimationLoop(null);
      if (!ready || document.hidden) return;

      if (reducedMotion.matches) selection.advance(0.5);
      renderer.render(scene, camera);
      canvas.dataset.rendered = "";
      if (reducedMotion.matches || (selection.active && !selection.animating)) return;

      let previousTime: number | undefined;
      renderer.setAnimationLoop((time) => {
        const delta = Math.min(0.05, (time - (previousTime ?? time)) / 1000);
        previousTime = time;
        if (selection.active) {
          selection.advance(delta);
          if (!selection.animating) renderer.setAnimationLoop(null);
        } else if (!gesture) {
          planet.rotation.y += delta * rotationSpeed;
        }
        renderer.render(scene, camera);
      });
    }

    clearSelectionRef.current = () => {
      if (!selection.active) return;
      selection.clear();
      syncMotion();
    };
    syncOverlayRef.current = () => {
      if (!surfaceOverlay) return;
      surfaceOverlay.group.visible = !isExploringRef.current;
      if (ready && !document.hidden) renderOnce();
    };
    syncOverlayRef.current();

    observer.observe(container);
    resize();
    reducedMotion.addEventListener("change", syncMotion);
    document.addEventListener("visibilitychange", syncMotion);

    return () => {
      disposed = true;
      clearGesture();
      domElement.removeEventListener("pointerdown", onPointerDown);
      container.removeEventListener("keydown", onKeyDown);
      renderer.setAnimationLoop(null);
      observer.disconnect();
      reducedMotion.removeEventListener("change", syncMotion);
      document.removeEventListener("visibilitychange", syncMotion);
      geometry.dispose();
      material.dispose();
      texture.dispose();
      bump.dispose();
      surfaceOverlay?.dispose();
      selection.clear();
      clearSelectionRef.current = null;
      syncOverlayRef.current = null;
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
  }, [showSurfaceOverlay, rotationSpeed]);

  return (
    <div
      aria-hidden={onSelect ? undefined : true}
      className={className ?? "absolute inset-0"}
    >
      {/* Outer atmospheric coronal diffusion */}
      <div
        className={`absolute -inset-[22%] pointer-events-none bg-[radial-gradient(ellipse_25%_16%_at_52%_18%,#ffaf7b85,transparent),radial-gradient(ellipse_18%_28%_at_81%_48%,#ffa77585,transparent),radial-gradient(ellipse_21%_19%_at_68%_76%,#ff854b64,transparent)] transition-[transform,opacity] duration-700 ease-out motion-reduce:transition-none ${
          isHovered ? "scale-[1.01] opacity-65" : "scale-100 opacity-60"
        }`}
      />
      {/* Soft limb rim glow */}
      <div
        className={`absolute inset-[2.5%] pointer-events-none rounded-full bg-[#251006] transition-[box-shadow] duration-700 ease-out motion-reduce:transition-none [background-image:radial-gradient(ellipse_at_73%_38%,#ff975f,#180603_75%)] ${
          isHovered
            ? "shadow-[3px_-2px_12px_#ffba7880,9px_-5px_38px_#ff763a55]"
            : "shadow-[3px_-2px_10px_#ffba7875,9px_-5px_34px_#ff763a4d]"
        }`}
      />
      <div
        ref={mount}
        role={onSelect ? "button" : undefined}
        tabIndex={onSelect ? 0 : undefined}
        aria-label={selectionLabel}
        className={`absolute inset-0 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-[#ffab57]/80 focus-visible:ring-offset-4 focus-visible:ring-offset-black transition-transform duration-700 ease-out motion-reduce:transition-none ${
          isHovered && !isExploring ? "scale-[1.018]" : "scale-100"
        }`}
      />
    </div>
  );
}
