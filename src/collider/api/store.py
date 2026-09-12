"""Event artifact storage behind an interface.

SPEC section 8.3 requires that the application not be locked to one storage
provider. The MVP reads gzipped JSON from the local filesystem; a future
implementation reads from object storage. Both satisfy ``EventStore``, so
nothing above this layer changes when the backend does.

The local implementation loads the index once at startup and the payloads
lazily, which matches how the client uses them: many summaries, exactly one
full event.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Protocol

from collider.api.schema import EventPayload, EventSummary

__all__ = ["EventNotFound", "EventStore", "LocalEventStore"]


class EventNotFound(KeyError):
    """Requested event id is not in the store."""


class EventStore(Protocol):
    """What the API needs from storage, and nothing more."""

    def list_events(self) -> list[EventSummary]: ...

    def get_event(self, event_id: str) -> EventPayload: ...


class LocalEventStore:
    """Reads curated artifacts from a versioned directory on disk."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        index_path = self._root / "index.json"
        if not index_path.exists():
            raise FileNotFoundError(f"no event index at {index_path}; run scripts/export_events.py")
        raw = json.loads(index_path.read_text())
        self._summaries = [EventSummary.model_validate(e) for e in raw["events"]]
        self._ids = {s.event_id for s in self._summaries}

    def list_events(self) -> list[EventSummary]:
        return list(self._summaries)

    def get_event(self, event_id: str) -> EventPayload:
        # Membership is checked against the index rather than by probing the
        # filesystem, so a crafted id can never be turned into a path lookup.
        if event_id not in self._ids:
            raise EventNotFound(event_id)
        path = self._root / "v1" / f"{event_id}.json.gz"
        with gzip.open(path, "rb") as f:
            return EventPayload.model_validate_json(f.read())
