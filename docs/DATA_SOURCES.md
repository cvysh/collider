# Data Sources

Every dataset used by COLLIDER is recorded here before it is used.
Facts below were verified on the access date shown, from the linked pages.

---

## ATLAS Open Data — 13 TeV, 2015+2016 proton-proton (2025 education release)

**Status:** primary candidate for both the 3D event display and the ML task.
Not yet downloaded.

| Field | Value |
|---|---|
| Experiment | ATLAS |
| Collision energy | 13 TeV (proton-proton) |
| Data-taking period | 2015 + 2016 (LHC Run 2) |
| Integrated luminosity | 36 fb⁻¹ |
| Format | ROOT ntuple, ~80 branches |
| Record | https://opendata.cern.ch/record/93910 |
| DOI | `10.7483/OPENDATA.ATLAS.B5M9.44TN` |
| Licence | CC0 1.0 Universal |
| Contents | **Both** real collision data and MC simulation |
| Full collection size | 9,837,961,169 events / 4,668 files / 2.5 TiB |
| Documentation | https://opendata.atlas.cern/docs/data/for_education/13TeV25_details |
| Accessed | 2026-09-12 |

### Why this dataset

It is the one source that supplies **per-object kinematics and labels from the
same file**. The alternative Higgs classification datasets (e.g. the UCI HIGGS
tabular set) provide only derived features with no per-particle four-vectors,
which means they cannot drive a 3D event display. See
[decisions/0001-dataset-choice.md](decisions/0001-dataset-choice.md).

### Available skims

Eleven pre-filtered collections, which avoid downloading the full 2.5 TiB:

| Skim | Enriched in |
|---|---|
| `1LMET30` | W boson |
| `2muons` | Z boson |
| `2to4lep`, `3lep`, `exactly3lep`, `4lep`, `exactly4lep` | multi-lepton |
| `3J1LMET30`, `2J2LMET30` | top quark |
| `GamGam` | H → γγ |
| `2bjets` | H → bb̄ |

### Variables

Confirmed to include: lepton `pt`/`eta`/`phi`/`E`/charge and identification
flags; jet kinematics and b-tagging; photons; tau leptons; missing transverse
energy; truth-level particles; and **event weights** (`mcWeight` plus several
`scaleFactor_*` efficiency corrections).

> **`mcWeight` and the scale factors are not optional.** MC events are
> generated with arbitrary normalisation. Ignoring the weights makes both
> histograms and class balance wrong. See
> [SCIENTIFIC_INTEGRITY.md](SCIENTIFIC_INTEGRITY.md).

### Citation

To be filled in with the exact citation string from the record page before any
public deployment. Acknowledgement of the ATLAS Collaboration is required.

---

## Datasets considered and not chosen

| Dataset | Why not |
|---|---|
| UCI HIGGS (Baldi/Sadowski/Whiteson) | 28 derived features only, no per-particle four-vectors → cannot render an event. Simulation only. |
| CMS Open Data (research-grade) | Requires CMSSW / heavier reconstruction stack; much steeper ramp than ATLAS education ntuples. Revisit later. |

---

## Reference index

- CERN Open Data Portal — https://opendata.cern.ch/
- ATLAS Open Data — https://opendata.atlas.cern/
- ATLAS uproot framework — https://opendata.atlas.cern/docs/13TeVDoc/frameworks/uproot
- ATLAS outreach uproot examples — https://github.com/atlas-outreach-data-tools/atlas-outreach-Python-uproot-framework-13tev
- "Open Data at ATLAS: Bringing TeV collisions to the World" — https://arxiv.org/html/2502.21133v1
