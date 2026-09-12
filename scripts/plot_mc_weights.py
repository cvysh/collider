"""Show what MC weights do: raw generated counts vs expected physical yield.

Produces docs/figures/mc_weights.png.

The 4-lepton samples make the point starkly. We generated 37x more Higgs
events than ZZ events, because ggH->ZZ->4l is rare and needs the statistics.
In reality ZZ->4l outnumbers the Higgs signal by roughly 28:1. The raw sample
is inverted relative to nature by a factor of about a thousand.
"""

from pathlib import Path

import awkward as ak
import matplotlib
import numpy as np
import uproot

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collider.physics.fourvector import invariant_mass  # noqa: E402
from collider.physics.weights import (  # noqa: E402
    SCALE_FACTOR_BRANCHES,
    effective_entries,
    event_weights,
)

DIR = Path("data/raw/4lep")
SIGNAL = DIR / (
    "ODEO_FEB2025_v0_4lep_mc_345060.PowhegPythia8EvtGen_NNLOPS_nnlo_30_ggH125_ZZ4l.4lep.root"
)
BACKGROUND = DIR / "ODEO_FEB2025_v0_4lep_mc_700600.Sh_2212_llll.4lep.root"
OUTPUT = Path("docs/figures/mc_weights.png")

LUMI_PB = 36_000.0  # 36 fb^-1, the full 2015+2016 release
KINEMATICS = ["lep_pt", "lep_eta", "lep_phi", "lep_e"]


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return four-lepton invariant mass and normalised weight per event."""
    with uproot.open(f"{path}:analysis") as tree:
        ev = tree.arrays(
            [
                *KINEMATICS,
                *(
                    set(("mcWeight", "xsec", "filteff", "kfac", "sum_of_weights"))
                    | set(SCALE_FACTOR_BRANCHES)
                ),
            ]
        )

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

    mass = ak.to_numpy(invariant_mass(ev.lep_pt, ev.lep_eta, ev.lep_phi, ev.lep_e))
    return mass, weights


def main() -> None:
    for p in (SIGNAL, BACKGROUND):
        if not p.exists():
            raise SystemExit(f"missing {p}; see data/raw/README.md")

    m_sig, w_sig = load(SIGNAL)
    m_bkg, w_bkg = load(BACKGROUND)

    bins, rng = 60, (80.0, 250.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))

    # --- raw: what we generated -----------------------------------------
    ax1.hist(
        m_bkg,
        bins=bins,
        range=rng,
        histtype="step",
        lw=1.5,
        color="#1f77b4",
        label=f"ZZ→4ℓ  ({len(m_bkg):,} gen.)",
    )
    ax1.hist(
        m_sig,
        bins=bins,
        range=rng,
        histtype="step",
        lw=1.5,
        color="#d62728",
        label=f"ggH→ZZ→4ℓ  ({len(m_sig):,} gen.)",
    )
    ax1.set_yscale("log")
    ax1.set_xlabel(r"$m_{4\ell}$  [GeV]")
    ax1.set_ylabel("generated events / bin")
    ax1.set_title("(a) RAW — counts we chose to generate")
    ax1.legend(fontsize=8)

    # --- weighted: what nature produces ----------------------------------
    ax2.hist(
        m_bkg,
        bins=bins,
        range=rng,
        weights=w_bkg,
        histtype="stepfilled",
        color="#1f77b4",
        alpha=0.45,
        edgecolor="#1f77b4",
        lw=1.3,
        label=f"ZZ→4ℓ  ({w_bkg.sum():.0f} expected)",
    )
    ax2.hist(
        m_sig,
        bins=bins,
        range=rng,
        weights=w_sig,
        histtype="stepfilled",
        color="#d62728",
        alpha=0.55,
        edgecolor="#d62728",
        lw=1.3,
        label=f"ggH→ZZ→4ℓ  ({w_sig.sum():.1f} expected)",
    )
    ax2.axvline(125, color="#2ca02c", ls=":", lw=1.2)
    ax2.annotate(
        r"$m_H = 125$ GeV",
        xy=(125, ax2.get_ylim()[1] * 0.55),
        xytext=(150, ax2.get_ylim()[1] * 0.72),
        fontsize=8,
        color="#2ca02c",
        arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=0.8),
    )
    ax2.set_xlabel(r"$m_{4\ell}$  [GeV]")
    ax2.set_ylabel(r"expected events / bin in 36 fb$^{-1}$")
    ax2.set_title("(b) WEIGHTED — events nature actually produces")
    ax2.legend(fontsize=8)

    fig.suptitle(
        "Monte Carlo weights invert the sample: same events, different question", fontsize=11
    )
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)
    print(f"wrote {OUTPUT}\n")

    for label, m, w in (("ggH→ZZ→4ℓ", m_sig, w_sig), ("ZZ→4ℓ", m_bkg, w_bkg)):
        print(f"{label}")
        print(f"  generated      : {len(m):,}")
        print(f"  expected yield : {w.sum():.2f}")
        print(
            f"  N_eff          : {effective_entries(w):,.0f} ({effective_entries(w) / len(w):.1%})"
        )
        print(f"  negative wts   : {(w < 0).sum():,} ({(w < 0).mean():.2%})")
    print(f"\nraw ratio     sig:bkg = {len(m_sig) / len(m_bkg):8.1f} : 1")
    print(f"physical ratio sig:bkg = {w_sig.sum() / w_bkg.sum():8.4f} : 1")
    print(
        f"weights change the balance by a factor of "
        f"{(len(m_sig) / len(m_bkg)) / (w_sig.sum() / w_bkg.sum()):,.0f}"
    )


if __name__ == "__main__":
    main()
