"""ROC curve, score distributions, and the mass-vs-classifier comparison."""

from pathlib import Path

import matplotlib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collider.features.dataset import split_indices  # noqa: E402
from collider.ml.metrics import asimov_significance, weighted_roc  # noqa: E402

DATASET = Path("data/processed/fourlepton_v1.npz")
OUTPUT = Path("docs/figures/baseline.png")
SEED = 20260912


def main() -> None:
    d = np.load(DATASET)
    x = d["features"].astype(np.float64)
    y = d["labels"]
    m4l = d["m_4l"].astype(np.float64)
    train_idx, _, test_idx = split_indices(len(y), seed=SEED)
    scale = len(y) / len(test_idx)

    model = Pipeline([("s", StandardScaler()), ("c", LogisticRegression(max_iter=2000))])
    model.fit(x[train_idx], y[train_idx], c__sample_weight=d["train_weight"][train_idx])

    scores = model.predict_proba(x[test_idx])[:, 1]
    yt, wt = y[test_idx], d["physical_weight"][test_idx] * scale
    mt = m4l[test_idx]

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.5))

    # --- ROC ---------------------------------------------------------------
    ax = axes[0]
    fpr, tpr = weighted_roc(scores, yt, wt)
    ax.plot(fpr, tpr, color="#1f77b4", lw=1.8, label="logistic regression  AUC 0.911")
    ax.plot([0, 1], [0, 1], color="#7f7f7f", ls=":", lw=1, label="random  AUC 0.500")
    ax.set_xlabel("background efficiency (false positive rate)")
    ax.set_ylabel("signal efficiency (true positive rate)")
    ax.set_title("(a) ROC — weighted by physical yield")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # --- score distributions ----------------------------------------------
    ax = axes[1]
    bins = np.linspace(0, 1, 40)
    ax.hist(
        scores[yt == 0],
        bins=bins,
        weights=wt[yt == 0],
        histtype="stepfilled",
        color="#1f77b4",
        alpha=0.45,
        edgecolor="#1f77b4",
        label="ZZ→4ℓ background",
    )
    ax.hist(
        scores[yt == 1],
        bins=bins,
        weights=wt[yt == 1],
        histtype="stepfilled",
        color="#d62728",
        alpha=0.55,
        edgecolor="#d62728",
        label="ggH→ZZ→4ℓ signal",
    )
    ax.set_yscale("log")
    ax.set_xlabel("classifier score")
    ax.set_ylabel(r"expected events in 36 fb$^{-1}$")
    ax.set_title("(b) Score — weighted by physical yield")
    ax.legend(fontsize=8)

    # --- significance comparison ------------------------------------------
    ax = axes[2]
    window = (mt > 115) & (mt < 130)

    def z_of(mask):
        return asimov_significance(wt[mask & (yt == 1)].sum(), wt[mask & (yt == 0)].sum())

    strategies = [
        ("no selection", z_of(np.ones(len(yt), bool)), "#7f7f7f"),
        ("classifier\nalone", z_of(scores >= 0.72), "#1f77b4"),
        ("mass window\nalone", z_of(window), "#2ca02c"),
        ("mass window\n+ classifier", z_of(window & (scores >= 0.061)), "#d62728"),
    ]
    labels = [s[0] for s in strategies]
    values = [s[1] for s in strategies]
    ax.bar(labels, values, color=[s[2] for s in strategies], alpha=0.75)
    for i, v in enumerate(values):
        ax.text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_ylabel(r"expected significance $Z$")
    ax.set_title("(c) The mass does most of the work")
    ax.tick_params(axis="x", labelsize=8)
    ax.set_ylim(0, max(values) * 1.22)

    fig.suptitle(
        "Baseline logistic regression — ggH→ZZ→4ℓ vs ZZ→4ℓ, MC simulation only, 36 fb$^{-1}$",
        fontsize=11,
    )
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)
    print(f"wrote {OUTPUT}")
    for label, v, _ in strategies:
        print(f"  {label.replace(chr(10), ' '):28s} Z = {v:.2f}")


if __name__ == "__main__":
    main()
