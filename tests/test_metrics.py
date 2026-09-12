"""Tests for classifier evaluation metrics."""

import numpy as np
import pytest

from collider.ml.metrics import asimov_significance, best_threshold, evaluate, yields_above


def test_asimov_reduces_to_s_over_sqrt_b_for_small_signal():
    """The familiar approximation must be recovered in its regime."""
    s, b = 1.0, 10_000.0
    assert asimov_significance(s, b) == pytest.approx(s / np.sqrt(b), rel=1e-3)


def test_asimov_is_below_s_over_sqrt_b_for_large_signal():
    """Where the approximation breaks, it overstates significance.

    This is why the Asimov form is used rather than s/sqrt(b) throughout.
    """
    s, b = 50.0, 50.0
    assert asimov_significance(s, b) < s / np.sqrt(b)


def test_asimov_returns_zero_without_background():
    """Significance against zero background is a depleted sample, not a discovery."""
    assert asimov_significance(5.0, 0.0) == 0.0
    assert asimov_significance(0.0, 10.0) == 0.0


def test_asimov_grows_with_more_data():
    """Doubling both yields should scale significance by sqrt(2)."""
    z1 = asimov_significance(10.0, 1000.0)
    z2 = asimov_significance(20.0, 2000.0)
    assert z2 == pytest.approx(np.sqrt(2) * z1, rel=1e-3)


def test_yields_above_respects_threshold_and_weights():
    scores = np.array([0.1, 0.5, 0.9])
    labels = np.array([1, 0, 1])
    weights = np.array([2.0, 3.0, 5.0])
    s, b = yields_above(scores, labels, weights, 0.4)
    assert s == pytest.approx(5.0)
    assert b == pytest.approx(3.0)


def test_best_threshold_refuses_to_exhaust_the_background():
    """Guard against the degenerate optimum at very high thresholds.

    Without a floor, the scan drives background to near zero and reports an
    enormous significance built on a couple of simulated events.
    """
    rng = np.random.default_rng(0)
    n = 5_000
    labels = rng.integers(0, 2, n)
    scores = np.clip(rng.normal(labels * 1.5, 1.0), 0, None)
    weights = np.where(labels == 1, 0.02, 1.0)
    best = best_threshold(scores, labels, weights, min_background=10.0)
    assert best["background"] >= 10.0


def test_yield_scale_leaves_auc_alone_but_moves_significance():
    """Scaling a subset to full size must not alter a ranking metric.

    Significance grows like sqrt(N); AUC does not depend on N at all.
    """
    rng = np.random.default_rng(1)
    n = 4_000
    labels = rng.integers(0, 2, n)
    scores = np.clip(rng.normal(labels * 1.2, 1.0), 0, None)
    weights = np.where(labels == 1, 0.05, 1.0)

    plain = evaluate(scores, labels, weights, min_background=5.0, yield_scale=1.0)
    scaled = evaluate(scores, labels, weights, min_background=5.0, yield_scale=4.0)

    assert scaled["roc_auc"] == pytest.approx(plain["roc_auc"])
    assert scaled["yield_signal_total"] == pytest.approx(4 * plain["yield_signal_total"])
    assert scaled["significance_no_cut"] == pytest.approx(
        2 * plain["significance_no_cut"], rel=1e-6
    )


def test_evaluate_handles_negative_weights():
    """Negative generator weights must not crash AUC or produce nan."""
    rng = np.random.default_rng(2)
    n = 2_000
    labels = rng.integers(0, 2, n)
    scores = rng.uniform(size=n)
    weights = np.where(rng.uniform(size=n) < 0.1, -1.0, 1.0)
    out = evaluate(scores, labels, weights, min_background=5.0)
    assert np.isfinite(out["roc_auc"])
    assert 0.0 <= out["roc_auc"] <= 1.0


def test_perfect_separation_gives_auc_one():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    weights = np.ones(4)
    assert evaluate(scores, labels, weights, min_background=0.0)["roc_auc"] == pytest.approx(1.0)
