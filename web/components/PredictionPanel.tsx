import type { EventPayload } from "@/lib/api";
import { Narrator } from "./Narrator";

/**
 * The laboratory's analysis readout.
 *
 * Presented as an instrument panel, per docs/design/BRIEF.md. Three rules from
 * SCIENTIFIC_INTEGRITY.md survive the styling intact, because the brief's own
 * priority order puts scientific correctness above visual personality:
 *
 * 1. The number is a **discriminant**, never a probability or a confidence.
 *    The training class balance was chosen, so there is no prior to read
 *    against.
 * 2. The threshold is always shown with it. A bare score is not reportable.
 * 3. Where no score exists, the reason is shown. Absent values are reported,
 *    never invented.
 *
 * Contribution bars are real per-event SHAP values over the features the model
 * actually uses. Invariant mass does not appear among them and cannot: it is
 * deliberately excluded from the feature set (FINDINGS.md #5).
 */

const FEATURE_LABELS: Record<string, string> = {
  m_z1: "Z₁ mass",
  m_z2: "Z₂ mass",
  m_z2_over_m_z1: "Z₂ / Z₁",
  lep_pt_0: "lepton 1 pT",
  lep_pt_1: "lepton 2 pT",
  lep_pt_2: "lepton 3 pT",
  lep_pt_3: "lepton 4 pT",
  lep_abs_eta_max: "max |η|",
  pt_4l: "system pT",
  delta_phi_zz: "Δφ(Z,Z)",
  delta_eta_zz: "Δη(Z,Z)",
  met: "missing ET",
  jet_n: "jet count",
  n_muons: "muon count",
};

function Casing({ children, label }: { children: React.ReactNode; label: string }) {
  return (
    <section className="panel rivets relative p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="stencil">{label}</h2>
        <span aria-hidden className="lamp bg-portal" />
      </div>
      {children}
    </section>
  );
}

export function PredictionPanel({ event }: { event: EventPayload }) {
  const prediction = event.prediction;

  if (!prediction) {
    return (
      <Casing label="ANALYSIS — OFFLINE">
        <p className="text-sm text-muted">No score for this event.</p>
        {event.prediction_unavailable_reason && (
          <p className="mt-2 text-xs leading-relaxed text-dim">
            {event.prediction_unavailable_reason}
          </p>
        )}
        <Narrator slot="model_cannot_score" seed={event.event_id} className="mt-4" />
      </Casing>
    );
  }

  const { score, threshold, classification, model_id } = prediction;
  const contributions = prediction.contributions ?? [];
  const nearThreshold = Math.abs(score - threshold) < 0.05;
  const disagrees =
    event.truth_label != null &&
    (classification === "signal-like") !== (event.truth_label === "signal");
  const signalLike = classification === "signal-like";
  const maxContribution = Math.max(
    ...contributions.map((c) => Math.abs(c.contribution)),
    0.001,
  );

  return (
    <Casing label="ANALYSIS — COMPLETE">
      <div className="flex items-end justify-between gap-3">
        <div>
          <div
            className={`tabular text-5xl leading-none ${signalLike ? "text-portal" : "text-muted"}`}
          >
            {score.toFixed(3)}
          </div>
          <div className="stencil mt-1.5">DISCRIMINANT</div>
        </div>
        <div
          className={`border-2 border-ink px-2 py-1 text-xs ${
            signalLike ? "bg-portal text-ground" : "bg-panel-hi text-muted"
          }`}
          style={{ borderRadius: "9px 5px 10px 4px" }}
        >
          {classification}
        </div>
      </div>

      {/* Threshold marker sits on the same bar: the score cannot be shown
          without it. */}
      <div className="meter relative mt-3 h-3 rounded-full">
        <div
          className={`h-full rounded-full ${signalLike ? "bg-portal" : "bg-muted"}`}
          style={{ width: `${Math.min(score, 1) * 100}%` }}
        />
        <div
          className="absolute top-[-4px] h-[calc(100%+8px)] w-[3px] bg-hazard"
          style={{ left: `${threshold * 100}%` }}
          title={`Threshold ${threshold.toFixed(3)}`}
        />
      </div>
      <div className="mt-1.5 flex justify-between text-[10px] text-dim">
        <span className="tabular">0.000</span>
        <span className="tabular text-hazard">
          threshold {threshold.toFixed(3)}
        </span>
        <span className="tabular">1.000</span>
      </div>

      {contributions.length > 0 && (
        <div className="mt-5">
          <h3 className="stencil">WHAT MOVED THE SCORE</h3>
          <ul className="mt-2 space-y-1.5">
            {contributions.map((c) => {
              const width = (Math.abs(c.contribution) / maxContribution) * 50;
              const positive = c.contribution > 0;
              return (
                <li key={c.feature} className="grid grid-cols-[6.5rem_1fr_3.2rem] items-center gap-2">
                  <span className="truncate text-[11px] text-muted">
                    {FEATURE_LABELS[c.feature] ?? c.feature}
                  </span>
                  {/* Diverging from a centre zero: sign is direction, length is
                      magnitude. */}
                  <span className="meter relative flex h-3 rounded-sm">
                    <span className="absolute left-1/2 top-0 h-full w-px bg-ink-soft" />
                    <span
                      className={`absolute top-0 h-full ${positive ? "bg-portal" : "bg-bruise"}`}
                      style={{
                        left: positive ? "50%" : `${50 - width}%`,
                        width: `${width}%`,
                      }}
                    />
                  </span>
                  <span className="tabular text-right text-[11px] text-dim">
                    {c.value.toFixed(1)}
                  </span>
                </li>
              );
            })}
          </ul>
          <p className="mt-2 text-[10px] leading-relaxed text-dim">
            Per-event SHAP contributions. Green pushed the score up, purple down.
            These describe what the model used — not what caused the physics.
          </p>
        </div>
      )}

      <dl className="mt-5 space-y-1.5 border-t-2 border-ink pt-3 text-xs">
        {event.truth_label && (
          <div className="flex justify-between">
            <dt className="text-dim">Truth label (simulation)</dt>
            <dd className={disagrees ? "text-alarm" : "text-muted"}>
              {event.truth_label}
              {disagrees && " — model disagreed"}
            </dd>
          </div>
        )}
        <div className="flex justify-between">
          <dt className="text-dim">Model</dt>
          <dd className="tabular text-muted">{model_id}</dd>
        </div>
      </dl>

      <p className="mt-3 text-[10px] leading-relaxed text-dim">
        A discriminant, not a probability. The training class balance was chosen,
        not measured, so this is not the chance that the event is signal.
      </p>

      {disagrees ? (
        <Narrator slot="prediction_wrong" seed={event.event_id} className="mt-4" />
      ) : nearThreshold ? (
        <Narrator slot="score_near_threshold" seed={event.event_id} className="mt-4" />
      ) : (
        <Narrator slot="score_shown" seed={event.event_id} className="mt-4" />
      )}
    </Casing>
  );
}
