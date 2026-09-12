"""Assemble the labelled training dataset from MC samples.

Weighting policy
----------------
There are two distinct problems that MC weights create, and they need
different treatment.

**Within a class**, weights vary because some simulated events represent more
real collisions than others. Ignoring this distorts the *shape* the model
learns for that class. These weights must be kept.

**Between classes**, the physical totals are 53.6 signal against 1508
background. Training at that ratio invites the model to minimise loss by
always answering "background". This ratio is a *choice*, not a property of the
data, and we choose 50/50.

So: preserve relative weights inside each class, then rescale each class to
the same total. Two weight columns are produced, and they are used for
different things:

``train_weight``
    Balanced. Used only to fit the model.
``physical_weight``
    True expected yields. Used for every plot, yield and significance figure.

Using ``train_weight`` for evaluation would report metrics for a universe in
which the Higgs is as common as its background.

Negative weights
----------------
Generator weights may be negative (8.6% of Sherpa ZZ events). They are
physically meaningful and are kept in ``physical_weight``. Most classifier
implementations either reject negative sample weights or behave badly with
them, so ``train_weight`` uses ``abs(w)``. This is an approximation, recorded
here because it is a real assumption rather than an implementation detail: it
slightly overstates the weight of events that should partially cancel.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["Dataset", "build_dataset", "split_indices"]


@dataclass(frozen=True)
class Dataset:
    """A labelled dataset with separate training and physical weights."""

    features: np.ndarray  # (n, n_features)
    labels: np.ndarray  # (n,) 1 = signal, 0 = background
    train_weight: np.ndarray  # class-balanced, for fitting
    physical_weight: np.ndarray  # expected yield, for evaluation
    m_4l: np.ndarray  # held out of features; for spectrum fits
    feature_names: tuple[str, ...]

    def __len__(self) -> int:
        return len(self.labels)


def build_dataset(
    *,
    signal_features: np.ndarray,
    signal_weights: np.ndarray,
    background_features: np.ndarray,
    background_weights: np.ndarray,
    signal_m4l: np.ndarray,
    background_m4l: np.ndarray,
    feature_names: tuple[str, ...],
) -> Dataset:
    """Stack signal and background into one labelled dataset."""
    features = np.vstack([signal_features, background_features])
    labels = np.concatenate(
        [
            np.ones(len(signal_features), dtype=np.int8),
            np.zeros(len(background_features), dtype=np.int8),
        ]
    )
    physical = np.concatenate([signal_weights, background_weights])
    m_4l = np.concatenate([signal_m4l, background_m4l])

    # Balance classes while preserving each class's internal weight structure.
    train = np.abs(physical).astype(np.float64)
    for cls in (0, 1):
        mask = labels == cls
        total = train[mask].sum()
        if total <= 0:
            raise ValueError(f"class {cls} has non-positive total weight")
        train[mask] /= total
    train *= len(labels) / 2.0  # cosmetic: mean weight ~1

    return Dataset(
        features=features,
        labels=labels,
        train_weight=train,
        physical_weight=physical,
        m_4l=m_4l,
        feature_names=feature_names,
    )


def split_indices(
    n: int, *, seed: int, fractions: tuple[float, float, float] = (0.6, 0.2, 0.2)
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Random disjoint train/validation/test indices.

    A single permutation is partitioned, which makes the three sets disjoint by
    construction -- the guarantee matters more than the shuffling. The seed is
    recorded in the model registry so a split can be reproduced exactly.

    The split is random rather than stratified because both classes are large
    after selection. Were one class small, stratification would be needed to
    avoid a test set that happened to contain almost none of it.
    """
    if not np.isclose(sum(fractions), 1.0):
        raise ValueError(f"fractions must sum to 1, got {sum(fractions)}")

    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    n_train = int(fractions[0] * n)
    n_val = int(fractions[1] * n)
    return order[:n_train], order[n_train : n_train + n_val], order[n_train + n_val :]
