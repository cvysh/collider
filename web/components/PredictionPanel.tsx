import type { EventPayload } from "@/lib/api";
import { Narrator } from "./Narrator";

/**
 * Model output.
 *
 * Three rules govern this component, all from docs/SCIENTIFIC_INTEGRITY.md:
 *
 * 1. The score is a **discriminant**, never a probability. The training class
 *    balance was a choice, so there is no prior to read a probability against.
 * 2. The threshold is always shown with it. A bare number is not reportable.
 * 3. When no score exists, the reason is shown. An absent value is reported,
 *    never invented.
 */
export function PredictionPanel({ event }: { event: EventPayload }) {
  const prediction = event.prediction;

  if (!prediction) {
    return (
      <section className="panel p-4">
        <h2 className="text-xs uppercase tracking-wider text-dim">Model</h2>
        <p className="mt-3 text-sm text-muted">No score for this event.</p>
        {event.prediction_unavailable_reason && (
          <p className="mt-2 text-xs leading-relaxed text-dim">
            {event.prediction_unavailable_reason}
          </p>
        )}
        <Narrator slot="model_cannot_score" seed={event.event_id} className="mt-4" />
      </section>
    );
  }

  const { score, threshold, classification, model_id, feature_set_version } = prediction;
  const nearThreshold = Math.abs(score - threshold) < 0.05;
  const disagrees =
    event.truth_label != null &&
    ((classification === "signal-like") !== (event.truth_label === "signal"));

  return (
    <section className="panel p-4">
      <h2 className="text-xs uppercase tracking-wider text-dim">Model</h2>

      <div className="mt-3 flex items-baseline gap-3">
        <span className="tabular text-4xl text-portal">{score.toFixed(3)}</span>
        <span className="text-xs text-dim">discriminant</span>
      </div>

      {/* Threshold marker on the bar: the score is never shown without it. */}
      <div className="relative mt-3 h-2 rounded-full bg-panel-hi">
        <div
          className="h-2 rounded-full bg-portal/70"
          style={{ width: `${Math.min(score, 1) * 100}%` }}
        />
        <div
          className="absolute top-[-3px] h-3.5 w-0.5 bg-paper"
          style={{ left: `${threshold * 100}%` }}
          title={`Threshold ${threshold.toFixed(3)}`}
        />
      </div>

      <dl className="mt-4 space-y-1.5 text-xs">
        <div className="flex justify-between">
          <dt className="text-dim">Threshold</dt>
          <dd className="tabular text-muted">{threshold.toFixed(3)}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-dim">Classification</dt>
          <dd className="text-paper">{classification}</dd>
        </div>
        {event.truth_label && (
          <div className="flex justify-between">
            <dt className="text-dim">Truth label (simulation)</dt>
            <dd className={disagrees ? "text-alarm" : "text-muted"}>
              {event.truth_label}
            </dd>
          </div>
        )}
        <div className="flex justify-between">
          <dt className="text-dim">Model</dt>
          <dd className="tabular text-muted">{model_id}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-dim">Features</dt>
          <dd className="tabular text-muted">{feature_set_version}</dd>
        </div>
      </dl>

      <p className="mt-4 border-t border-ink pt-3 text-xs leading-relaxed text-dim">
        A discriminant, not a probability. The training class balance was chosen,
        not measured, so this number is not the chance that the event is signal.
      </p>

      {disagrees ? (
        <Narrator slot="prediction_wrong" seed={event.event_id} className="mt-4" />
      ) : nearThreshold ? (
        <Narrator slot="score_near_threshold" seed={event.event_id} className="mt-4" />
      ) : (
        <Narrator slot="score_shown" seed={event.event_id} className="mt-4" />
      )}
    </section>
  );
}
