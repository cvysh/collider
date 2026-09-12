"""EDA: what does the detector actually see, and what does it miss?

Produces docs/figures/acceptance.png and prints quantitative findings.

This is 'acceptance' -- the map of which particles a detector can record at
all. It matters for the ML stage because it bounds the feature space: a model
can never learn about a region the detector cannot see, and a sharp edge in a
distribution is almost always an instrumental artefact rather than physics.
"""

from pathlib import Path

import awkward as ak
import matplotlib
import numpy as np
import uproot

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SOURCE = Path("data/raw/ODEO_FEB2025_v0_2muons_data15_periodD.2muons.root")
OUTPUT = Path("docs/figures/acceptance.png")
PDG_MUON = 13

BARREL_MAX_ETA = 1.05  # muon spectrometer barrel/endcap boundary
ENDCAP_MIN_ETA = 1.3


def chi2_per_dof_vs_uniform(counts: np.ndarray) -> float:
    """Test whether a histogram is consistent with being flat.

    For counts drawn from a uniform distribution, each bin is Poisson with
    variance equal to its mean, so (observed - expected)^2 / expected sums to
    roughly one per degree of freedom. A value near 1 means any wiggles are
    consistent with counting noise; a large value means the structure is real.
    """
    expected = counts.mean()
    return float((((counts - expected) ** 2) / expected).sum() / (len(counts) - 1))


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing {SOURCE}; see data/raw/README.md")

    with uproot.open(f"{SOURCE}:analysis") as tree:
        ev = tree.arrays(["lep_type", "lep_pt", "lep_eta", "lep_phi"])

    is_mu = ev.lep_type == PDG_MUON
    pt = ak.to_numpy(ak.flatten(ev.lep_pt[is_mu]))
    eta = ak.to_numpy(ak.flatten(ev.lep_eta[is_mu]))
    phi = ak.to_numpy(ak.flatten(ev.lep_phi[is_mu]))

    two_mu = ak.num(ev.lep_pt[is_mu]) == 2
    pt_pairs = ev.lep_pt[is_mu][two_mu]
    lead = ak.to_numpy(ak.max(pt_pairs, axis=1))
    sub = ak.to_numpy(ak.min(pt_pairs, axis=1))

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8))

    # --- (a) pt: the trigger threshold -----------------------------------
    ax = axes[0, 0]
    ax.hist(
        lead, bins=60, range=(0, 60), histtype="step", lw=1.4, color="#1f77b4", label="leading muon"
    )
    ax.hist(
        sub,
        bins=60,
        range=(0, 60),
        histtype="step",
        lw=1.4,
        color="#ff7f0e",
        label="subleading muon",
    )
    ax.axvline(10, color="#d62728", ls="--", lw=1)
    ax.annotate(
        "trigger threshold\n10 GeV",
        xy=(10, ax.get_ylim()[1] * 0.72),
        xytext=(18, ax.get_ylim()[1] * 0.78),
        fontsize=8,
        color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
    )
    ax.axvline(91.188 / 2, color="#2ca02c", ls=":", lw=1.2)
    ax.annotate(
        r"$m_Z/2 \approx 45.6$ GeV" + "\nmuons from Z decay",
        xy=(45.6, 3400),
        xytext=(30, 13500),
        fontsize=8,
        color="#2ca02c",
        arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=0.8),
    )
    ax.set_xlabel(r"$p_T$  [GeV]")
    ax.set_ylabel("muons / GeV")
    ax.set_title("(a) Transverse momentum: a hard trigger edge")
    ax.legend(fontsize=8, loc="center right")

    # --- (b) eta: acceptance edge and the crack --------------------------
    ax = axes[0, 1]
    ax.hist(
        eta,
        bins=110,
        range=(-2.75, 2.75),
        histtype="stepfilled",
        color="#1f77b4",
        alpha=0.35,
        edgecolor="#1f77b4",
        lw=1.1,
    )
    for edge in (-2.5, 2.5):
        ax.axvline(edge, color="#d62728", ls="--", lw=1)
    ax.annotate(
        r"acceptance edge $|\eta|=2.5$",
        xy=(2.5, ax.get_ylim()[1] * 0.35),
        xytext=(0.55, ax.get_ylim()[1] * 0.12),
        fontsize=8,
        color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
    )
    ax.annotate(
        r"service gap at $\eta\approx0$",
        xy=(0, 1500),
        xytext=(-2.4, 600),
        fontsize=8,
        color="#2ca02c",
        arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=0.8),
    )
    ax.set_xlabel(r"$\eta$")
    ax.set_ylabel("muons / bin")
    ax.set_title(r"(b) Pseudorapidity: the detector's physical limits")

    # --- (c) phi in the barrel: the support feet -------------------------
    ax = axes[1, 0]
    barrel = phi[np.abs(eta) < BARREL_MAX_ETA]
    counts_b, edges = np.histogram(barrel, bins=24, range=(-np.pi, np.pi))
    centres = 0.5 * (edges[:-1] + edges[1:])
    chi2_b = chi2_per_dof_vs_uniform(counts_b)
    ax.step(centres, counts_b, where="mid", color="#1f77b4", lw=1.4)
    ax.axhline(counts_b.mean(), color="#7f7f7f", ls=":", lw=1, label="uniform expectation")
    ax.axvline(-np.pi / 2, color="#d62728", ls="--", lw=1)
    ax.set_ylim(counts_b.min() * 0.93, counts_b.max() * 1.03)
    ax.annotate(
        "straight down\n(support feet)",
        xy=(-np.pi / 2, counts_b.min() * 1.01),
        xytext=(-1.15, counts_b.min() * 0.965),
        fontsize=8,
        color="#d62728",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8),
    )
    ax.set_xlabel(r"$\phi$  [rad]")
    ax.set_ylabel("muons / bin")
    ax.set_title(rf"(c) Barrel $|\eta|<{BARREL_MAX_ETA}$:  $\chi^2$/dof = {chi2_b:.1f}")
    ax.legend(fontsize=8, loc="lower right")

    # --- (d) phi in the endcap: the control ------------------------------
    ax = axes[1, 1]
    endcap = phi[np.abs(eta) > ENDCAP_MIN_ETA]
    counts_e, _ = np.histogram(endcap, bins=24, range=(-np.pi, np.pi))
    chi2_e = chi2_per_dof_vs_uniform(counts_e)
    ax.step(centres, counts_e, where="mid", color="#ff7f0e", lw=1.4)
    ax.axhline(counts_e.mean(), color="#7f7f7f", ls=":", lw=1, label="uniform expectation")
    ax.set_xlabel(r"$\phi$  [rad]")
    ax.set_ylabel("muons / bin")
    ax.set_title(rf"(d) Endcap $|\eta|>{ENDCAP_MIN_ETA}$:  $\chi^2$/dof = {chi2_e:.1f}")
    ax.legend(fontsize=8, loc="lower right")

    fig.suptitle(
        f"Muon acceptance — real ATLAS collision data (2015, 2muons skim, {len(pt):,} muons)",
        fontsize=11,
    )
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)

    # --- findings ---------------------------------------------------------
    crack = np.abs(eta) < 0.1
    shoulder = (np.abs(eta) > 0.2) & (np.abs(eta) < 0.5)
    density_crack = crack.sum() / 0.2
    density_shoulder = shoulder.sum() / 0.6

    print(f"wrote {OUTPUT}\n")
    print(f"muons                        : {len(pt):,}")
    print(f"pt   min / leading min       : {pt.min():.2f} / {lead.min():.2f} GeV")
    print(f"eta  min / max               : {eta.min():.3f} / {eta.max():.3f}")
    print(f"eta~0 density deficit        : {1 - density_crack / density_shoulder:.0%}")
    print(f"phi  chi2/dof barrel         : {chi2_b:.1f}")
    print(f"phi  chi2/dof endcap         : {chi2_e:.1f}")


if __name__ == "__main__":
    main()
