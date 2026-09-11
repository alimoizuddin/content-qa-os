"""Bounded, structured generation.

Two attempts per output type and no more: the initial request, then one corrective
retry that tells the model its previous response did not validate. A third attempt
on a model that has failed a schema twice is almost always a third failure with a
longer wait attached.

Provider error text never reaches the caller. A raw provider exception can carry a
URL, a request id, or in the worst case part of a key, and this app shows its
errors to a browser. The caller gets a fixed, safe sentence and the attempt count.
"""
from __future__ import annotations

import json
import re
import time
from typing import Any

from pydantic import BaseModel, ValidationError

from core import runlog
from core.brief import ContentBrief
from core.linter import strip_dashes
from core.personas import PersonaSpec, get_persona
from core.prompts import build_messages
from core.providers import (
    create_client,
    request_options,
    sampling_options,
    validate_selection,
)
from core.schemas import OUTPUT_SCHEMAS

# These are ceilings, not targets: a model that finishes early costs early. They
# were tuned against Nemotron and were too tight for a reasoning model, which
# spends part of the same budget thinking before it writes a character of JSON.
# When the budget runs out mid-string the response is a truncated object, and the
# old code reported that as "did not match the required structure", which sent
# people off to change their brief over a problem the brief did not cause.
MAX_TOKENS = {
    "post": 8000,
    "carousel": 9000,
    "calendar": 12000,
    "picture": 3000,
}

GENERIC_PROVIDER_ERROR = (
    "The provider could not complete this request. Check your connection and try again."
)

# Provider failures are classified, never quoted. The distinction matters: an HTTP
# status is a fact about the request, while the response body can carry a URL, a
# request id, or part of a key, and this app renders its errors into a browser.
#
# The generic message alone turned out to be too little. A model that had reached
# end of life produced exactly the same sentence as a dropped connection, which
# left the only actionable detail, "pick a different model", invisible.
STATUS_MESSAGES: dict[int, str] = {
    400: "The provider rejected the request as malformed. Try a shorter brief.",
    401: "The provider rejected the API key. Check NVIDIA_API_KEY in your .env file.",
    403: "This key is not permitted to use that model.",
    404: "That model is not available to this account. Choose another in the sidebar.",
    410: "That model has reached end of life and is no longer served. Choose another in the sidebar.",
    413: "The request was too large. Shorten the brief or the proof.",
    422: "The provider could not process the request as sent.",
    402: (
        "The provider account is out of credit. Top up the account for this key, or "
        "switch to another model in the sidebar."
    ),
    429: "Rate limited by the provider. Wait a moment and try again.",
    500: "The provider had an internal error. Try again shortly.",
    502: "The provider is unreachable right now. Try again shortly.",
    503: "The model is temporarily unavailable. Try again, or choose another model.",
    504: "The provider timed out. Try again, or choose a smaller model.",
}


def classify_provider_error(error: Exception) -> str:
    """A safe, actionable sentence for a provider failure. Never the raw text."""
    status = getattr(error, "status_code", None)
    if isinstance(status, int) and status in STATUS_MESSAGES:
        return STATUS_MESSAGES[status]
    name = type(error).__name__
    if "Timeout" in name:
        return "The request timed out. Try again, or choose a smaller model."
    if "Connection" in name:
        return "Could not reach the provider. Check your connection."
    return GENERIC_PROVIDER_ERROR


SCHEMA_FAILURE = (
    "The model returned a response that did not match the required structure, twice. "
    "Try a different model, or shorten the brief."
)

TRUNCATED = (
    "The model ran out of room before it finished writing, twice. Ask for fewer "
    "things at once, or choose another model in the sidebar."
)


_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def _clean_json(content: str) -> str:
    """Strip a code fence, drop prose either side, and repair a trailing comma.

    Small models fence their output or add a sentence of preamble even when told
    not to. Slicing between the first '{' and last '}' recovers both cases.

    The trailing-comma repair is attempted only when the sliced text does not
    already parse, so well-formed JSON is never rewritten and a comma inside a
    string literal cannot be damaged. The evaluation harness found this one: an
    otherwise-complete package was discarded and a whole retry spent over a single
    comma before a closing bracket.
    """
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.rstrip().endswith("```"):
            content = content.rstrip()[:-3]
    start, end = content.find("{"), content.rfind("}")
    if start != -1 and end > start:
        content = content[start : end + 1]
    content = content.strip()

    try:
        json.loads(content)
        return content
    except ValueError:
        pass

    repaired = _TRAILING_COMMA.sub(r"\1", content)
    try:
        json.loads(repaired)
        return repaired
    except ValueError:
        return content


def generate_output(
    brief: ContentBrief,
    output_type: str,
    provider: str,
    model: str,
) -> dict[str, Any]:
    """Generate one output type. Never raises for provider or schema problems.

    Every call is timed and written to the run log, content free: which person,
    which model, how long it took, whether it worked, and the app's own reason if
    it did not.
    """
    started = time.perf_counter()
    result = _generate_output(brief, output_type, provider, model)
    runlog.log_event(
        "generate",
        persona=brief.persona,
        output_type=output_type,
        provider=provider,
        model=model,
        success=bool(result.get("success")),
        attempts=result.get("attempts", 0),
        error=result.get("error", ""),
        seconds=round(time.perf_counter() - started, 2),
    )
    return result


def _generate_output(
    brief: ContentBrief,
    output_type: str,
    provider: str,
    model: str,
) -> dict[str, Any]:
    """The generation itself. See ``generate_output``."""
    if output_type not in OUTPUT_SCHEMAS:
        return {"success": False, "error": "Unsupported output type.", "attempts": 0}

    missing = brief.missing_required()
    if missing:
        return {
            "success": False,
            "error": "The brief is incomplete: " + ", ".join(missing) + ".",
            "attempts": 0,
        }

    try:
        spec = get_persona(brief.persona)
        validate_selection(provider, model)
        client = create_client(provider)
    except ValueError as error:
        return {"success": False, "error": str(error), "attempts": 0}

    schema = OUTPUT_SCHEMAS[output_type]
    safe_brief = brief.truncated()

    truncated = False

    for attempt in (1, 2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=build_messages(
                    spec, safe_brief, output_type, schema, corrective=attempt == 2
                ),
                max_tokens=MAX_TOKENS[output_type],
                **sampling_options(model, attempt),
                **request_options(model),
            )
            choice = response.choices[0]
            content = choice.message.content or ""
            # A cut-off response is a budget problem, not a comprehension problem,
            # and saying so is the difference between a fixable error and a
            # misleading one. Recordings replayed from disk carry no finish
            # reason, so its absence is never treated as truncation.
            if getattr(choice, "finish_reason", None) == "length":
                truncated = True
                continue
            parsed = schema.model_validate_json(_clean_json(content))
            data = normalise(spec, safe_brief, output_type, parsed)
            return {"success": True, "data": data, "attempts": attempt}
        except (ValidationError, json.JSONDecodeError, AttributeError, IndexError, TypeError):
            continue
        except Exception as error:
            # Classified, never quoted. See STATUS_MESSAGES.
            return {
                "success": False,
                "error": classify_provider_error(error),
                "attempts": attempt,
            }

    return {"success": False, "error": TRUNCATED if truncated else SCHEMA_FAILURE, "attempts": 2}


def generate_bundle(
    brief: ContentBrief,
    output_types: list[str],
    provider: str,
    model: str,
) -> dict[str, Any]:
    """Generate several output types. A partial bundle is still returned."""
    selected = [t for t in dict.fromkeys(output_types) if t in OUTPUT_SCHEMAS]
    if not selected:
        return {
            "success": False,
            "error": "Select at least one output before generating.",
            "outputs": {},
            "failures": {},
        }
    results = {
        output_type: generate_output(brief, output_type, provider, model)
        for output_type in selected
    }
    failures = {n: r["error"] for n, r in results.items() if not r["success"]}
    return {"success": not failures, "outputs": results, "failures": failures}


# ---------------------------------------------------------------------------
# Deterministic post-processing
# ---------------------------------------------------------------------------


# The brief allows six to eight carousel slides.
MAX_CAROUSEL_SLIDES = 8


def _without_dashes(value: Any) -> Any:
    """``strip_dashes`` applied to every string inside a nested structure."""
    if isinstance(value, str):
        return strip_dashes(value)
    if isinstance(value, list):
        return [_without_dashes(v) for v in value]
    if isinstance(value, dict):
        return {k: _without_dashes(v) for k, v in value.items()}
    return value


def normalise(
    spec: PersonaSpec,
    brief: ContentBrief,
    output_type: str,
    parsed: BaseModel,
) -> dict[str, Any]:
    """Fill the gaps a model reliably leaves, without inventing substance.

    Everything filled here is either a fact from the persona spec (the publishing
    window, the hashtag pool) or a structural default. Nothing here invents a
    claim, a metric, or a story: that is the whole point of doing it in Python
    rather than asking the model again.
    """
    # Dashes are removed here, at the moment of writing, from every field of every
    # output. Doing it only at the safety check left them visible in the boxes
    # people edit and copy from, which is exactly where text gets published from.
    data = _without_dashes(parsed.model_dump())

    if output_type == "carousel":
        # A model sometimes writes more slides than allowed. The cover and the
        # closing slide carry the arc, so they are kept and the middle is trimmed.
        cap = min(spec.carousel.max_slides, MAX_CAROUSEL_SLIDES)
        slides = data.get("slides") or []
        if len(slides) > cap:
            data["slides"] = slides[: cap - 1] + slides[-1:]

    if output_type != "post":
        return data

    data["publish_window"] = data.get("publish_window") or spec.publish.window

    hashtags = [h.strip() for h in data.get("hashtags") or [] if h.strip()]
    hashtags = [h if h.startswith("#") else f"#{h.lstrip('#')}" for h in hashtags]
    banned = {b.lower() for b in spec.hashtags_banned}
    hashtags = [h for h in hashtags if h.lower() not in banned]
    if not hashtags:
        hashtags = list(spec.hashtags_broad[:1] + spec.hashtags_niche[:2])
    data["hashtags"] = hashtags[:5]

    notes = [n.strip() for n in data.get("hashtag_notes") or [] if n.strip()]
    if len(notes) != len(data["hashtags"]):
        notes = notes[: len(data["hashtags"])]
        while len(notes) < len(data["hashtags"]):
            tag = data["hashtags"][len(notes)]
            notes.append(f"Categorises this post for readers already following {tag[1:]}.")
    data["hashtag_notes"] = notes

    keywords = [k.strip() for k in data.get("keywords") or [] if k.strip()]
    data["keywords"] = keywords[:8] or list(spec.keyword_tiers["Tier 1 identity"][:3])

    replies = [r.strip() for r in data.get("reply_templates") or [] if r.strip()]
    data["reply_templates"] = replies[:3]

    return data
