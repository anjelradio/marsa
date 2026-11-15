"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

const radius = 0.96;

export interface EarthPlanetProps {
  className?: string;
  isHovered?: boolean;
  isExploring?: boolean;
  rotationSpeed?: number;
}

export function EarthPlanet({
  className,
  isHovered = false,
  isExploring = false,
  rotationSpeed = 0.010,
}: EarthPlanetProps) {
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

    const earthMap = loader.load("/landing/earth.webp", () => {
      if (disposed) return;
      ready = true;
      syncMotion();
    });
    earthMap.colorSpace = THREE.SRGBColorSpace;

    const cloudMap = loader.load("/landing/clouds.webp", () => {
      if (!disposed && ready && !document.hidden) renderer.render(scene, camera);
    });
    cloudMap.colorSpace = THREE.SRGBColorSpace;

    const globeGeometry = new THREE.SphereGeometry(radius, 80, 64);
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: earthMap,
      specular: 0x1a2638,
      shininess: 15,
    });

    const earth = new THREE.Mesh(globeGeometry, earthMaterial);

    const cloudMaterial = new THREE.MeshPhongMaterial({
      map: cloudMap,
      transparent: true,
      opacity: 0.38,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const clouds = new THREE.Mesh(globeGeometry, cloudMaterial);
    clouds.scale.setScalar(1.006);

    // Atmosphere glowing rim shader
    const atmosphereMaterial = new THREE.ShaderMaterial({
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      vertexShader: `
        varying vec3 surfaceNormal;
        void main() {
          surfaceNormal = normalMatrix * normal;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 surfaceNormal;
        void main() {
          vec3 normal = normalize(surfaceNormal);
          float rim = pow(1.0 - max(normal.z, 0.0), 6.0);
          float daylight = smoothstep(-0.2, 0.85, normal.y * 0.4 + normal.x * 0.6);
          gl_FragColor = vec4(0.24, 0.62, 1.0, rim * (daylight * 0.85 + 0.15));
        }
      `,
    });
    const atmosphere = new THREE.Mesh(globeGeometry, atmosphereMaterial);
    atmosphere.scale.setScalar(1.015);

    const planetGroup = new THREE.Group();
    // 23.44° axial tilt
    planetGroup.rotation.set(-0.12, -2.6, 0.41, "ZYX");
    planetGroup.add(earth);
    planetGroup.add(clouds);
    planetGroup.add(atmosphere);
    scene.add(planetGroup);

    scene.add(new THREE.AmbientLight(0x356396, 0.25));

    const sun = new THREE.DirectionalLight(0xfff8ee, 7.5);
    sun.position.set(5.5, 2.5, 3.5);
    scene.add(sun);

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

      planetGroup.rotation.y += dx * 0.006;
      planetGroup.rotation.x = Math.max(-0.65, Math.min(0.65, planetGroup.rotation.x + dy * 0.004));

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
        earth.rotation.y += rotationSpeed * delta;
        clouds.rotation.y += (rotationSpeed * 1.25) * delta;
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

      globeGeometry.dispose();
      earthMaterial.dispose();
      cloudMaterial.dispose();
      atmosphereMaterial.dispose();
      earthMap.dispose();
      cloudMap.dispose();
      renderer.dispose();
      if (domElement.parentNode === container) {
        container.removeChild(domElement);
      }
    };
  }, [rotationSpeed]);

  return <div ref={mount} className={className ?? "size-full"} />;
}
