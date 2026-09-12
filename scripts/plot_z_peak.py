"""Plot the dimuon invariant-mass spectrum from real ATLAS data."""

from pathlib import Path

import awkward as ak
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collider.physics.fourvector import invariant_mass  # noqa: E402

FIXTURE = Path("tests/fixtures/dimuon_data15_periodD.npz")
OUTPUT = Path("docs/figures/z_peak.png")
Z_MASS_PDG = 91.188

# Resonances visible in the dimuon spectrum, with PDG masses in GeV.
RESONANCES = [
    (3.0969, r"J/$\psi$"),
    (3.6861, r"$\psi$(2S)"),
    (9.4603, r"$\Upsilon$"),
    (91.188, "Z"),
]


def main() -> None:
    d = np.load(FIXTURE)
    m = ak.to_numpy(
        invariant_mass(
            ak.Array(d["pt"]), ak.Array(d["eta"]), ak.Array(d["phi"]), ak.Array(d["energy"])
        )
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))

    # Full spectrum, log y: shows the Z sitting on a falling background.
    ax1.hist(m, bins=300, range=(1, 151), histtype="step", color="#1f77b4", lw=1.1)
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    # Stagger the labels: J/psi and psi(2S) are too close to sit at one height.
    for (mass, label), dy in zip(RESONANCES, (-10, -26, -10, -10), strict=True):
        ax1.axvline(mass, color="#d62728", ls="--", lw=0.8, alpha=0.7)
        ax1.annotate(
            label,
            xy=(mass, ax1.get_ylim()[1]),
            xytext=(0, dy),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
            color="#d62728",
        )
    ax1.set_xlabel(r"$m_{\mu\mu}$  [GeV]")
    ax1.set_ylabel("pairs / bin")
    ax1.set_title("Full spectrum (log-log)")

    # Zoom on the resonance.
    ax2.hist(
        m,
        bins=120,
        range=(60, 120),
        histtype="stepfilled",
        color="#1f77b4",
        alpha=0.35,
        edgecolor="#1f77b4",
        lw=1.2,
    )
    ax2.axvline(Z_MASS_PDG, color="#d62728", ls="--", lw=1, label=f"Z (PDG) {Z_MASS_PDG} GeV")
    ax2.set_xlabel(r"$m_{\mu\mu}$  [GeV]")
    ax2.set_ylabel("pairs / 0.5 GeV")
    ax2.set_title("Z resonance")
    ax2.legend(fontsize=8)

    fig.suptitle(
        "Dimuon invariant mass — real ATLAS collision data (2015, 2muons skim, 12k events)",
        fontsize=10,
    )
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)
    print(f"wrote {OUTPUT}")

    for lo, hi, nb, (pdg, _label) in [
        (2.5, 3.7, 60, RESONANCES[0]),
        (9.0, 10.5, 30, RESONANCES[2]),
        (60, 120, 120, RESONANCES[3]),
    ]:
        h, e = np.histogram(m, bins=nb, range=(lo, hi))
        c = 0.5 * (e[:-1] + e[1:])
        pk = c[np.argmax(h)]
        print(f"  peak {pk:8.3f} GeV   PDG {pdg:8.3f}   diff {pk - pdg:+.3f}")


if __name__ == "__main__":
    main()
