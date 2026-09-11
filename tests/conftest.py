"""Shared fixtures. Every test runs offline against a fake provider."""
from __future__ import annotations

import json
from typing import Any

import pytest

from core.brief import ContentBrief

VALID_POST = {
    "hook": "Prospect research went from about 10 hours a week to about 3.",
    "body_lines": [
        "The pipeline did not get smarter.",
        "The brief did. Named inputs, one review step, a number to measure against.",
        "That is the whole change.",
    ],
    "takeaway": "The bottleneck was the description, not the tooling.",
    "question": "Schema first or prompt first?",
    "keywords": ["AI automation", "n8n", "workflow automation"],
    "keyword_rationale": "These keep the account inside one topic lane so the ranking model keeps classifying it consistently.",
    "hashtags": ["#Automation", "#n8n", "#NoCode"],
    "hashtag_notes": [
        "Broad category tag for the automation audience.",
        "Names the exact tool the build uses.",
        "Reaches the non-technical founder side of the audience.",
    ],
    "comment_a": "One detail the post left out: the review step is manual on purpose. What would you automate first?",
    "comment_b": "The operational backbone here is the same one behind the SOP work.",
    "repost_caption": "A companion read for anyone building their first research workflow.",
    "reply_templates": [
        "Which part of yours breaks first?",
        "About 3 hours, down from about 10. The review step stays manual.",
        "Fair on the tooling. The description layer still decides the outcome.",
    ],
    "publish_window": "10:00 to 11:30 AM IST",
}

VALID_CAROUSEL = {
    "title": "The description layer",
    "slides": [
        {
            "headline": f"Slide headline {i}",
            "body": f"A short, phone readable line for slide {i}.",
            "design_note": f"A tangible object photographed against negative space, {i}.",
            "momentum": "keep going >" if i < 6 else "",
        }
        for i in range(1, 7)
    ],
}

VALID_CALENDAR = {
    "entries": [
        {
            "week": week,
            "pillar": "BIP Build in public",
            "content_format": ["post", "carousel", "framework", "proof"][index],
            "hook_angle": f"Week {week} entry {index + 1} angle.",
            "target_asset": "n8n SDR research pipeline",
            "cta": "Reply with where yours broke.",
            "goal": "Both",
            "evidence": "",
        }
        for week in (1, 2, 3, 4)
        for index in range(4)
    ]
}

VALID_PICTURE = {
    "prompt": (
        "A single frayed rope resting on a dark field, lit from the left, with generous "
        "negative space above it and one brass highlight catching the frayed end."
    ),
    "alt_text": "A frayed rope on a dark surface.",
}

PAYLOADS: dict[str, dict[str, Any]] = {
    "post": VALID_POST,
    "carousel": VALID_CAROUSEL,
    "calendar": VALID_CALENDAR,
    "picture": VALID_PICTURE,
}


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    """Returns a queued sequence of raw response strings, then repeats the last."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs) -> FakeResponse:
        self.calls.append(kwargs)
        index = min(len(self.calls) - 1, len(self._responses) - 1)
        return FakeResponse(self._responses[index])


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.completions = FakeCompletions(responses)
        self.chat = type("Chat", (), {"completions": self.completions})()


def fake_client_for(output_type: str, *, extra: list[str] | None = None) -> FakeClient:
    return FakeClient((extra or []) + [json.dumps(PAYLOADS[output_type])])


@pytest.fixture
def nvidia_only(monkeypatch):
    """A machine with NVIDIA configured and no Mesh key."""
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key-not-a-real-one")
    monkeypatch.setenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    monkeypatch.delenv("DEFAULT_MODEL", raising=False)
    monkeypatch.delenv("MESH_API_KEY", raising=False)
    monkeypatch.delenv("MESH_IMAGE_MODEL", raising=False)


@pytest.fixture
def brief() -> ContentBrief:
    return ContentBrief(
        persona="Ali Moizuddin",
        goal="Both: trust building that earns profile visits and DMs",
        audience="Non-technical founders",
        core_idea="The bottleneck in automation is the description, not the tooling.",
        proof="n8n SDR research pipeline: about 10 hours a week for about 100 leads down to about 3 hours.",
        formats=("post",),
        register="Clinical",
    )


@pytest.fixture
def patch_client(monkeypatch):
    """Install a fake provider client for a given output type."""

    def install(output_type: str, extra: list[str] | None = None) -> FakeClient:
        client = fake_client_for(output_type, extra=extra)
        monkeypatch.setattr("core.generator.create_client", lambda provider: client)
        monkeypatch.setattr("core.generator.validate_selection", lambda p, m: None)
        return client

    return install


@pytest.fixture(autouse=True)
def isolated_run_log(tmp_path, monkeypatch):
    """Every test writes to its own throwaway log, never the real one in data/logs."""
    from core import runlog

    monkeypatch.setattr(runlog, "LOG_PATH", tmp_path / "runs.jsonl")
    monkeypatch.setattr(runlog, "ENABLED", True)
