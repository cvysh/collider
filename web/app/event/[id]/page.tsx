import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiError, getEvent } from "@/lib/api";
import { DataKindBadge } from "@/components/DataKindBadge";
import { DerivedQuantities } from "@/components/DerivedQuantities";
import { Narrator } from "@/components/Narrator";
import { ParticleTable } from "@/components/ParticleTable";
import { PredictionPanel } from "@/components/PredictionPanel";
import { ProvenanceDrawer } from "@/components/ProvenanceDrawer";

export const dynamic = "force-dynamic";

/**
 * Single event view.
 *
 * Built 2D-first. The tabular view is not a degraded mode -- it is the
 * accessible presentation SPEC section 37 requires, and every quantity the 3D
 * scene will show is readable here. Building it first also means the page is
 * never broken while the viewer is in progress.
 */
export default async function EventPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let event;
  try {
    event = await getEvent(id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    return (
      <main className="mx-auto max-w-6xl px-6 py-16">
        <Narrator slot="api_error" seed={id} className="max-w-xl" />
      </main>
    );
  }

  const measured = event.data_kind === "measured";
  const leptons = event.objects.filter(
    (o) => o.type === "muon" || o.type === "electron",
  );

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Link href="/explore" className="text-xs text-dim hover:text-paper">
        ← Explore
      </Link>

      <header className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="tabular text-2xl text-paper">{event.event_id}</h1>
          <p className="mt-1 text-sm text-muted">
            {event.experiment} · {event.collision_energy_tev} TeV beams
            {event.mc_process && (
              <>
                {" · "}
                <span className="tabular">{event.mc_process}</span>
              </>
            )}
          </p>
        </div>
        <DataKindBadge kind={event.data_kind as "measured" | "simulated"} />
      </header>

      <Narrator
        slot={measured ? "measured_event_opened" : "simulated_event_opened"}
        seed={event.event_id}
        className="mt-5 max-w-2xl"
      />

      <div className="mt-8 grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        {/* min-w-0 is load-bearing. Grid items default to min-width:auto, so
            without it the table's min-width stretches this column and the whole
            page scrolls horizontally instead of the table scrolling inside its
            own container. */}
        <div className="min-w-0 space-y-4">
          {/* The 3D scene will mount above this table, never replace it. */}
          <section>
            <h2 className="mb-2 text-xs uppercase tracking-wider text-dim">
              Reconstructed objects
              <span className="tabular ml-2 text-paper/70">{event.objects.length}</span>
            </h2>
            <ParticleTable objects={event.objects} />
          </section>

          {/* The line names four particles, so it fires only when there are
              four. A narrator that misstates what is on screen is worse than
              silence. */}
          {leptons.length === 4 && (
            <Narrator slot="sparse_event" seed={event.event_id} className="max-w-xl" />
          )}
        </div>

        <div className="min-w-0 space-y-4">
          <DerivedQuantities derived={event.derived ?? {}} />

          {event.missing_energy && (
            <section className="panel p-4">
              <h2 className="text-xs uppercase tracking-wider text-dim">
                Missing transverse energy
              </h2>
              <p className="tabular mt-2 text-lg text-paper">
                {event.missing_energy.magnitude.toFixed(1)}
                <span className="ml-1 text-xs text-dim">GeV</span>
              </p>
              <p className="mt-1 text-xs text-dim">
                Momentum imbalance implying particles the detector cannot see.
              </p>
            </section>
          )}

          <PredictionPanel event={event} />
          <ProvenanceDrawer provenance={event.provenance} eventId={event.event_id} />
        </div>
      </div>
    </main>
  );
}
