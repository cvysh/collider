"""Event selection for the H->ZZ->4l channel.

Why a selection is mandatory, not optional
------------------------------------------
The ``4lep`` skim requires four lepton *candidates*, which is deliberately
loose so that downstream analyses can impose their own quality criteria. It is
not a physics selection.

Measured on the files in ``data/raw/4lep`` (see docs/FINDINGS.md):

============================  ======  ======  ======
                               ggH     ZZ      data
============================  ======  ======  ======
leptons passing tight ID       86.7%   87.6%   17.7%
leptons passing tight iso      79.8%   83.6%    1.9%
median \\|d0sig\\|               0.65    0.67    1.48
============================  ======  ======  ======

Real data at this stage is dominated by **fake and non-prompt leptons** --
jets misreconstructed as electrons, and leptons from heavy-flavour decays
inside jets, which is why their impact parameters are large. The MC samples
model only the *irreducible* background (genuine ZZ->4l) and contain no fakes.

A model trained on MC where 87% of leptons are tight, then applied to data
where 18% are, is being evaluated far outside its training distribution. The
same selection must be applied everywhere.
"""

from __future__ import annotations

import awkward as ak
import numpy as np

__all__ = ["PDG_ELECTRON", "PDG_MUON", "Z_MASS", "select_four_lepton", "pair_into_z_candidates"]

PDG_ELECTRON = 11
PDG_MUON = 13
Z_MASS = 91.1880  # GeV

LEPTON_BRANCHES = (
    "lep_n",
    "lep_type",
    "lep_pt",
    "lep_eta",
    "lep_phi",
    "lep_e",
    "lep_charge",
    "lep_isTightID",
    "lep_isTightIso",
)


def select_four_lepton(events: ak.Array) -> ak.Array:
    """Boolean mask: events with four good, prompt, charge-balanced leptons.

    Criteria, in order:

    1. Exactly four lepton candidates. Events with a fifth are ambiguous to
       pair and are a small fraction (~1%).
    2. All four pass tight identification and tight isolation. This is the cut
       that suppresses fakes, and the one that separates a physics sample from
       a skim.
    3. Net charge zero. Two Z bosons are neutral, so their decay products must
       balance. Non-zero net charge indicates at least one misreconstructed
       charge or a fake.
    """
    exactly_four = events.lep_n == 4
    good = events.lep_isTightID & events.lep_isTightIso
    all_good = ak.sum(good, axis=1) == 4
    neutral = ak.sum(events.lep_charge, axis=1) == 0
    return exactly_four & all_good & neutral


#: The three distinct ways to split four leptons into two pairs.
PAIRINGS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))


def pair_into_z_candidates(
    lep_type: np.ndarray,
    lep_charge: np.ndarray,
    pair_mass: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Split four leptons into two Z candidates.

    In a genuine ``H -> ZZ -> 4l`` decay one Z is on-shell near 91 GeV and the
    other is virtual and lighter, because a 125 GeV Higgs has too little mass
    to make two real Z bosons. In non-resonant ``ZZ`` background both tend to
    be on-shell. That asymmetry is among the strongest discriminators
    available, and crucially it does **not** require the four-lepton mass --
    so using it does not sculpt the spectrum we later want to fit.

    Pairing rule: among same-flavour opposite-sign (SFOS) pairings, take the
    one containing the pair closest to the Z mass. That pair is ``Z1``; the
    other is ``Z2``. This is the standard convention.

    Parameters
    ----------
    lep_type, lep_charge
        Shape ``(n_events, 4)``. PDG ids and charges.
    pair_mass
        Shape ``(n_events, 3, 2)``: for each of the three pairings, the masses
        of its two pairs, ordered to match :data:`PAIRINGS`.

    Returns
    -------
    ``(m_z1, m_z2, valid)``
        Candidate masses in GeV and a mask marking events where at least one
        SFOS pairing exists. Masses are ``nan`` where ``valid`` is ``False``.
    """
    n = len(lep_type)
    is_sfos = np.zeros((n, 3), dtype=bool)
    for k, (pair_a, pair_b) in enumerate(PAIRINGS):
        ok = np.ones(n, dtype=bool)
        for i, j in (pair_a, pair_b):
            ok &= lep_type[:, i] == lep_type[:, j]
            ok &= lep_charge[:, i] + lep_charge[:, j] == 0
        is_sfos[:, k] = ok

    # Within each pairing, Z1 is the pair nearer the Z mass.
    near = np.abs(pair_mass - Z_MASS)
    z1_idx = np.argmin(near, axis=2)  # (n, 3)
    rows, cols = np.indices(z1_idx.shape)
    m_z1_per_pairing = pair_mass[rows, cols, z1_idx]
    m_z2_per_pairing = pair_mass[rows, cols, 1 - z1_idx]

    # Choose the SFOS pairing whose Z1 is closest to the Z mass.
    score = np.where(is_sfos, np.abs(m_z1_per_pairing - Z_MASS), np.inf)
    best = np.argmin(score, axis=1)
    valid = is_sfos.any(axis=1)

    idx = np.arange(n)
    m_z1 = np.where(valid, m_z1_per_pairing[idx, best], np.nan)
    m_z2 = np.where(valid, m_z2_per_pairing[idx, best], np.nan)
    return m_z1, m_z2, valid
