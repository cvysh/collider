"""Logistic regression vs gradient-boosted trees, with honest uncertainties."""

import json
from pathlib import Path

import matplotlib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collider.features.dataset import split_indices  # noqa: E402
from collider.ml.metrics import asimov_significance, weighted_roc  # noqa: E402

DATASET = Path("data/processed/fourlepton_v1.npz")
METRICS = Path("ml/models/comparison.json")
OUTPUT = Path("docs/figures/model_comparison.png")
SEED = 20260912


def main() -> None:
    d = np.load(DATASET)
    x = d["features"].astype(np.float64)
    y, m4l = d["labels"], d["m_4l"].astype(np.float64)
    names = [str(n) for n in d["feature_names"]]
    tr, va, te = split_indices(len(y), seed=SEED)
    scale = len(y) / len(te)
    w_te = d["physical_weight"][te] * scale

    lr = Pipeline([("s", StandardScaler()), ("c", LogisticRegression(max_iter=2000))])
    lr.fit(x[tr], y[tr], c__sample_weight=d["train_weight"][tr])
    xgb = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        eval_metric="auc",
        early_stopping_rounds=30,
        random_state=SEED,
    )
    xgb.fit(
        x[tr],
        y[tr],
        sample_weight=d["train_weight"][tr],
        eval_set=[(x[va], y[va])],
        sample_weight_eval_set=[d["train_weight"][va]],
        verbose=False,
    )

    metrics = json.loads(METRICS.read_text())
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.7))

    # --- ROC ---------------------------------------------------------------
    ax = axes[0]
    fitted = (
        (lr, "logistic_regression", "#1f77b4"),
        (xgb, "xgboost", "#d62728"),
    )
    for model, name, colour in fitted:
        s = model.predict_proba(x[te])[:, 1]
        fpr, tpr = weighted_roc(s, y[te], d["physical_weight"][te])
        auc = metrics["models"][name]["test_auc"]
        ax.plot(fpr, tpr, color=colour, lw=1.8, label=f"{name.replace('_', ' ')}  AUC {auc:.4f}")
    ax.plot([0, 1], [0, 1], color="#7f7f7f", ls=":", lw=1, label="random  AUC 0.5")
    ax.set_xlabel("background efficiency")
    ax.set_ylabel("signal efficiency")
    ax.set_title("(a) Discrimination — a clear win")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0.5, 1.0)

    # --- significance with uncertainty --------------------------------------
    ax = axes[1]
    window = (m4l[te] > 115) & (m4l[te] < 130)
    z_win = asimov_significance(
        w_te[window & (y[te] == 1)].sum(), w_te[window & (y[te] == 0)].sum()
    )
    labels = ["mass window\nalone", "+ logistic\nregression", "+ XGBoost"]
    values = [
        z_win,
        metrics["models"]["logistic_regression"]["z_with_mass_window"],
        metrics["models"]["xgboost"]["z_with_mass_window"],
    ]
    errors = [
        0.0,
        metrics["models"]["logistic_regression"]["z_uncertainty"],
        metrics["models"]["xgboost"]["z_uncertainty"],
    ]
    ax.bar(
        labels, values, yerr=errors, capsize=6, color=["#2ca02c", "#1f77b4", "#d62728"], alpha=0.75
    )
    for i, (v, e) in enumerate(zip(values, errors, strict=True)):
        ax.text(i, v + e + 0.12, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_ylabel(r"expected significance $Z$")
    ax.set_title("(b) Significance — indistinguishable")
    ax.tick_params(axis="x", labelsize=8)
    ax.set_ylim(0, max(values) * 1.35)
    ax.annotate(
        "error bars from background\n$N_{eff}\\approx12$ — too thin to resolve",
        xy=(0.5, 0.06),
        xycoords="axes fraction",
        ha="center",
        fontsize=7.5,
        color="#555555",
    )

    # --- permutation importance ---------------------------------------------
    ax = axes[2]
    lr_imp = metrics["models"]["logistic_regression"]["permutation_importance"]
    xg_imp = metrics["models"]["xgboost"]["permutation_importance"]
    top = sorted(names, key=lambda k: -max(xg_imp[k], lr_imp[k]))[:7][::-1]
    pos = np.arange(len(top))
    ax.barh(
        pos - 0.2,
        [lr_imp[k] for k in top],
        height=0.38,
        color="#1f77b4",
        alpha=0.8,
        label="logistic regression",
    )
    ax.barh(
        pos + 0.2,
        [xg_imp[k] for k in top],
        height=0.38,
        color="#d62728",
        alpha=0.8,
        label="XGBoost",
    )
    ax.set_yticks(pos)
    ax.set_yticklabels(top, fontsize=8)
    ax.set_xlabel("drop in weighted AUC when shuffled")
    ax.set_title("(c) Permutation importance")
    ax.legend(fontsize=8, loc="lower right")

    fig.suptitle("Model comparison — ggH→ZZ→4ℓ vs ZZ→4ℓ, MC only, 36 fb$^{-1}$", fontsize=11)
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=140)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
