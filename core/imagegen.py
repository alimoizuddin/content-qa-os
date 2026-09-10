"""Optional raster image generation for the picture package.

The picture package always produces something useful: a detailed, safe
art-direction prompt. Rendering that prompt into an actual image is optional and
requires a Mesh API key, because NVIDIA NIM's text endpoint does not return
rasters.

This module has now been wrong twice, in the same way, and the history is worth
keeping. The first implementation posted to ``https://openrouter.ai/api/v1/images``,
a route OpenRouter does not serve, so the feature had never once produced an image.
The second went through OpenRouter chat completions with image modalities, which
is a real route but a fiddly one: the raster arrives buried in a data URI on a
non-standard message field. Mesh serves a plain OpenAI-compatible
``/images/generations`` that returns base64, so the third version is the boring
one, and boring is the point.

Two rules this module will not break: it never claims a prompt is a generated
image, and it never fails the surrounding generation. A missing key, a timeout, a
refusal, and an unexpected payload shape all land in the same place, which is
"here is your prompt, here is why there is no picture".
"""
from __future__ import annotations

import base64
import os
from typing import Any

from dotenv import load_dotenv

from core.personas import PersonaSpec

# The key checks below read the environment directly, so this module has to load
# the .env itself. It previously relied on core.providers having been imported
# first, which is true in the app and false in a bare unit test.
load_dotenv()

IMAGE_TIMEOUT = 120.0

STATUS_PROMPT_ONLY = "prompt_only"
STATUS_RENDERED = "rendered"
STATUS_FAILED = "failed"

# Confirmed against the live Mesh catalogue. Overridable with MESH_IMAGE_MODEL for
# anyone who wants a different look, but the default has to work out of the box.
DEFAULT_IMAGE_MODEL = "black-forest-labs/flux.1-schnell"

# LinkedIn's portrait slot is 4:5. Providers accept a fixed set of sizes rather
# than arbitrary pixels, so this is the nearest 4:5 that is widely supported, and
# a provider that rejects it gets a second attempt with no size at all.
IMAGE_SIZE = "1024x1280"

SAFETY_SUFFIX = (
    "No text overlays, no logos, no identifiable people, no faces, no charts of "
    "invented data, no medical or clinical imagery, no private information."
)


def image_model() -> str:
    return os.getenv("MESH_IMAGE_MODEL", "").strip() or DEFAULT_IMAGE_MODEL


def image_provider_configured() -> bool:
    return bool(os.getenv("MESH_API_KEY", "").strip())


def art_direction(spec: PersonaSpec, prompt: str) -> str:
    """The prompt that would be sent, with the persona palette and safety rules bound in.

    Returned to the UI whether or not an image is generated, because the prompt is
    itself a deliverable: it goes to a designer, or into a tool of the user's choice.
    """
    v = spec.visual
    return (
        f"Editorial LinkedIn visual, 4:5 portrait, 1080 x 1350. {prompt.strip()[:1200]} "
        f"Palette: background {v.background}, accent {v.accent}, type {v.ink}. "
        f"Composition: generous negative space, one tangible subject, soft directional "
        f"light. Sophisticated and editorial, never stock-photo corporate. {SAFETY_SUFFIX}"
    )


def _extract_image(payload: Any) -> bytes | None:
    """Pull raster bytes out of an images response.

    ``b64_json`` is the documented field. Some gateways return a data URI in
    ``url`` instead, so that is handled too rather than reported as a failure.
    """
    entries = getattr(payload, "data", None)
    if entries is None and isinstance(payload, dict):
        entries = payload.get("data")
    if not entries:
        return None

    entry = entries[0]
    if isinstance(entry, dict):
        encoded = entry.get("b64_json")
        url = entry.get("url")
    else:
        encoded = getattr(entry, "b64_json", None)
        url = getattr(entry, "url", None)

    if not encoded and isinstance(url, str) and "base64," in url:
        encoded = url.split("base64,", 1)[1]
    if not isinstance(encoded, str) or not encoded:
        return None

    try:
        return base64.b64decode(encoded)
    except Exception:
        return None


def create_picture(spec: PersonaSpec, prompt: str) -> dict[str, object]:
    """Return the art-direction prompt, and an image when one can be produced."""
    safe_prompt = art_direction(spec, prompt)

    if not image_provider_configured():
        return {
            "prompt": safe_prompt,
            "image_bytes": None,
            "image_status": STATUS_PROMPT_ONLY,
            "detail": (
                "No image provider configured. Add MESH_API_KEY to your local .env "
                "file to render this prompt, or take the prompt to the image tool of "
                "your choice. The prompt is the deliverable either way."
            ),
        }

    # Imported here so a missing Mesh configuration never affects import time.
    from core.providers import create_client

    try:
        client = create_client("Mesh")
        model = image_model()
        try:
            response = client.images.generate(
                model=model, prompt=safe_prompt, n=1, size=IMAGE_SIZE
            )
        except Exception:
            # A provider that rejects the size still renders happily without it, and
            # a square picture is a better outcome than no picture.
            response = client.images.generate(model=model, prompt=safe_prompt, n=1)
        data = _extract_image(response)
    except Exception:
        return {
            "prompt": safe_prompt,
            "image_bytes": None,
            "image_status": STATUS_FAILED,
            "detail": (
                "The image provider did not return an image. The prompt below is "
                "unaffected and still usable."
            ),
        }

    if not data:
        return {
            "prompt": safe_prompt,
            "image_bytes": None,
            "image_status": STATUS_FAILED,
            "detail": (
                "The image provider responded without an image, which usually means the "
                "configured model does not support image output."
            ),
        }

    return {
        "prompt": safe_prompt,
        "image_bytes": data,
        "image_status": STATUS_RENDERED,
        "detail": f"Rendered by {image_model()} through Mesh API.",
    }
