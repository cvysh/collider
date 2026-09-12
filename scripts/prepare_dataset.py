"""Build the labelled 4-lepton dataset from the MC files and cache it.

Usage:
    python scripts/prepare_dataset.py

Reads data/raw/4lep/, applies selection, computes features and weights, and
writes data/processed/fourlepton_v1.npz. Downstream training reads only the
cache, so the expensive ROOT pass happens once.

The cache records the luminosity, seed and feature names it was built with.
A model artifact is only valid for the feature ordering recorded here.
"""

from pathlib import Path

import awkward as ak
import numpy as np
import uproot

from collider.features.dataset import build_dataset
from collider.features.fourlepton import FEATURE_NAMES, READ_BRANCHES, build_features
from collider.physics.weights import SCALE_FACTOR_BRANCHES, effective_entries, event_weights

RAW = Path("data/raw/4lep")
OUTPUT = Path("data/processed/fourlepton_v1.npz")
LUMI_PB = 36_000.0

SAMPLES = {
    "signal": RAW
    / ("ODEO_FEB2025_v0_4lep_mc_345060.PowhegPythia8EvtGen_NNLOPS_nnlo_30_ggH125_ZZ4l.4lep.root"),
    "background": RAW / "ODEO_FEB2025_v0_4lep_mc_700600.Sh_2212_llll.4lep.root",
}

WEIGHT_READ = ["mcWeight", "xsec", "filteff", "kfac", "sum_of_weights", *SCALE_FACTOR_BRANCHES]


def load_sample(path: Path) -> dict:
    with uproot.open(f"{path}:analysis") as tree:
        ev = tree.arrays(sorted(set(READ_BRANCHES) | set(WEIGHT_READ)))

    scale = np.ones(len(ev), dtype=np.float64)
    for branch in SCALE_FACTOR_BRANCHES:
        scale *= ak.to_numpy(ev[branch]).astype(np.float64)

    weights = event_weights(
        ak.to_numpy(ev.mcWeight),
        xsec=float(ak.to_numpy(ev.xsec)[0]),
        filt_eff=float(ak.to_numpy(ev.filteff)[0]),
        kfac=float(ak.to_numpy(ev.kfac)[0]),
        sum_of_weights=float(ak.to_numpy(ev.sum_of_weights)[0]),
        luminosity_pb=LUMI_PB,
        scale_factors=scale,
    )

    result = build_features(ev)
    result["weights"] = weights[result["source_index"]]
    result["n_input"] = len(ev)
    return result


def main() -> None:
    for path in SAMPLES.values():
        if not path.exists():
            raise SystemExit(f"missing {path}; see data/raw/README.md")

    parts = {name: load_sample(path) for name, path in SAMPLES.items()}
    for name, part in parts.items():
        w = part["weights"]
        print(
            f"{name:11s} {part['n_input']:7,} -> {len(w):7,} selected  "
            f"yield {w.sum():8.2f}  N_eff {effective_entries(w):8,.0f}  "
            f"neg {(w < 0).mean():.2%}"
        )

    ds = build_dataset(
        signal_features=parts["signal"]["features"],
        signal_weights=parts["signal"]["weights"],
        background_features=parts["background"]["features"],
        background_weights=parts["background"]["weights"],
        signal_m4l=parts["signal"]["m_4l"],
        background_m4l=parts["background"]["m_4l"],
        feature_names=FEATURE_NAMES,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT,
        features=ds.features.astype(np.float32),
        labels=ds.labels,
        train_weight=ds.train_weight.astype(np.float64),
        physical_weight=ds.physical_weight.astype(np.float64),
        m_4l=ds.m_4l.astype(np.float32),
        feature_names=np.array(ds.feature_names),
        luminosity_pb=np.array(LUMI_PB),
    )
    print(f"\nwrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
    print(f"  {len(ds):,} events, {ds.features.shape[1]} features")


if __name__ == "__main__":
    main()
