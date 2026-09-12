"""Tests for narrator dialogue.

The copyright check is the important one here. A draft line naming a
copyrighted character reached review, which is exactly the sort of thing that
slips through when the only safeguard is remembering. Now it fails the build.
"""

from pathlib import Path

import pytest

from collider.api.dialogue import (
    MAX_LINE_LENGTH,
    find_forbidden_names,
    load_dialogue,
)

LINES = Path("assets/dialogue/lines.json")


@pytest.fixture(scope="module")
def slots():
    return load_dialogue(LINES)


def test_all_thirty_eight_slots_are_defined(slots):
    assert len(slots) == 38
    assert {s.number for s in slots.values()} == set(range(1, 39))


def test_every_tier_one_slot_has_a_line(slots):
    """Tier 1 carries scientific integrity; none of it may be silent."""
    for slot in slots.values():
        if slot.tier == 1:
            assert slot.lines, f"tier 1 slot {slot.id} has no line"


def test_no_line_names_a_copyrighted_character(slots):
    """SPEC 23.1/25 and CLAUDE.md: original writing only.

    The aesthetic vocabulary of the genre is fair to borrow. Its characters,
    catchphrases and props are not.
    """
    offenders = []
    for slot in slots.values():
        for line in slot.lines:
            found = find_forbidden_names(line.text)
            if found:
                offenders.append((slot.id, line.text, found))
    assert not offenders, f"copyrighted references found: {offenders}"


def test_forbidden_name_detection_actually_works():
    """Guard the guard: a check that never fires protects nothing."""
    assert find_forbidden_names("It's real data, Morty.") == ["morty"]
    assert find_forbidden_names("Wubba lubba.") == ["wubba", "lubba"]
    # Substrings of ordinary words must not trip it.
    assert find_forbidden_names("The trick is bricks and summertime.") == []
    assert find_forbidden_names("A muon is heavier than an electron.") == []


def test_lines_fit_beside_a_readout(slots):
    too_long = [
        (s.id, len(line.text), line.text)
        for s in slots.values()
        for line in s.lines
        if len(line.text) > MAX_LINE_LENGTH
    ]
    assert not too_long, f"lines exceeding {MAX_LINE_LENGTH} chars: {too_long}"


def test_no_line_claims_a_result(slots):
    """The governing rule: a line may state a limitation, never a result.

    Phrasings that would assert a discovery, a verified identification, or a
    probability reading of the discriminant.
    """
    banned = (
        "we discovered",
        "this is a higgs",
        "it's a higgs",
        "proves",
        "confirmed",
        "% probability",
        "% chance",
    )
    offenders = [
        (s.id, line.text)
        for s in slots.values()
        for line in s.lines
        for phrase in banned
        if phrase in line.text.lower()
    ]
    assert not offenders, f"lines claiming a result: {offenders}"


def test_expressions_are_valid_for_their_speaker(slots):
    """Expression names index character artwork, so they must be exact."""
    a_expressions = {"deadpan", "smug", "sarcastic", "annoyed"}
    b_expressions = {"nervous", "surprised", "excited"}
    for slot in slots.values():
        allowed = a_expressions if slot.speaker == "A" else b_expressions
        for line in slot.lines:
            assert line.expression in allowed, (
                f"{slot.id}: {line.expression!r} invalid for speaker {slot.speaker}"
            )


def test_tier_one_slots_record_what_they_must_convey(slots):
    """Tier 1 exists to carry a specific caveat; that intent is recorded."""
    for slot in slots.values():
        if slot.tier == 1:
            assert slot.must_convey, f"tier 1 slot {slot.id} does not say what it must convey"


def test_rejects_an_unknown_expression(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        '{"version":"1.0","speakers":{"A":{"role":"x","expressions":["deadpan"]}},'
        '"slots":[{"number":1,"id":"s","tier":1,"trigger":"t","speaker":"A",'
        '"must_convey":"m","lines":[{"text":"hi","expression":"jubilant"}]}]}'
    )
    with pytest.raises(ValueError, match="is not one of"):
        load_dialogue(bad)


def test_rejects_an_unknown_speaker(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        '{"version":"1.0","speakers":{"A":{"role":"x","expressions":["deadpan"]}},'
        '"slots":[{"number":1,"id":"s","tier":1,"trigger":"t","speaker":"Z",'
        '"must_convey":"m","lines":[{"text":"hi","expression":"deadpan"}]}]}'
    )
    with pytest.raises(ValueError, match="unknown speaker"):
        load_dialogue(bad)
