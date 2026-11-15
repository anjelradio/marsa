"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

const radius = 0.96;

export interface MoonPlanetProps {
  className?: string;
  isHovered?: boolean;
  isExploring?: boolean;
  rotationSpeed?: number;
}

export function MoonPlanet({
  className,
  isHovered = false,
  isExploring = false,
  rotationSpeed = 0.008,
}: MoonPlanetProps) {
  const mount = useRef<HTMLDivElement>(null);
  const isExploringRef = useRef(isExploring);

  useEffect(() => {
    isExploringRef.current = isExploring;
  }, [isExploring]);

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
    // Initial tilt matching Moon's 1.54° axial inclination
    planet.rotation.set(-0.02, -1.1, 0.03, "ZYX");
    scene.add(planet);

    // Subtle ambient light (earthshine reflection on lunar dark side)
    scene.add(new THREE.AmbientLight(0x406085, 0.12));

    // Directional sunlight - sharp contrast representing airless space
    const light = new THREE.DirectionalLight(0xffffff, 8.5);
    light.position.set(5.5, 1.8, 3.2);
    scene.add(light);

    // Drag interaction
    let isDragging = false;
    let prevX = 0;
    let prevY = 0;

    const renderOnce = () => renderer.render(scene, camera);

    const onPointerMove = (e: PointerEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevX;
      const dy = e.clientY - prevY;
      prevX = e.clientX;
      prevY = e.clientY;

      planet.rotation.y += dx * 0.006;
      planet.rotation.x = Math.max(-0.65, Math.min(0.65, planet.rotation.x + dy * 0.004));

      if (reducedMotion.matches) renderOnce();
    };

    const onPointerUp = () => {
      if (!isDragging) return;
      isDragging = false;
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);
    };

    const onPointerDown = (e: PointerEvent) => {
      if (!isExploringRef.current) return;
      isDragging = true;
      prevX = e.clientX;
      prevY = e.clientY;
      window.addEventListener("pointermove", onPointerMove, { passive: true });
      window.addEventListener("pointerup", onPointerUp, { passive: true });
      window.addEventListener("pointercancel", onPointerUp, { passive: true });
    };

    const domElement = renderer.domElement;
    domElement.addEventListener("pointerdown", onPointerDown, { passive: true });

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
      const delta = (time - lastTime) / 1000;
      lastTime = time;

      if (!isDragging && !isExploringRef.current) {
        planet.rotation.y += rotationSpeed * delta;
      }

      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };

    const syncMotion = () => {
      if (!ready || disposed) return;
      if (reducedMotion.matches) {
        cancelAnimationFrame(animationFrameId);
        renderOnce();
      } else {
        lastTime = performance.now();
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    reducedMotion.addEventListener("change", syncMotion);
    resize();

    return () => {
      disposed = true;
      reducedMotion.removeEventListener("change", syncMotion);
      resizeObserver.disconnect();
      cancelAnimationFrame(animationFrameId);
      domElement.removeEventListener("pointerdown", onPointerDown);
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

  return <div ref={mount} className={className ?? "size-full"} />;
}
