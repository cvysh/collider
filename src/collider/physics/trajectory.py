"""Charged-particle trajectories in the ATLAS solenoidal field.

A charged particle in a uniform magnetic field along the beam axis follows a
**helix**: a circle in the transverse plane, advancing linearly along z.

The radius follows from balancing the Lorentz force against circular motion::

    r [metres] = pt [GeV] / (0.3 * |q| * B [tesla])

The 0.3 is ``c`` in the unit system particle physicists use, where momentum is
in GeV and distance in metres.

What this means for the display -- and it is not what people expect
--------------------------------------------------------------------
The ATLAS solenoid is 2 T and the inner detector reaches about 1.1 m. For the
muons in this dataset:

========  ============  ==========================  ==========
pt (GeV)  radius (m)    bend across the ID (deg)    sagitta
========  ============  ==========================  ==========
1         1.67          38.5                        91 mm
10        16.7          3.8                          9 mm
45        75.0          0.84                         2 mm
90        150.0         0.42                         1 mm
========  ============  ==========================  ==========

**An honest track from a 45 GeV muon bends by under one degree.** The dramatic
spirals in famous event displays come from sub-GeV particles. High-momentum
tracks are nearly straight -- which is precisely why curvature measures
momentum: the less a track bends, the stiffer it is.

The renderer therefore draws true geometry by default. Any exaggeration must
be an explicitly labelled visual aid, never the default, and never presented
as the measured trajectory (docs/SCIENTIFIC_INTEGRITY.md section 4).

What *is* real even at small bend is the **direction**: positive and negative
charges curve opposite ways. That sign is genuine measured information.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "ATLAS_SOLENOID_TESLA",
    "INNER_DETECTOR_RADIUS_M",
    "helix_points",
    "helix_radius",
]

#: ATLAS central solenoid field strength, tesla.
ATLAS_SOLENOID_TESLA = 2.0

#: Approximate outer radius of the inner detector, metres. Beyond this the
#: field is the toroid rather than the solenoid and this model no longer holds.
INNER_DETECTOR_RADIUS_M = 1.1

#: c in the GeV/metre/tesla unit system.
_C_FACTOR = 0.299792458


def helix_radius(
    pt: np.ndarray | float,
    charge: np.ndarray | float,
    *,
    field_tesla: float = ATLAS_SOLENOID_TESLA,
) -> np.ndarray:
    """Radius of curvature in metres.

    Neutral particles return ``inf``: they do not bend, and the caller should
    draw a straight ray. Returning ``inf`` rather than raising lets a mixed
    list of charged and neutral objects be handled in one vectorised call.
    """
    pt = np.asarray(pt, dtype=np.float64)
    q = np.abs(np.asarray(charge, dtype=np.float64))
    with np.errstate(divide="ignore"):
        return np.where(q > 0, pt / (_C_FACTOR * np.maximum(q, 1e-12) * field_tesla), np.inf)


def helix_points(
    pt: float,
    eta: float,
    phi: float,
    charge: float,
    *,
    max_radius_m: float = INNER_DETECTOR_RADIUS_M,
    n_points: int = 32,
    field_tesla: float = ATLAS_SOLENOID_TESLA,
    curvature_scale: float = 1.0,
) -> np.ndarray:
    """Sample a helical trajectory starting at the interaction point.

    Parameters
    ----------
    curvature_scale
        Multiplies the bending only. ``1.0`` is the true trajectory. Larger
        values are a **visual aid** and must be labelled as such wherever they
        are shown -- an exaggerated track is not the measured one.

    Returns
    -------
    Array of shape ``(n_points, 3)`` in metres, starting at the origin.

    Notes
    -----
    Derivation of the transverse motion. Work in a frame where ``u`` is along
    the initial momentum direction and ``v`` is perpendicular to it. A particle
    of charge ``q`` in a field along ``+z`` feels ``F = qv x B``, which for a
    positive charge moving along ``+u`` points along ``-v``. Turning through
    angle ``a`` about the circle centre gives::

        u = r * sin(a)
        v = -q * r * (1 - cos(a))

    which is then rotated into the lab frame by ``phi``. Longitudinally the
    particle advances at constant ``pz/pt`` per unit transverse arc length,
    since the field does no work and ``pz`` is unchanged.
    """
    if n_points < 2:
        raise ValueError("n_points must be at least 2")

    # pz/pt = sinh(eta): the same relation used in to_cartesian().
    slope = np.sinh(eta)

    if charge == 0 or not np.isfinite(helix_radius(pt, charge, field_tesla=field_tesla)):
        # Neutral: straight ray along the momentum direction.
        s = np.linspace(0.0, max_radius_m, n_points)
        return np.column_stack([s * np.cos(phi), s * np.sin(phi), s * slope])

    radius = float(helix_radius(pt, charge, field_tesla=field_tesla))
    # Exaggeration acts on the bending, i.e. on a smaller effective radius.
    effective_radius = radius / max(curvature_scale, 1e-9)

    # Turn angle needed to reach max_radius_m in the transverse plane. For a
    # chord of length L on a circle of radius R, the subtended angle is
    # 2*arcsin(L/2R); clamp for the case where the circle is smaller than the
    # detector and the particle curls back inside it.
    ratio = np.clip(max_radius_m / (2.0 * effective_radius), -1.0, 1.0)
    max_angle = 2.0 * np.arcsin(ratio)

    angle = np.linspace(0.0, max_angle, n_points)
    sign = np.sign(charge)

    u = effective_radius * np.sin(angle)
    v = -sign * effective_radius * (1.0 - np.cos(angle))

    x = u * np.cos(phi) - v * np.sin(phi)
    y = u * np.sin(phi) + v * np.cos(phi)
    # Transverse arc length is r*angle; z advances by pz/pt times that.
    z = effective_radius * angle * slope

    return np.column_stack([x, y, z])
