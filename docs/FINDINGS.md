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
