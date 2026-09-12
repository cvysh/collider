"""Model registry: a model artifact is only valid with its metadata.

SPEC section 47 requires every deployed model to be described by a registry
entry. The rule this enforces is that a model file alone is useless and
dangerous: a set of trained weights says nothing about which features it
expects, in which order, what task it solves, or what threshold makes its
score actionable. Feeding it a feature vector built differently from the
training one produces confident nonsense rather than an error.

So the artifact and its contract are written and loaded together, and the
feature ordering is verified on load.

The API allowlists model ids from this registry and never accepts a path from
a client (SPEC section 39).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = ["ModelEntry", "load_registry"]


@dataclass(frozen=True)
class ModelEntry:
    """One registered model and everything needed to use it correctly."""

    model_id: str
    task: str
    framework: str
    artifact: str
    feature_set_version: str
    features: tuple[str, ...]
    threshold: float
    training: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def verify_features(self, names: list[str]) -> None:
        """Fail loudly if the feature vector does not match what was trained on.

        Silent mismatch is the failure mode this exists to prevent: a model
        handed columns in a different order still returns a plausible score.
        """
        if tuple(names) != self.features:
            raise ValueError(
                f"feature mismatch for {self.model_id}:\n"
                f"  expected {self.features}\n"
                f"  received {tuple(names)}"
            )


def load_registry(path: str | Path) -> dict[str, ModelEntry]:
    """Load the registry, keyed by model id."""
    raw = json.loads(Path(path).read_text())
    entries = {}
    for item in raw["models"]:
        entry = ModelEntry(
            model_id=item["model_id"],
            task=item["task"],
            framework=item["framework"],
            artifact=item["artifact"],
            feature_set_version=item["feature_set_version"],
            features=tuple(item["features"]),
            threshold=item["threshold"],
            training=item.get("training", {}),
            metrics=item.get("metrics", {}),
            limitations=item.get("limitations", []),
        )
        entries[entry.model_id] = entry
    return entries
