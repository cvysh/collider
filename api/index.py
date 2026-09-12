"""Serverless entry point for the API.

Vercel's Python runtime imports this module and serves the ASGI app it exposes.
Nothing about the application lives here: the package is in ``src/`` and the
artifacts are addressed absolutely, because a function's working directory is
not the repository root.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("COLLIDER_EVENTS_ROOT", str(ROOT / "data" / "processed" / "events"))
os.environ.setdefault("COLLIDER_DISTRIBUTIONS", str(ROOT / "data" / "processed" / "distributions"))
os.environ.setdefault("COLLIDER_REGISTRY", str(ROOT / "ml" / "models" / "registry.json"))

from collider.api.app import app  # noqa: E402  (path set up above)

__all__ = ["app"]
