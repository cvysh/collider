import Link from "next/link";
import type { EventSummary } from "@/lib/api";
import { DataKindBadge } from "./DataKindBadge";

/** Alternating tilt so a grid reads hand-placed, not machine-stamped. */
const TILTS = ["", "askew-b", "askew-a"] as const;

/**
 * One entry in the laboratory log.
 *
 * Presented as an instrument readout rather than a table row
 * (docs/design/BRIEF.md), but every value is the real summary from the API and
 * the measured/simulated badge is never decorative.
 */
export function EventCard({
  event,
  index = 0,
}: {
  event: EventSummary;
  index?: number;
}) {
  const headline = Object.entries(event.headline ?? {});

  return (
    <Link
      href={`/event/${encodeURIComponent(event.event_id)}`}
      className={[
        "panel grain group block transition-colors",
        "hover:border-portal focus:outline-none focus-visible:ring-2 focus-visible:ring-portal/60",
        TILTS[index % TILTS.length],
      ].join(" ")}
    >
      <div className="flex items-center justify-between border-b-2 border-ink px-3 py-1.5">
        <span className="stencil">LOG ENTRY</span>
        <span
          aria-hidden
          className={`lamp ${event.data_kind === "measured" ? "bg-portal" : "bg-toxic"}`}
        />
      </div>

      <div className="p-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="tabular truncate text-sm text-paper">
              {event.event_id}
            </div>
            <div className="mt-0.5 text-xs text-muted">{event.category}</div>
          </div>
          <DataKindBadge
            kind={event.data_kind as "measured" | "simulated"}
            size="sm"
          />
        </div>

        {/* The readout. Numbers large and monospaced; labels small and quiet. */}
        <div className="mt-3 flex flex-wrap items-end gap-x-5 gap-y-2">
          {headline.map(([key, value]) => (
            <div key={key}>
              <div className="tabular text-xl leading-none text-paper">
                {typeof value === "number" ? value.toFixed(1) : String(value)}
                <span className="ml-1 text-[10px] text-dim">GeV</span>
              </div>
              <div className="stencil mt-1">{key.replace(/_/g, " ")}</div>
            </div>
          ))}
          <div>
            <div className="tabular text-xl leading-none text-paper">
              {event.n_leptons}
            </div>
            <div className="stencil mt-1">LEPTONS</div>
          </div>
          {event.score != null && (
            <div>
              <div className="tabular text-xl leading-none text-portal">
                {event.score.toFixed(3)}
              </div>
              <div className="stencil mt-1">DISCRIMINANT</div>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
