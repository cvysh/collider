"""Show what honest track curvature actually looks like at LHC momenta."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collider.physics.trajectory import (  # noqa: E402
    INNER_DETECTOR_RADIUS_M,
    helix_points,
    helix_radius,
)

OUTPUT = Path("docs/figures/trajectories.png")


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5))

    # --- (a) true curvature across momenta --------------------------------
    ax = axes[0]
    for pt, colour in (
        (1, "#d62728"),
        (2, "#ff7f0e"),
        (5, "#2ca02c"),
        (10, "#1f77b4"),
        (45, "#9467bd"),
        (90, "#8c564b"),
    ):
        p = helix_points(pt, 0.0, 0.0, charge=-1, n_points=200)
        ax.plot(p[:, 0], p[:, 1] * 1000, color=colour, lw=1.6, label=f"{pt} GeV")
    ax.set_xlabel("x  [m]")
    ax.set_ylabel("y  [mm]   (note: millimetres)")
    ax.set_title("(a) True trajectories — y axis in mm")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)

    # --- (b) same tracks, equal axes: the honest picture -------------------
    ax = axes[1]
    for pt, colour in ((1, "#d62728"), (10, "#1f77b4"), (45, "#9467bd")):
        p = helix_points(pt, 0.0, 0.0, charge=-1, n_points=200)
        ax.plot(p[:, 0], p[:, 1], color=colour, lw=1.8, label=f"{pt} GeV")
    circle = plt.Circle((0, 0), INNER_DETECTOR_RADIUS_M, fill=False, color="#7f7f7f", ls="--", lw=1)
    ax.add_patch(circle)
    ax.set_aspect("equal")
    ax.set_xlim(-0.2, 1.3)
    ax.set_ylim(-0.75, 0.75)
    ax.set_xlabel("x  [m]")
    ax.set_ylabel("y  [m]")
    ax.set_title("(b) Equal axes — what a viewer really shows")
    ax.legend(fontsize=8, loc="lower right")
    ax.annotate("inner detector\nradius 1.1 m", xy=(0.78, 0.62), fontsize=7.5, color="#7f7f7f")

    # --- (c) charge separation, honest vs exaggerated ----------------------
    ax = axes[2]
    for scale, style, alpha in ((1.0, "-", 1.0), (60.0, "--", 0.85)):
        for q, colour in ((+1, "#d62728"), (-1, "#1f77b4")):
            p = helix_points(45.0, 0.0, 0.0, charge=q, n_points=200, curvature_scale=scale)
            label = (
                f"{'μ+' if q > 0 else 'μ−'}  {'true' if scale == 1 else f'×{scale:.0f} visual aid'}"
            )
            ax.plot(p[:, 0], p[:, 1] * 1000, style, color=colour, lw=1.6, alpha=alpha, label=label)
    ax.set_xlabel("x  [m]")
    ax.set_ylabel("y  [mm]")
    ax.set_title("(c) Charge sign is real; the size is not")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.25)

    fig.suptitle(
        "Track curvature at LHC momenta — ATLAS solenoid 2 T, "
        r"$r = p_T/(0.3qB)$",
        fontsize=11,
    )
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)
    print(f"wrote {OUTPUT}\n")
    print(f"{'pt (GeV)':>9} {'radius (m)':>11} {'deviation at 1.1 m':>20}")
    for pt in (1, 5, 10, 45, 90):
        p = helix_points(pt, 0.0, 0.0, charge=-1)
        print(f"{pt:9.0f} {float(helix_radius(pt, -1)):11.2f} {abs(p[-1, 1]) * 1000:17.1f} mm")


if __name__ == "__main__":
    main()
