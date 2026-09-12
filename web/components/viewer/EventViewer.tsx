"use client";

import { useEffect, useRef, useState } from "react";
import type { ReconstructedObject } from "@/lib/api";
import { Narrator } from "@/components/Narrator";
import { CAMERA_PRESETS, STOPPING_RADIUS, SUBSYSTEMS } from "./detector";
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
  const [preset, setPreset] = useState(CAMERA_PRESETS[0].id);
  const [showLegend, setShowLegend] = useState(false);
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

  useEffect(() => {
    viewerRef.current?.setCameraPreset(preset);
  }, [preset]);

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
      <div className="crt relative">
        <div ref={containerRef} className="h-[26rem] w-full" />
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t-2 border-ink px-3 py-2">
        {/* The three standard views used in real event displays. */}
        <div className="flex items-center gap-1">
          {CAMERA_PRESETS.map((p) => (
            <button
              key={p.id}
              onClick={() => setPreset(p.id)}
              title={p.hint}
              aria-pressed={preset === p.id}
              className={[
                "border-2 border-ink px-2 py-1 font-mono text-[11px] transition-colors",
                preset === p.id
                  ? "bg-portal text-ground"
                  : "bg-panel-hi text-muted hover:text-paper",
              ].join(" ")}
              style={{ borderRadius: "8px 5px 9px 4px" }}
            >
              {p.label}
            </button>
          ))}
          <span aria-hidden className="mx-1 h-4 w-px bg-ink-soft" />
          {([["−", 1.25], ["+", 0.8]] as const).map(([glyph, factor]) => (
            <button
              key={glyph}
              onClick={() => viewerRef.current?.zoomBy(factor)}
              aria-label={factor > 1 ? "Zoom out" : "Zoom in"}
              className="border-2 border-ink bg-panel-hi px-2 py-1 font-mono text-[11px] text-muted transition-colors hover:text-paper"
              style={{ borderRadius: "8px 5px 9px 4px" }}
            >
              {glyph}
            </button>
          ))}
          <button
            onClick={() => setShowLegend((v) => !v)}
            aria-expanded={showLegend}
            className="ml-1 text-[11px] text-dim underline decoration-dotted hover:text-paper"
          >
            layers
          </button>
        </div>
        <p className="text-[11px] text-dim">
          drag to rotate · ⌘/ctrl + scroll to zoom
        </p>
        <label className="flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={exaggerated}
            onChange={(e) => {
              setExaggerated(e.target.checked);
              setToggled(true);
            }}
            className="switch"
          />
          <span className={exaggerated ? "text-hazard" : "text-muted"}>
            Exaggerate curvature
            {exaggerated && <span className="ml-1 font-mono">(×60, visual aid)</span>}
          </span>
        </label>
      </div>
      {showLegend && (
        <div className="border-t-2 border-ink px-3 py-3">
          <h4 className="stencil">DETECTOR LAYERS — real ATLAS dimensions</h4>
          <ul className="mt-2 space-y-1">
            {SUBSYSTEMS.map((sys) => (
              <li key={sys.id} className="flex items-baseline gap-2 text-[11px]">
                <span
                  aria-hidden
                  className="mt-1 size-2 shrink-0 border border-ink"
                  style={{ background: `#${sys.colour.toString(16).padStart(6, "0")}` }}
                />
                <span className="w-28 shrink-0 text-muted">{sys.label}</span>
                <span className="tabular w-20 shrink-0 text-dim">
                  {sys.r[0] < 1 ? sys.r[0].toFixed(2) : sys.r[0].toFixed(1)}–
                  {sys.r[1].toFixed(1)} m
                </span>
                <span className="text-dim">{sys.note}</span>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[10px] leading-relaxed text-dim">
            Tracks stop where their physics says they stop: electrons and photons
            at {STOPPING_RADIUS.electron} m in the EM calorimeter, jets at{" "}
            {STOPPING_RADIUS.jet} m, muons out to {STOPPING_RADIUS.muon} m.
            Curvature is only computed inside the solenoid — beyond 1.3 m the
            field is toroidal and those segments are straight extrapolations,
            not modelled trajectories.
          </p>
        </div>
      )}

      {exaggerated && (
        <p className="border-t-2 border-ink bg-hazard/15 px-3 py-2 text-xs text-hazard">
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
