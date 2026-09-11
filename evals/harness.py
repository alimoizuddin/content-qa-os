"""The three arms, and the record/replay layer that makes a run reproducible.

**studio** is the full system: the persona specification in the prompt, the schema,
the deterministic normalisation, the linter, the auditor, and the approval gate.

**engine** is the Claude Project. It receives the studio's own system prompt, in
full: every voice rule, the verified fact table, the banned phrasings, the safety
rules, the numbers rule. Then nothing enforces any of it. No auditor, no gate; it
publishes whatever it wrote. That is exactly what a written engine document run as
a Claude Project is, and it isolates one variable and only one: whether the rules
are text the model is asked to obey, or code that runs.

Ali asked the honest question directly, which is why this arm exists. The earlier
report compared the studio only against a generic prompt, so it could say the
structure beat a stranger and could not say anything at all about whether it beat
his own engine.

**baseline** is the floor: the same model, the same schema so the output parses,
and nothing else. No persona facts, no verified-number list, no safety rules, no
audit, no gate. It answers what the structure buys over asking a good model
politely.

Every provider response is recorded to ``evals/recorded/``. A recorded run replays
through the real parser and the real gate without spending a credit, which is what
lets CI run the evaluation and lets anyone re-derive the numbers in this report
rather than take them on trust.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.brief import ContentBrief
from core.generator import _clean_json, generate_output
from core.personas import get_persona
from core.providers import (
    create_client,
    provider_for,
    request_options,
    sampling_options,
)
from core.schemas import OUTPUT_SCHEMAS
from core.studio import approve_package, build_sections, run_qa
from evals.scoring import Violation, score_text, serious

EVALS = Path(__file__).resolve().parent
RECORDED = EVALS / "recorded"

ARMS = ("studio", "engine", "baseline")


# ---------------------------------------------------------------------------
# Record and replay
# ---------------------------------------------------------------------------


def _slot(case_id: str, arm: str, output_type: str, attempt: int) -> Path:
    return RECORDED / f"{case_id}.{arm}.{output_type}.{attempt}.txt"


class RecordingClient:
    """Wraps a real client and writes every response body to disk."""

    def __init__(self, inner, case_id: str, arm: str, output_type: str) -> None:
        self._inner = inner
        self._case_id = case_id
        self._arm = arm
        self._output_type = output_type
        self._attempt = 0
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        self._attempt += 1
        response = self._inner.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        path = _slot(self._case_id, self._arm, self._output_type, self._attempt)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return response


class ReplayClient:
    """Serves recorded response bodies in the order they were captured."""

    def __init__(self, case_id: str, arm: str, output_type: str) -> None:
        self._case_id = case_id
        self._arm = arm
        self._output_type = output_type
        self._attempt = 0
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **_kwargs):
        self._attempt += 1
        path = _slot(self._case_id, self._arm, self._output_type, self._attempt)
        if not path.is_file():
            # A recorded attempt that raised before returning left no file, so a
            # gap here means the provider failed on that attempt during the live
            # run. Replaying a failure as a failure keeps the retry behaviour
            # faithful; only a genuinely absent recording is a missing recording.
            later = _slot(self._case_id, self._arm, self._output_type, self._attempt + 1)
            if later.is_file():
                raise RuntimeError("recorded provider failure on this attempt")
            raise FileNotFoundError(
                f"No recording for {self._case_id} {self._arm} {self._output_type} "
                f"attempt {self._attempt}. Run with --live --record first."
            )
        content = path.read_text(encoding="utf-8")
        message = type("Message", (), {"content": content})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()


MANIFEST = RECORDED / "manifest.json"


def has_recordings() -> bool:
    return RECORDED.is_dir() and any(RECORDED.glob("*.txt"))


def recorded_arms() -> set[str]:
    """Which arms the recordings on disk actually cover.

    Recordings predate the arms added after them. Replaying an arm that was never
    recorded produces twenty identical "no recording" lines, which reads like a
    broken harness rather than an absent measurement. Knowing what is on disk lets
    the runner say the true thing instead.
    """
    if not RECORDED.is_dir():
        return set()
    found: set[str] = set()
    for path in RECORDED.glob("*.txt"):
        parts = path.name.split(".")
        if len(parts) >= 2:
            found.add(parts[1])
    return found & set(ARMS)


def write_manifest(model: str) -> None:
    RECORDED.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"model": model}, indent=2), encoding="utf-8")


def recorded_model() -> str:
    """Which model produced the recordings.

    Without this a replay reports whatever model the local .env happens to name,
    which is not the model the numbers came from. A report that misattributes its
    own model is worse than one with no model in it.
    """
    if MANIFEST.is_file():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8")).get("model", "")
        except ValueError:
            return ""
    return ""


# ---------------------------------------------------------------------------
# The baseline arm
# ---------------------------------------------------------------------------


BASELINE_SYSTEM = (
    "You are a skilled LinkedIn ghostwriter. Write in a confident, professional "
    "voice that suits the person described. Respond with a single JSON object and "
    "nothing else. It must validate against this JSON Schema:\n{schema}"
)


def baseline_messages(persona: str, title: str, brief: ContentBrief, output_type: str, schema):
    """A competent, generic request. No facts, no rules, no guardrails.

    This is written to be a fair control rather than a straw man: it names the
    person and their role, states the task clearly, and enforces the same schema.
    What it does not carry is any of the structure the studio adds.
    """
    parts = [
        f"Write a LinkedIn {output_type} for {persona}, a {title}.",
        f"Topic: {brief.core_idea}",
        f"Audience: {brief.audience}",
        f"Goal: {brief.goal}",
    ]
    if brief.proof.strip():
        parts.append(f"Background material: {brief.proof}")
    return [
        {
            "role": "system",
            "content": BASELINE_SYSTEM.format(
                schema=json.dumps(schema.model_json_schema(), separators=(",", ":"))
            ),
        },
        {"role": "user", "content": "\n".join(parts)},
    ]


def run_baseline(
    case_id: str,
    brief: ContentBrief,
    output_type: str,
    model: str,
    client,
) -> dict[str, Any]:
    """Two attempts, same as the studio, so the arms differ in structure not effort."""
    spec = get_persona(brief.persona)
    schema = OUTPUT_SCHEMAS[output_type]
    messages = baseline_messages(spec.name, spec.title, brief, output_type, schema)

    for attempt in (1, 2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=3000,
                **sampling_options(model, attempt),
                **request_options(model),
            )
            content = response.choices[0].message.content or ""
            parsed = schema.model_validate_json(_clean_json(content))
            return {"success": True, "data": parsed.model_dump(), "attempts": attempt}
        except FileNotFoundError:
            raise
        except Exception:
            continue
    return {"success": False, "error": "baseline produced no valid structure", "attempts": 2}


# ---------------------------------------------------------------------------
# Running one case
# ---------------------------------------------------------------------------


@dataclass
class ArmResult:
    arm: str
    case_id: str
    generated: bool
    shipped: bool  # would this text reach LinkedIn
    text: str = ""
    violations: list[Violation] = field(default_factory=list)
    block_reasons: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def serious_violations(self) -> list[Violation]:
        return serious(self.violations)

    @property
    def shipped_unsafe(self) -> bool:
        """The failure that matters: unpublishable text that nothing stopped."""
        return self.shipped and bool(self.serious_violations)


def _brief_from(case: dict[str, Any]) -> ContentBrief:
    raw = case["brief"]
    return ContentBrief(
        persona=case["persona"],
        goal=raw.get("goal", ""),
        audience=raw.get("audience", ""),
        core_idea=raw.get("core_idea", ""),
        proof=raw.get("proof", ""),
        formats=tuple(case["outputs"]),
        register=raw.get("register", ""),
    )


def _flatten(spec, output_type: str, data: dict[str, Any]) -> str:
    """Everything that would actually be published, as one block."""
    return "\n\n".join(s.text for s in build_sections(spec, output_type, data) if s.text.strip())


def run_case(
    case: dict[str, Any],
    arm: str,
    model: str,
    live: bool,
    record: bool,
) -> ArmResult:
    brief = _brief_from(case)
    spec = get_persona(case["persona"])
    output_type = case["outputs"][0]
    case_id = case["id"]

    provider = provider_for(model)

    def client_for(_provider=None):
        if live:
            inner = create_client(provider)
            return RecordingClient(inner, case_id, arm, output_type) if record else inner
        return ReplayClient(case_id, arm, output_type)

    try:
        if arm in ("studio", "engine"):
            # The engine arm shares the studio's generation exactly. They differ
            # only in what happens afterwards, which is the whole point.
            import core.generator as generator

            original = generator.create_client
            original_validate = generator.validate_selection
            generator.create_client = client_for
            if not live:
                # Replay must not need a key. The app hides a provider's models
                # when its key is missing, which is right for the app and wrong
                # here: replay never calls the provider. Without this, replaying
                # a Claude run on a machine with no Mesh key produced 0 of 20 for
                # the studio and still exited cleanly, so CI passed while measuring
                # nothing. The allowlist check stays; only the key check goes.
                from core.providers import ALL_MODELS

                def validate_allowlisted(_provider, requested):
                    if requested not in {m.model for m in ALL_MODELS}:
                        raise ValueError("That model is not in the allowlist.")

                generator.validate_selection = validate_allowlisted
            try:
                outcome = generate_output(brief, output_type, provider, model)
            finally:
                generator.create_client = original
                generator.validate_selection = original_validate
        else:
            outcome = run_baseline(case_id, brief, output_type, model, client_for())
    except FileNotFoundError as error:
        return ArmResult(arm, case_id, generated=False, shipped=False, error=str(error))

    if not outcome["success"]:
        # A failure to generate is not a pass. It ships nothing, but the case is
        # recorded as ungenerated so it cannot be mistaken for a clean result.
        return ArmResult(arm, case_id, generated=False, shipped=False, error=outcome["error"])

    text = _flatten(spec, output_type, outcome["data"])

    if arm == "studio":
        built = build_sections(spec, output_type, outcome["data"])
        sections = {s.key: s.text for s in built}
        planning = {s.key for s in built if not s.publishable}
        qa = run_qa(spec, sections, proof=brief.proof, planning=planning)
        verdict = approve_package(qa)
        shipped = verdict["approved"]
        # What the studio would actually publish is the sanitised text, not the raw
        # generation: scoring the pre-audit copy would credit the gate for nothing.
        text = "\n\n".join(v for v in qa["outputs"].values() if v.strip())
        reasons = list(verdict["reasons"])
    else:
        # Neither the engine arm nor the baseline has a gate. For the baseline that
        # is the absence of rules. For the engine it is the presence of rules with
        # nothing enforcing them, which is the more interesting of the two.
        shipped = True
        reasons = []

    return ArmResult(
        arm=arm,
        case_id=case_id,
        generated=True,
        shipped=shipped,
        text=text,
        violations=score_text(case["persona"], text, brief.proof),
        block_reasons=reasons,
    )


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    data = json.loads((path or EVALS / "cases.json").read_text(encoding="utf-8"))
    return data["cases"]
