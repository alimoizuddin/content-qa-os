"""Generation, schema, and provider behaviour. No network, no credits."""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from core.brief import ContentBrief
from core.generator import (
    GENERIC_PROVIDER_ERROR,
    _clean_json,
    classify_provider_error,
    generate_bundle,
    generate_output,
)
from core.personas import get_persona
from core.providers import (
    NVIDIA_MODELS,
    available_models,
    default_model,
    has_openrouter_key,
    validate_selection,
)
from core.schemas import CarouselDraft, ContentCalendar, PicturePrompt, PostDraft
from tests.conftest import PAYLOADS, FakeClient

OUTPUT_TYPES = ("post", "carousel", "calendar", "picture")


# ---------------------------------------------------------------------------
# Every output type
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("output_type", OUTPUT_TYPES)
def test_each_output_type_generates_and_validates(
    output_type, brief, patch_client, nvidia_only
):
    patch_client(output_type)
    result = generate_output(brief, output_type, "NVIDIA", default_model().model)
    assert result["success"], result.get("error")
    assert result["attempts"] == 1
    assert result["data"]


def test_mixed_bundle_returns_every_requested_type(brief, monkeypatch, nvidia_only):
    def client_for(_provider):
        # One client that answers whichever type was asked for, by reading the prompt.
        class Router:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        system = kwargs["messages"][0]["content"]
                        for name in OUTPUT_TYPES:
                            if f"TASK: {name}" in system:
                                payload = PAYLOADS[name]
                                break
                        else:  # pragma: no cover - the router always matches
                            payload = PAYLOADS["post"]
                        return FakeClient([json.dumps(payload)]).chat.completions.create(
                            **kwargs
                        )

        return Router()

    monkeypatch.setattr("core.generator.create_client", client_for)
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)

    result = generate_bundle(brief, list(OUTPUT_TYPES), "NVIDIA", default_model().model)
    assert result["success"], result["failures"]
    assert set(result["outputs"]) == set(OUTPUT_TYPES)


def test_empty_selection_is_refused(brief, nvidia_only):
    result = generate_bundle(brief, [], "NVIDIA", default_model().model)
    assert not result["success"]
    assert "at least one" in result["error"].lower()
    assert result["outputs"] == {}


def test_incomplete_brief_is_refused_before_any_provider_call(nvidia_only):
    empty = ContentBrief(persona="Ali Moizuddin")
    result = generate_output(empty, "post", "NVIDIA", default_model().model)
    assert not result["success"]
    assert result["attempts"] == 0
    assert "incomplete" in result["error"].lower()


# ---------------------------------------------------------------------------
# The two-attempt contract
# ---------------------------------------------------------------------------


def test_schema_retry_succeeds_on_the_second_attempt(brief, patch_client, nvidia_only):
    client = patch_client("post", extra=["this is not JSON at all"])
    result = generate_output(brief, "post", "NVIDIA", default_model().model)
    assert result["success"]
    assert result["attempts"] == 2
    assert len(client.completions.calls) == 2


def test_second_attempt_is_told_it_is_corrective(brief, patch_client, nvidia_only):
    client = patch_client("post", extra=["{"])
    generate_output(brief, "post", "NVIDIA", default_model().model)
    first, second = (c["messages"][0]["content"] for c in client.completions.calls[:2])
    assert "did not match the required structure" not in first
    assert "did not match the required structure" in second


def test_schema_failure_stops_at_two_attempts_and_leaks_nothing(
    brief, monkeypatch, nvidia_only
):
    client = FakeClient(["not json", "still not json", "never reached"])
    monkeypatch.setattr("core.generator.create_client", lambda provider: client)
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)

    result = generate_output(brief, "post", "NVIDIA", default_model().model)
    assert not result["success"]
    assert result["attempts"] == 2
    assert len(client.completions.calls) == 2
    assert "not json" not in result["error"]


def test_provider_exception_never_reaches_the_caller(brief, monkeypatch, nvidia_only):
    class Exploding:
        class chat:
            class completions:
                @staticmethod
                def create(**_kwargs):
                    raise RuntimeError(
                        "401 Unauthorized for https://integrate.api.nvidia.com key nvapi-SECRET"
                    )

    monkeypatch.setattr("core.generator.create_client", lambda provider: Exploding())
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)

    result = generate_output(brief, "post", "NVIDIA", default_model().model)
    assert not result["success"]
    assert "SECRET" not in result["error"]
    assert "nvapi" not in result["error"]
    assert "integrate.api.nvidia.com" not in result["error"]


@pytest.mark.parametrize(
    "raw",
    [
        '```json\n{"prompt":"' + "x" * 60 + '","alt_text":"a"}\n```',
        'Here you go:\n{"prompt":"' + "x" * 60 + '","alt_text":"a"}\nHope that helps.',
        '{"prompt":"' + "x" * 60 + '","alt_text":"a"}',
    ],
)
def test_fenced_and_chatty_responses_are_recovered(raw, brief, monkeypatch, nvidia_only):
    monkeypatch.setattr("core.generator.create_client", lambda provider: FakeClient([raw]))
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)
    result = generate_output(brief, "picture", "NVIDIA", default_model().model)
    assert result["success"], result.get("error")


def test_clean_json_leaves_a_bare_object_alone():
    assert _clean_json('  {"a": 1}  ') == '{"a": 1}'


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------


def test_openrouter_models_are_hidden_without_a_key(nvidia_only):
    assert not has_openrouter_key()
    providers = {m["provider"] for m in available_models()}
    assert providers == {"NVIDIA"}
    with pytest.raises(ValueError):
        validate_selection("OpenRouter", "openai/gpt-4o")


def test_openrouter_models_appear_once_a_key_exists(monkeypatch, nvidia_only):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    providers = {m["provider"] for m in available_models()}
    assert providers == {"NVIDIA", "OpenRouter"}
    validate_selection("OpenRouter", "openai/gpt-4o")


def test_nvidia_model_env_var_is_honoured(monkeypatch, nvidia_only):
    monkeypatch.setenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")
    assert default_model().model == "meta/llama-3.2-11b-vision-instruct"
    assert available_models()[0]["model"] == "meta/llama-3.2-11b-vision-instruct"


def test_unknown_nvidia_model_env_var_falls_back_instead_of_crashing(monkeypatch, nvidia_only):
    monkeypatch.setenv("NVIDIA_MODEL", "someone/not-allowlisted")
    assert default_model().model in {m["model"] for m in available_models()}


def test_a_model_outside_the_allowlist_is_refused(nvidia_only):
    with pytest.raises(ValueError):
        validate_selection("NVIDIA", "meta/llama-4-definitely-not-configured")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


def test_calendar_requires_sixteen_entries_four_per_week():
    entries = PAYLOADS["calendar"]["entries"][:15]
    with pytest.raises(ValidationError):
        ContentCalendar.model_validate({"entries": entries})


def test_calendar_rejects_a_week_that_never_changes_format():
    entries = [dict(e) for e in PAYLOADS["calendar"]["entries"]]
    for entry in entries:
        if entry["week"] == 2:
            entry["content_format"] = "carousel"
    with pytest.raises(ValidationError, match="single format"):
        ContentCalendar.model_validate({"entries": entries})


def test_a_hashtag_note_mismatch_is_repaired_rather_than_rejected(brief, monkeypatch, nvidia_only):
    """A cosmetic mismatch must not cost a retry."""
    payload = dict(PAYLOADS["post"])
    payload["hashtag_notes"] = ["only one note"]
    monkeypatch.setattr(
        "core.generator.create_client", lambda provider: FakeClient([json.dumps(payload)])
    )
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)

    result = generate_output(brief, "post", "NVIDIA", default_model().model)
    assert result["success"]
    assert result["attempts"] == 1
    data = result["data"]
    assert len(data["hashtag_notes"]) == len(data["hashtags"])


def test_carousel_rejects_fewer_than_six_slides():
    payload = {"title": "x", "slides": PAYLOADS["carousel"]["slides"][:5]}
    with pytest.raises(ValidationError):
        CarouselDraft.model_validate(payload)


def test_picture_prompt_requires_real_detail():
    with pytest.raises(ValidationError):
        PicturePrompt.model_validate({"prompt": "a nice image"})


# ---------------------------------------------------------------------------
# Prompt content
# ---------------------------------------------------------------------------


def test_the_prompt_carries_the_verified_facts_and_refuses_the_unverified_ones(
    brief, patch_client, nvidia_only
):
    client = patch_client("post")
    generate_output(brief, "post", "NVIDIA", default_model().model)
    system = client.completions.calls[0]["messages"][0]["content"]

    assert "Top 0.1% global ChatGPT user" in system
    assert "20+ documented systems" in system
    assert "300+ hours of multilingual audio at 95%+ accuracy" in system

    # The figure Ali withdrew as invented must never be offered as a fact, and the
    # prompt must carry the wording that replaced it.
    assert "10 hours a week" not in system
    assert "15 minutes of manual research per lead" in system

    assert "must never be written" in system
    assert "No em dashes" in system


def test_a_brief_without_proof_instructs_open_slots(nvidia_only):
    spec = get_persona("Ali Moizuddin")
    unproven = ContentBrief(
        persona=spec.name,
        goal="Reach",
        audience="Founders",
        core_idea="Automation is a clarity problem.",
        formats=("post",),
    )
    prompt = unproven.to_prompt(spec)
    assert "No proof was supplied" in prompt
    assert "[OPEN SLOT]" in prompt


# ---------------------------------------------------------------------------
# Provider error classification
#
# A retired model and a dropped connection used to produce the identical sentence,
# which hid the only useful detail: pick a different model. Status codes are facts
# about the request and are safe to act on; response bodies are not, and are never
# quoted.
# ---------------------------------------------------------------------------


class _Status(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__("raw body with a key nvapi-SECRET and a url")
        self.status_code = status_code


@pytest.mark.parametrize(
    "status,fragment",
    [
        (401, "API key"),
        (404, "not available to this account"),
        (410, "end of life"),
        (429, "Rate limited"),
        (503, "temporarily unavailable"),
    ],
)
def test_known_statuses_become_actionable_sentences(status, fragment):
    message = classify_provider_error(_Status(status))
    assert fragment in message
    assert "SECRET" not in message


def test_an_unrecognised_failure_falls_back_to_the_generic_sentence():
    assert classify_provider_error(RuntimeError("boom")) == GENERIC_PROVIDER_ERROR


def test_a_retired_model_tells_the_user_to_pick_another(brief, monkeypatch, nvidia_only):
    class Retired:
        class chat:
            class completions:
                @staticmethod
                def create(**_kwargs):
                    raise _Status(410)

    monkeypatch.setattr("core.generator.create_client", lambda provider: Retired())
    monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)
    result = generate_output(brief, "post", "NVIDIA", default_model().model)
    assert "Choose another in the sidebar" in result["error"]
    assert "SECRET" not in result["error"]


def test_reasoning_models_are_asked_not_to_think_out_loud(brief, patch_client, nvidia_only):
    """A chain of thought spends the token budget before the JSON arrives."""
    client = patch_client("post")
    reasoning = next(m for m in NVIDIA_MODELS if m.reasoning)
    generate_output(brief, "post", "NVIDIA", reasoning.model)
    sent = client.completions.calls[0]
    assert sent["extra_body"]["chat_template_kwargs"]["thinking"] is False


def test_a_plain_model_is_sent_no_thinking_flag(brief, patch_client, nvidia_only):
    client = patch_client("post")
    plain = next(m for m in NVIDIA_MODELS if not m.reasoning)
    generate_output(brief, "post", "NVIDIA", plain.model)
    assert "extra_body" not in client.completions.calls[0]


def test_every_allowlisted_model_is_uniquely_labelled():
    models = available_models()
    assert len({m["model"] for m in models}) == len(models)
    assert len({m["label"] for m in models}) == len(models)
