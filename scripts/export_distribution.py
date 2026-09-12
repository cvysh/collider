"""Export the weighted four-lepton mass spectrum for the web app.

Usage:
    python scripts/export_distribution.py

Writes data/processed/distributions/m4l_v1.json.

This is the plot the whole 'exclude m_4l from the features' decision exists to
protect. Because the classifier never saw the mass, cutting on its score does
not carve a bump-shaped hole in the background, and the spectrum can still be
read for an excess.

Everything here is **simulation**. Real 4-lepton data is not overlaid: only one
event in the available file survives selection (docs/FINDINGS.md #4), and a
single entry on a histogram is noise, not a measurement.
"""

import json
from pathlib import Path

import numpy as np

from collider.features.dataset import split_indices
from collider.physics.weights import effective_entries

DATASET = Path("data/processed/fourlepton_v1.npz")
OUTPUT = Path("data/processed/distributions/m4l_v1.json")
LO, HI, N_BINS = 80.0, 250.0, 34  # 5 GeV bins
SEED = 20260912


def main() -> None:
    if not DATASET.exists():
        raise SystemExit(f"missing {DATASET}; run scripts/prepare_dataset.py first")

    d = np.load(DATASET)
    labels, weights = d["labels"], d["physical_weight"]
    m4l = d["m_4l"].astype(np.float64)
    lumi = float(d["luminosity_pb"])

    edges = np.linspace(LO, HI, N_BINS + 1)
    centres = 0.5 * (edges[:-1] + edges[1:])

    # Leading-lepton pT per event, so the spectrum can be recut interactively
    # in the browser. Precomputing one histogram per threshold keeps the
    # interaction instant without shipping per-event data to the client.
    lead_pt = d["features"][:, list(map(str, d["feature_names"])).index("lep_pt_0")]
    CUTS = [0, 20, 30, 40, 50, 60]

    def binned(mask):
        counts, _ = np.histogram(m4l[mask], bins=edges, weights=weights[mask])
        # Statistical uncertainty on a weighted sum is sqrt(sum w^2), never
        # sqrt(N) -- see docs/FINDINGS.md #3.
        sq, _ = np.histogram(m4l[mask], bins=edges, weights=weights[mask] ** 2)
        rows, _ = np.histogram(m4l[mask], bins=edges)
        return counts, np.sqrt(sq), rows

    sig, sig_err, sig_rows = binned(labels == 1)
    bkg, bkg_err, bkg_rows = binned(labels == 0)

    # N_eff per bin for the background: the honest statement of how much the
    # simulation can actually support, bin by bin.
    bkg_neff = []
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        in_bin = (labels == 0) & (m4l >= lo) & (m4l < hi)
        bkg_neff.append(round(effective_entries(weights[in_bin]), 1))

    cut_series = []
    for cut in CUTS:
        passing = lead_pt >= cut
        sig_c, _, _ = binned((labels == 1) & passing)
        bkg_c, _, _ = binned((labels == 0) & passing)
        cut_series.append(
            {
                "cut": cut,
                "signal": [round(float(v), 4) for v in sig_c],
                "background": [round(float(v), 4) for v in bkg_c],
                "signal_total": round(float(sig_c.sum()), 3),
                "background_total": round(float(bkg_c.sum()), 3),
            }
        )

    _, _, test_idx = split_indices(len(labels), seed=SEED)

    payload = {
        "schema_version": "1.0",
        "quantity": "m_4l",
        "unit": "GeV",
        "luminosity_pb": lumi,
        "bin_width": float(edges[1] - edges[0]),
        "edges": [round(float(e), 2) for e in edges],
        "centres": [round(float(c), 2) for c in centres],
        "series": [
            {
                "id": "background",
                "label": "ZZ→4ℓ (simulated background)",
                "values": [round(float(v), 4) for v in bkg],
                "errors": [round(float(v), 4) for v in bkg_err],
                "raw_rows": [int(v) for v in bkg_rows],
                "n_eff": bkg_neff,
            },
            {
                "id": "signal",
                "label": "ggH→ZZ→4ℓ (simulated signal)",
                "values": [round(float(v), 4) for v in sig],
                "errors": [round(float(v), 4) for v in sig_err],
                "raw_rows": [int(v) for v in sig_rows],
            },
        ],
        "annotations": [
            {"at": 125.0, "label": "m_H = 125 GeV", "note": "Particle Data Group value"},
            {"at": 91.2, "label": "m_Z = 91.2 GeV", "note": "single-Z background"},
            {"at": 182.0, "label": "2·m_Z", "note": "two on-shell Z bosons become possible"},
        ],
        "pt_cuts": {
            "feature": "lep_pt_0",
            "label": "leading lepton pT",
            "unit": "GeV",
            "series": cut_series,
        },
        "caveats": [
            "Simulation only. Real 4-lepton data is not overlaid: one event in the "
            "available file survives selection, and a single entry is not a measurement.",
            "Signal is gluon-gluon fusion production only; VBF, VH and ttH are excluded.",
            "Background is the irreducible ZZ→4ℓ only. Fake and non-prompt leptons, "
            "which dominate real data before selection, are not modelled.",
            "m_4l is deliberately withheld from the classifier's features, so a score "
            "cut does not sculpt this spectrum.",
        ],
        "totals": {
            "signal": round(float(sig.sum()), 2),
            "background": round(float(bkg.sum()), 2),
            "test_split_fraction": round(len(test_idx) / len(labels), 3),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=1) + "\n")

    peak = int(np.argmax(sig))
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KB)")
    print(f"  signal total     {sig.sum():8.2f} events in {lumi / 1000:.0f} fb^-1")
    print(f"  background total {bkg.sum():8.2f}")
    print(f"  signal peak bin  {centres[peak]:.1f} GeV  ({sig[peak]:.2f} events)")
    print(f"  S/B at peak      {sig[peak] / max(bkg[peak], 1e-9):.2f}")
    print(f"  bkg N_eff there  {bkg_neff[peak]:.1f}")
    print("\n  leading-lepton pT cut scan:")
    for c in cut_series:
        s_, b_ = c["signal_total"], c["background_total"]
        print(
            f"    >= {c['cut']:2d} GeV   S {s_:6.2f}   B {b_:8.2f}   S/B {s_ / max(b_, 1e-9):.4f}"
        )


if __name__ == "__main__":
    main()
