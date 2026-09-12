"""Tests for Monte Carlo event weighting."""

import numpy as np
import pytest

from collider.physics.weights import (
    effective_entries,
    event_weights,
    weighted_uncertainty,
)


def test_weight_is_proportional_to_luminosity():
    """Twice the data means twice the expected events."""
    kw = dict(xsec=1.0, filt_eff=1.0, kfac=1.0, sum_of_weights=100.0)
    w1 = event_weights(np.ones(10), luminosity_pb=1000.0, **kw)
    w2 = event_weights(np.ones(10), luminosity_pb=2000.0, **kw)
    assert w2.sum() == pytest.approx(2 * w1.sum())


def test_yield_is_independent_of_how_many_events_were_generated():
    """The defining property of the normalisation.

    Generating ten times more events must not change the predicted yield --
    each weight simply shrinks tenfold. This is what `sum_of_weights` in the
    denominator buys, and it is the reason the formula is not just 'xsec times
    luminosity over the number of rows in my file'.
    """
    kw = dict(xsec=2.0, filt_eff=1.0, kfac=1.0, luminosity_pb=1000.0)
    small = event_weights(np.ones(100), sum_of_weights=100.0, **kw)
    large = event_weights(np.ones(1000), sum_of_weights=1000.0, **kw)
    assert small.sum() == pytest.approx(large.sum())
    assert small.sum() == pytest.approx(2.0 * 1000.0)  # xsec * lumi


def test_negative_weights_are_preserved():
    """Negative generator weights must survive untouched.

    Clipping them at zero would break the cancellation that makes
    higher-order calculations finite, and would bias every yield upward.
    """
    mc = np.array([1.0, -1.0, 1.0, -1.0, 2.0])
    w = event_weights(
        mc, xsec=1.0, filt_eff=1.0, kfac=1.0, sum_of_weights=10.0, luminosity_pb=100.0
    )
    assert (w < 0).sum() == 2
    assert w.sum() == pytest.approx(10.0 * 2.0)  # norm=10, sum(mc)=2


def test_scale_factors_multiply_through():
    kw = dict(xsec=1.0, filt_eff=1.0, kfac=1.0, sum_of_weights=1.0, luminosity_pb=1.0)
    plain = event_weights(np.ones(4), **kw)
    scaled = event_weights(np.ones(4), scale_factors=np.full(4, 0.5), **kw)
    assert scaled.sum() == pytest.approx(0.5 * plain.sum())


def test_rejects_nonpositive_normalisation():
    """A zero or negative sum_of_weights is unrecoverable, not merely wrong."""
    for bad in (0.0, -1.0):
        with pytest.raises(ValueError, match="sum_of_weights"):
            event_weights(
                np.ones(3),
                xsec=1.0,
                filt_eff=1.0,
                kfac=1.0,
                sum_of_weights=bad,
                luminosity_pb=1.0,
            )
    with pytest.raises(ValueError, match="luminosity_pb"):
        event_weights(
            np.ones(3),
            xsec=1.0,
            filt_eff=1.0,
            kfac=1.0,
            sum_of_weights=1.0,
            luminosity_pb=0.0,
        )


def test_effective_entries_equals_count_for_equal_weights():
    assert effective_entries(np.full(500, 0.3)) == pytest.approx(500.0)


def test_effective_entries_collapses_when_one_weight_dominates():
    """The failure mode this function exists to detect."""
    w = np.concatenate([[500.0], np.full(9_999, 0.01)])
    assert effective_entries(w) < 5.0


def test_effective_entries_reduced_by_negative_weights():
    """Cancelling weights carry less information than their count suggests."""
    balanced = np.concatenate([np.ones(90), -np.ones(10)])
    assert effective_entries(balanced) < 100.0


def test_weighted_uncertainty_reduces_to_sqrt_n():
    """With unit weights the general formula must recover Poisson sqrt(N)."""
    assert weighted_uncertainty(np.ones(400)) == pytest.approx(20.0)


def test_weighted_uncertainty_exceeds_sqrt_n_when_weights_are_unequal():
    """Unequal weights always cost precision relative to the same raw count."""
    n = 1000
    equal = np.full(n, 1.0)
    unequal = np.concatenate([np.full(n // 2, 1.9), np.full(n // 2, 0.1)])
    assert unequal.sum() == pytest.approx(equal.sum())
    assert weighted_uncertainty(unequal) > weighted_uncertainty(equal)
