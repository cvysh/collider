"""Train and evaluate the baseline logistic-regression classifier.

Usage:
    python scripts/train_baseline.py

The point of a baseline is not to win. It is to be simple enough that a wrong
answer is visible, and to set the bar any more complex model must clear. If a
gradient-boosted tree cannot beat this, the tree is not earning its
complexity.

Discipline enforced here:

* Fit on train only. Standardisation statistics come from train only -- fitting
  the scaler on all data leaks test information into training.
* Tune on validation. Test is touched exactly once, at the end.
* Fit with ``train_weight`` (balanced), evaluate with ``physical_weight``
  (real yields). Mixing these is the easiest way to report a meaningless
  number.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from collider.features.dataset import split_indices
from collider.ml.metrics import evaluate

DATASET = Path("data/processed/fourlepton_v1.npz")
OUTPUT = Path("ml/models")
SEED = 20260912


def main() -> None:
    if not DATASET.exists():
        raise SystemExit(f"missing {DATASET}; run scripts/prepare_dataset.py first")

    d = np.load(DATASET, allow_pickle=False)
    x = d["features"].astype(np.float64)
    y = d["labels"]
    w_train = d["train_weight"]
    w_phys = d["physical_weight"]
    names = [str(n) for n in d["feature_names"]]

    train_idx, val_idx, test_idx = split_indices(len(y), seed=SEED)
    print(f"dataset {len(y):,} events, {x.shape[1]} features")
    print(f"split   train {len(train_idx):,} / val {len(val_idx):,} / test {len(test_idx):,}\n")

    # Standardisation matters for logistic regression: the features span
    # wildly different scales (jet_n ~ 1, lep_pt ~ 50) and an unscaled fit
    # both converges poorly and makes coefficients incomparable.
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, C=1.0)),
        ]
    )
    model.fit(x[train_idx], y[train_idx], clf__sample_weight=w_train[train_idx])

    results = {}
    for label, idx in (("train", train_idx), ("val", val_idx), ("test", test_idx)):
        scores = model.predict_proba(x[idx])[:, 1]
        # Scale this subset's yields up to the full dataset. Significance grows
        # like sqrt(N), so quoting it on 20% of the events understates it by
        # more than a factor of two.
        results[label] = evaluate(scores, y[idx], w_phys[idx], yield_scale=len(y) / len(idx))
        r = results[label]
        print(
            f"{label:5s}  AUC {r['roc_auc']:.4f}   "
            f"best Z {r['best_significance']:5.2f} at score {r['best_threshold']:.3f}   "
            f"(S {r['best_signal']:5.2f}, B {r['best_background']:7.2f})"
        )

    base = results["test"]
    print(
        f"\nno cut: S {base['yield_signal_total']:.2f}, "
        f"B {base['yield_background_total']:.2f}, Z {base['significance_no_cut']:.2f}"
    )
    print(
        f"with cut: Z {base['best_significance']:.2f}  "
        f"({base['best_significance'] / max(base['significance_no_cut'], 1e-9):.2f}x improvement)"
    )

    # Coefficients are interpretable only because the inputs were standardised:
    # each is the log-odds shift per standard deviation of that feature.
    coefs = model.named_steps["clf"].coef_[0]
    print("\nstandardised coefficients (log-odds per sigma):")
    for name, c in sorted(zip(names, coefs, strict=True), key=lambda t: -abs(t[1])):
        bar = "#" * int(30 * abs(c) / np.abs(coefs).max())
        print(f"  {name:18s} {c:+7.3f}  {bar}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "baseline_logreg_metrics.json").open("w") as f:
        json.dump(
            {
                "model": "logistic_regression",
                "seed": SEED,
                "features": names,
                "results": results,
                "coefficients": dict(zip(names, coefs.tolist(), strict=True)),
            },
            f,
            indent=2,
        )
    print(f"\nwrote {OUTPUT / 'baseline_logreg_metrics.json'}")


if __name__ == "__main__":
    main()
