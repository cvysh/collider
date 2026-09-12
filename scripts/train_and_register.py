"""Train the production model, save the artifact, and write the registry entry.

Usage:
    python scripts/train_and_register.py

Writes ml/models/xgb-0.1.0.json and ml/models/registry.json.

The threshold is chosen on the **validation** split, not the test split.
Choosing it on test would make the reported test metrics optimistic, because
the threshold would have been tuned to the data it is evaluated on.
"""

import json
from pathlib import Path

import numpy as np
from xgboost import XGBClassifier

from collider.features.dataset import split_indices
from collider.ml.metrics import best_threshold, evaluate

DATASET = Path("data/processed/fourlepton_v1.npz")
MODELS = Path("ml/models")
MODEL_ID = "xgb-0.1.0"
FEATURE_SET_VERSION = "fourlepton-v1"
SEED = 20260912

PARAMS = dict(
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


def main() -> None:
    d = np.load(DATASET)
    x = d["features"].astype(np.float64)
    y, w_train, w_phys = d["labels"], d["train_weight"], d["physical_weight"]
    names = [str(n) for n in d["feature_names"]]
    tr, va, te = split_indices(len(y), seed=SEED)

    model = XGBClassifier(**PARAMS)
    model.fit(
        x[tr],
        y[tr],
        sample_weight=w_train[tr],
        eval_set=[(x[va], y[va])],
        sample_weight_eval_set=[w_train[va]],
        verbose=False,
    )

    # Threshold from validation only.
    val_scores = model.predict_proba(x[va])[:, 1]
    chosen = best_threshold(
        val_scores, y[va], w_phys[va] * (len(y) / len(va)), min_background_neff=10.0
    )
    threshold = chosen["threshold"]

    test_scores = model.predict_proba(x[te])[:, 1]
    test_metrics = evaluate(
        test_scores, y[te], w_phys[te], yield_scale=len(y) / len(te), min_background_neff=10.0
    )

    MODELS.mkdir(parents=True, exist_ok=True)
    model.save_model(MODELS / f"{MODEL_ID}.json")

    registry = {
        "models": [
            {
                "model_id": MODEL_ID,
                "task": "signal-vs-background",
                "framework": f"xgboost=={__import__('xgboost').__version__}",
                "artifact": f"{MODEL_ID}.json",
                "feature_set_version": FEATURE_SET_VERSION,
                "features": names,
                "threshold": round(threshold, 6),
                "training": {
                    "signal": "ggH125->ZZ->4l (MC, channel 345060)",
                    "background": "ZZ->4l (MC, Sherpa 700600/700587/700591)",
                    "luminosity_pb": float(d["luminosity_pb"]),
                    "split_seed": SEED,
                    "n_train": len(tr),
                    "class_balance": "rebalanced to 1:1; physical ratio is 1:37.5",
                    "trees_used": int(model.best_iteration),
                    "threshold_selected_on": "validation split",
                },
                # Numeric only. The registry's `metrics` is typed dict[str, float]
                # at the API boundary, so prose belongs in `training`.
                "metrics": {
                    "test_roc_auc": round(test_metrics["roc_auc"], 4),
                    "test_significance": round(test_metrics["best_significance"], 3),
                },
                "limitations": [
                    "Trained on simulation only. Real collision data carries no truth "
                    "label, so a score on measured data cannot be verified.",
                    "Signal is gluon-gluon fusion production only; VBF, VH and ttH are "
                    "not included.",
                    "Background is the irreducible ZZ->4l only. Fake and non-prompt "
                    "leptons, which dominate real data before selection, are not modelled.",
                    "m_4l is deliberately excluded from the features to avoid sculpting "
                    "the mass spectrum.",
                    "Score is a discriminant, not a probability: the training class "
                    "balance is a choice, not a physical prior.",
                    "Background N_eff in the 115-130 GeV window is 14, a ~27% "
                    "uncertainty. Significance differences are not resolvable.",
                ],
            }
        ]
    }
    (MODELS / "registry.json").write_text(json.dumps(registry, indent=2))

    print(f"model    {MODELS / f'{MODEL_ID}.json'}")
    print(f"registry {MODELS / 'registry.json'}")
    print(f"  trees used     {model.best_iteration}")
    print(f"  threshold      {threshold:.4f}  (chosen on validation)")
    print(f"  test AUC       {test_metrics['roc_auc']:.4f}")


if __name__ == "__main__":
    main()
