"""Allowlisted, local provider configuration.

NVIDIA NIM is the default and the only required provider. Mesh API is optional and
its models only appear once ``MESH_API_KEY`` is set locally, so a machine with no
Mesh key never sees an option it cannot use.

Mesh replaced OpenRouter. Both are OpenAI-compatible gateways, so the swap is a
base URL and a key name, but Mesh carries the Anthropic catalogue, which is what
makes "let Claude write and let the rules block" possible in one process. It also
serves a real ``/images/generations`` route, which OpenRouter did not, so the
picture package renders instead of falling back to its prompt.

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
MESH_BASE_URL = "https://api.meshapi.ai/v1"

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
    temperature: bool = True  # accepts a temperature parameter at all


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

# Mesh serves over 1,300 models. The allowlist stays deliberately small and every
# entry below was called and confirmed to return usable JSON, for the same reason
# the NVIDIA list is short: an unverified id is a failure that happens later, in
# front of the user, instead of now.
MESH_MODELS: tuple[ModelOption, ...] = (
    # The newest Anthropic models reject `temperature` outright with a 400 rather
    # than ignoring it, so it is declared here instead of being discovered in the
    # middle of a twenty case evaluation.
    ModelOption(
        "Mesh", "anthropic/claude-opus-5", "Mesh . Claude Opus 5 (best writing)",
        temperature=False,
    ),
    ModelOption(
        "Mesh", "anthropic/claude-sonnet-5", "Mesh . Claude Sonnet 5 (fast, strong)",
        temperature=False,
    ),
    ModelOption("Mesh", "anthropic/claude-haiku-4.5", "Mesh . Claude Haiku 4.5 (cheapest)"),
)


ALL_MODELS: tuple[ModelOption, ...] = NVIDIA_MODELS + MESH_MODELS


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


def sampling_options(model: str, attempt: int) -> dict[str, object]:
    """Temperature for the models that take one, nothing for the models that do not.

    Both attempts used to hardcode a temperature at the call site. Claude Opus 5
    and Sonnet 5 reject the parameter with a 400, which turned every case in a live
    run into "did not generate" and looked like a schema problem rather than a
    request problem. Sampling is a property of the model, so it is resolved here.
    """
    for option in ALL_MODELS:
        if option.model == model and not option.temperature:
            return {}
    return {"temperature": 0.4 if attempt == 1 else 0.1}


def has_mesh_key() -> bool:
    return bool(os.getenv("MESH_API_KEY", "").strip())


def has_nvidia_key() -> bool:
    return bool(os.getenv("NVIDIA_API_KEY", "").strip())


def default_model() -> ModelOption:
    """The model DEFAULT_MODEL or NVIDIA_MODEL names, or the first allowlisted one.

    An unknown value is ignored rather than fatal: the studio should still start,
    and the sidebar reports which model it actually resolved. DEFAULT_MODEL can name
    a Mesh model, which is how a machine chooses Claude as its writer; it is ignored
    when no Mesh key is present, so the app never defaults to something it cannot
    call.
    """
    requested = os.getenv("DEFAULT_MODEL", "").strip() or os.getenv("NVIDIA_MODEL", "").strip()
    if requested and has_mesh_key():
        for option in MESH_MODELS:
            if option.model == requested:
                return option
    for option in NVIDIA_MODELS:
        if option.model == requested:
            return option
    return NVIDIA_MODELS[0]


def available_models() -> list[dict[str, str]]:
    """Every model this machine is configured to call, the resolved default first."""
    options: list[ModelOption] = []
    preferred = default_model()
    options.append(preferred)
    options.extend(m for m in NVIDIA_MODELS if m.model != preferred.model)
    if has_mesh_key():
        options.extend(m for m in MESH_MODELS if m.model != preferred.model)
    return [asdict(option) for option in options]


def provider_for(model: str) -> str:
    """Which provider serves this model id.

    The evaluation harness used to hardcode "NVIDIA", which silently sent a Claude
    model id to the NIM endpoint. Deriving it from the allowlist means a model name
    is the only thing a caller has to get right.
    """
    for option in ALL_MODELS:
        if option.model == model:
            return option.provider
    raise ValueError("That model is not in the allowlist.")


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
            "provider": "Mesh API",
            "ready": has_mesh_key(),
            "detail": (
                "Claude models and picture rendering available."
                if has_mesh_key()
                else "Not configured. NVIDIA-only mode, which is fully supported."
            ),
            "required": False,
        },
    ]


def _live_ids(provider: str) -> set[str]:
    client = create_client(provider)
    return {model.id for model in client.models.list().data}


def check_live_catalogue() -> dict[str, object]:
    """Compare the allowlist against what each provider is serving right now.

    Models are retired on a schedule, and a retired one fails at generation time
    with a status the studio then has to explain. One catalogue call up front turns
    that into a sidebar line instead of a failed run.
    """
    if not has_nvidia_key():
        return {"ok": False, "detail": "No NVIDIA key configured.", "missing": []}

    checked: list[ModelOption] = list(NVIDIA_MODELS)
    missing: list[str] = []
    try:
        live = _live_ids("NVIDIA")
        missing.extend(m.model for m in NVIDIA_MODELS if m.model not in live)
        if has_mesh_key():
            checked.extend(MESH_MODELS)
            mesh_live = _live_ids("Mesh")
            missing.extend(m.model for m in MESH_MODELS if m.model not in mesh_live)
    except Exception:
        return {
            "ok": False,
            "detail": "Could not reach the provider catalogue. Check your connection.",
            "missing": [],
        }

    if missing:
        return {
            "ok": False,
            "detail": f"{len(missing)} allowlisted model(s) are no longer served.",
            "missing": missing,
        }
    return {
        "ok": True,
        "detail": f"All {len(checked)} allowlisted models are available.",
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

    if provider == "Mesh":
        api_key = os.getenv("MESH_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Mesh API is not configured.")
        return OpenAI(
            base_url=MESH_BASE_URL,
            api_key=api_key,
            timeout=REQUEST_TIMEOUT,
            max_retries=1,
        )

    raise ValueError("Unknown provider.")
