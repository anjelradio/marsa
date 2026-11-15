"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { createMarsSurfaceOverlay } from "./mars-surface-overlay";

const radius = 0.96;

interface MarsPlanetProps {
  isHovered?: boolean;
  isExploring?: boolean;
  className?: string;
}

// Surface and atmosphere adapted from Aditya-567/3D-Planets (Apache-2.0)
export function MarsPlanet({
  isHovered = false,
  isExploring = false,
  className,
}: MarsPlanetProps) {
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
    const texture = loader.load("/mars/marsmap.jpg");
    texture.colorSpace = THREE.SRGBColorSpace;
    const bump = loader.load("/mars/marsbump.jpg");
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

    const surfaceOverlay = createMarsSurfaceOverlay(radius);
    scene.add(surfaceOverlay.group);

    scene.add(new THREE.AmbientLight(0xff411b, 0.09));
    const light = new THREE.DirectionalLight(0xffefe7, 10.5);
    light.position.set(6, 2.2, 3.6);
    scene.add(light);

    // Optimized Drag Interaction: Only listen to pointermove while dragging
    let isDragging = false;
    let prevX = 0;
    let prevY = 0;
    let previousPointerTime = 0;
    let angularVelocity = 0;

    const renderOnce = () => renderer.render(scene, camera);

    const onPointerMove = (e: PointerEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevX;
      const dy = e.clientY - prevY;
      const now = performance.now();
      const elapsed = Math.max(16, now - previousPointerTime) / 1000;
      prevX = e.clientX;
      prevY = e.clientY;
      previousPointerTime = now;

      planet.rotation.y += dx * 0.006;
      planet.rotation.x = Math.max(-0.65, Math.min(0.65, planet.rotation.x + dy * 0.004));
      angularVelocity = THREE.MathUtils.clamp((dx * 0.006) / elapsed, -1.8, 1.8);

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
      previousPointerTime = performance.now();
      angularVelocity = 0;
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
      camera.left = -width / height;
      camera.right = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      renderOnce();
    };

    const observer = new ResizeObserver(resize);
    observer.observe(container);
    resize();

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let previousTime = performance.now();
    let frameId: number | null = null;
    let isInViewport = true;

    const animate = (time: number) => {
      const delta = Math.min(0.05, (time - previousTime) / 1000);
      previousTime = time;

      if (!isDragging) {
        planet.rotation.y += delta * (0.012 + angularVelocity);
        angularVelocity = THREE.MathUtils.damp(angularVelocity, 0, 4.8, delta);
      }
      renderer.render(scene, camera);

      frameId = requestAnimationFrame(animate);
    };

    const stopAnimation = () => {
      if (frameId === null) return;
      cancelAnimationFrame(frameId);
      frameId = null;
    };

    const syncAnimation = () => {
      const shouldAnimate =
        !reducedMotion.matches &&
        isInViewport &&
        document.visibilityState === "visible";

      if (!shouldAnimate) {
        stopAnimation();
        renderOnce();
        return;
      }

      if (frameId === null) {
        previousTime = performance.now();
        frameId = requestAnimationFrame(animate);
      }
    };

    const intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        isInViewport = entry?.isIntersecting ?? true;
        syncAnimation();
      },
      { rootMargin: "120px" },
    );
    intersectionObserver.observe(container);

    document.addEventListener("visibilitychange", syncAnimation);
    reducedMotion.addEventListener("change", syncAnimation);
    syncAnimation();

    return () => {
      domElement.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);
      document.removeEventListener("visibilitychange", syncAnimation);
      reducedMotion.removeEventListener("change", syncAnimation);
      stopAnimation();
      intersectionObserver.disconnect();
      observer.disconnect();
      geometry.dispose();
      material.dispose();
      texture.dispose();
      bump.dispose();
      surfaceOverlay.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className={className ?? "absolute inset-0"}
    >
      {/* Outer atmospheric coronal diffusion */}
      <div
        className={`absolute -inset-[22%] pointer-events-none transition-[transform,opacity] duration-700 ease-out motion-reduce:transition-none ${
          isHovered
            ? "scale-105 opacity-100 bg-[radial-gradient(ellipse_28%_18%_at_52%_18%,#ffaf7ba0,transparent),radial-gradient(ellipse_20%_30%_at_81%_48%,#ffa775a0,transparent),radial-gradient(ellipse_23%_21%_at_68%_76%,#ff854b80,transparent)]"
            : "scale-100 opacity-80 bg-[radial-gradient(ellipse_25%_16%_at_52%_18%,#ffaf7b85,transparent),radial-gradient(ellipse_18%_28%_at_81%_48%,#ffa77585,transparent),radial-gradient(ellipse_21%_19%_at_68%_76%,#ff854b64,transparent)]"
        }`}
      />
      {/* Soft limb rim glow */}
      <div
        className={`absolute inset-[2.5%] pointer-events-none rounded-full bg-[#251006] transition-[box-shadow] duration-700 ease-out motion-reduce:transition-none [background-image:radial-gradient(ellipse_at_73%_38%,#ff975f,#180603_75%)] ${
          isHovered
            ? "shadow-[4px_-3px_24px_#ffba78df,13px_-7px_65px_#ff763aab]"
            : "shadow-[4px_-3px_14px_#ffba78b0,13px_-7px_50px_#ff763a86]"
        }`}
      />
      <div
        ref={mount}
        className={`absolute inset-0 transition-transform duration-700 ease-out motion-reduce:transition-none ${
          isHovered && !isExploring ? "scale-[1.018]" : "scale-100"
        }`}
      />
    </div>
  );
}
