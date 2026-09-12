import Link from "next/link";
import { listModels } from "@/lib/api";
import { Narrator } from "@/components/Narrator";

export const dynamic = "force-dynamic";

const PIPELINE = [
  {
    step: "Source",
    detail: "ATLAS Open Data, 13 TeV, 2015–2016, CC0",
    note: "36 fb⁻¹ of proton-proton collisions. Real detector data and Monte Carlo simulation, from the same release.",
  },
  {
    step: "Read",
    detail: "uproot + awkward",
    note: "ROOT ntuples hold a variable number of particles per event. Jagged arrays, not rows — the whole column is operated on at once, never looped.",
  },
  {
    step: "Validate",
    detail: "Four resonances at their known masses",
    note: "The dimuon spectrum reproduces J/ψ, ψ(2S), Υ and Z. The J/ψ lands within 2 MeV of the PDG value, which rules out a momentum-scale error.",
  },
  {
    step: "Select",
    detail: "Four tight, isolated, charge-balanced leptons",
    note: "Not cosmetic. Raw 4-lepton data is dominated by fake leptons: 17.7% of its leptons pass tight ID against 87% in simulation.",
  },
  {
    step: "Weight",
    detail: "Cross-section × luminosity ÷ generated weight",
    note: "Simulation is produced in convenient proportions, not physical ones. Weights invert the sample by a factor of about 1,000.",
  },
  {
    step: "Train",
    detail: "XGBoost, 14 features, m₄ℓ withheld",
    note: "Fitted on class-balanced weights, evaluated on physical ones. The mass is excluded so a score cut cannot sculpt the spectrum.",
  },
  {
    step: "Serve",
    detail: "Precomputed scores, static event artifacts",
    note: "Predictions are deterministic for a fixed event and model, so they are computed once. A payload is 826 bytes gzipped.",
  },
];

const NUMBERS = [
  ["0.9882", "test ROC-AUC"],
  ["826 B", "event payload, gzipped"],
  ["134 KB", "JS on the landing page"],
  ["136", "tests"],
];

export default async function About() {
  let models: Awaited<ReturnType<typeof listModels>> = [];
  try {
    models = await listModels();
  } catch {
    models = [];
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl tracking-wide text-paper">How it works</h1>
      <p className="mt-2 max-w-2xl text-sm text-muted">
        Real collision data from CERN, a reproducible pipeline, and a classifier
        that is careful about what it claims.
      </p>

      <dl className="mt-8 grid gap-3 sm:grid-cols-4">
        {NUMBERS.map(([value, label]) => (
          <div key={label} className="panel p-4">
            <dt className="tabular text-xl text-portal">{value}</dt>
            <dd className="mt-1 text-xs text-dim">{label}</dd>
          </div>
        ))}
      </dl>

      <section className="mt-12">
        <h2 className="text-xs uppercase tracking-wider text-dim">The pipeline</h2>
        <ol className="mt-4 space-y-0">
          {PIPELINE.map((p, i) => (
            <li key={p.step} className="relative flex gap-4 pb-6 last:pb-0">
              {i < PIPELINE.length - 1 && (
                <span
                  aria-hidden
                  className="absolute left-[11px] top-6 h-full w-px bg-ink-soft"
                />
              )}
              <span
                aria-hidden
                className="relative mt-1 size-[23px] shrink-0 rounded-full border border-portal/50 bg-ground text-center font-mono text-[11px] leading-[21px] text-portal"
              >
                {i + 1}
              </span>
              <div className="min-w-0">
                <h3 className="text-sm text-paper">
                  {p.step}
                  <span className="ml-2 font-mono text-xs text-portal/80">{p.detail}</span>
                </h3>
                <p className="mt-1 text-xs leading-relaxed text-muted">{p.note}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-12">
        <h2 className="text-xs uppercase tracking-wider text-dim">
          What the model is, and is not
        </h2>
        <Narrator slot="limitations_panel" className="mt-4 max-w-2xl" />
        {models.length === 0 ? (
          <p className="mt-4 text-sm text-muted">Model registry unavailable.</p>
        ) : (
          models.map((m) => (
            <div key={m.model_id} className="panel mt-4 p-5">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <h3 className="tabular text-sm text-paper">{m.model_id}</h3>
                <span className="text-xs text-dim">{m.framework}</span>
              </div>
              <dl className="mt-3 grid gap-x-6 gap-y-2 text-xs sm:grid-cols-3">
                {[
                  ["Task", m.task],
                  ["Features", `${m.n_features} (${m.feature_set_version})`],
                  ["Threshold", `${m.threshold.toFixed(3)} (${m.threshold_selected_on})`],
                  ...Object.entries(m.metrics).map(([k, v]) => [
                    k.replace(/_/g, " "),
                    typeof v === "number" ? v.toFixed(4) : String(v),
                  ]),
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt className="text-dim">{label}</dt>
                    <dd className="tabular mt-0.5 text-muted">{value}</dd>
                  </div>
                ))}
              </dl>
              <h4 className="mt-5 text-xs uppercase tracking-wider text-dim">
                Limitations
              </h4>
              <ul className="mt-2 space-y-2">
                {m.limitations.map((l) => (
                  <li key={l} className="flex gap-2 text-xs leading-relaxed text-muted">
                    <span aria-hidden className="text-alarm">—</span>
                    <span>{l}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </section>

      <section className="panel mt-12 p-5">
        <h2 className="text-sm text-paper">The one thing worth knowing</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted">
          Labelled data is simulation. A real collision carries no truth label —
          nobody knows what any individual event &ldquo;was&rdquo;. So the
          classifier is trained and evaluated entirely on simulation, and a score
          on measured data is a number with nothing to check it against.
        </p>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          That is why every event here is badged, why the score is called a
          discriminant rather than a probability, and why the two-muon events
          carry no score at all: the model was built for four leptons, and
          inventing the missing features to force a number would be fabrication.
        </p>
        <div className="mt-4 flex flex-wrap gap-3 text-xs">
          <Link href="/physics" className="text-portal hover:underline">
            See the mass spectrum →
          </Link>
          <a
            href="https://opendata.cern.ch/record/93910"
            className="text-toxic hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            The source dataset →
          </a>
        </div>
      </section>
    </main>
  );
}
