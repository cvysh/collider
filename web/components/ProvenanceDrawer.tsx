"use client";

import { useState } from "react";
import type { Provenance } from "@/lib/api";
import { Narrator } from "./Narrator";

/**
 * Where this event came from.
 *
 * SPEC section 46 calls provenance the strongest differentiator from a generic
 * AI demo, and it is: a number that cannot be traced to a dataset, a DOI and a
 * pipeline commit is not a scientific result. Collapsed by default so it does
 * not compete with the data, but never more than one click away.
 */
export function ProvenanceDrawer({
  provenance,
  eventId,
}: {
  provenance: Provenance;
  eventId: string;
}) {
  const [open, setOpen] = useState(false);

  const rows: [string, React.ReactNode][] = [
    ["Dataset", provenance.dataset],
    [
      "Record",
      <a
        key="rec"
        href={provenance.record_url}
        className="text-cyan underline decoration-dotted"
        target="_blank"
        rel="noreferrer"
      >
        {provenance.record_url.replace("https://", "")}
      </a>,
    ],
    ["DOI", <span key="doi" className="tabular">{provenance.doi}</span>],
    ["Licence", provenance.licence],
    ["Source file", <span key="f" className="tabular break-all">{provenance.source_file}</span>],
    ["Pipeline commit", <span key="p" className="tabular">{provenance.pipeline_version}</span>],
    ["Accessed", <span key="a" className="tabular">{provenance.accessed}</span>],
  ];

  return (
    <section className="panel">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between p-4 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-mint/60"
      >
        <span className="text-xs uppercase tracking-wider text-dim">
          Data provenance
        </span>
        <span aria-hidden className="text-dim">{open ? "−" : "+"}</span>
      </button>

      {open && (
        <div className="border-t border-edge/60 p-4 pt-3">
          <dl className="space-y-2 text-xs">
            {rows.map(([label, value]) => (
              <div key={label} className="grid grid-cols-[9rem_1fr] gap-2">
                <dt className="text-dim">{label}</dt>
                <dd className="text-muted">{value}</dd>
              </div>
            ))}
          </dl>
          <Narrator slot="provenance_opened" seed={eventId} className="mt-4" />
        </div>
      )}
    </section>
  );
}
