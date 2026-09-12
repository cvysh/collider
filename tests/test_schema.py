"""Tests for the event artifact schema.

The measured/simulated invariant is the important one: it is the schema-level
enforcement of docs/SCIENTIFIC_INTEGRITY.md, and it must fail loudly rather
than allow a mislabelled payload to reach the browser.
"""

import pytest
from pydantic import ValidationError

from collider.api.schema import (
    EventPayload,
    MissingEnergy,
    Prediction,
    Provenance,
    ReconstructedObject,
)

PROV = Provenance(
    dataset="ATLAS 13 TeV 2015+2016 education",
    record_url="https://opendata.cern.ch/record/93921",
    doi="10.7483/OPENDATA.ATLAS.6VGH.HN41",
    source_file="example.root",
    pipeline_version="1.0",
    accessed="2026-09-12",
)

MUON = ReconstructedObject(
    id=1,
    type="muon",
    charge=-1,
    pt=45.0,
    eta=0.3,
    phi=1.1,
    energy=47.0,
    px=20.4,
    py=40.1,
    pz=13.7,
)


def _measured(**kw):
    return EventPayload(event_id="m1", data_kind="measured", objects=[MUON], provenance=PROV, **kw)


def _simulated(**kw):
    kw.setdefault("truth_label", "signal")
    return EventPayload(event_id="s1", data_kind="simulated", objects=[MUON], provenance=PROV, **kw)


def test_measured_event_is_valid_without_labels():
    ev = _measured()
    assert ev.data_kind == "measured"
    assert ev.truth_label is None
    assert ev.mc_weight is None


@pytest.mark.parametrize(
    ("field", "value"),
    [("truth_label", "signal"), ("mc_process", "ggH125"), ("mc_weight", 0.5)],
)
def test_measured_event_rejects_simulation_only_fields(field, value):
    """Real collisions have no truth label, process or weight.

    A payload asserting otherwise is a scientific error and must not construct.
    """
    with pytest.raises(ValidationError, match="measured events cannot carry"):
        _measured(**{field: value})


def test_simulated_event_requires_a_truth_label():
    with pytest.raises(ValidationError, match="must carry a truth_label"):
        EventPayload(event_id="s2", data_kind="simulated", objects=[MUON], provenance=PROV)


def test_data_kind_has_no_default():
    """Omitting data_kind must fail rather than silently assume one."""
    with pytest.raises(ValidationError):
        EventPayload(event_id="x", objects=[MUON], provenance=PROV)


def test_unknown_fields_are_rejected():
    """A typo must not be silently discarded."""
    with pytest.raises(ValidationError):
        _measured(colision_energy_tev=13.0)


def test_score_must_be_a_unit_interval_discriminant():
    for bad in (-0.1, 1.5):
        with pytest.raises(ValidationError):
            Prediction(
                model_id="xgb-0.1.0",
                task="signal-vs-background",
                score=bad,
                threshold=0.5,
                classification="signal-like",
                feature_set_version="v1",
            )


def test_prediction_carries_its_threshold():
    """A bare score is not reportable; the threshold travels with it."""
    p = Prediction(
        model_id="xgb-0.1.0",
        task="signal-vs-background",
        score=0.87,
        threshold=0.6,
        classification="signal-like",
        feature_set_version="v1",
    )
    assert p.threshold == 0.6


def test_payload_round_trips_through_json():
    ev = _simulated(
        mc_process="ggH125_ZZ4l",
        mc_weight=1.3e-4,
        missing_energy=MissingEnergy(magnitude=22.0, phi=-0.4),
        derived={"m_4l": 124.9},
    )
    restored = EventPayload.model_validate_json(ev.model_dump_json())
    assert restored == ev


def test_provenance_is_required():
    with pytest.raises(ValidationError):
        EventPayload(event_id="x", data_kind="measured", objects=[MUON])


def test_absent_derived_quantities_are_omitted_not_nulled():
    """SPEC section 36: absent measurements are reported, never invented."""
    ev = _measured()
    assert ev.derived == {}
    assert "m_4l" not in ev.derived
