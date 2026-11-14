"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { createMarsSurfaceOverlay } from "./mars-surface-overlay";

const radius = 0.96;

// Superficie y atmósfera adaptadas de Aditya-567/3D-Planets (Apache-2.0).
export function MarsPlanet() {
  const mount = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mount.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 2.8;
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2", { alpha: true, antialias: true });
    if (!context) return;

    const renderer = new THREE.WebGLRenderer({ canvas, context, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
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

    // Añade luz cálida dispersa en el lado diurno y un borde fino en la silueta.
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

    scene.add(new THREE.AmbientLight(0xff411b, 0.08));
    const light = new THREE.DirectionalLight(0xffefe7, 10);
    light.position.set(6, 2.2, 3.6);
    scene.add(light);

    const resize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      if (!width || !height) return;
      camera.left = -width / height;
      camera.right = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(container);
    resize();
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let previousTime = performance.now();
    renderer.setAnimationLoop((time) => {
      const delta = Math.min(0.05, (time - previousTime) / 1000);
      previousTime = time;
      if (!reducedMotion.matches) planet.rotation.y += delta * 0.012;
      renderer.render(scene, camera);
    });

    return () => {
      renderer.setAnimationLoop(null);
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
    <div aria-hidden="true" className="pointer-events-none absolute inset-0">
      <div className="absolute -inset-[22%] bg-[radial-gradient(ellipse_25%_16%_at_52%_18%,#ffaf7b85,transparent),radial-gradient(ellipse_18%_28%_at_81%_48%,#ffa77585,transparent),radial-gradient(ellipse_21%_19%_at_68%_76%,#ff854b64,transparent)]" />
      <div className="absolute inset-[2.5%] rounded-full bg-[#251006] shadow-[4px_-3px_14px_#ffba78b0,13px_-7px_50px_#ff763a86] [background-image:radial-gradient(ellipse_at_73%_38%,#ff975f,#180603_75%)]" />
      <div ref={mount} className="absolute inset-0" />
    </div>
  );
}
