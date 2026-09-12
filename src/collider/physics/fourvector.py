"""Relativistic four-vector arithmetic on (possibly jagged) arrays.

The detector reports objects in collider coordinates (pt, eta, phi, E) rather
than Cartesian (px, py, pz, E). This module converts between them and computes
invariant mass.

Unit convention
---------------
Everything in this module is in **GeV**. Conversion from the source file's
units happens once, at the loader boundary, never here. A mixed-unit codebase
is how you end up with a Z peak at 91,200.
"""

from __future__ import annotations

import awkward as ak
import numpy as np

__all__ = ["to_cartesian", "invariant_mass", "pseudorapidity"]


def to_cartesian(pt, eta, phi):
    """Convert collider coordinates to Cartesian momentum components.

    Geometry: the beam runs along z. ``pt`` is the momentum projected into the
    transverse (x, y) plane, ``phi`` is the azimuthal angle within that plane,
    and ``eta`` encodes the polar angle relative to the beam.

        px = pt * cos(phi)
        py = pt * sin(phi)
        pz = pt * sinh(eta)

    The ``sinh`` is the line people get wrong. It follows from the definition
    eta = -ln(tan(theta/2)), which inverts to pz/pt = sinh(eta). Using tan or
    cos here produces a plausible-looking but wrong momentum, and the error is
    small at central eta -- so it survives casual inspection and then quietly
    corrupts every mass downstream.

    Works elementwise on NumPy or jagged awkward arrays alike.
    """
    return (
        pt * np.cos(phi),
        pt * np.sin(phi),
        pt * np.sinh(eta),
    )


def invariant_mass(pt, eta, phi, energy):
    """Invariant mass of all objects in each event, summed over the inner axis.

    m^2 = (sum E)^2 - |sum p|^2

    This is the mass of whatever parent particle could have produced this set
    of objects. It is 'invariant' because every inertial observer computes the
    same value, which is why it identifies a particle.

    Parameters take jagged arrays shaped (n_events, n_objects_in_event). The
    sum runs over axis=1, so each event collapses to one mass.

    Returns
    -------
    Array of one mass per event, in GeV.

    Notes
    -----
    The ``m2 < 0`` clamp is not cosmetic. Muons are nearly massless relative to
    their energy, so (sum E)^2 and |sum p|^2 are two large nearly-equal
    floats; their difference can land slightly below zero purely from float32
    rounding. Without the clamp, ``sqrt`` returns NaN, one NaN poisons the
    histogram bin, and the failure looks like missing data rather than a
    numerical artifact.
    """
    px, py, pz = to_cartesian(pt, eta, phi)

    # Sum the four-vector components over the objects within each event.
    # Energy and momentum are additive -- this is the whole physical basis of
    # the calculation.
    e_tot = ak.sum(energy, axis=1)
    px_tot = ak.sum(px, axis=1)
    py_tot = ak.sum(py, axis=1)
    pz_tot = ak.sum(pz, axis=1)

    m2 = e_tot**2 - (px_tot**2 + py_tot**2 + pz_tot**2)
    return np.sqrt(np.maximum(m2, 0.0))


def pseudorapidity(pz, p):
    """Pseudorapidity from longitudinal and total momentum.

    eta = 0.5 * ln((p + pz) / (p - pz))

    Diverges as the momentum aligns with the beam (pz -> p), which is physical:
    eta is unbounded in the forward direction. We clip the ratio into the
    representable range and return a large finite value rather than inf, so
    downstream aggregations do not silently become NaN.
    """
    num = p + pz
    den = p - pz
    tiny = np.finfo(np.float64).tiny
    return 0.5 * np.log(np.maximum(num, tiny) / np.maximum(den, tiny))
