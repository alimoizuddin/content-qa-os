"""Allowlisted, local provider configuration.

NVIDIA NIM is the default and the only required provider. OpenRouter is optional
and its models only appear once ``OPENROUTER_API_KEY`` is set locally, so a machine
with no OpenRouter key never sees an option it cannot use.

Two things were fixed here rather than worked around. ``NVIDIA_MODEL`` was
documented in the README and the .env for months and read by nothing, because the
model was hardcoded; it is now honoured, and it is still checked against the
allowlist so an env var cannot smuggle in an arbitrary model. And ``create_client``
previously took a ``model`` argument it never used, which made the signature lie
about what it does.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# One bounded timeout for every call. A large model writing a sixteen-entry calendar
# genuinely takes most of a minute, and a cold NIM endpoint adds to that, so this is
# generous on purpose. It is still bounded: nothing here can hang forever.
REQUEST_TIMEOUT = 120.0


@dataclass(frozen=True)
class ModelOption:
    provider: str
    model: str
    label: str
    reasoning: bool = False  # emits a chain of thought unless told not to


# Every entry here was called against the live NIM catalogue and confirmed to
# return usable JSON. That verification matters more than it sounds: a plausible
# model id that has reached end of life fails at generation time with a 410, and
# NVIDIA retires models on a schedule. `check_live_catalogue()` re-verifies on
# demand, and the sidebar surfaces the result.
NVIDIA_MODELS: tuple[ModelOption, ...] = (
    ModelOption(
        "NVIDIA",
        "nvidia/nemotron-3-super-120b-a12b",
        "NVIDIA NIM . Nemotron 3 Super 120B",
        reasoning=True,
    ),
    ModelOption(
        "NVIDIA", "meta/llama-3.2-11b-vision-instruct", "NVIDIA NIM . Llama 3.2 11B (fast)"
    ),
    ModelOption(
        "NVIDIA",
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        "NVIDIA NIM . Nemotron 3.5 Lightning 30B",
        reasoning=True,
    ),
)

OPENROUTER_MODELS: tuple[ModelOption, ...] = (
    ModelOption("OpenRouter", "anthropic/claude-sonnet-4.5", "OpenRouter . Claude Sonnet 4.5"),
    ModelOption("OpenRouter", "openai/gpt-4o", "OpenRouter . GPT-4o"),
    ModelOption("OpenRouter", "google/gemini-2.0-flash-001", "OpenRouter . Gemini 2.0 Flash"),
)


ALL_MODELS: tuple[ModelOption, ...] = NVIDIA_MODELS + OPENROUTER_MODELS


def request_options(model: str) -> dict[str, object]:
    """Per-model request options.

    Reasoning models on NIM emit their chain of thought into the response body and
    will happily spend an entire token budget on it before reaching the JSON. Asking
    the chat template to turn thinking off is the difference between a valid package
    and two wasted attempts, so it is bound to the model rather than left to luck.
    """
    for option in ALL_MODELS:
        if option.model == model and option.reasoning:
            return {"extra_body": {"chat_template_kwargs": {"thinking": False}}}
    return {}


def has_openrouter_key() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY", "").strip())


def has_nvidia_key() -> bool:
    return bool(os.getenv("NVIDIA_API_KEY", "").strip())


def default_model() -> ModelOption:
    """The NVIDIA model NVIDIA_MODEL names, or the first allowlisted one.

    An unknown value in NVIDIA_MODEL is ignored rather than fatal: the studio
    should still start, and the sidebar reports which model it actually resolved.
    """
    requested = os.getenv("NVIDIA_MODEL", "").strip()
    for option in NVIDIA_MODELS:
        if option.model == requested:
            return option
    return NVIDIA_MODELS[0]


def available_models() -> list[dict[str, str]]:
    """Every model this machine is configured to call, NVIDIA first."""
    options: list[ModelOption] = []
    preferred = default_model()
    options.append(preferred)
    options.extend(m for m in NVIDIA_MODELS if m.model != preferred.model)
    if has_openrouter_key():
        options.extend(OPENROUTER_MODELS)
    return [asdict(option) for option in options]


def validate_selection(provider: str, model: str) -> None:
    allowed = {(item["provider"], item["model"]) for item in available_models()}
    if (provider, model) not in allowed:
        raise ValueError(
            "The selected provider or model is not available in local configuration."
        )


def provider_status() -> list[dict[str, object]]:
    """What the sidebar shows. Never includes a key, or any part of one."""
    return [
        {
            "provider": "NVIDIA NIM",
            "ready": has_nvidia_key(),
            "detail": (
                f"Default model: {default_model().label}"
                if has_nvidia_key()
                else "Add NVIDIA_API_KEY to your local .env file."
            ),
            "required": True,
        },
        {
            "provider": "OpenRouter",
            "ready": has_openrouter_key(),
            "detail": (
                "Extra models available."
                if has_openrouter_key()
                else "Not configured. NVIDIA-only mode, which is fully supported."
            ),
            "required": False,
        },
    ]


def check_live_catalogue() -> dict[str, object]:
    """Compare the allowlist against what NVIDIA is serving right now.

    Models are retired on a schedule, and a retired one fails at generation time
    with a status the studio then has to explain. One catalogue call up front turns
    that into a sidebar line instead of a failed run.
    """
    if not has_nvidia_key():
        return {"ok": False, "detail": "No NVIDIA key configured.", "missing": []}
    try:
        client = create_client("NVIDIA")
        live = {model.id for model in client.models.list().data}
    except Exception:
        return {
            "ok": False,
            "detail": "Could not reach the provider catalogue. Check your connection.",
            "missing": [],
        }

    missing = [m.model for m in NVIDIA_MODELS if m.model not in live]
    if missing:
        return {
            "ok": False,
            "detail": f"{len(missing)} allowlisted model(s) are no longer served.",
            "missing": missing,
        }
    return {
        "ok": True,
        "detail": f"All {len(NVIDIA_MODELS)} allowlisted models are available.",
        "missing": [],
    }


def create_client(provider: str) -> OpenAI:
    if provider == "NVIDIA":
        api_key = os.getenv("NVIDIA_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "NVIDIA is not configured. Add NVIDIA_API_KEY to your local .env file."
            )
        return OpenAI(
            base_url=NVIDIA_BASE_URL, api_key=api_key, timeout=REQUEST_TIMEOUT, max_retries=1
        )

    if provider == "OpenRouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OpenRouter is not configured.")
        return OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
            timeout=REQUEST_TIMEOUT,
            max_retries=1,
        )

    raise ValueError("Unknown provider.")
