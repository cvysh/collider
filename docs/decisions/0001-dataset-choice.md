# ADR-0001: Primary dataset

- **Status:** Accepted
- **Date:** 2026-09-12

## Context

The project needs collision events that can serve **two** purposes at once:

1. Drive a 3D event display — requires per-object four-vectors.
2. Train a supervised signal-vs-background classifier — requires labels.

Most well-known "Higgs ML" datasets satisfy only (2). The UCI HIGGS dataset is
28 derived features per event with no per-particle kinematics, so an event from
it cannot be drawn. Choosing it would force the project to render one dataset
and classify a different one, which is the failure mode described in SPEC §65
("Trap 3: Fake physics").

## Decision

Use the **ATLAS Open Data 13 TeV 2015+2016 education release**
(DOI `10.7483/OPENDATA.ATLAS.B5M9.44TN`) as the single source for both.

It provides ROOT ntuples (~80 branches) containing per-object lepton, jet,
photon, tau and missing-ET kinematics, MC truth information, and event weights
— for both real collision data and MC simulation. Pre-filtered skims
(`4lep`, `2muons`, `GamGam`, …) make it possible to work with a small subset
rather than the 2.5 TiB full collection.

## Consequences

- Read with `uproot` + `awkward`; no ROOT/C++ installation needed.
- Data is **jagged** (variable object count per event). This does not fit a
  flat DataFrame naturally and is a genuine learning curve.
- **Units in this release are GeV.** This was verified by inspecting the file,
  not assumed: median `lep_pt` is 17.9 and median `lep_e` is 39.4. Note that
  the older 2020 13 TeV education release used MeV, so tutorials written
  against it divide by 1000 — do not copy that. `tests/test_z_peak.py`
  asserts the convention so a future dataset swap cannot silently break it.
- Labels come from MC only, which forces the `data_kind` distinction described
  in `docs/SCIENTIFIC_INTEGRITY.md`.

## Validated

Confirmed against the real-data `2muons` skim (record 93921, single 34 MB
file, 124,935 events). The dimuon spectrum reproduces four known resonances:

| Resonance | Measured | PDG | Difference |
|---|---|---|---|
| J/ψ | 3.095 GeV | 3.097 | −0.06% |
| ψ(2S) | 3.675 GeV | 3.686 | −0.3% |
| Υ(1S) | 9.435 GeV | 9.460 | −0.26% |
| Z | 90.750 GeV | 91.188 | −0.48% |

All peaks sit slightly low, by an amount that grows with mass. That is the
expected signature of final-state radiation plus finite momentum resolution,
not a calibration error — the J/ψ agreement at 0.06% rules out a systematic
momentum-scale problem.

## Not yet decided

Which skim is the flagship. `4lep` is the likely choice (H→ZZ→4ℓ is visually
striking and is a genuine signal-vs-background problem), with `GamGam` as the
alternative since H→γγ produces a *visible* bump rather than only a score.
