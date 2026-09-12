"""Acceptance invariants of the ATLAS muon dataset.

These are not physics checks like tests/test_z_peak.py -- they assert
properties of the *instrument*. They exist so that swapping in a different
file, skim or data-taking period cannot silently change the region of phase
space we are training and rendering on.

A model trained on data with |eta| < 2.5 has learned nothing about |eta| > 2.5.
If the acceptance shifts, features and thresholds must be revisited.
"""

from pathlib import Path

import numpy as np
import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "dimuon_data15_periodD.npz"

ETA_ACCEPTANCE = 2.5  # ATLAS muon reconstruction limit
TRIGGER_PT_GEV = 10.0  # dimuon trigger threshold in this skim


@pytest.fixture(scope="module")
def muons() -> dict[str, np.ndarray]:
    d = np.load(FIXTURE)
    return {k: d[k] for k in ("pt", "eta", "phi", "charge")}


def test_eta_within_detector_acceptance(muons):
    """No muon may lie outside the instrumented region."""
    assert np.abs(muons["eta"]).max() <= ETA_ACCEPTANCE + 1e-3


def test_acceptance_edge_is_actually_populated(muons):
    """The edge must be a real boundary, not an artefact of a sparse sample.

    If muons thinned out well before 2.5 we would be looking at a kinematic
    effect rather than the detector limit.
    """
    near_edge = np.abs(muons["eta"]) > 2.3
    assert near_edge.sum() > 0.01 * muons["eta"].size


def test_all_muons_pass_trigger_threshold(muons):
    """Both legs of the pair are above the dimuon trigger threshold.

    Consequence for modelling: this dataset carries no information about muons
    below 10 GeV, so no feature may assume the low-pt region is populated.
    """
    assert muons["pt"].min() >= TRIGGER_PT_GEV - 0.1


def test_eta_zero_service_gap_is_present(muons):
    """The muon spectrometer has a gap at eta ~ 0 for cabling and services.

    Verifying it is present confirms we are reading genuine detector output
    rather than a smooth simulation or a resampled approximation.
    """
    eta = muons["eta"].ravel()
    gap_density = np.sum(np.abs(eta) < 0.1) / 0.2
    ref_density = np.sum((np.abs(eta) > 0.2) & (np.abs(eta) < 0.5)) / 0.6
    assert gap_density < 0.8 * ref_density, "expected a depletion at eta ~ 0"


def test_phi_is_not_uniform_in_the_barrel(muons):
    """Barrel azimuth is measurably non-uniform; the endcap is much less so.

    The barrel muon chambers are obstructed by the detector's support feet at
    the bottom. This asymmetry is real and must not be 'corrected' away.
    """
    eta, phi = muons["eta"].ravel(), muons["phi"].ravel()

    def chi2_per_dof(sample: np.ndarray) -> float:
        counts, _ = np.histogram(sample, bins=24, range=(-np.pi, np.pi))
        exp = counts.mean()
        return float((((counts - exp) ** 2) / exp).sum() / (len(counts) - 1))

    barrel = chi2_per_dof(phi[np.abs(eta) < 1.05])
    endcap = chi2_per_dof(phi[np.abs(eta) > 1.3])
    assert barrel > 2.0, "barrel phi should show structure"
    assert barrel > endcap, "barrel should be less uniform than the endcap"
