"""Tests for four-vector arithmetic, against hand-checkable values."""

import awkward as ak
import numpy as np
import pytest

from collider.physics.fourvector import invariant_mass, to_cartesian


def test_to_cartesian_along_x():
    """phi=0, eta=0 means all momentum along +x."""
    px, py, pz = to_cartesian(np.array([10.0]), np.array([0.0]), np.array([0.0]))
    assert px[0] == pytest.approx(10.0)
    assert py[0] == pytest.approx(0.0)
    assert pz[0] == pytest.approx(0.0)


def test_to_cartesian_along_y():
    """phi=pi/2 rotates the transverse momentum onto +y."""
    px, py, pz = to_cartesian(np.array([10.0]), np.array([0.0]), np.array([np.pi / 2]))
    assert px[0] == pytest.approx(0.0, abs=1e-12)
    assert py[0] == pytest.approx(10.0)


def test_to_cartesian_uses_sinh_not_tan():
    """eta=1 must give pz = pt*sinh(1) = 1.1752*pt, guarding the classic bug."""
    _, _, pz = to_cartesian(np.array([10.0]), np.array([1.0]), np.array([0.0]))
    assert pz[0] == pytest.approx(10.0 * np.sinh(1.0))
    assert pz[0] == pytest.approx(11.752, abs=1e-3)
    # A tan(eta) mistake would give 15.57; assert we are not that.
    assert pz[0] != pytest.approx(10.0 * np.tan(1.0), abs=1e-2)


def test_invariant_mass_back_to_back_massless_pair():
    """Two massless objects, equal pt, opposite phi, eta=0.

    Momenta cancel exactly, so m = sum of energies = 2*pt.
    """
    pt = ak.Array([[50.0, 50.0]])
    eta = ak.Array([[0.0, 0.0]])
    phi = ak.Array([[0.0, np.pi]])
    energy = ak.Array([[50.0, 50.0]])
    m = invariant_mass(pt, eta, phi, energy)
    assert m[0] == pytest.approx(100.0)


def test_invariant_mass_single_massless_object_is_zero():
    """One object with E == |p| has zero invariant mass."""
    m = invariant_mass(ak.Array([[30.0]]), ak.Array([[0.0]]), ak.Array([[0.0]]), ak.Array([[30.0]]))
    assert m[0] == pytest.approx(0.0, abs=1e-6)


def test_invariant_mass_collinear_pair_is_zero():
    """Two massless objects in the same direction: masses add to zero, not 2E."""
    m = invariant_mass(
        ak.Array([[25.0, 25.0]]),
        ak.Array([[0.0, 0.0]]),
        ak.Array([[0.0, 0.0]]),
        ak.Array([[25.0, 25.0]]),
    )
    assert m[0] == pytest.approx(0.0, abs=1e-5)


def test_invariant_mass_never_returns_nan_on_rounding():
    """float32 rounding can push m^2 slightly negative; the clamp must hold."""
    pt = ak.Array([[45.0, 45.0]], with_name=None)
    pt = ak.values_astype(pt, np.float32)
    eta = ak.values_astype(ak.Array([[0.5, 0.5]]), np.float32)
    phi = ak.values_astype(ak.Array([[1.0, 1.0]]), np.float32)
    # Energy set exactly to |p| for a massless pair -- the worst case for
    # catastrophic cancellation.
    px, py, pz = to_cartesian(pt, eta, phi)
    e = np.sqrt(px**2 + py**2 + pz**2)
    m = invariant_mass(pt, eta, phi, e)
    assert not np.isnan(np.asarray(m)).any()
    assert m[0] >= 0.0


def test_invariant_mass_handles_jagged_events():
    """Different object counts per event must all work in one vectorised call."""
    pt = ak.Array([[50.0, 50.0], [30.0], [20.0, 20.0, 20.0]])
    eta = ak.Array([[0.0, 0.0], [0.0], [0.0, 0.0, 0.0]])
    phi = ak.Array([[0.0, np.pi], [0.0], [0.0, 2.094, 4.189]])
    energy = ak.Array([[50.0, 50.0], [30.0], [20.0, 20.0, 20.0]])
    m = invariant_mass(pt, eta, phi, energy)
    assert len(m) == 3
    assert m[0] == pytest.approx(100.0)
    assert m[1] == pytest.approx(0.0, abs=1e-6)
    # Three massless objects at 120 degrees: momenta cancel, m = 60.
    assert m[2] == pytest.approx(60.0, abs=1e-2)
