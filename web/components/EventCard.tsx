import Link from "next/link";
import type { EventSummary } from "@/lib/api";
import { DataKindBadge } from "./DataKindBadge";

const TILTS = ["", "askew-b", "askew-a"] as const;

/** One row in the explore list. */
export function EventCard({ event, index = 0 }: { event: EventSummary; index?: number }) {
  const headline = Object.entries(event.headline ?? {});

  return (
    <Link
      href={`/event/${encodeURIComponent(event.event_id)}`}
      className={[
        "panel grain group block p-4 transition-colors",
        "hover:border-portal focus:outline-none focus-visible:ring-2 focus-visible:ring-portal/60",
        // Alternating tilt so a grid of cards reads as hand-placed rather than
        // machine-stamped. Cleared under prefers-reduced-motion.
        TILTS[index % TILTS.length],
      ].join(" ")}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="tabular truncate text-sm text-paper/90">
            {event.event_id}
          </div>
          <div className="mt-1 text-xs text-muted">{event.category}</div>
        </div>
        <DataKindBadge kind={event.data_kind as "measured" | "simulated"} size="sm" />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-dim">
        <span>
          <span className="tabular text-paper/70">{event.n_leptons}</span> leptons
        </span>
        <span>
          <span className="tabular text-paper/70">{event.n_objects}</span> objects
        </span>
        {headline.map(([key, value]) => (
          <span key={key}>
            {key.replace(/_/g, " ")}{" "}
            <span className="tabular text-paper/70">
              {typeof value === "number" ? value.toFixed(1) : String(value)}
            </span>{" "}
            GeV
          </span>
        ))}
      </div>

      {/* A score is never shown bare. If one exists it appears with its
          threshold on the event page; here we only note that it exists. */}
      {event.score != null && (
        <div className="mt-3 border-t border-ink pt-2 text-xs">
          <span className="text-dim">discriminant </span>
          <span className="tabular text-paper">{event.score.toFixed(3)}</span>
        </div>
      )}
    </Link>
  );
}
