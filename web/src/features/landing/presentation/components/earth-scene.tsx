"use client";

import { useEffect, useRef } from "react";
import {
  AdditiveBlending,
  AmbientLight,
  DirectionalLight,
  Group,
  Mesh,
  MeshPhongMaterial,
  OrthographicCamera,
  Scene,
  ShaderMaterial,
  SphereGeometry,
  SRGBColorSpace,
  TextureLoader,
  WebGLRenderer,
} from "three";

const planetRadius = 1;
const moonRadius = 0.105;

// Texturas de los ejemplos oficiales de Three.js (examples/textures/planets).
export function EarthScene() {
  const mount = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mount.current;
    const backdrop = container?.parentElement;
    if (!container || !backdrop) return;

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2", { alpha: true, antialias: true });
    if (!context) return;

    const renderer = new WebGLRenderer({ canvas, context });
    canvas.style.visibility = "hidden";
    container.append(canvas);

    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const scene = new Scene();
    const camera = new OrthographicCamera(-1, 1, 1, -1, 0.1, 20);
    camera.position.z = 6;
    const loader = new TextureLoader();
    let disposed = false;
    let ready = false;
    let orbitAngle = 0;
    let orbitWidth = 1;
    let previousTime: number | undefined;

    const draw = () => {
      moon.position.set(
        Math.cos(orbitAngle) * orbitWidth,
        0.8 + Math.sin(orbitAngle) * 0.22,
        Math.sin(orbitAngle) * 1.45,
      );
      renderer.render(scene, camera);
      if (!canvas.hasAttribute("data-rendered")) {
        canvas.style.visibility = "visible";
        canvas.setAttribute("data-rendered", "");
      }
    };

    const earthMap = loader.load("/landing/earth.webp", () => {
      if (disposed) return;
      ready = true;
      syncMotion();
    });
    earthMap.colorSpace = SRGBColorSpace;

    const cloudMap = loader.load("/landing/clouds.webp", redraw);
    cloudMap.colorSpace = SRGBColorSpace;
    const moonMap = loader.load("/landing/moon.webp", redraw);
    moonMap.colorSpace = SRGBColorSpace;

    const globeGeometry = new SphereGeometry(planetRadius, 96, 64);
    const earthMaterial = new MeshPhongMaterial({ map: earthMap, shininess: 9, specular: 0x182233 });
    const earth = new Mesh(globeGeometry, earthMaterial);
    earth.rotation.y = -3.24;
    const cloudMaterial = new MeshPhongMaterial({
      map: cloudMap,
      transparent: true,
      opacity: 0.32,
      depthWrite: false,
      blending: AdditiveBlending,
    });
    const clouds = new Mesh(globeGeometry, cloudMaterial);
    clouds.scale.setScalar(1.005);
    clouds.rotation.y = earth.rotation.y;
    const globe = new Group();
    globe.rotation.set(-0.2, 0, -0.13);
    globe.add(earth, clouds);
    scene.add(globe);

    const atmosphereMaterial = new ShaderMaterial({
      transparent: true,
      blending: AdditiveBlending,
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
          float rim = pow(1.0 - max(normal.z, 0.0), 7.0);
          float daylight = smoothstep(-0.18, 0.92, normal.y - normal.x * 0.26);
          gl_FragColor = vec4(0.27, 0.62, 1.0, rim * daylight);
        }
      `,
    });
    const atmosphere = new Mesh(globeGeometry, atmosphereMaterial);
    atmosphere.scale.setScalar(1.008);
    scene.add(atmosphere);

    const moonGeometry = new SphereGeometry(moonRadius, 32, 24);
    const moonMaterial = new MeshPhongMaterial({ map: moonMap, shininess: 4 });
    const moon = new Mesh(moonGeometry, moonMaterial);
    scene.add(moon);

    const sun = new DirectionalLight(0xfff2df, 2.8);
    sun.position.set(-2.5, 4, 2);
    const rim = new DirectionalLight(0x4495ff, 1.3);
    rim.position.set(1, 2, -3);
    scene.add(sun, rim, new AmbientLight(0x8daaf1, 0.42));

    function redraw() {
      if (ready && !disposed) draw();
    }

    const resize = () => {
      const { clientWidth: width, clientHeight: height } = container;
      const diameter = backdrop.clientWidth;
      if (!width || !height || !diameter) return;

      // Mantiene el tamaño de la Tierra al ampliar el canvas para la órbita.
      const unitsPerPixel = (2 * planetRadius) / diameter;
      camera.right = (width * unitsPerPixel) / 2;
      camera.left = -camera.right;
      camera.top = planetRadius - container.offsetTop * unitsPerPixel;
      camera.bottom = camera.top - height * unitsPerPixel;
      orbitWidth = (document.documentElement.clientWidth * unitsPerPixel) / 2 + moonRadius;
      camera.updateProjectionMatrix();
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
      renderer.setSize(width, height);
      redraw();
    };

    function syncMotion() {
      renderer.setAnimationLoop(null);
      previousTime = undefined;
      if (!ready || document.hidden) return;

      draw();
      if (motion.matches) return;

      renderer.setAnimationLoop((time) => {
        const delta = Math.min(0.05, (time - (previousTime ?? time)) / 1000);
        previousTime = time;
        earth.rotation.y += delta * 0.065;
        clouds.rotation.y += delta * 0.081;
        orbitAngle += delta * 0.16;
        draw();
      });
    }

    const observer = new ResizeObserver(resize);
    observer.observe(container);
    observer.observe(backdrop);
    observer.observe(document.documentElement);
    resize();
    motion.addEventListener("change", syncMotion);
    document.addEventListener("visibilitychange", syncMotion);

    return () => {
      disposed = true;
      renderer.setAnimationLoop(null);
      observer.disconnect();
      motion.removeEventListener("change", syncMotion);
      document.removeEventListener("visibilitychange", syncMotion);
      globeGeometry.dispose();
      moonGeometry.dispose();
      earthMaterial.dispose();
      cloudMaterial.dispose();
      atmosphereMaterial.dispose();
      moonMaterial.dispose();
      earthMap.dispose();
      cloudMap.dispose();
      moonMap.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      canvas.remove();
    };
  }, []);

  return (
    <div
      ref={mount}
      className="absolute bottom-0 left-1/2 w-[max(100%,100vw)] -translate-x-1/2"
      style={{ top: "calc(-0.15 * var(--earth-diameter))" }}
    />
  );
}
