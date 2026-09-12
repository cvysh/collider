"""Monte Carlo event weights.

Simulated events are *not* generated in the proportions nature produces them.
Rare processes would need impossibly many generated events to yield a usable
sample, so each process is generated separately in whatever quantity gives good
statistical precision. A weight is the factor that restores reality: it says
how many real events, in a given amount of collected data, an individual
simulated event stands for.

**Unweighted MC histograms are meaningless.** They count events you chose to
generate, not events nature produces.

The weight
----------
::

    w_i = (L * xsec * filteff * kfac / sum_of_weights) * mcWeight_i * prod(SF_i)

======================  ==========================================================
``L``                   Integrated luminosity of the data being modelled (pb^-1).
``xsec``                Cross-section: the intrinsic rate of this process (pb).
``filteff``             Efficiency of any generator-level filter.
``kfac``                Correction from the generator's order to a better-known one.
``sum_of_weights``      Total generator weight over *every generated event*.
``mcWeight``            Per-event generator weight. **Can be negative.**
``SF``                  Per-event corrections for simulation/detector mismatch.
======================  ==========================================================

Why ``sum_of_weights`` and not the sum over your file
-----------------------------------------------------
``sum_of_weights`` counts every event the generator produced, *before* any
skim. The files here are skims: the ggH sample retains 27% of the generated
weight and the ZZ sample 3.5%. Normalising by the sum over your own file would
silently assert the skim kept everything, inflating yields by 4x-30x.

Negative weights are real
-------------------------
Higher-order QCD calculations combine terms of opposite sign -- real emission
and virtual corrections are individually divergent and only their difference is
finite. Generators realise this by emitting some events as negative
contributions. Discarding them breaks the cancellation and biases the result.
In the samples here, 8.7% of Sherpa ZZ events and 0.2% of Powheg ggH events
carry negative weights.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "SCALE_FACTOR_BRANCHES",
    "WEIGHT_BRANCHES",
    "effective_entries",
    "event_weights",
    "weighted_uncertainty",
]

#: Per-event efficiency corrections applied to simulation.
SCALE_FACTOR_BRANCHES = (
    "ScaleFactor_PILEUP",
    "ScaleFactor_MUON",
    "ScaleFactor_ELE",
    "ScaleFactor_LepTRIGGER",
)

#: Branches needed to build a weight. Per-sample constants plus the per-event ones.
WEIGHT_BRANCHES = (
    "mcWeight",
    "xsec",
    "filteff",
    "kfac",
    "sum_of_weights",
    *SCALE_FACTOR_BRANCHES,
)


def event_weights(
    mc_weight: np.ndarray,
    *,
    xsec: float,
    filt_eff: float,
    kfac: float,
    sum_of_weights: float,
    luminosity_pb: float,
    scale_factors: np.ndarray | None = None,
) -> np.ndarray:
    """Normalised per-event weights, in units of expected events.

    Summing the result over a selection gives the number of events that
    selection would contain in ``luminosity_pb`` of real data.

    Parameters
    ----------
    mc_weight
        Per-event generator weight. May contain negative values.
    sum_of_weights
        Generator weight summed over *all generated events*, taken from the
        ``sum_of_weights`` branch -- never recomputed from the file at hand,
        which holds only a skim.
    luminosity_pb
        Integrated luminosity being modelled, in inverse picobarns.
    scale_factors
        Product of the per-event efficiency corrections. Defaults to 1.

    Raises
    ------
    ValueError
        If ``sum_of_weights`` is not positive, which would make the
        normalisation meaningless rather than merely wrong.
    """
    if sum_of_weights <= 0:
        raise ValueError(f"sum_of_weights must be positive, got {sum_of_weights}")
    if luminosity_pb <= 0:
        raise ValueError(f"luminosity_pb must be positive, got {luminosity_pb}")

    norm = luminosity_pb * xsec * filt_eff * kfac / sum_of_weights
    weights = norm * np.asarray(mc_weight, dtype=np.float64)
    if scale_factors is not None:
        weights = weights * np.asarray(scale_factors, dtype=np.float64)
    return weights


def effective_entries(weights: np.ndarray) -> float:
    """Kish effective sample size: how many unweighted events this is worth.

    ::

        N_eff = (sum w)^2 / sum w^2

    Equal weights give ``N_eff == len(weights)``. Unequal weights give less,
    because a few large-weight events dominate. Negative weights reduce it
    further, since they cancel against positive ones.

    This is the number to consult before trusting a simulated prediction. A bin
    holding 10,000 events where one carries weight 500 and the rest 0.01 has
    ``N_eff`` of about 1 -- it looks precise and is a single event in disguise.
    """
    w = np.asarray(weights, dtype=np.float64)
    denom = np.sum(w**2)
    if denom == 0:
        return 0.0
    return float(np.sum(w) ** 2 / denom)


def weighted_uncertainty(weights: np.ndarray) -> float:
    """Statistical uncertainty on a weighted sum: ``sqrt(sum w^2)``.

    The familiar ``sqrt(N)`` applies only to unweighted counts. For weighted
    events the variance is the sum of squared weights, which is larger relative
    to the total whenever weights are unequal.
    """
    w = np.asarray(weights, dtype=np.float64)
    return float(np.sqrt(np.sum(w**2)))
