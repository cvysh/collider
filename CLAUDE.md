# COLLIDER — Project Instructions

Interactive CERN Open Data + ML application. `docs/SPEC.md` defines scope.
`docs/SCIENTIFIC_INTEGRITY.md` defines non-negotiable data-handling rules.

## Working mode (important)

This project is a learning vehicle as much as a product. The author is a CS
student who intends to be able to explain every subsystem without assistance.

- Explain important concepts **before or while** implementing them: what it
  does, why it is needed, how it works, the design tradeoff, and the common
  mistake. Boilerplate can be generated freely; load-bearing logic must be
  understood.
- Work incrementally. State what is being built and why before building it.
  Do not generate whole subsystems unprompted.
- Push back on bad architecture, overengineering, unjustified dependencies,
  and scientific errors. Do not implement a bad idea just because it was asked
  for — say so first.
- Verify rather than assert. Run the code, the tests, the linter, the type
  checker. Never report that something works without having observed it work.

## Scientific rules (see docs/SCIENTIFIC_INTEGRITY.md)

- Labelled data is **simulation**. Real detector data has **no truth label**.
  Every event carries `data_kind` (`measured` | `simulated`); the UI must
  always distinguish them.
- MC events are **weighted** (`mcWeight`, `scaleFactor_*`). Unweighted MC
  histograms are wrong.
- Model output is a **discriminant score**, not a probability. Always show the
  threshold. Training class balance is arbitrary and is not a physical prior.
- Never fabricate a value. Absent data is reported as unavailable.
- Never claim a discovery, proof, or confirmation.
- Mock data exists only in explicitly named development fixtures.
- Do not change a scientific definition or formula silently.

## Engineering rules

- Do not put raw datasets in the browser. The client receives one event.
- Do not initialise Three.js on pages that do not render an event. The 3D
  bundle is lazy-loaded.
- Typed, validated schemas at every API boundary (Pydantic server side, Zod or
  generated types client side).
- Preserve dataset / feature-set / model versioning. Artifacts are immutable;
  new versions get new paths.
- Measure before optimising. Do not convert a performance problem into an
  infrastructure problem without a profile.
- No new dependency without stating what problem it solves.
- Every load-bearing module gets tests. Physics helpers get tests against
  known values (see the Z-peak check).
- Secrets in environment variables only. Model IDs are allowlisted; never
  accept a model path from a client.

## Design rules

- Aesthetic: original adult-sci-fi-cartoon laboratory. Playful but legible.
- Original artwork only. No copyrighted characters, frames, dialogue, or logos.
- Scientific readouts stay readable; decoration never obscures data.
- Respect reduced-motion. Provide a 2D fallback summary for the 3D view.
