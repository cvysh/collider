# COLLIDER

An interactive CERN Open Data + machine-learning laboratory for exploring
particle-collision events in the browser.

> **Status: Phase 0 — repository setup and dataset research.**
> Nothing is built yet. This README describes intent, not achieved results.
> No performance number, metric, or physics result appears here until it has
> been measured and is reproducible from this repository.

## What this will be

A web application where you can browse a curated set of ATLAS Open Data
collision events, inspect the reconstructed particles in an interactive 3D
event display, and run a trained classifier over the event's physics features
to get a signal-vs-background discriminant with an explanation of which
features drove it.

## Scientific honesty rules

These are load-bearing, not decoration:

- **Simulated and measured data are always distinguished.** Labelled training
  data is Monte Carlo simulation. Real detector data carries no truth label,
  so the model's output on a real event is a *score*, never a verified class.
- **No fabricated values.** If a quantity is absent from the source dataset,
  the UI says it is unavailable.
- **No discovery claims.** The model classifies events from an educational
  dataset. It does not discover particles.
- **Everything is traceable** to a source dataset, DOI, preprocessing commit,
  feature-set version, and model version.

See [docs/SCIENTIFIC_INTEGRITY.md](docs/SCIENTIFIC_INTEGRITY.md).

## Documentation

| Document | Purpose |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | Full original project specification (source of truth for scope) |
| [docs/SCIENTIFIC_INTEGRITY.md](docs/SCIENTIFIC_INTEGRITY.md) | Rules for handling real vs. simulated data, weights, and claims |
| [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) | Datasets, DOIs, licences, access dates |
| [docs/decisions/](docs/decisions/) | Architecture decision records |

## Licence

Code in this repository is MIT licensed (see [LICENSE](LICENSE)).

ATLAS Open Data is released by CERN under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
Citation of the data and acknowledgement of the ATLAS Collaboration is
requested; see [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
