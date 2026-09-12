"""Regenerate the dimuon test fixture from the source ROOT file.

Usage:
    python scripts/make_dimuon_fixture.py

Requires data/raw/ODEO_FEB2025_v0_2muons_data15_periodD.2muons.root
(see data/raw/README.md for provenance and checksum).
"""

from pathlib import Path

import awkward as ak
import numpy as np

from collider.data.atlas import load_leptons, select_dilepton

SOURCE = Path("data/raw/ODEO_FEB2025_v0_2muons_data15_periodD.2muons.root")
OUTPUT = Path("tests/fixtures/dimuon_data15_periodD.npz")
N_EVENTS = 12_000
SEED = 20260912  # fixed so the fixture is byte-reproducible

FIELDS = ("pt", "eta", "phi", "energy", "charge")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing source file: {SOURCE}\nSee data/raw/README.md")

    muons = select_dilepton(load_leptons(SOURCE))
    n_available = len(muons["pt"])
    print(f"selected {n_available:,} opposite-charge dimuon events")

    rng = np.random.default_rng(SEED)
    idx = np.sort(rng.choice(n_available, size=N_EVENTS, replace=False))

    arrays = {f: ak.to_numpy(muons[f])[idx].astype(np.float32) for f in FIELDS}
    for f, arr in arrays.items():
        assert arr.shape == (N_EVENTS, 2), f"{f}: unexpected shape {arr.shape}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUTPUT, **arrays)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
