"""Feature extraction for the H->ZZ->4l classification task.

Design decision: ``m_4l`` is NOT a feature
-------------------------------------------
The four-lepton invariant mass is the single most discriminating variable --
the Higgs sits at 125 GeV and the background does not. Including it would
give a near-perfect classifier that has learned nothing except "is it 125?".

Worse, it would be scientifically self-defeating. Cutting on a score that
depends on mass **sculpts** the background: it carves a bump-shaped deficit
into the mass spectrum, destroying the ability to later fit that spectrum for
an excess. Since the mass spectrum is the measurement, the mass must not be
the thing we cut on.

This mirrors the real analysis strategy: use the other kinematics to enrich
the signal, then examine ``m_4l`` for the excess. ``m_4l`` is still computed
and carried alongside the features, so it can be plotted and fitted -- it is
simply excluded from the model's inputs.
"""

from __future__ import annotations

import awkward as ak
import numpy as np

from collider.physics.fourvector import to_cartesian
from collider.physics.selection import PAIRINGS, pair_into_z_candidates, select_four_lepton

__all__ = ["FEATURE_NAMES", "build_features"]

#: Model inputs, in a fixed order. Order is part of the contract -- a model
#: artifact is only valid for the feature vector it was trained on.
FEATURE_NAMES = (
    "m_z1",  # on-shell Z candidate mass
    "m_z2",  # off-shell Z candidate mass; small for signal, on-shell for ZZ
    "m_z2_over_m_z1",
    "lep_pt_0",  # lepton pt, sorted descending
    "lep_pt_1",
    "lep_pt_2",
    "lep_pt_3",
    "lep_abs_eta_max",
    "pt_4l",  # transverse momentum of the four-lepton system
    "delta_phi_zz",  # azimuthal separation of the two Z candidates
    "delta_eta_zz",
    "met",
    "jet_n",
    "n_muons",  # flavour composition: 4mu / 2mu2e / 4e
)

READ_BRANCHES = (
    "lep_n",
    "lep_type",
    "lep_pt",
    "lep_eta",
    "lep_phi",
    "lep_e",
    "lep_charge",
    "lep_isTightID",
    "lep_isTightIso",
    "met",
    "jet_n",
)


def _pair_masses(px, py, pz, e, idx_a, idx_b):
    """Invariant mass of the two leptons at the given column indices."""
    ex, ey = px[:, idx_a] + px[:, idx_b], py[:, idx_a] + py[:, idx_b]
    ez, et = pz[:, idx_a] + pz[:, idx_b], e[:, idx_a] + e[:, idx_b]
    m2 = et**2 - (ex**2 + ey**2 + ez**2)
    return np.sqrt(np.maximum(m2, 0.0))


def build_features(events: ak.Array) -> dict[str, np.ndarray]:
    """Select four-lepton events and compute model features.

    Returns a dict with ``features`` of shape ``(n_selected, len(FEATURE_NAMES))``,
    the held-out ``m_4l``, and the index of each surviving event in the input.
    """
    keep = select_four_lepton(events)
    ev = events[keep]
    source_index = np.flatnonzero(ak.to_numpy(keep))
    if len(ev) == 0:
        return {
            "features": np.empty((0, len(FEATURE_NAMES))),
            "m_4l": np.empty(0),
            "source_index": source_index,
        }

    # Selection guarantees exactly four leptons, so a rectangular array is
    # valid here and lets the rest of this run as plain NumPy.
    order = ak.argsort(ev.lep_pt, axis=1, ascending=False)
    pt = ak.to_numpy(ev.lep_pt[order]).astype(np.float64)
    eta = ak.to_numpy(ev.lep_eta[order]).astype(np.float64)
    phi = ak.to_numpy(ev.lep_phi[order]).astype(np.float64)
    energy = ak.to_numpy(ev.lep_e[order]).astype(np.float64)
    ltype = ak.to_numpy(ev.lep_type[order]).astype(np.int64)
    charge = ak.to_numpy(ev.lep_charge[order]).astype(np.int64)

    px, py, pz = to_cartesian(pt, eta, phi)

    # m_4l -- computed, carried, but deliberately excluded from the features.
    m2_4l = energy.sum(1) ** 2 - (px.sum(1) ** 2 + py.sum(1) ** 2 + pz.sum(1) ** 2)
    m_4l = np.sqrt(np.maximum(m2_4l, 0.0))

    pair_mass = np.stack(
        [
            np.stack([_pair_masses(px, py, pz, energy, a[0], a[1]) for a in pairing], axis=1)
            for pairing in PAIRINGS
        ],
        axis=1,
    )  # (n, 3, 2)
    m_z1, m_z2, valid = pair_into_z_candidates(ltype, charge, pair_mass)

    # Drop events with no valid same-flavour opposite-sign pairing.
    px, py, pz = px[valid], py[valid], pz[valid]
    pt, eta, energy = pt[valid], eta[valid], energy[valid]
    ltype = ltype[valid]
    m_4l, m_z1, m_z2 = m_4l[valid], m_z1[valid], m_z2[valid]
    source_index = source_index[valid]
    met = ak.to_numpy(ev.met).astype(np.float64)[valid]
    jet_n = ak.to_numpy(ev.jet_n).astype(np.float64)[valid]

    # Z-candidate kinematics, using the leading pair as a proxy for Z1 axis.
    zz_phi_a = np.arctan2(py[:, 0] + py[:, 1], px[:, 0] + px[:, 1])
    zz_phi_b = np.arctan2(py[:, 2] + py[:, 3], px[:, 2] + px[:, 3])
    dphi = np.abs(np.mod(zz_phi_a - zz_phi_b + np.pi, 2 * np.pi) - np.pi)

    p_a = np.sqrt((px[:, :2].sum(1)) ** 2 + (py[:, :2].sum(1)) ** 2 + (pz[:, :2].sum(1)) ** 2)
    p_b = np.sqrt((px[:, 2:].sum(1)) ** 2 + (py[:, 2:].sum(1)) ** 2 + (pz[:, 2:].sum(1)) ** 2)
    eta_a = np.arctanh(np.clip(pz[:, :2].sum(1) / np.maximum(p_a, 1e-12), -0.999999, 0.999999))
    eta_b = np.arctanh(np.clip(pz[:, 2:].sum(1) / np.maximum(p_b, 1e-12), -0.999999, 0.999999))

    columns = {
        "m_z1": m_z1,
        "m_z2": m_z2,
        "m_z2_over_m_z1": m_z2 / np.maximum(m_z1, 1e-9),
        "lep_pt_0": pt[:, 0],
        "lep_pt_1": pt[:, 1],
        "lep_pt_2": pt[:, 2],
        "lep_pt_3": pt[:, 3],
        "lep_abs_eta_max": np.abs(eta).max(axis=1),
        "pt_4l": np.sqrt(px.sum(1) ** 2 + py.sum(1) ** 2),
        "delta_phi_zz": dphi,
        "delta_eta_zz": np.abs(eta_a - eta_b),
        "met": met,
        "jet_n": jet_n,
        "n_muons": (ltype == 13).sum(axis=1).astype(np.float64),
    }
    features = np.column_stack([columns[name] for name in FEATURE_NAMES])

    return {"features": features, "m_4l": m_4l, "source_index": source_index}
