# Findings

Empirical results, each reproducible from a script in `scripts/` and guarded by
a test. Nothing here is quoted from documentation — every number was measured
from the data.

---

## 1. The dimuon spectrum contains four known resonances

**Script:** `scripts/plot_z_peak.py` · **Test:** `tests/test_z_peak.py`
· **Figure:** `figures/z_peak.png`

Reconstructing invariant mass from opposite-charge muon pairs in 124,935 real
2015 collision events:

| Resonance | Measured | PDG | Difference |
|---|---|---|---|
| J/ψ | 3.095 GeV | 3.0969 | −0.06% |
| ψ(2S) | 3.675 GeV | 3.6861 | −0.3% |
| Υ(1S) | 9.435 GeV | 9.4603 | −0.26% |
| Z | 90.750 GeV | 91.188 | −0.48% |

**Every peak sits low, by an amount that grows with mass.** This is the
signature of final-state radiation — a muon radiating a photon carries away
energy that is missing from our sum — compounded by finite momentum
resolution. A momentum-scale calibration error would instead produce a
*constant fractional* offset. The J/ψ agreement at 0.06% therefore rules out a
scale problem and is the tightest validation in the suite.

This validates the four-vector arithmetic, the pt/η/φ → Cartesian conversion,
the GeV unit convention, and the pair selection simultaneously.

---

## 2. Detector acceptance bounds the usable feature space

**Script:** `scripts/eda_acceptance.py` · **Test:** `tests/test_acceptance.py`
· **Figure:** `figures/acceptance.png`

| Property | Measured | Interpretation |
|---|---|---|
| `pt` minimum (paired muons) | 10.0 GeV | Dimuon trigger threshold — sharp, not a turn-on curve |
| `pt` minimum (any muon) | 7.0 GeV | Reconstruction threshold; extra muons in ≥3-muon events reach lower |
| \|η\| maximum | 2.500 exactly | Muon reconstruction acceptance limit |
| η ≈ 0 density deficit | 34% | Service gap in the muon spectrometer |
| φ χ²/dof, barrel (\|η\|<1.05) | 63.1 | Strongly non-uniform |
| φ χ²/dof, endcap (\|η\|>1.3) | 4.0 | Nearly uniform |

### Three instrumental features are directly visible

1. **A hard `pt` edge at 10 GeV.** Not a physical effect — the trigger simply
   did not record dimuon events below it. The dataset contains *no information*
   about muons below 10 GeV, so no feature may assume that region is populated.

2. **A 34% hole at η ≈ 0.** The muon spectrometer has a gap at the centre for
   cabling and services. It is a physical hole in the instrument.

3. **The support feet, in the φ distribution.** The barrel deficit is centred
   on φ = −π/2, which is straight down, and is absent in the endcap — which the
   feet do not obstruct. χ²/dof of 63.1 vs 4.0 makes this unambiguous.

### Why this matters downstream

Acceptance is a hard boundary on what any model can learn. A classifier trained
here knows nothing about |η| > 2.5 or pt < 10 GeV. Sharp edges in these
distributions are instrumental, not physical, and must never be presented to a
user as a property of nature.

The φ asymmetry must **not** be normalised away. It is a real property of the
apparatus, and a model that learns it is learning something true about how the
data was collected.

---

## 3. MC weights invert the sample by a factor of ~1,000

**Script:** `scripts/plot_mc_weights.py` · **Test:** `tests/test_weights.py`
· **Figure:** `figures/mc_weights.png`

The two 4-lepton samples, normalised to 36 fb⁻¹:

| | ggH→ZZ→4ℓ (signal) | ZZ→4ℓ (background) |
|---|---|---|
| Generated events | 424,880 | 11,458 |
| **Expected events in 36 fb⁻¹** | **53.6** | **1,508** |
| `xsec` | 28.3 pb | 1.2974 pb |
| `filteff` | 1.24 × 10⁻⁴ | 1.0 |
| `kfac` | 1.717 | 1.0 |
| Negative weights | 0.22% | 8.58% |
| N_eff | 403,230 (94.9%) | 3,621 (**31.6%**) |
| Skim retained | 26.6% of generated weight | 3.5% |

Raw, signal outnumbers background **37 : 1**. Physically, background
outnumbers signal **28 : 1**. The generated sample is inverted relative to
nature by a factor of **1,044**.

### Consequences

1. **Unweighted MC histograms are meaningless.** They describe a generation
   campaign, not the universe.
2. **Training class balance is a free parameter**, not a measurement. This is
   why a classifier output must be reported as a *discriminant score* and never
   as a probability — the prior is something we chose. See
   `SCIENTIFIC_INTEGRITY.md` §3.
3. **The background sample is weaker than it looks.** N_eff of 3,621 from
   11,458 rows: only 32% of the apparent statistical power survives the spread
   of weights and the 8.6% negative fraction. Statistical uncertainty is
   `sqrt(sum w²)`, not `sqrt(N)`.
4. **Negative weights must be kept.** Sherpa produces 8.6% of ZZ events with
   negative weight. Dropping them breaks the cancellation that makes
   higher-order calculations finite and biases yields upward.
5. **Normalise by `sum_of_weights`, never by the sum over your own file.**
   These files are skims retaining 27% and 3.5% of generated weight; using the
   local sum would inflate yields by 4× and 28× respectively.

### Schema note

MC and data trees are **not identical**: data has a `category` branch (116 vs
117 branches) that MC lacks. Any loader reading both must not assume a common
branch list.

### Open item — luminosity

The 36 fb⁻¹ figure is the full 2015+2016 release. The real-data file currently
held is `data15 periodD` only, a small fraction of that. MC normalised to
36 fb⁻¹ **cannot** be overlaid on it directly. Resolve the per-period
luminosity before making any data/MC comparison plot.

---

## 4. Raw 4-lepton data is dominated by fake leptons

**Module:** `collider.physics.selection`

Lepton quality, measured across the three 4ℓ files:

| | ggH signal | ZZ background | **real data** |
|---|---|---|---|
| Leptons passing tight ID | 86.7% | 87.6% | **17.7%** |
| Leptons passing tight isolation | 79.8% | 83.6% | **1.9%** |
| Median \|d₀/σ\| | 0.65 | 0.67 | **1.48** |
| Events after full selection | 125,272 / 424,880 | 4,491 / 11,458 | **1 / 3,708** |

Raw data flavour composition is also unlike MC: 39% of data events are 1μ3e,
a combination essentially absent from both simulated samples, and only 45%
have net charge zero versus 97% in MC.

**Interpretation.** The `4lep` skim requires four lepton *candidates*, not four
good prompt leptons — it is deliberately loose so analyses can impose their own
criteria. Real data at that stage is dominated by **fakes**: jets
misreconstructed as electrons, and real leptons from heavy-flavour decays
inside jets, whose large impact-parameter significance shows they do not come
from the primary vertex.

Our MC models only the **irreducible** background (genuine ZZ→4ℓ). It contains
no fakes whatsoever.

### Consequences

1. **Raw data/MC comparison is meaningless.** The apparent excess is entirely
   detector artefact, not new physics.
2. **Selection must be identical everywhere.** A model trained on MC where 87%
   of leptons are tight, then applied to data where 18% are, is being run far
   outside its training distribution.
3. A full fake-background estimate would require data-driven methods
   (control regions with inverted identification), which is out of scope. The
   honest position is that **this project models the irreducible background
   only**, and says so.

---

## 5. The labelled dataset

**Modules:** `collider.features.fourlepton`, `collider.features.dataset`

After selection, at 36 fb⁻¹:

| | rows | expected yield | negative wts | N_eff |
|---|---|---|---|---|
| ggH→ZZ→4ℓ | 125,272 | 15.68 | 0.22% | 118,876 |
| ZZ→4ℓ | 4,491 | 587.87 | 8.86% | **1,443** |

Physical ratio signal:background is **1 : 37.5**. Training ratio is set to
**1 : 1**.

### `m_4l` is deliberately excluded from the features

The four-lepton mass is by far the most discriminating variable — signal
median 124.4 GeV, background 231.1 GeV. Including it would yield a
near-perfect classifier that has learned only "is it 125?".

More importantly it would **sculpt** the background: cutting on a
mass-dependent score carves a bump-shaped deficit into the very spectrum we
would later fit for an excess. The mass is the measurement, so it must not be
the thing we cut on. `m_4l` is computed and carried alongside for plotting and
fitting, but never enters the model.

### Feature separation (median difference in units of pooled σ)

| Feature | Signal | Background | Separation |
|---|---|---|---|
| `m_z2` | 27.00 | 87.64 | **3.38** |
| `m_z2_over_m_z1` | 0.309 | 0.964 | **2.06** |
| `lep_pt_2` | 19.56 | 36.73 | 1.72 |
| `lep_pt_3` | 12.05 | 22.97 | 1.72 |
| `lep_pt_1` | 33.88 | 53.38 | 1.30 |
| `lep_pt_0` | 49.03 | 74.68 | 0.90 |
| `delta_phi_zz` | 1.82 | 2.41 | 0.61 |
| `m_z1` | 88.07 | 90.60 | 0.21 |

`m_z2` is the strongest discriminator, and the reason is pure physics: a
125 GeV Higgs has too little mass to produce two on-shell Z bosons, so the
second is virtual and light. Non-resonant ZZ production makes both on-shell.
`m_z1` barely separates, exactly as expected — both processes contain one
real Z.

### Known limitation

The background N_eff of 1,443 (from 4,491 rows) is thin. Uncertainties on
background predictions will be correspondingly large, and additional ZZ
samples should be added before any result is quoted seriously.
