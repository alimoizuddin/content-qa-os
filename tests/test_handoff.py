"""What Ali found running the app himself, and what a handoff needs.

Each test here exists because the target user hit the problem, not because a
review predicted it. That is the evidence the Quest asks for under "feedback from
the target user and the changes made in response".
"""
from __future__ import annotations

import json
from pathlib import Path

from core import history, runlog
from core.generator import generate_output, normalise
from core.linter import strip_dashes
from core.personas import PERSONA_NAMES, get_persona
from core.providers import default_model
from core.schemas import OUTPUT_SCHEMAS
from tests.conftest import PAYLOADS

ROOT = Path(__file__).resolve().parents[1]
EM, EN = "\u2014", "\u2013"


# ---------------------------------------------------------------------------
# "Reply templates are using em dashes"
# ---------------------------------------------------------------------------


def test_strip_dashes_follows_the_voice_rules():
    assert strip_dashes(f"It worked {EM} the output did not.") == "It worked, the output did not."
    assert strip_dashes(f"usually inside 10{EN}14 days") == "usually inside 10 to 14 days"
    assert strip_dashes(f"Thanks {EM}") == "Thanks"
    assert strip_dashes(f"{EM} a line that starts with one") == "a line that starts with one"
    # Hyphens are not dashes. Words and dates that use them must survive untouched.
    assert strip_dashes("A follow-up on 2026-09-10.") == "A follow-up on 2026-09-10."


def test_every_generated_field_comes_back_without_dashes(brief):
    """Found by Ali: the reply templates he was about to copy still had em dashes.

    The cleaner only ran at the safety check, one step after the boxes he edits and
    copies from. It now runs the moment the text is written, on every field.
    """
    spec = get_persona(brief.persona)
    payload = json.loads(json.dumps(PAYLOADS["post"]))
    payload["reply_templates"] = [
        f"Fair point {EM} and thank you.",
        f"Which part {EN} the hook or the proof?",
        "A plain one.",
    ]
    payload["comment_a"] = f"One detail the post left out {EM} the review step."
    parsed = OUTPUT_SCHEMAS["post"].model_validate(payload)

    blob = json.dumps(normalise(spec, brief, "post", parsed), ensure_ascii=False)
    assert EM not in blob and EN not in blob


# ---------------------------------------------------------------------------
# "I am not getting where the files are getting saved"
# ---------------------------------------------------------------------------


def test_a_saved_package_can_be_downloaded_as_a_text_file():
    entry = {
        "id": 7,
        "created_at": "2026-09-11 10:00",
        "persona": "Ali Moizuddin",
        "model": "anthropic/claude-opus-5",
        "outputs": {"post.post": "Hello there.", "post.hashtags": "#Automation"},
    }
    text = history.package_as_text(entry)
    assert "Hello there." in text
    assert "#Automation" in text
    assert "#7" in text


# ---------------------------------------------------------------------------
# The carousel limit in the original brief
# ---------------------------------------------------------------------------


def test_every_persona_asks_for_six_to_eight_slides():
    for name in PERSONA_NAMES:
        c = get_persona(name).carousel
        assert 6 <= c.min_slides <= c.default_slides <= c.max_slides <= 8, name


def test_a_long_carousel_is_trimmed_to_eight_keeping_cover_and_close(brief):
    spec = get_persona(brief.persona)
    payload = json.loads(json.dumps(PAYLOADS["carousel"]))
    first = payload["slides"][0]
    payload["slides"] = [dict(first, headline=f"Slide {i}") for i in range(1, 11)]
    parsed = OUTPUT_SCHEMAS["carousel"].model_validate(payload)

    headlines = [s["headline"] for s in normalise(spec, brief, "carousel", parsed)["slides"]]
    assert len(headlines) == 8
    assert headlines[0] == "Slide 1"
    assert headlines[-1] == "Slide 10"


# ---------------------------------------------------------------------------
# Logs, and setup a non-developer can do
# ---------------------------------------------------------------------------


def test_the_run_log_records_timing_and_outcome_but_no_content(brief, patch_client, nvidia_only):
    patch_client("post")
    generate_output(brief, "post", "NVIDIA", default_model().model)

    last = runlog.read_events()[-1]
    assert last["event"] == "generate"
    assert last["success"] is True
    assert isinstance(last["seconds"], float)

    raw = runlog.LOG_PATH.read_text(encoding="utf-8")
    for private in (brief.core_idea, brief.proof, "test-key"):
        if private:
            assert private not in raw


def test_the_log_cannot_accept_a_field_outside_its_allowlist():
    runlog.log_event("generate", success=True, brief="my private idea", api_key="nvapi-x")
    raw = runlog.LOG_PATH.read_text(encoding="utf-8")
    assert "my private idea" not in raw
    assert "nvapi-x" not in raw


def test_setup_is_one_double_click_on_windows_and_one_command_elsewhere():
    """Ali's first attempt failed: a command written for one terminal, typed into
    another. A launcher removes the terminal from the setup entirely."""
    bat = (ROOT / "run.bat").read_text(encoding="utf-8")
    for needed in ("requirements.lock", ".env.example", "streamlit run app.py"):
        assert needed in bat, needed
    sh = (ROOT / "run.sh").read_text(encoding="utf-8")
    for needed in ("requirements.lock", ".env.example", "streamlit run app.py"):
        assert needed in sh, needed


def test_the_saved_posts_screen_says_where_things_are_kept(nvidia_only):
    """Found by Ali: he approved a post and could not tell where it had gone."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.session_state["stage"] = "history"
    app.run()

    assert not app.exception
    captions = " ".join(c.value for c in app.caption)
    assert "Where it is kept" in captions
    assert "download" in captions.lower()
