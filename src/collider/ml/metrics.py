"""Evaluation metrics for a signal-vs-background classifier.

Why accuracy is useless here
----------------------------
Physically, background outnumbers signal 37:1 after selection. A model that
answers "background" for every event is 97% accurate and completely worthless.
Accuracy measures nothing in an imbalanced problem, and it is never reported
in this project.

What is used instead
--------------------
``roc_auc``
    Threshold-free ranking quality. Answers: given one random signal event and
    one random background event, how often does the model score the signal
    higher? 0.5 is a coin flip, 1.0 is perfect separation.

``significance``
    What the physics actually cares about. A threshold is only useful if the
    surviving signal stands above the statistical noise of the surviving
    background.

Every metric here takes physical weights. Evaluating with the balanced
training weights would describe a universe in which the Higgs is as common as
its background.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve

from collider.physics.weights import effective_entries

__all__ = [
    "asimov_significance",
    "best_threshold",
    "evaluate",
    "weighted_roc",
    "yields_above",
]


def asimov_significance(s: float, b: float) -> float:
    """Expected discovery significance for ``s`` signal over ``b`` background.

    ::

        Z = sqrt( 2 * ( (s+b) * ln(1 + s/b) - s ) )

    This is the Asimov formula. For ``s << b`` it reduces to the familiar
    ``s / sqrt(b)``, but unlike that approximation it stays valid when the
    signal is not small compared to the background -- where ``s/sqrt(b)``
    overstates the significance considerably.

    Returns 0 when there is no background left, because a significance
    computed against zero background is not meaningful: it reflects an
    exhausted simulation sample rather than a real discovery.
    """
    if b <= 0 or s <= 0:
        return 0.0
    return float(np.sqrt(2.0 * ((s + b) * np.log1p(s / b) - s)))


def yields_above(
    scores: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray,
    threshold: float,
) -> tuple[float, float]:
    """Expected signal and background yields passing a score threshold."""
    passing = scores >= threshold
    s = float(weights[passing & (labels == 1)].sum())
    b = float(weights[passing & (labels == 0)].sum())
    return s, b


def best_threshold(
    scores: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray,
    *,
    min_background: float = 1.0,
    min_background_neff: float = 25.0,
    n_steps: int = 200,
) -> dict[str, float]:
    """Scan thresholds and return the one maximising Asimov significance.

    Choosing a threshold is a decision about how to trade signal efficiency
    against background rejection. Maximising significance answers "where do I
    have the best chance of seeing this signal at all", which is the question a
    search actually asks -- unlike accuracy or F1, which answer nothing in
    particular here.

    Two separate guards are needed against the degenerate optimum, and
    constraining only the first is a trap this project fell into:

    ``min_background``
        A floor on the expected background *yield*.

    ``min_background_neff``
        A floor on the *effective* sample size behind that yield. Note this is
        ``N_eff``, not a row count: 100 rows with unequal weights routinely
        carry an effective sample size of under 10, and it is ``N_eff`` that
        sets the uncertainty (roughly ``1/sqrt(N_eff)``). Guarding the yield
        alone, or even the row count, still admits optima resting on noise --
        both mistakes were made and corrected in this project.
    """
    candidates = np.quantile(scores, np.linspace(0.0, 1.0, n_steps))
    best = {
        "threshold": float(candidates[0]),
        "significance": 0.0,
        "signal": 0.0,
        "background": 0.0,
        "background_rows": 0.0,
        "background_neff": 0.0,
    }

    is_background = labels == 0
    for threshold in np.unique(candidates):
        s, b = yields_above(scores, labels, weights, threshold)
        surviving_background = is_background & (scores >= threshold)
        n_eff = effective_entries(weights[surviving_background])
        if b < min_background or n_eff < min_background_neff:
            continue
        z = asimov_significance(s, b)
        if z > best["significance"]:
            best = {
                "threshold": float(threshold),
                "significance": z,
                "signal": s,
                "background": b,
                "background_rows": float(surviving_background.sum()),
                "background_neff": float(n_eff),
            }
    return best


def evaluate(
    scores: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray,
    *,
    min_background: float = 1.0,
    min_background_neff: float = 25.0,
    yield_scale: float = 1.0,
) -> dict[str, float]:
    """Full weighted evaluation of a set of scores.

    Parameters
    ----------
    yield_scale
        Factor converting this subset's yields to full-dataset yields. When
        evaluating on a 20% test split, the physical weights sum to 20% of the
        experiment's expected events, and significance computed from them is
        wrong -- significance grows like sqrt(N), so it does not survive being
        quoted on a fraction of the data. For a random split, pass
        ``len(all) / len(subset)``.

        AUC is unaffected: it is a ranking property and does not depend on how
        many events are present.

    Notes
    -----
    ``physical_weight`` may contain negative entries from the generator. AUC is
    computed on the magnitudes, because a negative-weight event has no
    meaningful position in a ranking. Yields and significance use the signed
    weights, where negative entries are physically correct and must cancel.
    """
    auc = float(roc_auc_score(labels, scores, sample_weight=np.abs(weights)))
    scaled = weights * yield_scale
    baseline_s = float(scaled[labels == 1].sum())
    baseline_b = float(scaled[labels == 0].sum())
    best = best_threshold(
        scores,
        labels,
        scaled,
        min_background=min_background,
        min_background_neff=min_background_neff,
    )

    return {
        "roc_auc": auc,
        "yield_signal_total": baseline_s,
        "yield_background_total": baseline_b,
        "significance_no_cut": asimov_significance(baseline_s, baseline_b),
        **{f"best_{k}": v for k, v in best.items()},
    }


def weighted_roc(
    scores: np.ndarray, labels: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Weighted ROC curve: (false positive rate, true positive rate)."""
    fpr, tpr, _ = roc_curve(labels, scores, sample_weight=np.abs(weights))
    return fpr, tpr
