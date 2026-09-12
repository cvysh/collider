# Test fixtures

## `dimuon_data15_periodD.npz`

Opposite-charge dimuon kinematics from **real ATLAS collision data**, used by
`tests/test_z_peak.py` so the physics validation runs without a 34 MB download.

| | |
|---|---|
| Source file | `ODEO_FEB2025_v0_2muons_data15_periodD.2muons.root` |
| Record | [CERN Open Data 93921](https://opendata.cern.ch/record/93921) |
| DOI | `10.7483/OPENDATA.ATLAS.6VGH.HN41` (CC0 1.0) |
| Selection | `lep_type == 13`, exactly 2 muons, net charge 0 |
| Events available | 113,228 |
| Events in fixture | 12,000, uniform subsample, `numpy` seed `20260912` |
| Fields | `pt`, `eta`, `phi`, `energy`, `charge`, each `float32` shape `(12000, 2)` |
| Units | GeV |

This is **real measured data with no truth label**. It is used to validate
arithmetic, not to train or evaluate a classifier.

Regenerate with `scripts/make_dimuon_fixture.py` after placing the source file
in `data/raw/`.
