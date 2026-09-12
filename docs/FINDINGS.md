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
