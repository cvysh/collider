# Scientific Integrity Rules

These rules constrain the architecture, the schema, and the UI copy. They are
not a disclaimer appended at the end — several of them change what fields the
database must have.

---

## 1. Real data has no label. Simulation does.

This is the single most important fact about the project.

- **MC simulation** is labelled. You know a sample is `H→ZZ→4ℓ` because you
  generated it that way (identified by `channelNumber`).
- **Real detector data** has no truth label. There is no column that says what
  an actual collision "was".

Therefore:

- The classifier is **trained and evaluated on simulation only**.
- Running it on a real event produces **a score, not a verdict**. There is
  nothing to check the score against.
- Both populations may be displayed and explored, but they must be
  **visually and structurally distinguished everywhere**.

**Schema consequence:** every event record carries

```
data_kind      : "measured" | "simulated"
mc_process     : nullable, e.g. "ggH125_ZZ4lep"   (null for measured)
channel_number : nullable                          (null for measured)
```

A UI that cannot tell the user which of the two it is showing is a bug.

---

## 2. Monte Carlo events are weighted.

MC samples are produced in arbitrary quantities that have no relation to
physical rates. Each event carries `mcWeight` and several `scaleFactor_*`
efficiency corrections, plus a per-sample cross-section × luminosity
normalisation.

Consequences:

- Any histogram of MC must be **weighted**, or it is meaningless.
- The **class balance of the training set is a choice, not a measurement.**
  Real signal-to-background rates are smaller by many orders of magnitude.

---

## 3. Do not call the model output a probability.

Because the training class balance is arbitrary (rule 2), a model output of
`0.874` is **not** "an 87.4% chance this is signal". The prior is fabricated.

- Present it as a **discriminant score** in `[0, 1]`, which is the standard
  term in experimental particle physics.
- Report the **decision threshold** alongside it, always.
- If a calibrated probability is ever claimed, it must be backed by an actual
  calibration curve on a held-out set, with the assumed prior stated.

Preferred UI:

```
SIGNAL DISCRIMINANT        0.874
Threshold 0.60 → classified SIGNAL-LIKE
```

Not:

```
87.4% probability of Higgs
```

---

## 4. The 3D display is a stylisation of reconstructed objects.

Open data gives a **four-vector per reconstructed object**. It does not give
the trajectory of the particle through the detector.

- Drawing a ray from the interaction point along the momentum direction is
  honest, and must be labelled as a direction indicator.
- Drawing a *curved* track implies a magnetic-field trajectory. That is only
  permitted if the curvature is actually computed from charge, `pt`, and the
  field (radius ≈ `pt` / (0.3 · B)). A curve chosen because it looks good is
  fabricated physics.
- Detector geometry is schematic, not a CAD model, and is labelled as such.

---

## 5. Some quantities are per-run, not per-event.

Collision energy (13 TeV) is a property of the beam configuration, not a
measurement of the individual event. Do not render it as if it were measured
per collision.

---

## 6. Numerical edge cases are correctness bugs, not cosmetics.

- **Invariant mass:** `m² = (ΣE)² − |Σp⃗|²`. Floating-point error can make `m²`
  slightly negative for near-massless objects; `sqrt` then yields `NaN`. Clamp
  at zero and test the clamp.
- **Pseudorapidity:** `η = −ln(tan(θ/2))` diverges as `θ → 0`. Handle the
  forward/backward limit explicitly.

---

## 7. Physics validation belongs in the test suite.

A pipeline that computes invariant mass correctly must reproduce known
results. The primary check:

> Dimuon invariant mass on the `2muons` skim must show a clear peak at the
> Z-boson mass, **91.2 GeV**.

If that peak is absent or in the wrong place, the four-vector handling, the
unit convention (MeV vs GeV), or the object selection is wrong — and every
downstream result is invalid. This test runs in CI and gates everything else.

---

## 8. Language rules

Never: "we discovered the Higgs", "proves", "confirms", "87% probability of a
Higgs boson".

Instead: "signal-like candidate", "discriminant score", "consistent with",
"in this educational dataset", "the model assigns".

Explanation methods (SHAP, permutation importance) describe **what the model
used**, never **what caused the physics**. The UI separates `MODEL FACT` from
`PHYSICS INTERPRETATION`.
