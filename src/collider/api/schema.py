"""Typed schema for a single event artifact.

This is the contract between the pipeline, the API and the 3D viewer. It is
defined once, validated on write, and validated again on read.

Two design rules shape it.

**Provenance is mandatory, not decorative.** Every payload carries the dataset,
DOI, pipeline version and (where applicable) model version that produced it.
A number on screen that cannot be traced to a source is not a scientific
result. This is what the UI's provenance drawer reads.

**``data_kind`` is required and has no default.** Measured and simulated events
are different in kind: simulation carries a truth label and a weight, measured
data carries neither. Making the field required means a payload that cannot
say which it is fails to construct, rather than silently rendering as though
it were real data.

Size
----
Payloads are intended to stay small enough to be served as immutable,
CDN-cached artifacts. A four-lepton event is a few kilobytes of JSON, under a
kilobyte compressed -- far below the 100 KB budget in SPEC section 21.7. There
is no need for a binary format, and SPEC section 11.2 is explicit that one
should only be introduced if measurement shows JSON is a bottleneck.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SCHEMA_VERSION",
    "EventPayload",
    "EventSummary",
    "MissingEnergy",
    "Prediction",
    "Provenance",
    "ReconstructedObject",
]

SCHEMA_VERSION = "1.0"

#: What a reconstructed object is. Jets are included because they carry real
#: kinematics; anything not on this list must not be invented for display.
ObjectType = Literal["muon", "electron", "jet", "photon"]

#: Measured data has no truth label. Simulated data does. See
#: docs/SCIENTIFIC_INTEGRITY.md.
DataKind = Literal["measured", "simulated"]


class _Strict(BaseModel):
    """Reject unknown fields rather than silently dropping them."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ReconstructedObject(_Strict):
    """One reconstructed particle or jet.

    Momentum is stored in both collider coordinates (what the detector reports)
    and Cartesian components (what the renderer needs), because deriving one
    from the other in the browser would duplicate physics code that is already
    tested in Python. ``px``/``py``/``pz`` define the direction of the display
    ray; see the note on tracks below.
    """

    id: int
    type: ObjectType
    charge: int | None = Field(None, description="None where charge is not measured, e.g. jets")

    pt: float = Field(..., description="Transverse momentum, GeV")
    eta: float = Field(..., description="Pseudorapidity")
    phi: float = Field(..., description="Azimuthal angle, radians")
    energy: float = Field(..., description="Energy, GeV")

    px: float
    py: float
    pz: float


class MissingEnergy(_Strict):
    """Missing transverse energy: the imbalance implying unseen particles."""

    magnitude: float = Field(..., description="GeV")
    phi: float = Field(..., description="radians")


class Prediction(_Strict):
    """A model's output for this event.

    ``score`` is a **discriminant**, not a probability. The training class
    balance is a choice rather than a physical prior, so the number cannot be
    read as "chance this is signal". See docs/SCIENTIFIC_INTEGRITY.md section 3.
    The threshold is carried alongside so the score is never shown bare.
    """

    model_id: str
    task: str
    score: float = Field(..., ge=0.0, le=1.0, description="Discriminant, not a probability")
    threshold: float = Field(..., ge=0.0, le=1.0)
    classification: Literal["signal-like", "background-like"]
    feature_set_version: str


class Provenance(_Strict):
    """Where this event came from and how it was processed."""

    dataset: str
    record_url: str
    doi: str
    licence: str = "CC0-1.0"
    source_file: str
    pipeline_version: str
    accessed: str = Field(..., description="ISO date the source was downloaded")


class EventPayload(_Strict):
    """One complete event, as delivered to the browser."""

    schema_version: str = SCHEMA_VERSION
    event_id: str

    data_kind: DataKind = Field(
        ..., description="Required. 'measured' events carry no truth label."
    )
    #: Generator process for simulation; None for measured data. Its presence
    #: is what makes a simulated event's origin explicit in the UI.
    mc_process: str | None = None
    #: Truth label, simulation only. Measured data has none and never will.
    truth_label: Literal["signal", "background"] | None = None
    #: Physical event weight, simulation only.
    mc_weight: float | None = None

    experiment: str = "ATLAS"
    collision_energy_tev: float = Field(
        13.0, description="Beam configuration, not a per-event measurement"
    )
    run_number: int | None = None
    event_number: int | None = None

    objects: list[ReconstructedObject]
    missing_energy: MissingEnergy | None = None

    #: Derived quantities. Keys absent rather than null when not computable --
    #: the UI reports absence rather than inventing a value.
    derived: dict[str, float] = Field(default_factory=dict)

    prediction: Prediction | None = None
    #: Why no model score is available, when one is not. Populated rather than
    #: leaving the UI to guess -- SPEC section 36 requires that absent
    #: quantities be reported, never invented.
    prediction_unavailable_reason: str | None = None
    provenance: Provenance

    def model_post_init(self, _context: object) -> None:
        """Enforce the measured/simulated invariant at construction."""
        if self.data_kind == "measured":
            for field in ("truth_label", "mc_process", "mc_weight"):
                if getattr(self, field) is not None:
                    raise ValueError(
                        f"measured events cannot carry {field!r}: real collisions have no "
                        "truth label, generator process or event weight"
                    )
        elif self.truth_label is None:
            raise ValueError("simulated events must carry a truth_label")


class EventSummary(_Strict):
    """Lightweight row for the explore/browse list.

    Deliberately small: the browser fetches many of these and exactly one full
    payload. Keeping them separate is what stops the list view from pulling
    kinematics for hundreds of events.
    """

    event_id: str
    data_kind: DataKind
    category: str
    n_objects: int
    n_leptons: int
    score: float | None = None
    headline: dict[str, float] = Field(
        default_factory=dict, description="One or two display quantities, e.g. m_4l"
    )
