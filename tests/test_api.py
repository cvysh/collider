"""Tests for the HTTP API."""

import pytest
from fastapi.testclient import TestClient

from collider.api.app import create_app, get_models, get_store


@pytest.fixture(scope="module")
def client():
    get_store.cache_clear()
    get_models.cache_clear()
    return TestClient(create_app())


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_list_events_returns_the_curated_set(client):
    r = client.get("/api/events", params={"limit": 200})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == body["count"] == 120
    assert {e["data_kind"] for e in body["events"]} == {"measured", "simulated"}


def test_filter_by_data_kind(client):
    """Separating real from simulated must be a first-class query."""
    measured = client.get("/api/events", params={"data_kind": "measured", "limit": 200}).json()
    simulated = client.get("/api/events", params={"data_kind": "simulated", "limit": 200}).json()
    assert measured["total"] == 40
    assert simulated["total"] == 80
    assert all(e["data_kind"] == "measured" for e in measured["events"])


def test_pagination_is_disjoint(client):
    first = client.get("/api/events", params={"limit": 10, "offset": 0}).json()["events"]
    second = client.get("/api/events", params={"limit": 10, "offset": 10}).json()["events"]
    assert {e["event_id"] for e in first} & {e["event_id"] for e in second} == set()


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 500}, {"offset": -1}])
def test_invalid_pagination_is_rejected(client, params):
    assert client.get("/api/events", params=params).status_code == 422


def test_invalid_data_kind_is_rejected(client):
    """Only the two real kinds exist; anything else is a client error."""
    assert client.get("/api/events", params={"data_kind": "real"}).status_code == 422


def test_get_single_event(client):
    listed = client.get("/api/events", params={"limit": 1}).json()["events"][0]
    r = client.get(f"/api/events/{listed['event_id']}")
    assert r.status_code == 200
    assert r.json()["event_id"] == listed["event_id"]


def test_measured_event_never_carries_a_truth_label(client):
    """The integrity invariant, checked at the boundary clients actually use."""
    listed = client.get("/api/events", params={"data_kind": "measured", "limit": 200}).json()
    for summary in listed["events"][:10]:
        payload = client.get(f"/api/events/{summary['event_id']}").json()
        assert payload["data_kind"] == "measured"
        assert "truth_label" not in payload
        assert "mc_weight" not in payload
        assert "mc_process" not in payload


def test_simulated_event_declares_its_process_and_label(client):
    listed = client.get("/api/events", params={"data_kind": "simulated", "limit": 200}).json()
    payload = client.get(f"/api/events/{listed['events'][0]['event_id']}").json()
    assert payload["truth_label"] in ("signal", "background")
    assert payload["mc_process"]


def test_every_event_carries_provenance(client):
    listed = client.get("/api/events", params={"limit": 200}).json()["events"]
    for summary in listed[::20]:
        prov = client.get(f"/api/events/{summary['event_id']}").json()["provenance"]
        assert prov["doi"]
        assert prov["record_url"].startswith("https://opendata.cern.ch/")
        assert prov["pipeline_version"]


def test_unknown_event_is_404_not_500(client):
    assert client.get("/api/events/does-not-exist").status_code == 404


@pytest.mark.parametrize("bad", ["../../etc/passwd", "..%2F..%2Fsecrets", "v1/../../x"])
def test_path_traversal_is_refused(client, bad):
    """Ids are validated against the index, never turned into a path."""
    assert client.get(f"/api/events/{bad}").status_code in (404, 422)


def test_event_responses_are_marked_immutable(client):
    """Artifacts never change in place, so they can be cached hard."""
    listed = client.get("/api/events", params={"limit": 1}).json()["events"][0]
    r = client.get(f"/api/events/{listed['event_id']}")
    assert "immutable" in r.headers["cache-control"]


def test_models_endpoint_publishes_limitations(client):
    """A client that can show a score can always show what it does not mean."""
    models = client.get("/api/models").json()
    assert models, "registry should contain at least one model"
    m = models[0]
    assert 0.0 <= m["threshold"] <= 1.0
    assert m["limitations"]
    joined = " ".join(m["limitations"]).lower()
    assert "discriminant" in joined
    assert "simulation" in joined


def test_openapi_document_is_generated(client):
    """The frontend generates its types from this, so it must be complete."""
    spec = client.get("/openapi.json").json()
    assert "/api/events/{event_id}" in spec["paths"]
    assert "EventPayload" in spec["components"]["schemas"]


def test_an_event_without_a_score_says_why(client):
    """SPEC section 36: absent quantities are reported, never invented.

    The trained model consumes four-lepton features. A two-muon Z candidate
    has no second lepton pair, so those features do not exist for it and the
    model cannot score it. The payload must say so rather than leaving the UI
    to guess or, worse, inventing inputs to make a score possible.
    """
    listed = client.get("/api/events", params={"limit": 200}).json()["events"]
    seen_unscored = False
    for summary in listed:
        payload = client.get(f"/api/events/{summary['event_id']}").json()
        if "prediction" not in payload:
            seen_unscored = True
            assert payload["prediction_unavailable_reason"]
    assert seen_unscored, "expected at least one event the model cannot score"


def test_scored_events_carry_model_and_threshold(client):
    """A discriminant is never shown bare: version and threshold travel with it."""
    listed = client.get("/api/events", params={"data_kind": "simulated", "limit": 200}).json()[
        "events"
    ]
    payload = client.get(f"/api/events/{listed[0]['event_id']}").json()
    pred = payload["prediction"]
    assert pred["model_id"]
    assert 0.0 <= pred["score"] <= 1.0
    assert 0.0 <= pred["threshold"] <= 1.0
    assert pred["classification"] in ("signal-like", "background-like")
    expected = "signal-like" if pred["score"] >= pred["threshold"] else "background-like"
    assert pred["classification"] == expected


def test_measured_events_are_never_scored_by_a_four_lepton_model(client):
    """A model must not be applied to a topology it was not built for."""
    listed = client.get("/api/events", params={"data_kind": "measured", "limit": 200}).json()[
        "events"
    ]
    for summary in listed[:5]:
        payload = client.get(f"/api/events/{summary['event_id']}").json()
        assert "prediction" not in payload
        assert "four-lepton" in payload["prediction_unavailable_reason"]
