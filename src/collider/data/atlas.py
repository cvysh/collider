"""Loading ATLAS Open Data education ntuples.

Source: ATLAS 13 TeV 2015+2016 education release (see docs/DATA_SOURCES.md).

Verified facts about this release, established by inspecting the files rather
than assuming (docs/decisions/0001-dataset-choice.md):

* Kinematic quantities are in **GeV**. (The older 2020 13 TeV release used MeV;
  do not carry that assumption over.)
* ``lep_type`` is the absolute PDG id: 11 = electron, 13 = muon.
* ``mcWeight == 1.0`` and ``category`` starts with ``"data"`` for real
  collision data. MC carries genuine weights.
* The tree is named ``analysis``.
"""

from __future__ import annotations

from pathlib import Path

import awkward as ak
import uproot

__all__ = ["PDG_ELECTRON", "PDG_MUON", "TREE_NAME", "load_leptons", "select_dilepton"]

TREE_NAME = "analysis"
PDG_ELECTRON = 11
PDG_MUON = 13

_LEPTON_BRANCHES = [
    "lep_type",
    "lep_pt",
    "lep_eta",
    "lep_phi",
    "lep_e",
    "lep_charge",
]


def load_leptons(path: str | Path, *, entry_stop: int | None = None) -> ak.Array:
    """Read the lepton branches from an ATLAS education ntuple.

    Only the columns we need are read. ROOT is a columnar format, so requesting
    6 of 119 branches reads roughly 6/119 of the bytes -- this is why we do not
    load the whole tree and filter afterwards.
    """
    with uproot.open(f"{Path(path)}:{TREE_NAME}") as tree:
        return tree.arrays(_LEPTON_BRANCHES, entry_stop=entry_stop)


def select_dilepton(events: ak.Array, *, flavour: int = PDG_MUON) -> dict[str, ak.Array]:
    """Select events with exactly two opposite-charge leptons of one flavour.

    Why 'exactly two' rather than 'at least two'
    --------------------------------------------
    Invariant mass is only meaningful for a set of objects that plausibly came
    from one parent. The ``2muons`` skim guarantees at least two muons, but
    about 7% of events contain a third or fourth lepton from another source.
    Feeding all of them into one mass sum adds unrelated momentum and pushes
    those events to higher mass, smearing the resonance into the background.

    Why 'opposite charge'
    ---------------------
    The Z is neutral, so its decay products must carry net zero charge. Keeping
    same-charge pairs admits combinatorial background that cannot be signal.
    Here it removes about 8% of two-muon events.

    Returns
    -------
    Dict of ``pt``, ``eta``, ``phi``, ``energy``, ``charge``, each a jagged
    array of exactly two entries per surviving event.
    """
    is_flavour = events.lep_type == flavour

    picked = {
        "pt": events.lep_pt[is_flavour],
        "eta": events.lep_eta[is_flavour],
        "phi": events.lep_phi[is_flavour],
        "energy": events.lep_e[is_flavour],
        "charge": events.lep_charge[is_flavour],
    }

    keep = (ak.num(picked["pt"]) == 2) & (ak.sum(picked["charge"], axis=1) == 0)
    return {k: v[keep] for k, v in picked.items()}
