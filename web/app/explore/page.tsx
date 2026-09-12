import { listEvents, type DataKind } from "@/lib/api";
import { EventCard } from "@/components/EventCard";
import { Narrator } from "@/components/Narrator";
import { FilterBar } from "./FilterBar";

export const dynamic = "force-dynamic";

/**
 * Event browser.
 *
 * Fetched on the server so the list is present in the first HTML response:
 * no spinner, no client-side waterfall, and the page is useful without
 * JavaScript. The filter is a plain link-based control for the same reason.
 */
export default async function Explore({
  searchParams,
}: {
  searchParams: Promise<{ kind?: string }>;
}) {
  const { kind } = await searchParams;
  const dataKind =
    kind === "measured" || kind === "simulated" ? (kind as DataKind) : undefined;

  let data;
  try {
    data = await listEvents({ dataKind, limit: 200 });
  } catch {
    return (
      <main className="mx-auto max-w-6xl px-6 py-16">
        <h1 className="font-display text-3xl tracking-wide">Explore</h1>
        <Narrator slot="api_error" className="mt-6 max-w-xl" />
        <p className="mt-4 text-sm text-dim">
          The API is not reachable. Start it with{" "}
          <code className="tabular text-muted">
            uvicorn collider.api.app:app --reload
          </code>
          .
        </p>
      </main>
    );
  }

  const narratorSlot =
    dataKind === "measured"
      ? "filter_measured"
      : dataKind === "simulated"
        ? "filter_simulated"
        : "explore_default";

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl tracking-wide text-paper">
            Explore
          </h1>
          <p className="mt-1 text-sm text-muted">
            <span className="tabular text-paper/80">{data.total}</span> events
            {dataKind ? ` · ${dataKind} only` : " · real data and simulation"}
          </p>
        </div>
        <FilterBar active={dataKind} />
      </div>

      <Narrator slot={narratorSlot} className="mt-6 max-w-2xl" />

      {data.events.length === 0 ? (
        <div className="mt-10">
          <Narrator slot="filter_empty" className="max-w-xl" />
        </div>
      ) : (
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.events.map((event) => (
            <EventCard key={event.event_id} event={event} />
          ))}
        </div>
      )}
    </main>
  );
}
