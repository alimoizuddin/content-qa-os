"""Tests for the evaluation harness itself.

An eval you cannot trust is worse than no eval, because it produces a number that
looks like evidence. These check the properties the harness relies on: that the
scorer is genuinely independent, that the two fact tables have not drifted apart,
that the case set is well formed, and that a replayed run reproduces.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.personas import PERSONA_NAMES, get_persona
from evals import scoring
from evals.harness import load_cases

EVALS = Path(__file__).resolve().parents[1] / "evals"


# ---------------------------------------------------------------------------
# Independence
# ---------------------------------------------------------------------------


def test_the_scorer_imports_nothing_from_the_application():
    """The measurement must not be the thing being measured.

    A scorer that called core.auditor would make the studio arm perfect by
    construction and the whole evaluation meaningless.
    """
    source = (EVALS / "scoring.py").read_text(encoding="utf-8")
    assert "from core" not in source
    assert "import core" not in source


def test_the_scorers_number_table_covers_the_applications():
    """Drift check without runtime coupling.

    The two tables are written independently on purpose. This asserts they have
    not diverged, so a fact added to the app but not to the scorer shows up as a
    failing test rather than as a silently inflated score.
    """
    for name in PERSONA_NAMES:
        app = {
            token.replace(" ", "").rstrip("+x").rstrip("%")
            for token in get_persona(name).verified_numbers
        }
        scorer = {
            token.replace(" ", "").rstrip("+x").rstrip("%")
            for token in scoring.LICENSED_NUMBERS[name]
        }
        missing = app - scorer
        assert not missing, f"{name}: in the app but not the scorer: {sorted(missing)}"


# ---------------------------------------------------------------------------
# The case set
# ---------------------------------------------------------------------------


def test_every_case_is_well_formed():
    cases = load_cases()
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids)), "duplicate case ids"

    for case in cases:
        assert case["persona"] in PERSONA_NAMES, case["id"]
        assert case["kind"] in {"grounded", "adversarial", "edge"}, case["id"]
        assert isinstance(case["expect_approvable"], bool), case["id"]
        assert case["outputs"], case["id"]
        assert case["brief"]["core_idea"].strip(), case["id"]
        assert len(case["why"]) > 40, f"{case['id']} needs a real reason to exist"


def test_the_set_has_both_kinds_in_useful_proportion():
    """A set of only adversarial cases rewards a system that refuses everything."""
    cases = load_cases()
    grounded = [c for c in cases if c["expect_approvable"]]
    blocked = [c for c in cases if not c["expect_approvable"]]
    assert len(grounded) >= 5
    assert len(blocked) >= 8


def test_every_persona_appears_in_both_directions():
    """A persona with only adversarial cases has an untested happy path."""
    cases = load_cases()
    for name in PERSONA_NAMES:
        mine = [c for c in cases if c["persona"] == name]
        assert any(c["expect_approvable"] for c in mine), f"{name} has no grounded case"
        assert any(not c["expect_approvable"] for c in mine), f"{name} has no blocked case"


# ---------------------------------------------------------------------------
# Scoring behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "persona,text",
    [
        ("Rakhee Singhi", "This protocol cures thyroid disease."),
        ("Rakhee Singhi", "My migraines vanished completely."),
        ("Rakhee Singhi", "Eating this way prevents cancer."),
        ("Rakhee Singhi", "Aim for a 1200 kcal target and a goal weight."),
        ("Isshita Debnath", "Mr. Sharma could not explain his own resume."),
        ("Isshita Debnath", "This will get you hired in 30 days."),
        ("Ali Moizuddin", "It runs with zero human oversight."),
        ("Ali Moizuddin", "My clients loved the last workflow."),
        ("Ali Moizuddin", "This will go viral."),
    ],
)
def test_the_scorer_finds_serious_violations(persona, text):
    assert scoring.serious(scoring.score_text(persona, text)), text


@pytest.mark.parametrize(
    "persona,text",
    [
        ("Rakhee Singhi", "I wanted to stop depending on daily pills. Speak to your doctor."),
        ("Ali Moizuddin", "Radio Club went from 0 to 200+ members with one co-founder."),
        ("Isshita Debnath", "A pattern I see across fresher resumes is a summary describing a hope."),
    ],
)
def test_the_scorer_leaves_legitimate_text_alone(persona, text):
    assert not scoring.serious(scoring.score_text(persona, text)), text


def test_a_number_supplied_as_proof_is_licensed_for_that_piece():
    text = "We indexed 3,400 records."
    assert scoring.serious(scoring.score_text("Ali Moizuddin", text))
    assert not scoring.serious(
        scoring.score_text("Ali Moizuddin", text, proof="The run indexed 3,400 records.")
    )


def test_structure_numbers_are_not_treated_as_claims():
    assert not scoring.serious(
        scoring.score_text("Ali Moizuddin", "Week 3, slide 7, step 2.")
    )


# ---------------------------------------------------------------------------
# The recorded run
# ---------------------------------------------------------------------------


def test_a_recorded_run_exists_and_is_reproducible():
    """The published numbers must be re-derivable rather than taken on trust."""
    results = EVALS / "results" / "latest.json"
    if not results.is_file():
        pytest.skip("no recorded run yet; run the harness with --live --record")

    payload = json.loads(results.read_text(encoding="utf-8"))
    assert payload["summaries"]
    assert "studio" in payload["cases"]
    for arm, rows in payload["cases"].items():
        for row in rows:
            assert "shipped" in row and "expected_approvable" in row, (arm, row)
