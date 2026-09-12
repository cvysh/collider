"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import type { ReconstructedObject } from "@/lib/api";
import { Narrator } from "@/components/Narrator";
import { ParticleTable } from "@/components/ParticleTable";

/**
 * Loads the 3D viewer only when an event page renders.
 *
 * `ssr: false` plus a dynamic import keeps Three.js out of the shared bundle
 * entirely -- SPEC sections 6.1 and 21.2 require that the landing page not pay
 * for the 3D experience. The table renders immediately either way, so the page
 * is useful before and regardless of WebGL.
 */
const EventViewer = dynamic(
  () => import("./EventViewer").then((m) => m.EventViewer),
  {
    ssr: false,
    loading: () => (
      <div className="panel grid h-[26rem] place-items-center">
        <p className="stencil animate-pulse">
          CALIBRATING THE VERY IMPORTANT MACHINES...
        </p>
      </div>
    ),
  },
);

export function EventViewerPanel({
  objects,
  eventId,
}: {
  objects: ReconstructedObject[];
  eventId: string;
}) {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const selected = objects.find((o) => o.id === selectedId);

  return (
    <div className="space-y-4">
      <EventViewer
        objects={objects}
        eventId={eventId}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      {selected && (
        <section className="panel-hi p-4">
          <h3 className="text-xs uppercase tracking-wider text-dim">
            {selected.type}
            {selected.charge != null && (
              <span className="ml-1 font-mono">
                {selected.charge > 0 ? "+" : selected.charge < 0 ? "−" : ""}
              </span>
            )}
          </h3>
          <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm sm:grid-cols-4">
            {[
              ["pT", `${selected.pt.toFixed(1)} GeV`],
              ["Energy", `${selected.energy.toFixed(1)} GeV`],
              ["η", selected.eta.toFixed(3)],
              ["φ", selected.phi.toFixed(3)],
            ].map(([label, value]) => (
              <div key={label}>
                <dt className="text-xs text-dim">{label}</dt>
                <dd className="tabular text-paper">{value}</dd>
              </div>
            ))}
          </dl>
          <Narrator
            slot={selected.type === "muon" ? "muon_selected" : "electron_selected"}
            seed={`${eventId}-${selected.id}`}
            className="mt-4"
          />
        </section>
      )}

      <section>
        <h2 className="mb-2 text-xs uppercase tracking-wider text-dim">
          Reconstructed objects
          <span className="tabular ml-2 text-paper/70">{objects.length}</span>
        </h2>
        <ParticleTable objects={objects} selectedId={selectedId ?? undefined} />
      </section>
    </div>
  );
}
