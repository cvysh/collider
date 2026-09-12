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
import { helixPoints, type TrackInput } from "@/lib/trajectory";
import {
  CAMERA_PRESETS,
  SOLENOID_OUTER_M,
  STOPPING_RADIUS,
  SUBSYSTEMS,
} from "./detector";

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

/**
 * The detector, built from the published subsystem dimensions in detector.ts.
 *
 * One wireframe cylinder per subsystem, at its outer radius and real
 * half-length. An earlier version drew both radii plus endcap discs for all
 * seven layers; from any angled view that is dozens of overlapping ellipses
 * and the event disappeared inside them. The full radial extents stay in the
 * legend, where they can be read rather than merely seen.
 *
 * Opacity falls off with radius. The outer chambers are there to give a sense
 * of scale, not to be studied.
 */
function buildDetector(): THREE.Group {
  const group = new THREE.Group();

  for (const sys of SUBSYSTEMS) {
    const radius = sys.r[1];
    const geom = new THREE.EdgesGeometry(
      new THREE.CylinderGeometry(radius, radius, sys.halfZ * 2, radius > 2 ? 20 : 36, 1, true),
      40,
    );
    const mesh = lineOf(geom, sys.colour, sys.opacity);
    mesh.rotation.x = Math.PI / 2; // cylinder axis onto z, the beam line
    mesh.userData.subsystem = sys.id;
    group.add(mesh);
  }

  const beam = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, -12),
    new THREE.Vector3(0, 0, 12),
  ]);
  group.add(lineOf(beam, 0x3fd4ef, 0.4));

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
    // Each type stops where its physics says it stops. The helix is only valid
    // inside the solenoid, so the segment beyond it is a straight extrapolation
    // along the exit direction rather than a modelled trajectory.
    const stop = STOPPING_RADIUS[obj.type] ?? STOPPING_RADIUS.jet;
    const bent = helixPoints(obj, {
      nPoints: 40,
      curvatureScale,
      maxRadius: SOLENOID_OUTER_M,
    });
    const positions = extendStraight(bent, stop, obj.eta);
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

/**
 * Continue a track in a straight line from its last point out to `stopRadius`.
 *
 * Beyond the solenoid the field is toroidal and this project does not model it,
 * so extrapolating the helix would be inventing a trajectory. A straight
 * continuation along the exit direction is the honest approximation, and the
 * viewer labels the outer region as extrapolated.
 */
function extendStraight(
  bent: Float32Array,
  stopRadius: number,
  eta: number,
): Float32Array {
  const n = bent.length / 3;
  const ex = bent[(n - 1) * 3];
  const ey = bent[(n - 1) * 3 + 1];
  const ez = bent[(n - 1) * 3 + 2];
  const px = ex - bent[(n - 2) * 3];
  const py = ey - bent[(n - 2) * 3 + 1];
  const len = Math.hypot(px, py) || 1;
  const transverse = Math.hypot(ex, ey);
  const extra = Math.max(stopRadius - transverse, 0);

  const EXTRA_POINTS = 8;
  const out = new Float32Array((n + EXTRA_POINTS) * 3);
  out.set(bent, 0);
  for (let i = 1; i <= EXTRA_POINTS; i++) {
    const t = (extra * i) / EXTRA_POINTS;
    const j = (n + i - 1) * 3;
    out[j] = ex + (px / len) * t;
    out[j + 1] = ey + (py / len) * t;
    out[j + 2] = ez + Math.sinh(eta) * t;
  }
  return out;
}

export interface Viewer {
  setCurvatureScale(scale: number): void;
  setSelected(id: number | null): void;
  setCameraPreset(id: string): void;
  zoomBy(factor: number): void;
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
    200,
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
  let theta = CAMERA_PRESETS[0].theta;
  let phi = CAMERA_PRESETS[0].phi;
  let distance = CAMERA_PRESETS[0].distance;
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
  /**
   * Zoom only with a modifier held, or a pinch gesture (which arrives as a
   * wheel event with ctrlKey set).
   *
   * A plain wheel must scroll the page. An earlier version swallowed every
   * wheel event, which trapped the reader inside a viewer occupying most of
   * the viewport -- the canvas is large, and a control that hijacks scrolling
   * is a usability failure regardless of how good the zoom feels.
   */
  const onWheel = (e: WheelEvent) => {
    if (!e.ctrlKey && !e.metaKey) return; // let the page scroll
    e.preventDefault();
    distance = Math.min(24, Math.max(0.35, distance * (1 + e.deltaY * 0.0012)));
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
    zoomBy(factor) {
      distance = Math.min(24, Math.max(0.35, distance * factor));
      applyCamera();
    },
    setCameraPreset(id) {
      const preset = CAMERA_PRESETS.find((p) => p.id === id);
      if (!preset) return;
      theta = preset.theta;
      phi = preset.phi;
      distance = preset.distance;
      applyCamera();
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
