/**
 * Three.js scene construction for an event display.
 *
 * Kept out of React entirely. React owns the DOM and the controls; this module
 * owns the WebGL scene. Mixing them means every state change risks a React
 * re-render tearing down GPU resources, which is the most common way one of
 * these apps becomes slow.
 *
 * On the geometry budget: an event here has about four objects
 * (docs/FINDINGS.md #5). That is tens of vertices, not thousands. There is
 * deliberately no InstancedMesh, no level-of-detail system and no manual
 * frustum culling -- SPEC section 19.4 proposes all three, and each solves a
 * problem this project does not have. Adding them would be unmeasured
 * complexity, which SPEC section 65 lists as trap 6.
 */
import * as THREE from "three";
import { helixPoints, INNER_DETECTOR_RADIUS_M, type TrackInput } from "@/lib/trajectory";

export const OBJECT_COLOURS: Record<string, number> = {
  muon: 0x9bcf4f,
  electron: 0x3fbfb0,
  photon: 0xe8c547,
  jet: 0x93a894,
};

export interface SceneObject extends TrackInput {
  id: number;
  type: string;
  energy: number;
}

function lineOf(geom: THREE.BufferGeometry, colour: number, opacity: number) {
  return new THREE.LineSegments(
    geom,
    new THREE.LineBasicMaterial({ color: colour, transparent: true, opacity }),
  );
}

/** Schematic detector: barrel rings and endcap discs, deliberately not a CAD
 *  model (SPEC section 19.2). It exists to give the tracks somewhere to be. */
function buildDetector(): THREE.Group {
  const group = new THREE.Group();

  for (const [radius, opacity] of [
    [0.45, 0.5],
    [0.75, 0.38],
    [INNER_DETECTOR_RADIUS_M, 0.3],
  ] as const) {
    const geom = new THREE.EdgesGeometry(
      new THREE.CylinderGeometry(radius, radius, 3.2, 32, 1, true),
      40,
    );
    const mesh = lineOf(geom, 0x4a6b52, opacity);
    mesh.rotation.x = Math.PI / 2; // cylinder axis onto z, the beam line
    group.add(mesh);
  }

  for (const z of [-1.6, 1.6]) {
    const geom = new THREE.EdgesGeometry(
      new THREE.RingGeometry(0.12, INNER_DETECTOR_RADIUS_M, 24, 1),
    );
    const ring = lineOf(geom, 0x4a6b52, 0.42);
    ring.position.z = z;
    group.add(ring);
  }

  const beam = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, -1.9),
    new THREE.Vector3(0, 0, 1.9),
  ]);
  group.add(lineOf(beam, 0x3fbfb0, 0.45));

  return group;
}

/**
 * One track per object, as buffer-backed line geometry.
 *
 * Children carry `userData.objectId`, so a click maps back to an object
 * without the renderer knowing anything about React.
 */
export function buildTracks(objects: SceneObject[], curvatureScale: number): THREE.Group {
  const group = new THREE.Group();

  for (const obj of objects) {
    const positions = helixPoints(obj, { nPoints: 48, curvatureScale });
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const colour = OBJECT_COLOURS[obj.type] ?? OBJECT_COLOURS.jet;
    const track = new THREE.Line(
      geom,
      new THREE.LineBasicMaterial({ color: colour, transparent: true, opacity: 0.95 }),
    );
    track.userData.objectId = obj.id;
    group.add(track);

    // Marker at the track end, sized sublinearly by energy so one hard object
    // does not swamp the rest.
    const n = positions.length;
    const marker = new THREE.Mesh(
      new THREE.SphereGeometry(0.018 + 0.03 * Math.sqrt(obj.energy / 100), 12, 12),
      new THREE.MeshBasicMaterial({ color: colour }),
    );
    marker.position.set(positions[n - 3], positions[n - 2], positions[n - 1]);
    marker.userData.objectId = obj.id;
    group.add(marker);
  }
  return group;
}

export interface Viewer {
  setCurvatureScale(scale: number): void;
  setSelected(id: number | null): void;
  resize(): void;
  dispose(): void;
}

export function createViewer(
  container: HTMLElement,
  objects: SceneObject[],
  opts: { onSelect?: (id: number | null) => void; reducedMotion?: boolean } = {},
): Viewer {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / Math.max(container.clientHeight, 1),
    0.01,
    100,
  );

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, Math.max(container.clientHeight, 1));
  container.appendChild(renderer.domElement);

  scene.add(buildDetector());
  scene.add(
    new THREE.Mesh(
      new THREE.SphereGeometry(0.028, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xede6d3 }),
    ),
  );

  let tracks = buildTracks(objects, 1);
  scene.add(tracks);

  // Orbit implemented directly rather than importing OrbitControls: drag to
  // rotate and wheel to zoom is all this needs.
  let theta = Math.PI / 4;
  let phi = Math.PI / 3;
  let distance = 4.0;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  const applyCamera = () => {
    camera.position.set(
      distance * Math.sin(phi) * Math.cos(theta),
      distance * Math.cos(phi),
      distance * Math.sin(phi) * Math.sin(theta),
    );
    camera.lookAt(0, 0, 0);
  };
  applyCamera();

  const onPointerDown = (e: PointerEvent) => {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
  };
  const onPointerMove = (e: PointerEvent) => {
    if (!dragging) return;
    theta -= (e.clientX - lastX) * 0.008;
    phi = Math.min(Math.PI - 0.12, Math.max(0.12, phi - (e.clientY - lastY) * 0.008));
    lastX = e.clientX;
    lastY = e.clientY;
    applyCamera();
  };
  const onPointerUp = () => {
    dragging = false;
  };
  const onWheel = (e: WheelEvent) => {
    e.preventDefault();
    distance = Math.min(9, Math.max(1.4, distance + e.deltaY * 0.003));
    applyCamera();
  };

  const raycaster = new THREE.Raycaster();
  raycaster.params.Line = { threshold: 0.05 };
  const pointer = new THREE.Vector2();
  const onClick = (e: MouseEvent) => {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(tracks.children, false)[0];
    opts.onSelect?.(hit ? (hit.object.userData.objectId as number) : null);
  };

  const el = renderer.domElement;
  el.style.touchAction = "none";
  el.addEventListener("pointerdown", onPointerDown);
  el.addEventListener("pointermove", onPointerMove);
  el.addEventListener("pointerup", onPointerUp);
  el.addEventListener("pointercancel", onPointerUp);
  el.addEventListener("wheel", onWheel, { passive: false });
  el.addEventListener("click", onClick);

  let frame = 0;
  const loop = () => {
    frame = requestAnimationFrame(loop);
    if (!opts.reducedMotion && !dragging) {
      theta += 0.0009; // slow drift, disabled under reduced motion
      applyCamera();
    }
    renderer.render(scene, camera);
  };
  loop();

  const disposeGroup = (group: THREE.Object3D) => {
    group.traverse((child) => {
      const any = child as THREE.Mesh;
      any.geometry?.dispose();
      const mat = any.material as THREE.Material | THREE.Material[] | undefined;
      if (Array.isArray(mat)) mat.forEach((m) => m.dispose());
      else mat?.dispose();
    });
  };

  return {
    setCurvatureScale(scale) {
      scene.remove(tracks);
      disposeGroup(tracks);
      tracks = buildTracks(objects, scale);
      scene.add(tracks);
    },
    setSelected(id) {
      tracks.children.forEach((child) => {
        const mat = (child as THREE.Line).material as THREE.LineBasicMaterial;
        const isSelected = id != null && child.userData.objectId === id;
        mat.opacity = id == null ? 0.95 : isSelected ? 1 : 0.22;
      });
    },
    resize() {
      const w = container.clientWidth;
      const h = Math.max(container.clientHeight, 1);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    },
    dispose() {
      cancelAnimationFrame(frame);
      for (const [type, fn] of [
        ["pointerdown", onPointerDown],
        ["pointermove", onPointerMove],
        ["pointerup", onPointerUp],
        ["pointercancel", onPointerUp],
        ["wheel", onWheel],
        ["click", onClick],
      ] as const) {
        el.removeEventListener(type, fn as EventListener);
      }
      disposeGroup(scene);
      renderer.dispose();
      el.remove();
    },
  };
}
