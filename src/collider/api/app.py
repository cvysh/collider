"""COLLIDER HTTP API.

Endpoints (SPEC section 17):

``GET /api/events``          paginated event summaries, filterable
``GET /api/events/{id}``     one full event payload
``GET /api/models``          registered models and their limitations
``GET /api/health``          liveness

Design notes
------------
**Responses are typed.** Every endpoint declares a ``response_model``, so
FastAPI validates what goes out as well as what comes in and publishes an
OpenAPI document. The frontend generates its TypeScript types from that
document rather than hand-maintaining a duplicate of this schema -- which is
why SPEC section 45's shared ``packages/schemas`` is unnecessary.

**Model ids are allowlisted** from the registry and a path is never accepted
from a client (SPEC section 39).

**Artifacts are immutable**, so event responses carry a long cache lifetime.
An event that changes gets a new version and a new path; it is never mutated
in place.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

from collider.api.schema import EventPayload, EventSummary
from collider.api.store import EventNotFound, EventStore, LocalEventStore
from collider.ml.registry import ModelEntry, load_registry

__all__ = ["app", "create_app"]

DEFAULT_EVENTS_ROOT = Path("data/processed/events")
DEFAULT_REGISTRY = Path("ml/models/registry.json")

# Immutable artifacts: cache hard. One year, and marked immutable so browsers
# skip revalidation entirely.
IMMUTABLE_CACHE = "public, max-age=31536000, immutable"
# The index changes when the curated set changes, so it is revalidated.
INDEX_CACHE = "public, max-age=300"


class EventListResponse(BaseModel):
    """A page of event summaries."""

    total: int = Field(..., description="Matching events before pagination")
    count: int = Field(..., description="Events in this page")
    events: list[EventSummary]


class ModelInfo(BaseModel):
    """Public description of a registered model.

    Limitations are part of the response, not a footnote elsewhere. A client
    that shows a score can always show what the score does not mean.
    """

    model_id: str
    task: str
    framework: str
    feature_set_version: str
    threshold: float
    threshold_selected_on: str = Field(..., description="Which split the threshold was chosen on")
    n_features: int
    metrics: dict[str, float] = Field(..., description="Numeric metrics only")
    limitations: list[str]


@lru_cache(maxsize=1)
def get_store() -> EventStore:
    return LocalEventStore(os.environ.get("COLLIDER_EVENTS_ROOT", DEFAULT_EVENTS_ROOT))


@lru_cache(maxsize=1)
def get_models() -> dict[str, ModelEntry]:
    path = Path(os.environ.get("COLLIDER_REGISTRY", DEFAULT_REGISTRY))
    return load_registry(path) if path.exists() else {}


def create_app() -> FastAPI:
    app = FastAPI(
        title="COLLIDER API",
        version="0.1.0",
        description=(
            "Curated ATLAS Open Data events and model scores. "
            "Measured events carry no truth label; model output is a discriminant "
            "score, not a probability."
        ),
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/events", response_model=EventListResponse)
    def list_events(
        response: Response,
        store: Annotated[EventStore, Depends(get_store)],
        data_kind: Annotated[
            Literal["measured", "simulated"] | None,
            Query(description="Filter by real collision data or simulation"),
        ] = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> EventListResponse:
        events = store.list_events()
        if data_kind is not None:
            events = [e for e in events if e.data_kind == data_kind]
        response.headers["Cache-Control"] = INDEX_CACHE
        page = events[offset : offset + limit]
        return EventListResponse(total=len(events), count=len(page), events=page)

    # exclude_none so the wire format matches the artifact on disk: a measured
    # event omits truth_label/mc_process/mc_weight rather than sending nulls.
    @app.get(
        "/api/events/{event_id}",
        response_model=EventPayload,
        response_model_exclude_none=True,
    )
    def get_event(
        event_id: str,
        response: Response,
        store: Annotated[EventStore, Depends(get_store)],
    ) -> EventPayload:
        try:
            payload = store.get_event(event_id)
        except EventNotFound:
            raise HTTPException(status_code=404, detail=f"unknown event {event_id!r}") from None
        response.headers["Cache-Control"] = IMMUTABLE_CACHE
        return payload

    @app.get("/api/models", response_model=list[ModelInfo])
    def list_models(
        models: Annotated[dict[str, ModelEntry], Depends(get_models)],
    ) -> list[ModelInfo]:
        return [
            ModelInfo(
                model_id=m.model_id,
                task=m.task,
                framework=m.framework,
                feature_set_version=m.feature_set_version,
                threshold=m.threshold,
                threshold_selected_on=m.training.get("threshold_selected_on", "unknown"),
                n_features=len(m.features),
                metrics=m.metrics,
                limitations=m.limitations,
            )
            for m in models.values()
        ]

    return app


app = create_app()
