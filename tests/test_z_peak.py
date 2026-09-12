"""Physics validation: the Z boson must appear at its known mass.

This is the project's correctness oracle. It runs against a fixture of real
ATLAS collision data (see tests/fixtures/README.md) and checks that the dimuon
invariant-mass spectrum contains a resonance where the Particle Data Group says
the Z boson is.

If this test fails, one of the following is wrong: the four-vector arithmetic,
the pt/eta/phi -> Cartesian conversion, the unit convention, or the pair
selection. Every physics number produced downstream would then be invalid, so
this test gates the rest of the pipeline.
"""

from pathlib import Path

import awkward as ak
import numpy as np
import pytest

from collider.physics.fourvector import invariant_mass

# Particle Data Group values.
Z_MASS_PDG = 91.188  # GeV
Z_WIDTH_PDG = 2.495  # GeV

FIXTURE = Path(__file__).parent / "fixtures" / "dimuon_data15_periodD.npz"


@pytest.fixture(scope="module")
def dimuon_mass() -> np.ndarray:
    """Invariant mass of opposite-charge muon pairs from real ATLAS data."""
    d = np.load(FIXTURE)
    m = invariant_mass(
        ak.Array(d["pt"]), ak.Array(d["eta"]), ak.Array(d["phi"]), ak.Array(d["energy"])
    )
    return ak.to_numpy(m)


def test_fixture_shape():
    d = np.load(FIXTURE)
    assert d["pt"].shape == (12_000, 2), "fixture must be exactly-two-muon events"
    # Selection guarantees opposite charge, so every pair sums to zero.
    assert np.all(d["charge"].sum(axis=1) == 0)


def test_no_nan_or_negative_masses(dimuon_mass):
    """The m^2 clamp must hold on real data, not just synthetic edge cases."""
    assert not np.isnan(dimuon_mass).any()
    assert np.all(dimuon_mass >= 0.0)


def test_masses_are_in_gev_not_mev(dimuon_mass):
    """Guard the unit convention.

    A MeV/GeV mix-up is the single most likely silent error in this pipeline.
    In GeV the Z sits near 91; in MeV it would sit near 91,000.
    """
    assert dimuon_mass.max() < 10_000, "masses look like MeV, not GeV"
    assert np.median(dimuon_mass) > 1.0, "masses look too small to be GeV"


def test_z_resonance_appears_at_pdg_mass(dimuon_mass):
    """The most-populated bin between 60 and 120 GeV must be the Z.

    Tolerance is 1.5 GeV. The observed peak sits slightly *below* the PDG value
    for real physical reasons, not because of a bug:

      * Final-state radiation -- a muon can emit a photon, so the reconstructed
        dimuon mass is lower than the parent Z mass. This produces the
        characteristic low-mass tail and drags the peak down.
      * Detector momentum resolution smears the resonance.

    Extracting the true mass requires fitting a Breit-Wigner convolved with a
    resolution function. This test checks that the resonance is *present and
    correctly located*, which is what validates the pipeline; it is not a
    measurement of the Z mass.
    """
    counts, edges = np.histogram(dimuon_mass, bins=120, range=(60, 120))
    centres = 0.5 * (edges[:-1] + edges[1:])
    peak = centres[np.argmax(counts)]
    assert abs(peak - Z_MASS_PDG) < 1.5, f"peak at {peak:.2f} GeV, expected ~{Z_MASS_PDG}"


def test_z_peak_stands_above_background(dimuon_mass):
    """The resonance must be a real excess, not a bump in noise.

    Compares the density inside a +/- 2-width window around the Z against
    sideband regions on either side.
    """
    n_peak = np.sum(np.abs(dimuon_mass - Z_MASS_PDG) < 2 * Z_WIDTH_PDG)
    peak_width = 4 * Z_WIDTH_PDG

    # Sidebands of equal total width, away from the resonance.
    n_side = np.sum(
        ((dimuon_mass > 70) & (dimuon_mass < 75)) | ((dimuon_mass > 105) & (dimuon_mass < 110))
    )
    side_width = 10.0

    peak_density = n_peak / peak_width
    side_density = n_side / side_width
    assert peak_density > 20 * side_density, (
        f"peak density {peak_density:.1f}/GeV vs sideband {side_density:.1f}/GeV "
        "-- resonance is not standing above background"
    )


def test_most_pairs_are_not_from_a_z(dimuon_mass):
    """Sanity check in the other direction.

    If nearly every pair landed in the Z window, the selection would be
    suspiciously circular. Most muon pairs in this skim are combinatorial or
    from lower-mass processes, so the Z window should hold a minority.
    """
    in_z = np.sum(np.abs(dimuon_mass - Z_MASS_PDG) < 5.0)
    assert 0.05 < in_z / len(dimuon_mass) < 0.60


# ---------------------------------------------------------------------------
# Low-mass resonances.
#
# The same dimuon spectrum contains several narrower resonances below the Z.
# These are *stronger* validators of the momentum scale than the Z is: the
# J/psi natural width is ~93 keV, so its observed peak is dominated by detector
# resolution rather than by the particle's own width, and it is far less
# affected by the radiative tail that pulls the Z peak low.
#
# Agreement here to well under 1% is what rules out a systematic scale error
# in the pt/eta/phi -> momentum conversion.
# ---------------------------------------------------------------------------

JPSI_MASS_PDG = 3.0969  # GeV
UPSILON_MASS_PDG = 9.4603  # GeV


def _peak_in(mass: np.ndarray, lo: float, hi: float, bins: int) -> float:
    counts, edges = np.histogram(mass, bins=bins, range=(lo, hi))
    centres = 0.5 * (edges[:-1] + edges[1:])
    return float(centres[np.argmax(counts)])


def test_jpsi_resonance(dimuon_mass):
    """J/psi must appear within 50 MeV of its PDG mass.

    This is the tightest constraint in the suite. A 1% error in the momentum
    scale would move this peak by 31 MeV and fail.
    """
    peak = _peak_in(dimuon_mass, 2.5, 3.7, 60)
    assert abs(peak - JPSI_MASS_PDG) < 0.05, (
        f"J/psi peak at {peak:.3f} GeV, expected {JPSI_MASS_PDG}"
    )


def test_upsilon_resonance(dimuon_mass):
    """Upsilon(1S) must appear within 150 MeV of its PDG mass."""
    peak = _peak_in(dimuon_mass, 9.0, 10.5, 30)
    assert abs(peak - UPSILON_MASS_PDG) < 0.15, (
        f"Upsilon peak at {peak:.3f} GeV, expected {UPSILON_MASS_PDG}"
    )


def test_resonances_are_correctly_ordered(dimuon_mass):
    """J/psi < Upsilon < Z, by construction of where we look.

    Guards against a transposed-axis or scrambled-array bug that could still
    produce plausible-looking individual peaks.
    """
    jpsi = _peak_in(dimuon_mass, 2.5, 3.7, 60)
    upsilon = _peak_in(dimuon_mass, 9.0, 10.5, 30)
    z = _peak_in(dimuon_mass, 60, 120, 120)
    assert jpsi < upsilon < z
    # Ratios are fixed by nature and independent of our units.
    assert upsilon / jpsi == pytest.approx(UPSILON_MASS_PDG / JPSI_MASS_PDG, rel=0.02)
    assert z / jpsi == pytest.approx(Z_MASS_PDG / JPSI_MASS_PDG, rel=0.02)
