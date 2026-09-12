"""Tests for helical trajectories in the solenoidal field."""

import numpy as np
import pytest

from collider.physics.trajectory import (
    ATLAS_SOLENOID_TESLA,
    INNER_DETECTOR_RADIUS_M,
    helix_points,
    helix_radius,
)


def test_radius_matches_the_textbook_formula():
    """r = pt / (0.3 q B). A 45 GeV muon in 2 T has r = 75 m."""
    r = helix_radius(45.0, -1.0)
    assert r == pytest.approx(45.0 / (0.299792458 * 2.0), rel=1e-9)
    assert r == pytest.approx(75.0, rel=0.01)


def test_radius_grows_linearly_with_momentum():
    """Stiffer tracks bend less -- the basis of momentum measurement."""
    assert helix_radius(90.0, 1.0) == pytest.approx(2 * helix_radius(45.0, 1.0))


def test_radius_ignores_charge_sign():
    """Sign sets the direction of the bend, not how tight it is."""
    assert helix_radius(30.0, 1.0) == pytest.approx(helix_radius(30.0, -1.0))


def test_neutral_particles_do_not_bend():
    assert np.isinf(helix_radius(50.0, 0.0))


def test_neutral_track_is_a_straight_ray():
    pts = helix_points(50.0, 0.0, 0.0, charge=0)
    y = pts[:, 1]
    assert np.allclose(y, 0.0, atol=1e-12)
    assert pts[-1, 0] == pytest.approx(INNER_DETECTOR_RADIUS_M)


def test_track_starts_at_the_interaction_point():
    pts = helix_points(20.0, 0.5, 1.0, charge=-1)
    assert np.allclose(pts[0], 0.0, atol=1e-12)


def test_opposite_charges_bend_opposite_ways():
    """The bend direction is real measured information, even when small."""
    pos = helix_points(20.0, 0.0, 0.0, charge=+1)
    neg = helix_points(20.0, 0.0, 0.0, charge=-1)
    # Along phi=0 the transverse deflection is in y, with opposite signs.
    assert pos[-1, 1] < 0.0
    assert neg[-1, 1] > 0.0
    assert pos[-1, 1] == pytest.approx(-neg[-1, 1])


def test_high_momentum_tracks_are_nearly_straight():
    """The physically important, visually disappointing fact.

    Two different deviations get quoted for the same track and they must not be
    confused. For a 45 GeV muon crossing the 1.1 m inner detector:

    * **sagitta**, the deviation from the chord joining the endpoints, is
      2.0 mm. This is the quantity a tracking detector measures.
    * **deviation from the initial tangent**, which is what a renderer starting
      a straight ray at the interaction point would show, is 8.1 mm -- exactly
      four times larger, since it goes as ``1 - cos(a)`` against
      ``1 - cos(a/2)``.

    Either way the track is straight to within one percent of its length. A
    display showing a dramatic curve at this momentum is not showing the
    measured trajectory.
    """
    pts = helix_points(45.0, 0.0, 0.0, charge=-1)
    deviation = abs(pts[-1, 1])
    assert deviation == pytest.approx(0.0081, abs=0.0005)
    assert deviation < 0.01 * INNER_DETECTOR_RADIUS_M


def test_low_momentum_tracks_bend_visibly():
    """The same code must produce real curvature where physics says it should."""
    pts = helix_points(1.0, 0.0, 0.0, charge=-1)
    assert abs(pts[-1, 1]) > 0.05


def test_trajectory_reaches_the_requested_radius():
    pts = helix_points(30.0, 0.0, 0.7, charge=1, max_radius_m=1.1)
    transverse = np.hypot(pts[-1, 0], pts[-1, 1])
    assert transverse == pytest.approx(1.1, rel=1e-3)


def test_initial_direction_matches_phi():
    """The track must leave along the measured momentum direction."""
    phi = 2.1
    pts = helix_points(60.0, 0.0, phi, charge=-1, n_points=64)
    step = pts[1, :2] - pts[0, :2]
    assert np.arctan2(step[1], step[0]) == pytest.approx(phi, abs=1e-3)


def test_longitudinal_slope_follows_sinh_eta():
    """dz/ds_transverse = pz/pt = sinh(eta), the same relation as to_cartesian."""
    eta = 1.2
    pts = helix_points(80.0, eta, 0.0, charge=1)
    arc = np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1])).sum()
    assert pts[-1, 2] / arc == pytest.approx(np.sinh(eta), rel=1e-3)


def test_eta_zero_stays_in_the_transverse_plane():
    pts = helix_points(25.0, 0.0, 0.3, charge=-1)
    assert np.allclose(pts[:, 2], 0.0, atol=1e-12)


def test_curvature_scale_only_exaggerates_the_bend():
    """The visual aid must not alter where the track ends radially."""
    true = helix_points(45.0, 0.0, 0.0, charge=-1, curvature_scale=1.0)
    loud = helix_points(45.0, 0.0, 0.0, charge=-1, curvature_scale=40.0)
    assert abs(loud[-1, 1]) > abs(true[-1, 1]) * 10
    for pts in (true, loud):
        assert np.hypot(pts[-1, 0], pts[-1, 1]) == pytest.approx(INNER_DETECTOR_RADIUS_M, rel=1e-3)


def test_field_strength_scales_the_radius_inversely():
    a = helix_radius(40.0, 1.0, field_tesla=ATLAS_SOLENOID_TESLA)
    b = helix_radius(40.0, 1.0, field_tesla=2 * ATLAS_SOLENOID_TESLA)
    assert b == pytest.approx(a / 2)


def test_rejects_degenerate_sampling():
    with pytest.raises(ValueError, match="at least 2"):
        helix_points(10.0, 0.0, 0.0, charge=1, n_points=1)
