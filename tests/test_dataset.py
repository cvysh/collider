"""Tests for dataset assembly, weighting policy, and splitting."""

import numpy as np
import pytest

from collider.features.dataset import build_dataset, split_indices


def _toy(n_sig=100, n_bkg=50, n_feat=4, sig_w=0.01, bkg_w=2.0, seed=0):
    rng = np.random.default_rng(seed)
    return dict(
        signal_features=rng.normal(size=(n_sig, n_feat)),
        signal_weights=np.full(n_sig, sig_w),
        background_features=rng.normal(size=(n_bkg, n_feat)),
        background_weights=np.full(n_bkg, bkg_w),
        signal_m4l=rng.normal(125, 2, n_sig),
        background_m4l=rng.normal(200, 40, n_bkg),
        feature_names=tuple(f"f{i}" for i in range(n_feat)),
    )


def test_labels_and_shapes_line_up():
    ds = build_dataset(**_toy())
    assert len(ds) == 150
    assert ds.features.shape == (150, 4)
    assert ds.labels.sum() == 100
    assert ds.m_4l.shape == ds.labels.shape


def test_training_weights_balance_the_classes():
    """The central weighting decision: training prior is 50/50 by construction."""
    ds = build_dataset(**_toy())
    sig = ds.train_weight[ds.labels == 1].sum()
    bkg = ds.train_weight[ds.labels == 0].sum()
    assert sig == pytest.approx(bkg)


def test_physical_weights_are_left_alone():
    """Physical weights must survive untouched -- they carry the real yields."""
    ds = build_dataset(**_toy())
    assert ds.physical_weight[ds.labels == 1].sum() == pytest.approx(100 * 0.01)
    assert ds.physical_weight[ds.labels == 0].sum() == pytest.approx(50 * 2.0)


def test_within_class_weight_structure_is_preserved():
    """Balancing must not flatten the weights inside a class.

    Relative weights within a class encode how much physics each event
    represents, which determines the shape the model learns. Only the
    between-class totals may be rescaled.
    """
    kw = _toy(n_sig=4, n_bkg=4)
    kw["signal_weights"] = np.array([1.0, 2.0, 3.0, 4.0])
    ds = build_dataset(**kw)
    w = ds.train_weight[ds.labels == 1]
    assert np.allclose(w / w[0], [1.0, 2.0, 3.0, 4.0])


def test_negative_physical_weights_are_kept_but_training_uses_magnitude():
    """Documented approximation: classifiers cannot consume negative weights."""
    kw = _toy(n_sig=4, n_bkg=4)
    kw["background_weights"] = np.array([1.0, -1.0, 2.0, 1.0])
    ds = build_dataset(**kw)
    assert (ds.physical_weight < 0).sum() == 1, "physical weights must keep the sign"
    assert (ds.train_weight >= 0).all(), "training weights must be non-negative"


def test_rejects_class_with_no_weight():
    kw = _toy()
    kw["signal_weights"] = np.zeros(100)
    with pytest.raises(ValueError, match="non-positive total weight"):
        build_dataset(**kw)


def test_splits_are_disjoint_and_complete():
    """The guarantee that actually prevents train/test leakage."""
    tr, va, te = split_indices(1000, seed=42)
    assert len(set(tr) & set(va)) == 0
    assert len(set(tr) & set(te)) == 0
    assert len(set(va) & set(te)) == 0
    assert len(set(tr) | set(va) | set(te)) == 1000


def test_split_is_reproducible_from_the_seed():
    a = split_indices(500, seed=7)
    b = split_indices(500, seed=7)
    for x, y in zip(a, b, strict=True):
        assert np.array_equal(x, y)


def test_different_seeds_give_different_splits():
    a, _, _ = split_indices(500, seed=1)
    b, _, _ = split_indices(500, seed=2)
    assert not np.array_equal(a, b)


def test_split_fractions_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1"):
        split_indices(100, seed=0, fractions=(0.5, 0.3, 0.3))
