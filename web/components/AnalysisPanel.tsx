"use client";

import { useCallback, useState } from "react";
import type { EventPayload } from "@/lib/api";
import { AnalysisSequence } from "./AnalysisSequence";
import { Narrator } from "./Narrator";
import { PredictionPanel } from "./PredictionPanel";

/**
 * Gates the analysis behind a deliberate action, per SPEC section 6.5.
 *
 * Three states: idle with a button, the comic-panel replay, then the full
 * readout. The replay is skippable — someone returning to an event they have
 * already seen should not have to watch it again, and an animation nobody can
 * escape is a usability failure regardless of how good it looks.
 */
export function AnalysisPanel({ event }: { event: EventPayload }) {
  const [phase, setPhase] = useState<"idle" | "running" | "done">("idle");
  const handleDone = useCallback(() => setPhase("done"), []);

  if (phase === "done") {
    return <PredictionPanel event={event} />;
  }

  if (phase === "running") {
    return (
      <div className="space-y-2">
        <AnalysisSequence event={event} onDone={handleDone} />
        <button
          onClick={handleDone}
          className="text-[11px] text-dim underline decoration-dotted hover:text-paper"
        >
          Skip
        </button>
      </div>
    );
  }

  return (
    <section className="panel rivets relative p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="stencil">ANALYSIS — STANDBY</h2>
        <span aria-hidden className="lamp bg-hazard" />
      </div>

      <p className="text-sm leading-relaxed text-muted">
        {event.prediction
          ? "The classifier has a score for this event."
          : "This event is outside the model's topology."}
      </p>

      <button
        onClick={() => setPhase("running")}
        className="mt-4 w-full border-2 border-ink bg-portal px-4 py-3 font-display text-lg tracking-wide text-ground shadow-[3px_3px_0_0_var(--color-ink)] transition-transform hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0_0_var(--color-ink)] focus:outline-none focus-visible:ring-2 focus-visible:ring-portal"
        style={{ borderRadius: "14px 9px 15px 8px" }}
      >
        ANALYSE EVENT
      </button>

      <p className="scrawl mt-3 text-center text-xs text-dim">
        nothing has ever gone wrong here
      </p>

      <Narrator slot="analysis_starts" seed={event.event_id} className="mt-4" />
    </section>
  );
}
