import { ApiError, getDistribution } from "@/lib/api";
import { MassSpectrum } from "@/components/MassSpectrum";
import { Narrator } from "@/components/Narrator";

export const dynamic = "force-dynamic";

export default async function PhysicsPage() {
  let spectrum;
  try {
    spectrum = await getDistribution("m_4l");
  } catch (err) {
    const missing = err instanceof ApiError && err.status === 404;
    return (
      <main className="mx-auto max-w-4xl px-6 py-16">
        <h1 className="font-display text-3xl tracking-wide">The spectrum</h1>
        <Narrator slot={missing ? "event_not_found" : "api_error"} className="mt-6 max-w-xl" />
      </main>
    );
  }

  const sig = spectrum.totals.signal;
  const bkg = spectrum.totals.background;

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl tracking-wide text-paper">The spectrum</h1>
      <p className="mt-2 max-w-2xl text-sm text-muted">
        Add up the energy and momentum of four leptons and you get the mass of
        whatever produced them. Do it for enough events and a particle shows up
        as a bump.
      </p>

      <Narrator slot="mass_bump" className="mt-6 max-w-2xl" />

      <div className="mt-6">
        <MassSpectrum spectrum={spectrum} />
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          [sig.toFixed(1), "expected signal events"],
          [bkg.toFixed(0), "expected background events"],
          [(sig / bkg).toFixed(3), "signal-to-background, integrated"],
        ].map(([value, label]) => (
          <div key={label} className="panel p-4">
            <div className="tabular text-2xl text-portal">{value}</div>
            <div className="mt-1 text-xs text-dim">{label}</div>
          </div>
        ))}
      </div>

      <section className="panel mt-6 p-5">
        <h2 className="text-sm text-paper">Why the classifier never sees this</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted">
          The four-lepton mass is by far the most discriminating variable
          available — signal sits at 125 GeV, background does not. Feeding it to
          the model would produce a near-perfect classifier that had learned
          nothing except where to look.
        </p>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          It would also be self-defeating. Cutting on a score that depends on
          mass carves a bump-shaped deficit into this very spectrum, destroying
          the ability to fit it for an excess. The mass is the measurement, so it
          must not be the thing we cut on. The model uses the other kinematics;
          the spectrum stays honest.
        </p>
      </section>

      <section className="mt-6">
        <h2 className="text-xs uppercase tracking-wider text-dim">
          What this plot is not
        </h2>
        <ul className="mt-2 space-y-2">
          {spectrum.caveats.map((c) => (
            <li key={c} className="flex gap-2 text-xs leading-relaxed text-muted">
              <span aria-hidden className="text-dim">—</span>
              <span>{c}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
