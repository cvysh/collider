"use client";

import { useEffect, useRef, useState } from "react";
import type { ReconstructedObject } from "@/lib/api";
import { Narrator } from "@/components/Narrator";
import { createViewer, type SceneObject, type Viewer } from "./scene";

/**
 * Whether this browser can give us a WebGL context.
 *
 * Checked before attempting to build a scene rather than by catching a failure
 * afterwards: a capability test is cheap and deterministic, whereas recovering
 * from a half-constructed renderer is neither.
 */
function supportsWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(
      canvas.getContext("webgl2") ?? canvas.getContext("webgl"),
    );
  } catch {
    return false;
  }
}

/**
 * WebGL event display.
 *
 * React owns the surrounding DOM and the controls; `scene.ts` owns the WebGL.
 * The scene is created once on mount and driven through imperative handles, so
 * a state change never tears down GPU resources.
 *
 * Curvature is **true by default**. A 45 GeV muon deviates about 8 mm across
 * the inner detector, so the honest display is nearly straight -- which is why
 * curvature measures momentum at all. The exaggeration control is available
 * but labelled a visual aid, never presented as the measured trajectory
 * (docs/SCIENTIFIC_INTEGRITY.md section 4).
 */
export function EventViewer({
  objects,
  onSelect,
  selectedId,
  eventId,
}: {
  objects: ReconstructedObject[];
  onSelect?: (id: number | null) => void;
  selectedId?: number | null;
  eventId: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const onSelectRef = useRef(onSelect);

  const [exaggerated, setExaggerated] = useState(false);
  // Null until the user has actually toggled, so the narrator comments on a
  // deliberate action rather than on the initial render.
  const [toggled, setToggled] = useState(false);
  // Evaluated once, on the client only -- this component never renders on the
  // server. A lazy initialiser keeps it out of the effect, so no state is set
  // synchronously during an effect.
  const [supported] = useState(supportsWebGL);

  // Keeping the latest callback in a ref lets the scene be created once, rather
  // than being torn down whenever the parent re-renders with a new closure.
  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !supported) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const scene: SceneObject[] = objects.map((o) => ({
      id: o.id,
      type: o.type,
      pt: o.pt,
      eta: o.eta,
      phi: o.phi,
      charge: o.charge,
      energy: o.energy,
    }));

    const viewer = createViewer(container, scene, {
      onSelect: (id) => onSelectRef.current?.(id),
      reducedMotion: reduced,
    });
    viewerRef.current = viewer;

    const onResize = () => viewer.resize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      viewer.dispose();
      viewerRef.current = null;
    };
  }, [objects, supported]);

  useEffect(() => {
    viewerRef.current?.setCurvatureScale(exaggerated ? 60 : 1);
  }, [exaggerated]);

  useEffect(() => {
    viewerRef.current?.setSelected(selectedId ?? null);
  }, [selectedId]);

  if (!supported) {
    return (
      <div className="panel grid h-[26rem] place-items-center p-6 text-center">
        <p className="text-sm text-muted">
          WebGL is unavailable in this browser. Every quantity is in the table
          below.
        </p>
      </div>
    );
  }

  return (
    <div className="panel overflow-hidden">
      <div ref={containerRef} className="h-[26rem] w-full" />
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-edge/60 px-3 py-2">
        <p className="text-xs text-dim">
          Drag to rotate · scroll to zoom · click a track
        </p>
        <label className="flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={exaggerated}
            onChange={(e) => {
              setExaggerated(e.target.checked);
              setToggled(true);
            }}
            className="accent-mint"
          />
          <span className={exaggerated ? "text-plasma" : "text-muted"}>
            Exaggerate curvature
            {exaggerated && <span className="ml-1 font-mono">(×60, visual aid)</span>}
          </span>
        </label>
      </div>
      {exaggerated && (
        <p className="border-t border-plasma/30 bg-plasma/10 px-3 py-2 text-xs text-plasma">
          Curvature is exaggerated 60× and is not the measured trajectory. At
          these momenta real tracks deviate by millimetres.
        </p>
      )}
      {toggled && (
        <Narrator
          key={exaggerated ? "exaggerated" : "true"}
          slot={exaggerated ? "curvature_exaggerated" : "curvature_true"}
          seed={`${eventId}-${exaggerated}`}
          className="m-3"
        />
      )}
    </div>
  );
}
