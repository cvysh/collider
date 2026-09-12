"""Compare logistic regression against gradient-boosted trees.

Usage:
    python scripts/train_compare.py

A stronger model is only worth its complexity if it buys something. This
script runs both on identical features, split and weights, and reports the
metric that matters (expected significance) alongside the one that flatters
(AUC).

It also computes permutation importance, which -- unlike a linear model's
coefficients -- remains meaningful when features are correlated. It measures
how much a metric degrades when one feature's values are shuffled, breaking
its relationship with the label while leaving its marginal distribution
intact.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from collider.features.dataset import split_indices
from collider.ml.metrics import asimov_significance, evaluate
from collider.physics.weights import effective_entries

DATASET = Path("data/processed/fourlepton_v1.npz")
OUTPUT = Path("ml/models/comparison.json")
SEED = 20260912


def significance_with_mass_window(
    scores, labels, weights, m4l, *, lo=115.0, hi=130.0, min_background_neff=10.0
):
    """Best significance from a joint scan, inside the mass window.

    Optimised jointly rather than by stacking an independently-chosen
    threshold, which was shown to reduce significance (docs/FINDINGS.md #6).

    ``min_background_neff`` floors the *effective* background sample size. A
    row-count floor is not enough: 100 weighted rows routinely carry an
    effective sample size under 10, and it is N_eff that sets the uncertainty.
    """
    window = (m4l > lo) & (m4l < hi)
    best = {
        "significance": 0.0,
        "threshold": 0.0,
        "signal": 0.0,
        "background": 0.0,
        "background_rows": 0,
        "background_neff": 0.0,
    }
    for t in np.quantile(scores, np.linspace(0.0, 0.999, 300)):
        mask = window & (scores >= t)
        is_bkg = mask & (labels == 0)
        s = weights[mask & (labels == 1)].sum()
        b = weights[is_bkg].sum()
        n_eff = effective_entries(weights[is_bkg])
        if b < 1.0 or n_eff < min_background_neff:
            continue
        z = asimov_significance(s, b)
        if z > best["significance"]:
            best = {
                "significance": float(z),
                "threshold": float(t),
                "signal": float(s),
                "background": float(b),
                "background_rows": int(is_bkg.sum()),
                "background_neff": float(n_eff),
            }
    return best


def permutation_importance(model, x, y, w, *, n_repeats=5, seed=0):
    """Drop in weighted AUC when each feature is shuffled."""
    rng = np.random.default_rng(seed)
    base = roc_auc_score(y, model.predict_proba(x)[:, 1], sample_weight=np.abs(w))
    drops = np.zeros(x.shape[1])
    for j in range(x.shape[1]):
        deltas = []
        for _ in range(n_repeats):
            xp = x.copy()
            xp[:, j] = rng.permutation(xp[:, j])
            auc = roc_auc_score(y, model.predict_proba(xp)[:, 1], sample_weight=np.abs(w))
            deltas.append(base - auc)
        drops[j] = np.mean(deltas)
    return drops


def main() -> None:
    d = np.load(DATASET)
    x = d["features"].astype(np.float64)
    y = d["labels"]
    w_train, w_phys = d["train_weight"], d["physical_weight"]
    m4l = d["m_4l"].astype(np.float64)
    names = [str(n) for n in d["feature_names"]]

    tr, va, te = split_indices(len(y), seed=SEED)
    scale = len(y) / len(te)
    w_te = w_phys[te] * scale

    models = {
        "logistic_regression": Pipeline(
            [("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))]
        ),
        "xgboost": XGBClassifier(
            n_estimators=400,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            eval_metric="auc",
            early_stopping_rounds=30,
            random_state=SEED,
        ),
    }

    results = {}
    for name, model in models.items():
        if name == "xgboost":
            model.fit(
                x[tr],
                y[tr],
                sample_weight=w_train[tr],
                eval_set=[(x[va], y[va])],
                sample_weight_eval_set=[w_train[va]],
                verbose=False,
            )
        else:
            model.fit(x[tr], y[tr], clf__sample_weight=w_train[tr])

        scores = model.predict_proba(x[te])[:, 1]
        base = evaluate(scores, y[te], w_phys[te], yield_scale=scale, min_background_neff=10.0)
        joint = significance_with_mass_window(scores, y[te], w_te, m4l[te])
        results[name] = {
            "test_auc": base["roc_auc"],
            "z_classifier_only": base["best_significance"],
            "z_with_mass_window": joint["significance"],
            "window_signal": joint["signal"],
            "window_background": joint["background"],
            "window_background_rows": joint["background_rows"],
            "window_background_neff": joint["background_neff"],
            # Significance inherits the background's statistical uncertainty,
            # which is ~1/sqrt(N_eff). With a thin MC sample this dominates.
            "z_uncertainty": (
                0.5 * joint["significance"] / np.sqrt(joint["background_neff"])
                if joint["background_neff"] > 0
                else float("inf")
            ),
        }
        imp = permutation_importance(model, x[te], y[te], w_phys[te], seed=SEED)
        results[name]["permutation_importance"] = dict(zip(names, imp.tolist(), strict=True))

    # Mass window with no classifier at all, as the reference to beat.
    window = (m4l[te] > 115) & (m4l[te] < 130)
    z_window = asimov_significance(
        w_te[window & (y[te] == 1)].sum(), w_te[window & (y[te] == 0)].sum()
    )

    print(f"{'model':22s} {'test AUC':>9s} {'Z (clf only)':>13s} {'Z (+mass win)':>14s}")
    print("-" * 78)
    print(f"{'mass window alone':22s} {'-':>9s} {'-':>13s} {z_window:14.2f}")
    for name, r in results.items():
        print(
            f"{name:22s} {r['test_auc']:9.4f} {r['z_classifier_only']:13.2f} "
            f"{r['z_with_mass_window']:14.2f}  +-{r['z_uncertainty']:4.2f}  "
            f"(B={r['window_background']:.1f}, N_eff={r['window_background_neff']:.0f})"
        )

    print("\npermutation importance (drop in weighted AUC when shuffled):")
    print(f"{'feature':20s} {'logreg':>9s} {'xgboost':>9s}")
    lr_imp = results["logistic_regression"]["permutation_importance"]
    xg_imp = results["xgboost"]["permutation_importance"]
    for n in sorted(names, key=lambda k: -xg_imp[k]):
        print(f"  {n:18s} {lr_imp[n]:9.4f} {xg_imp[n]:9.4f}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as f:
        json.dump({"seed": SEED, "z_mass_window_only": z_window, "models": results}, f, indent=2)
    print(f"\nwrote {OUTPUT}")


if __name__ == "__main__":
    main()
