"""Narrator dialogue: slot definitions and the lines that fill them.

Lines live in ``assets/dialogue/lines.json``, keyed by slot id, not scattered
through components. Two consequences follow, and both are the point:

* A slot with no line renders nothing, so the dialogue system can never block
  a feature.
* Lines can be written and edited without touching code.

The constraint that governs every line
--------------------------------------
**A line may state a limitation, never a result.** "I can't score this" is
fine. "This is a Higgs" never is. The narrator exists to make the caveats the
UI is obliged to surface read as character rather than as a disclaimer -- it
does not exist to interpret physics.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "FORBIDDEN_NAMES",
    "MAX_LINE_LENGTH",
    "DialogueLine",
    "DialogueSlot",
    "load_dialogue",
]

#: Lines must sit beside a scientific readout, not displace it.
MAX_LINE_LENGTH = 95

#: Characters, catchphrases and props belonging to the works this project takes
#: its *energy* from but none of its assets. SPEC 23.1/25 and CLAUDE.md require
#: original writing; this list makes the rule enforceable rather than
#: aspirational. A draft line naming one of these was caught in review, which
#: is why the check exists at all.
FORBIDDEN_NAMES = (
    "rick",
    "morty",
    "sanchez",
    "smith",
    "wubba",
    "lubba",
    "portal gun",
    "szechuan",
    "meeseeks",
    "plumbus",
    "jerry",
    "summer",
    "beth",
)


@dataclass(frozen=True)
class DialogueLine:
    text: str
    expression: str


@dataclass(frozen=True)
class DialogueSlot:
    number: int
    id: str
    tier: int
    trigger: str
    speaker: str
    must_convey: str
    lines: tuple[DialogueLine, ...]


def load_dialogue(path: str | Path) -> dict[str, DialogueSlot]:
    """Load and validate the dialogue file, keyed by slot id.

    Validation is deliberately strict. A malformed dialogue file should fail at
    load rather than surface a broken or non-compliant line to a user.
    """
    raw = json.loads(Path(path).read_text())
    speakers = raw["speakers"]

    slots: dict[str, DialogueSlot] = {}
    for item in raw["slots"]:
        speaker = item["speaker"]
        if speaker not in speakers:
            raise ValueError(f"slot {item['id']}: unknown speaker {speaker!r}")

        allowed = set(speakers[speaker]["expressions"])
        lines = []
        for line in item["lines"]:
            expression = line["expression"]
            if expression not in allowed:
                raise ValueError(
                    f"slot {item['id']}: expression {expression!r} is not one of "
                    f"{sorted(allowed)} for speaker {speaker}"
                )
            lines.append(DialogueLine(text=line["text"], expression=expression))

        if item["id"] in slots:
            raise ValueError(f"duplicate slot id {item['id']!r}")

        slots[item["id"]] = DialogueSlot(
            number=item["number"],
            id=item["id"],
            tier=item["tier"],
            trigger=item["trigger"],
            speaker=speaker,
            must_convey=item.get("must_convey", ""),
            lines=tuple(lines),
        )
    return slots


def find_forbidden_names(text: str) -> list[str]:
    """Return any forbidden names appearing in ``text`` as whole words."""
    lowered = text.lower()
    return [
        name
        for name in FORBIDDEN_NAMES
        if re.search(rf"(?<![a-z]){re.escape(name)}(?![a-z])", lowered)
    ]
