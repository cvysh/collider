"""Generated artifacts must not drift from their sources.

Two files in the frontend are copies of things the backend owns: the dialogue
lines and the OpenAPI-derived TypeScript types. Copies drift, and drift between
a schema and its client shows up as a runtime surprise rather than a type
error. These tests fail the build instead.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE_SOURCE = ROOT / "assets" / "dialogue" / "lines.json"
DIALOGUE_COPY = ROOT / "web" / "lib" / "dialogue.json"
OPENAPI = ROOT / "docs" / "openapi.json"


def test_frontend_dialogue_matches_the_source():
    """`npm run sync:dialogue` runs on predev/prebuild; this catches a stale copy."""
    if not DIALOGUE_COPY.exists():
        pytest.skip("frontend not installed")
    assert json.loads(DIALOGUE_COPY.read_text()) == json.loads(DIALOGUE_SOURCE.read_text()), (
        "web/lib/dialogue.json is stale; run `npm run sync:dialogue` in web/"
    )


def test_openapi_document_matches_the_live_app():
    """The committed spec is what the frontend generates its types from."""
    from collider.api.app import create_app

    live = create_app().openapi()
    committed = json.loads(OPENAPI.read_text())
    assert live == committed, (
        "docs/openapi.json is stale. Regenerate it, then re-run `npm run sync:types` in web/."
    )
