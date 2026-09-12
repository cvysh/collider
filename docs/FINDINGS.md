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

---

## 6. Baseline classifier — and why the mass does most of the work

**Scripts:** `scripts/train_baseline.py`, `scripts/plot_baseline.py`
· **Tests:** `tests/test_metrics.py` · **Figure:** `figures/baseline.png`

Logistic regression, 14 features, fitted on balanced weights, evaluated on
physical weights, test split touched once.

| Split | AUC |
|---|---|
| train | 0.9136 |
| validation | 0.9151 |
| test | **0.9110** |

No overfitting — validation sits marginally above train.

### The result that matters

Expected significance at 36 fb⁻¹, test split scaled to the full dataset:

| Strategy | S | B | Z |
|---|---|---|---|
| No selection | 15.73 | 558.98 | 0.66 |
| Classifier alone (score > 0.72) | 11.28 | 64.73 | 1.36 |
| **Mass window alone (115–130 GeV)** | **15.09** | **16.87** | **3.26** |
| Mass window + classifier at 0.72 | 10.89 | 15.74 | **2.50** |
| Mass window + classifier re-optimised | 15.07 | 15.74 | 3.35 |

**Three things to take from this.**

1. **The mass window alone (3.26) beats the classifier alone (1.36) by a
   factor of 2.4.** A single physically-motivated cut outperforms a
   fourteen-feature model. This vindicates excluding `m_4l` from the features —
   had it been included, the classifier would simply have rediscovered the mass
   cut and we would have learned nothing.

2. **Combining them naively makes things *worse*: 2.50 < 3.26.** The threshold
   0.72 was optimal for the classifier *in isolation*. Applied inside the mass
   window it removes more signal than background. **Cuts must be optimised
   jointly, never independently and then stacked.**

3. **Properly combined, the classifier adds almost nothing: 3.35 vs 3.26,
   a 3% gain.** This is an honest negative result and it has an explanation.

### Why the classifier is redundant with the mass

Correlation of each feature with the held-out `m_4l`, computed on background:

| Feature | corr with `m_4l` |
|---|---|
| `m_z2` | **+0.599** |
| `lep_pt_1` | +0.540 |
| `lep_pt_2` | +0.466 |
| `m_z1` | +0.122 |

Split by class, `corr(m_z2, m_4l)` is **+0.046 in signal** but **+0.563 in
background**. For background there is no mass constraint, so a heavier
four-lepton system simply means a heavier second pair — the strongest feature
is largely restating the mass. In signal, `m_4l` is pinned at 125, so `m_z2`
carries independent information.

The classifier is therefore mostly re-deriving the mass cut through a proxy.
Adding features correlated with the held-out variable reintroduces the
sculpting risk by the back door, and this is the quantitative evidence for it.

### Methodological note — an error caught and fixed

Significance was initially computed on the test split alone, whose physical
weights sum to 20% of the experiment's expected yield. Significance grows like
√N, so this understated it by more than a factor of two. `evaluate()` now takes
`yield_scale` and the test asserts AUC is unaffected by it while significance
scales as √N.

### Coefficients are not feature importances

`pt_4l` carries the largest standardised coefficient (+1.748) with `lep_pt_0`
opposing it (−1.398), despite `pt_4l` having almost no univariate separation
(0.16σ). They correlate at ρ = 0.78 (VIF 5.7), so the model is using their
*difference*. Correlated inputs make coefficients unreadable as importance;
permutation importance is the appropriate tool.

### Scope reminder

Signal is **ggF production only**; other Higgs production modes are excluded.
Background is the **irreducible ZZ→4ℓ only** — no fakes, which real data is
dominated by before selection. These numbers describe a simplified analysis on
simulation and are not an ATLAS result.

---

## 7. XGBoost vs logistic regression — and a prediction that was wrong

**Script:** `scripts/train_compare.py` · **Figure:** `figures/model_comparison.png`

Identical features, split, and weights. Background enlarged to three ZZ
samples (6,680 rows, N_eff 1,478).

| | test AUC | Z (classifier alone) | Z (+ mass window) |
|---|---|---|---|
| mass window alone | — | — | 2.96 |
| logistic regression | 0.9134 | 1.25 | 3.02 ± 0.42 |
| **XGBoost** | **0.9882** | **3.10** | 3.15 ± 0.46 |

### The prediction was wrong

Before running this, the stated expectation was "a modest AUC gain, negligible
significance gain, because the features are near their ceiling."

**Discrimination improved enormously.** AUC 0.9134 → 0.9882; at 10% background
efficiency the signal efficiency rises from roughly 55% to 97%. Classifier-only
significance went 1.25 → 3.10, a factor of 2.5.

The features were nowhere near their ceiling — the **linear model** was. The
discriminating structure in `(m_z1, m_z2)` is non-linear and involves
interactions that no linear decision boundary can express.

### The combined significance is *not* measurable here

The three combined numbers — 2.96, 3.02 ± 0.42, 3.15 ± 0.46 — are
statistically indistinguishable. That is **not** evidence that XGBoost fails to
help. It is a statement that our background sample cannot resolve the
difference:

| Region (test split, scaled) | rows | B | N_eff | rel. unc. |
|---|---|---|---|---|
| All selected | 1,360 | 618.8 | 288.4 | 6% |
| Mass window 115–130 | 117 | 21.3 | **14.0** | **27%** |
| Mass window 120–130 | 105 | 15.7 | 10.1 | 31% |

"No effect" and "cannot measure the effect" are different claims, and only the
second is supported.

### Two guard bugs, found and fixed

The threshold scan originally floored only the background **yield**. That
admitted an optimum of Z = 4.21 resting on **5 rows with N_eff = 3** (~60%
uncertainty).

The first fix added a **row-count** floor. Also insufficient: the corrected
optimum used 100 rows but still only **N_eff = 7**, because weights are
unequal. Row count is not statistical content.

The guard is now on **N_eff**, which is what sets the uncertainty
(~1/√N_eff). `tests/test_metrics.py` includes a case where 1,000 rows carry
N_eff < 2.

### Permutation importance corrects the coefficient story

| Feature | logreg | XGBoost |
|---|---|---|
| `m_z2` | 0.032 | **0.047** |
| `m_z1` | 0.058 | 0.035 |
| `pt_4l` | **0.090** | 0.005 |
| `lep_pt_0` | 0.072 | 0.006 |

Logistic regression leans hardest on `pt_4l` and `lep_pt_0` — the pair
correlated at ρ = 0.78 whose *difference* it exploits as a crude proxy.
XGBoost barely uses them (0.005) because it can use `m_z1` and `m_z2` directly
and non-linearly. The linear model was compensating for what it could not
express.

### The binding constraint

Every quoted significance is limited by background MC statistics, not by the
model. The next meaningful improvement is **more ZZ samples**, not more tuning.

---

## 8. The background sample cannot be enlarged — verified, not assumed

The 4-lepton irreducible background is limited by what this release contains,
not by our selection.

- The MC 4ℓ record holds exactly **three** qq→ZZ→4ℓ samples (`llll`,
  `lllljj`, `lllljj_Int`). All three are in use.
- There are **no gg→ZZ samples** in the release.
- The remaining `lllv` / `llvv` / `lvvv` samples are different final states,
  not ZZ→4ℓ.

### The no-skim record adds nothing

Checked directly rather than assumed:

| File | entries | `lep_n == 4` | passing full selection |
|---|---|---|---|
| `llll` 4lep skim | 11,458 | 11,260 | 4,536 |
| `llll` **no skim** | 248,881 | **11,260** | **4,536** |

Identical. The skim discards only events with fewer than four leptons, so it
is lossless for this analysis. The 100 MB no-skim file was removed after the
check.

### Consequence

Background N_eff inside the 115–130 GeV mass window is **14 (test split) /
37.7 (full sample)** and cannot be raised with available data. Any statement
about whether the classifier improves significance carries ~27% background
uncertainty and will remain unresolvable here.

Part of that sparseness is physical rather than statistical: ZZ→4ℓ below
182 GeV is the off-shell tail, so the region under the Higgs peak is
intrinsically thin.

**This is a permanent, documented limitation of the project, not a task
pending completion.**

---

## 9. Honest track curvature is nearly invisible at LHC momenta

**Module:** `collider.physics.trajectory` · **Test:** `tests/test_trajectory.py`
· **Figure:** `figures/trajectories.png`

A charged particle in the 2 T ATLAS solenoid follows a helix of radius
`r = pt / (0.3·q·B)` metres. Across the 1.1 m inner detector:

| pt (GeV) | radius | deviation from a straight ray |
|---|---|---|
| 1 | 1.67 m | 363 mm |
| 5 | 8.3 m | 72 mm |
| 10 | 16.7 m | 36 mm |
| **45** | **75 m** | **8.1 mm** |
| 90 | 150 m | 4.0 mm |

**Our muons are 10–90 GeV.** A 45 GeV track deviates by 8 mm over 1.1 m —
under 1% of its length. The dramatic spirals in famous event displays are
sub-GeV particles, not the stiff tracks in this dataset.

This is the reason curvature measures momentum at all: *less bend means more
momentum*. A display showing a strongly curved 45 GeV muon is not showing a
measured trajectory.

### Two deviations that are easy to confuse

For the same 45 GeV track:

- **Sagitta** — deviation from the chord joining the endpoints: **2.0 mm**.
  This is what a tracking detector measures.
- **Deviation from the initial tangent** — what a renderer drawing a straight
  ray from the interaction point would show: **8.1 mm**.

The ratio is exactly 4, since one goes as `1 − cos(α)` and the other as
`1 − cos(α/2)`. An early version of the test asserted the first value while
measuring the second.

### Rendering policy

- Default is the **true helix**, `curvature_scale = 1.0`.
- Exaggeration is available but must be **labelled as a visual aid** wherever
  shown, never presented as the measured trajectory
  (`SCIENTIFIC_INTEGRITY.md` §4).
- The **sign** of the bend is genuine measured information at any scale:
  positive and negative charges curve opposite ways. Panel (c) of the figure
  shows the true separation and a labelled ×60 aid side by side.
- Beyond 1.1 m the field is the toroid, not the solenoid, and this model stops
  being valid. The module documents that limit rather than extrapolating
  through it.
