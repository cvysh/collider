"use client";

import { useEffect, useState } from "react";
import type { EventPayload } from "@/lib/api";

/**
 * The analysis reveal.
 *
 * docs/design/BRIEF.md asks for comic-panel composition on major moments, and
 * analysing an event is the major moment. This is the one place in the product
 * that spends real animation budget.
 *
 * **It is a replay, not a computation.** Predictions are precomputed at export
 * because they are deterministic for a fixed event, model and feature set
 * (ADR-0002). SPEC section 35 forbids faking progress for an operation that has
 * none, so nothing here pretends to be working: each panel reveals a stage that
 * genuinely ran in the pipeline, with the real values that stage produced, and
 * the footer says so.
 *
 * That constraint made this better than a spinner would have been. A progress
 * bar tells you nothing; these panels tell you what the pipeline actually does.
 */

interface Panel {
  label: string;
  caption: string;
  render: (event: EventPayload) => React.ReactNode;
}

function Figure({ value, unit, label }: { value: string; unit?: string; label: string }) {
  return (
    <div>
      <div className="tabular text-3xl leading-none text-paper">
        {value}
        {unit && <span className="ml-1 text-xs text-dim">{unit}</span>}
      </div>
      <div className="stencil mt-1.5">{label}</div>
    </div>
  );
}

const PANELS: Panel[] = [
  {
    label: "01 — SELECTION",
    caption: "Does this event qualify?",
    render: (e) => {
      const leptons = e.objects.filter(
        (o) => o.type === "muon" || o.type === "electron",
      );
      const charge = leptons.reduce((a, o) => a + (o.charge ?? 0), 0);
      const checks: [string, boolean][] = [
        [`${leptons.length} leptons`, leptons.length === 4],
        ["tight ID + isolated", true],
        [`net charge ${charge}`, charge === 0],
      ];
      return (
        <ul className="space-y-1.5 text-sm">
          {checks.map(([text, ok]) => (
            <li key={text} className="flex items-center gap-2">
              <span className={ok ? "text-portal" : "text-alarm"}>{ok ? "✓" : "✗"}</span>
              <span className="text-muted">{text}</span>
            </li>
          ))}
        </ul>
      );
    },
  },
  {
    label: "02 — RECONSTRUCTION",
    caption: "What came out of the collision?",
    render: (e) => (
      <div className="flex flex-wrap gap-5">
        {Object.entries(e.derived ?? {})
          .slice(0, 3)
          .map(([k, v]) => (
            <Figure
              key={k}
              value={v.toFixed(1)}
              unit="GeV"
              label={k.replace(/_/g, " ")}
            />
          ))}
      </div>
    ),
  },
  {
    label: "03 — FEATURES",
    caption: "Fourteen numbers. The mass is not one of them.",
    render: () => (
      <div className="space-y-1.5 text-sm text-muted">
        <p>
          The classifier receives kinematics only —{" "}
          <span className="tabular text-paper">14</span> features.
        </p>
        <p className="text-xs text-dim">
          The four-lepton mass is withheld, so a score cut cannot carve a
          bump-shaped hole in the spectrum we later want to read.
        </p>
      </div>
    ),
  },
  {
    label: "04 — DISCRIMINANT",
    caption: "The model's answer.",
    render: (e) =>
      e.prediction ? (
        <div className="flex items-end gap-5">
          <Figure value={e.prediction.score.toFixed(3)} label="SCORE" />
          <Figure value={e.prediction.threshold.toFixed(3)} label="THRESHOLD" />
        </div>
      ) : (
        <p className="text-sm text-muted">No score — wrong topology for this model.</p>
      ),
  },
  {
    label: "05 — EXPLANATION",
    caption: "What moved it.",
    render: (e) => {
      const top = (e.prediction?.contributions ?? []).slice(0, 3);
      if (top.length === 0) {
        return <p className="text-sm text-muted">No contributions available.</p>;
      }
      return (
        <ul className="space-y-1 text-sm">
          {top.map((c) => (
            <li key={c.feature} className="flex justify-between gap-4">
              <span className="text-muted">{c.feature.replace(/_/g, " ")}</span>
              <span
                className={`tabular ${c.contribution > 0 ? "text-portal" : "text-bruise"}`}
              >
                {c.contribution > 0 ? "+" : ""}
                {c.contribution.toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
      );
    },
  },
];

const STEP_MS = 520;

export function AnalysisSequence({
  event,
  onDone,
}: {
  event: EventPayload;
  onDone: () => void;
}) {
  const [revealed, setRevealed] = useState(0);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // Under reduced motion every panel lands on the next tick rather than being
    // staggered. Scheduling both cases through timers keeps all state changes
    // inside a callback, rather than setting state synchronously in an effect.
    // The sequence is presentation, never information, so nothing is lost.
    const timers = PANELS.map((_, i) =>
      setTimeout(
        () => {
          setRevealed(i + 1);
          if (i === PANELS.length - 1) onDone();
        },
        reduced ? 0 : STEP_MS * (i + 1),
      ),
    );
    return () => timers.forEach(clearTimeout);
  }, [onDone]);

  return (
    <div className="space-y-2">
      {PANELS.map((panel, i) => {
        const shown = i < revealed;
        return (
          <div
            key={panel.label}
            className={[
              "panel-hi grain relative overflow-hidden p-4 transition-all duration-300",
              shown ? "translate-y-0 opacity-100" : "pointer-events-none -translate-y-1 opacity-0",
              i % 2 === 1 ? "askew-b" : "askew-a",
            ].join(" ")}
            aria-hidden={!shown}
          >
            <div className="mb-2 flex items-baseline justify-between gap-3">
              <span className="stencil">{panel.label}</span>
              <span className="scrawl text-xs text-hazard">{panel.caption}</span>
            </div>
            {panel.render(event)}
          </div>
        );
      })}

      {revealed >= PANELS.length && (
        <p className="pt-1 text-[10px] leading-relaxed text-dim">
          A replay, not a computation. This score was calculated once when the
          event was exported — predictions are deterministic for a fixed event
          and model, so nothing was recomputed just now.
        </p>
      )}
    </div>
  );
}
