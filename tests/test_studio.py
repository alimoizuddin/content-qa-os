"""Personas, safety, QA, assets, history, and the full UI flow."""
from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ui.guide import fix_for

from core import history
from core.auditor import audit_content
from core.carousel import build_carousel_assets, portrait_slug, render_slides
from core.imagegen import art_direction, create_picture, image_provider_configured
from core.linter import lint_text
from core.personas import OPEN_SLOT, PERSONA_NAMES, get_persona, voice_brief
from core.schemas import CarouselDraft
from core.studio import approve_package, build_sections, run_qa
from tests.conftest import PAYLOADS

APP = Path(__file__).resolve().parents[1] / "app.py"

ALI = get_persona("Ali Moizuddin")
ISSHITA = get_persona("Isshita Debnath")
RAKHEE = get_persona("Rakhee Singhi")


# ---------------------------------------------------------------------------
# Persona identity
# ---------------------------------------------------------------------------


def test_all_three_personas_are_present():
    assert PERSONA_NAMES == ("Ali Moizuddin", "Isshita Debnath", "Rakhee Singhi")


def test_ali_title_is_exactly_the_approved_one():
    assert ALI.title == "AI Automation Engineer"


@pytest.mark.parametrize("banned", ["10,000 credits", "10000 credits"])
def test_retired_metrics_never_reach_a_prompt(banned):
    for spec in (ALI, ISSHITA, RAKHEE):
        assert banned.lower() not in voice_brief(spec).lower()


def test_past_titles_appear_only_as_prohibitions():
    """Systems Architect is a past title, not a nonexistent one.

    The prompt has to name it in order to forbid it, so the test cannot simply
    assert its absence. What matters is that every line mentioning it is telling
    the model not to use it.
    """
    for spec in (ALI, ISSHITA, RAKHEE):
        for line in voice_brief(spec).splitlines():
            if "systems architect" in line.lower():
                assert "past title" in line.lower() or "never" in line.lower(), line


def test_ali_verified_achievements_are_the_corpus_ones():
    claims = " ".join(f.claim for f in ALI.star_facts)
    assert "Be10x AI Generalist Hackathon" in claims
    assert "Top 0.1% global ChatGPT user" in claims
    assert "20+ documented systems" in claims
    assert "0 to 200+ members" in claims


def test_the_withdrawn_sdr_figure_is_not_a_fact_anywhere():
    """Ali withdrew this figure on 3 August 2026 as invented.

    It was seeded into this app from an engine document written before the
    retraction and shipped as a verified fact, inside the system whose whole
    purpose is refusing invented figures. This test is the reason it cannot come
    back.
    """
    claims = " ".join(f.claim for f in ALI.star_facts)
    assert "10 hours a week" not in claims
    assert "70% reduction" not in claims
    assert "15 minutes of manual research per lead" in claims

    banned = " ".join(ALI.banned_claims).lower()
    assert "10 hrs/week" in banned
    assert "70% reduction" in banned


def test_the_withdrawn_figure_is_blocked_if_a_human_types_it():
    result = audit_content(ALI, "Prospect research went from 10 hours a week to 3.")
    assert any(f.startswith("BLOCKED") for f in result["flags"])


def test_unmeasured_outcomes_are_quarantined():
    """Outreach results were never measured, so they are not facts."""
    pending = " ".join(ALI.pending_verification).lower()
    assert "reply rate" in pending
    assert "hours saved per week" in pending
    assert "follow-up sequences" in pending


def test_claims_the_master_profile_confirms_are_facts_not_gaps():
    claims = " ".join(f.claim for f in ALI.star_facts)
    pending = " ".join(ALI.pending_verification)
    for confirmed in (
        "300+ hours of multilingual audio at 95%+ accuracy",
        "Agentic SDR Personalization Engine",
    ):
        assert confirmed in claims
        assert confirmed not in pending


def test_every_persona_has_a_visual_system_with_a_recorded_source():
    for spec in (ALI, ISSHITA, RAKHEE):
        assert spec.visual.background.startswith("#")
        assert spec.visual.accent.startswith("#")
        assert len(spec.visual.source) > 20


def test_ali_is_dark_and_gold_isshita_is_light_and_rose():
    assert ALI.visual.mode == "dark"
    assert ALI.visual.background == "#0D0D0D"
    assert ALI.visual.accent == "#C9A84C"
    assert ISSHITA.visual.mode == "light"
    assert ISSHITA.visual.background == "#FAF7F5"
    assert ISSHITA.visual.accent == "#DC7086"


def test_only_ali_has_a_second_surface():
    assert ALI.surfaces.count == 2
    assert ISSHITA.surfaces.count == 1
    assert RAKHEE.surfaces.count == 1


def test_no_persona_spec_reproduces_a_contact_detail():
    """Corpus engine documents carry email addresses. None may reach the app."""
    for spec in (ALI, ISSHITA, RAKHEE):
        blob = voice_brief(spec) + " ".join(spec.pending_verification)
        assert "@gmail.com" not in blob
        assert "@" not in blob


# ---------------------------------------------------------------------------
# Safety rules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "This protocol cures thyroid problems in weeks.",
        "WILDFIT reverses thyroid disease.",
        "Eating this way prevents cancer.",
        "You can stop your medication once cravings settle.",
        "Live pill free after ninety days.",
        "Fast for 16 hours every day to see results.",
        "Aim for a 1200 kcal target and a goal weight.",
        "India's first certified coach.",
    ],
)
def test_rakhee_medical_rules_fail_closed(text):
    result = audit_content(RAKHEE, text)
    assert any(f.startswith("BLOCKED") for f in result["flags"]), text


def test_rakhee_may_still_describe_her_own_experience():
    safe = (
        "I wanted to stop depending on daily pills, and this is what happened in my "
        "body. Speak to your doctor about your own situation."
    )
    result = audit_content(RAKHEE, safe)
    assert not [f for f in result["flags"] if f.startswith("BLOCKED")]


@pytest.mark.parametrize(
    "text",
    [
        "Mr. Sharma interviewed on Tuesday and did not make the shortlist.",
        "Their compensation was above the band.",
        "The internal grievance took three weeks.",
        "This resume will get you shortlisted.",
        "India's youngest soft skills trainer.",
    ],
)
def test_isshita_confidentiality_rules_fail_closed(text):
    result = audit_content(ISSHITA, text)
    assert any(f.startswith("BLOCKED") for f in result["flags"]), text


def test_isshita_anonymised_pattern_language_passes():
    safe = "A pattern I see across fresher resumes is a summary that describes a hope."
    result = audit_content(ISSHITA, safe)
    assert not [f for f in result["flags"] if f.startswith("BLOCKED")]


@pytest.mark.parametrize(
    "text",
    [
        "It runs with zero human oversight.",
        "This took CAC to zero.",
        "My client saw the same thing.",
        "As a Systems Architect I would build it differently.",
        "This post will go viral.",
    ],
)
def test_ali_hyperbole_and_identity_rules_fail_closed(text):
    result = audit_content(ALI, text)
    assert any(f.startswith("BLOCKED") for f in result["flags"]), text


# ---------------------------------------------------------------------------
# Metric auditing
# ---------------------------------------------------------------------------


def test_an_unverified_number_is_redacted_not_merely_flagged():
    result = audit_content(ALI, "The system saved 47 hours a week.")
    assert "[OPEN SLOT]" in result["audited_text"]
    assert "47" not in result["audited_text"]


def test_a_verified_number_survives():
    result = audit_content(ALI, "Radio Club went from 0 to 200+ members.")
    assert "[OPEN SLOT]" not in result["audited_text"]


def test_a_number_supplied_as_proof_is_trusted_for_that_piece():
    text = "We processed 3,400 records in the first run."
    without = audit_content(ALI, text)
    with_proof = audit_content(ALI, text, proof="The first run processed 3,400 records.")
    assert "[OPEN SLOT]" in without["audited_text"]
    assert "[OPEN SLOT]" not in with_proof["audited_text"]


def test_structure_numbers_are_not_treated_as_claims():
    result = audit_content(ALI, "Week 3, slide 7, step 2 of the framework.")
    assert "[OPEN SLOT]" not in result["audited_text"]


def test_an_inflated_version_of_a_true_claim_is_blocked():
    result = audit_content(ISSHITA, "I trained 15,000+ learners.")
    assert any("inflated version" in f for f in result["flags"])


# ---------------------------------------------------------------------------
# Linter
# ---------------------------------------------------------------------------


def test_em_dashes_are_removed():
    result = lint_text("The system worked — the output did not.", ALI)
    assert "—" not in result["cleaned_text"]
    assert any("Em dash" in f for f in result["flags"])


def test_metric_ranges_become_words():
    result = lint_text("It cut 10-15% of the time.", ALI)
    assert "10 to 15%" in result["cleaned_text"]


def test_engagement_bait_is_flagged():
    result = lint_text("Comment YES if you agree. Thoughts?", ALI)
    assert len([f for f in result["flags"] if "Engagement bait" in f]) >= 2


def test_a_persona_use_word_is_not_flagged_as_a_cliche():
    """'leverage' is on the universal cliche list and on Ali's own use list."""
    result = lint_text("The leverage is in the description layer.", ALI)
    assert not any("leverage" in f for f in result["flags"])


def test_links_are_flagged_in_the_post_body_but_not_in_a_comment():
    body = lint_text("Read it at https://example.com", ALI, section="post")
    comment = lint_text("Read it at https://example.com", ALI, section="comment_a")
    assert any("Link in the post body" in f for f in body["flags"])
    assert not any("Link in the post body" in f for f in comment["flags"])


def test_more_than_five_hashtags_is_flagged():
    result = lint_text("#a #b #c #d #e #f", ALI)
    assert any("hashtags" in f for f in result["flags"])


# ---------------------------------------------------------------------------
# Approval gate
# ---------------------------------------------------------------------------


def test_open_slots_block_approval():
    qa = run_qa(ALI, {"post": "We saved [OPEN SLOT] hours a week."})
    verdict = approve_package(qa)
    assert not verdict["approved"]
    assert "[OPEN SLOT]" in verdict["reason"]


def test_a_medical_claim_typed_by_hand_blocks_approval():
    qa = run_qa(RAKHEE, {"post": "This plan cures thyroid disease."})
    verdict = approve_package(qa)
    assert not verdict["approved"]
    assert verdict["blocking_flags"]


def test_clean_grounded_text_approves():
    qa = run_qa(
        ALI,
        {"post": "The description layer decides the outcome. Named inputs, one review step."},
    )
    verdict = approve_package(qa)
    assert verdict["approved"], qa["audit_flags"]


def test_a_style_flag_alone_never_blocks_approval():
    qa = run_qa(ALI, {"post": "Thoughts?"})
    verdict = approve_package(qa)
    assert qa["lint_flags"]
    assert verdict["approved"]


def test_the_gate_reports_every_reason_not_just_the_first():
    qa = run_qa(RAKHEE, {"post": "This cures diabetes and saved [OPEN SLOT] people."})
    verdict = approve_package(qa)
    assert len(verdict["reasons"]) == 2


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def test_post_sections_split_the_package_into_editable_parts():
    sections = {s.key for s in build_sections(ALI, "post", PAYLOADS["post"])}
    assert {
        "post",
        "hashtags",
        "hashtag_notes",
        "keywords",
        "comment_a",
        "comment_b",
        "repost_caption",
        "reply_templates",
        "publish_window",
    } <= sections


def test_the_post_body_never_carries_the_hashtags():
    sections = {s.key: s.text for s in build_sections(ALI, "post", PAYLOADS["post"])}
    assert "#" not in sections["post"]
    assert "#" in sections["hashtags"]


def test_second_comment_label_follows_the_persona_surface_count():
    ali = {s.key: s.label for s in build_sections(ALI, "post", PAYLOADS["post"])}
    isshita = {s.key: s.label for s in build_sections(ISSHITA, "post", PAYLOADS["post"])}
    assert "Radio Club" in ali["comment_b"]
    assert "Isshita" in isshita["comment_b"]


def test_calendar_sections_are_one_per_week():
    sections = build_sections(ALI, "calendar", PAYLOADS["calendar"])
    assert [s.key for s in sections] == ["week_1", "week_2", "week_3", "week_4"]


# ---------------------------------------------------------------------------
# Carousel assets
# ---------------------------------------------------------------------------


@pytest.fixture
def carousel() -> CarouselDraft:
    return CarouselDraft.model_validate(PAYLOADS["carousel"])


@pytest.mark.parametrize("persona", PERSONA_NAMES)
def test_slides_render_at_the_right_size_for_every_persona(persona, carousel):
    images = render_slides(get_persona(persona), carousel)
    assert len(images) == 6
    assert all(image.size == (1080, 1350) for image in images)


def test_carousel_produces_png_pdf_and_zip(carousel):
    assets = build_carousel_assets(ALI, carousel)
    assert assets["count"] == 6
    assert all(png.startswith(b"\x89PNG") for png in assets["slides"])
    assert assets["pdf"].startswith(b"%PDF")
    assert assets["zip"].startswith(b"PK")


def test_the_zip_contains_every_slide_the_pdf_and_the_copy(carousel):
    import io
    import zipfile

    assets = build_carousel_assets(ALI, carousel)
    with zipfile.ZipFile(io.BytesIO(assets["zip"])) as archive:
        names = archive.namelist()
    assert sum(n.endswith(".png") for n in names) == 6
    assert any(n.endswith(".pdf") for n in names)
    assert "slide-copy.txt" in names


def test_a_very_long_headline_still_renders_without_raising(carousel):
    long_slide = carousel.slides[0].model_copy(
        update={"headline": "An unreasonably long headline " * 3}
    )
    draft = carousel.model_copy(update={"slides": [long_slide, *carousel.slides[1:]]})
    images = render_slides(ALI, draft)
    assert images[0].size == (1080, 1350)


def test_slides_render_without_a_portrait_on_disk(carousel, monkeypatch):
    monkeypatch.setattr("core.carousel.portrait_path", lambda name: None)
    images = render_slides(ALI, carousel)
    assert len(images) == 6


def test_the_personas_render_visibly_different_slides(carousel):
    ali = render_slides(ALI, carousel)[0].getpixel((10, 10))
    isshita = render_slides(ISSHITA, carousel)[0].getpixel((10, 10))
    assert ali != isshita
    assert sum(ali) < sum(isshita)  # dark system versus light system


def test_portrait_slug_is_filesystem_safe():
    assert portrait_slug("Ali Moizuddin") == "ali-moizuddin"


# ---------------------------------------------------------------------------
# Image provider
# ---------------------------------------------------------------------------


def test_nvidia_only_returns_the_prompt_and_never_claims_an_image(nvidia_only):
    assert not image_provider_configured()
    result = create_picture(ALI, "A frayed rope on a dark field, lit from the left.")
    assert result["image_status"] == "prompt_only"
    assert result["image_bytes"] is None
    assert len(str(result["prompt"])) > 80


def test_the_art_direction_prompt_carries_the_palette_and_the_safety_rules():
    prompt = art_direction(ALI, "A frayed rope.")
    assert ALI.visual.background in prompt
    assert ALI.visual.accent in prompt
    assert "no identifiable people" in prompt


def test_an_image_provider_failure_degrades_to_the_prompt(monkeypatch):
    monkeypatch.setenv("MESH_API_KEY", "test-key")
    monkeypatch.setenv("MESH_IMAGE_MODEL", "some/image-model")

    def exploding(_provider):
        raise RuntimeError("gateway timeout at https://api.meshapi.ai key rsk-SECRET")

    monkeypatch.setattr("core.providers.create_client", exploding)
    result = create_picture(ALI, "A frayed rope on a dark field.")
    assert result["image_status"] == "failed"
    assert result["image_bytes"] is None
    assert "SECRET" not in str(result["detail"])


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def test_approved_packages_round_trip(tmp_path):
    db = tmp_path / "history.db"
    package_id = history.save_approved_package(
        db,
        persona="Ali Moizuddin",
        outputs={"post.post": "A grounded line."},
        provider="NVIDIA",
        model="nvidia/nemotron-3-super-120b-a12b",
        output_types=["post"],
    )
    rows = history.list_approved_packages(db)
    assert len(rows) == 1
    assert rows[0]["id"] == package_id
    assert rows[0]["outputs"]["post.post"] == "A grounded line."


def test_history_filters_by_persona(tmp_path):
    db = tmp_path / "history.db"
    for persona in ("Ali Moizuddin", "Rakhee Singhi"):
        history.save_approved_package(
            db, persona=persona, outputs={"post": "x"}, provider="NVIDIA", model="m"
        )
    assert len(history.list_approved_packages(db, persona="Ali Moizuddin")) == 1
    assert len(history.list_approved_packages(db)) == 2


def test_history_is_empty_not_broken_before_anything_is_approved(tmp_path):
    assert history.list_approved_packages(tmp_path / "nothing-here.db") == []


def test_an_unapproved_package_cannot_be_stored(tmp_path):
    import sqlite3

    db = tmp_path / "history.db"
    history.save_approved_package(
        db, persona="Ali Moizuddin", outputs={}, provider="NVIDIA", model="m"
    )
    with sqlite3.connect(db) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO approved_packages "
                "(persona, output_types, outputs, provider, model, approved) "
                "VALUES ('x', '', '{}', 'NVIDIA', 'm', 0)"
            )


# ---------------------------------------------------------------------------
# Full UI flow, no provider credits
# ---------------------------------------------------------------------------


def _stub_generation(monkeypatch):
    def fake_bundle(brief, output_types, provider, model):
        return {
            "success": True,
            "failures": {},
            "outputs": {
                t: {"success": True, "data": PAYLOADS[t], "attempts": 1}
                for t in output_types
                if t in PAYLOADS
            },
        }

    monkeypatch.setattr("ui.stages.generate_bundle", fake_bundle)


def _submit(app, label: str):
    """Form submit buttons carry no key, so they are addressed by label."""
    next(b for b in app.button if b.label == label).click().run()
    return app


def _fill_brief(app, formats=("post", "carousel")):
    app.text_area(key="core_idea").set_value(
        "The bottleneck in automation is the description, not the tooling."
    )
    app.text_area(key="proof").set_value(
        "n8n SDR research pipeline: about 10 hours a week down to about 3."
    )
    app.multiselect(key="formats").set_value(list(formats))
    return _submit(app, "Save and continue")


def test_the_app_starts_on_the_brief_stage(nvidia_only):
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert app.session_state["stage"] == "brief"


def test_the_full_flow_reaches_editable_sections_and_rendered_slides(
    monkeypatch, nvidia_only
):
    _stub_generation(monkeypatch)
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    _fill_brief(app)

    assert app.session_state["stage"] == "generate"
    app.button(key="generate_button").click().run()

    assert app.session_state["stage"] == "edit"
    assert set(app.session_state["package"]) == {"post", "carousel"}

    assert app.text_area(key="edit_post_post").value
    assert app.text_input(key="edit_post_hashtags").value.startswith("#")
    assert app.text_area(key="edit_post_comment_a").value

    assets = app.session_state["carousel_assets"]
    assert assets and assets["count"] == 6
    assert len(app.download_button) == 2
    assert not app.exception


def test_editing_a_field_then_running_qa_audits_the_edit_not_the_original(
    monkeypatch, nvidia_only
):
    _stub_generation(monkeypatch)
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    _fill_brief(app, formats=("post",))
    app.button(key="generate_button").click().run()

    app.text_area(key="edit_post_post").set_value(
        "We shaved 91 hours off the process last week."
    ).run()
    app.button(key="edit_to_qa").click().run()

    assert app.session_state["stage"] == "qa"
    flags = " ".join(app.session_state["qa"]["audit_flags"])
    assert "91" in flags
    assert app.button(key="approve_button").disabled


def test_a_hand_typed_medical_claim_blocks_approval_in_the_ui(monkeypatch, nvidia_only):
    _stub_generation(monkeypatch)
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.selectbox(key="persona").set_value("Rakhee Singhi").run()
    _fill_brief(app, formats=("post",))
    app.button(key="generate_button").click().run()

    app.text_area(key="edit_post_post").set_value(
        "This protocol cures thyroid disease in ninety days."
    ).run()
    app.button(key="edit_to_qa").click().run()

    assert app.button(key="approve_button").disabled
    assert any("cure" in f.lower() for f in app.session_state["qa"]["audit_flags"])


def test_a_blocked_finding_is_shown_with_the_action_that_clears_it(monkeypatch, nvidia_only):
    """A finding states the problem. A stopped person needs the next move.

    The audit message is written for accuracy: it names the rule that fired. On its
    own that leaves a non-technical user staring at a red box with no idea what to
    change, which is the difference between a guardrail and a dead end.
    """
    _stub_generation(monkeypatch)
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    app.selectbox(key="persona").set_value("Rakhee Singhi").run()
    _fill_brief(app, formats=("post",))
    app.button(key="generate_button").click().run()

    app.text_area(key="edit_post_post").set_value(
        "This protocol cures thyroid disease in ninety days."
    ).run()
    app.button(key="edit_to_qa").click().run()

    captions = " ".join(c.value for c in app.caption)
    assert "What to do:" in captions
    assert fix_for("BLOCKED: cures thyroid disease") in captions


def test_every_shipped_fix_message_is_plain_and_actionable():
    """The guidance is the product here, so it gets asserted like code.

    Every fix line has to tell someone what to change. None of them may carry a
    dash character: all three personas ban em dashes and en dashes, and guidance
    that breaks the house style teaches the wrong thing.
    """
    from ui.guide import FIXES, STAGE_GUIDE, WHAT_THIS_IS

    prose = [WHAT_THIS_IS]
    prose += [g["title"] for g in STAGE_GUIDE.values()]
    prose += [g["body"] for g in STAGE_GUIDE.values()]
    prose += [instruction for _, instruction in FIXES]

    for text in prose:
        assert "\u2014" not in text and "\u2013" not in text, text

    for _, instruction in FIXES:
        assert instruction[0].isupper(), instruction
        assert instruction.endswith("."), instruction


def test_a_missing_key_explains_setup_instead_of_failing_later(monkeypatch):
    """With no key at all the app must say so on screen one, not at generation."""
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("MESH_API_KEY", raising=False)
    monkeypatch.delenv("DEFAULT_MODEL", raising=False)

    app = AppTest.from_file(str(APP), default_timeout=60).run()
    errors = " ".join(e.value for e in app.error)
    assert "cannot write anything yet" in errors
    # And it must not have drawn the brief form behind the error.
    assert "fill_example" not in {b.key for b in app.button}


def test_the_sidebar_reports_nvidia_only_and_offers_no_mesh_model(nvidia_only):
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    labels = app.selectbox(key="model_label").options
    assert labels
    assert all("Mesh" not in label for label in labels)
    assert app.session_state["provider"] == "NVIDIA"


def test_an_empty_output_selection_keeps_the_user_on_the_brief(monkeypatch, nvidia_only):
    _stub_generation(monkeypatch)
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    app.text_area(key="core_idea").set_value("An idea.")
    app.multiselect(key="formats").set_value([])
    _submit(app, "Save and continue")

    assert app.session_state["stage"] == "brief"
    assert app.error


# ---------------------------------------------------------------------------
# Planning sections
#
# Both of these are regressions from bugs the evaluation harness found. Neither
# was reachable through the unit tests as they stood, because both needed a real
# calendar to exist before they showed up.
# ---------------------------------------------------------------------------


def test_calendar_weeks_are_planning_not_publishable():
    sections = build_sections(ALI, "calendar", PAYLOADS["calendar"])
    assert sections and all(not s.publishable for s in sections)


def test_post_sections_are_publishable():
    sections = build_sections(ALI, "post", PAYLOADS["post"])
    assert all(s.publishable for s in sections)


def test_an_open_slot_in_a_plan_does_not_block_but_one_in_a_post_does():
    """A calendar is asked to mark the proof it still needs. A post is not."""
    plan = run_qa(ALI, {"week_1": f"Evidence needed: {OPEN_SLOT}"}, planning={"week_1"})
    post = run_qa(ALI, {"post": f"We saved {OPEN_SLOT} hours."})
    assert approve_package(plan)["approved"]
    assert not approve_package(post)["approved"]


def test_an_unverified_figure_in_a_plan_is_information_not_a_blocker():
    qa = run_qa(ALI, {"week_1": "Anchored to the 47 hour rebuild."}, planning={"week_1"})
    assert qa["audit_flags"], "the figure should still be flagged and redacted"
    assert not qa["blocking_flags"]
    assert approve_package(qa)["approved"]


def test_a_safety_breach_in_a_plan_still_blocks():
    """A calendar row becomes a post later, so a claim in one is not harmless."""
    qa = run_qa(
        RAKHEE,
        {"week_1": "Hook angle: how the programme cures thyroid disease."},
        planning={"week_1"},
    )
    assert not approve_package(qa)["approved"]


def test_a_clean_result_is_not_mistaken_for_an_absent_one():
    """An empty blocking list is falsy, and the gate used to recompute on it.

    That discarded the planning exclusion and left a calendar blocked with nothing
    blocking it. Asserting on the empty case directly is the only way this stays
    fixed.
    """
    qa = run_qa(ALI, {"week_1": f"Evidence: {OPEN_SLOT}"}, planning={"week_1"})
    assert qa["blocking_flags"] == []
    verdict = approve_package(qa)
    assert verdict["approved"]
    assert verdict["blocking_flags"] == []
