# ADR-0001: Primary dataset

- **Status:** Proposed
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
- Units in ATLAS ntuples are typically **MeV**; a unit convention must be fixed
  early and tested, or every mass will be off by 1000×.
- Labels come from MC only, which forces the `data_kind` distinction described
  in `docs/SCIENTIFIC_INTEGRITY.md`.

## Not yet decided

Which skim is the flagship. `2muons` is the best *first* target because the
Z peak at 91.2 GeV provides an unambiguous correctness check. `4lep` is the
better eventual flagship (H→ZZ→4ℓ is visually striking and is a genuine
signal-vs-background problem).
