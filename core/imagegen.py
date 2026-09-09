"""Optional raster image generation for the picture package.

The picture package always produces something useful: a detailed, safe
art-direction prompt. Rendering that prompt into an actual image is optional and
requires an OpenRouter key plus an image-capable model, because NVIDIA NIM's text
endpoint does not return rasters.

The previous implementation posted to ``https://openrouter.ai/api/v1/images``,
which is not a route OpenRouter serves, so the feature had never once produced an
image; it fell through to the prompt every time and the tests only ever exercised
the fallback. Image output on OpenRouter comes back through chat completions with
image modalities requested, which is what this does.

Two rules this module will not break: it never claims a prompt is a generated
image, and it never fails the surrounding generation. A missing key, a timeout, a
refusal, and an unexpected payload shape all land in the same place, which is
"here is your prompt, here is why there is no picture".
"""
from __future__ import annotations

import base64
import os
from typing import Any

from core.personas import PersonaSpec

IMAGE_TIMEOUT = 60.0

STATUS_PROMPT_ONLY = "prompt_only"
STATUS_RENDERED = "rendered"
STATUS_FAILED = "failed"

SAFETY_SUFFIX = (
    "No text overlays, no logos, no identifiable people, no faces, no charts of "
    "invented data, no medical or clinical imagery, no private information."
)


def image_provider_configured() -> bool:
    return bool(
        os.getenv("OPENROUTER_API_KEY", "").strip()
        and os.getenv("OPENROUTER_IMAGE_MODEL", "").strip()
    )


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


def _extract_image(message: Any) -> bytes | None:
    """Pull raster bytes out of an OpenRouter chat response.

    The shape is `message.images[i].image_url.url` holding a data URI. Both dict
    and object forms show up depending on SDK version, so both are handled.
    """
    images = getattr(message, "images", None)
    if images is None and isinstance(message, dict):
        images = message.get("images")
    if not images:
        return None

    entry = images[0]
    url = None
    if isinstance(entry, dict):
        url = (entry.get("image_url") or {}).get("url")
    else:
        image_url = getattr(entry, "image_url", None)
        url = getattr(image_url, "url", None)
    if not isinstance(url, str) or "base64," not in url:
        return None

    try:
        return base64.b64decode(url.split("base64,", 1)[1])
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
                "No image provider configured. Set OPENROUTER_API_KEY and "
                "OPENROUTER_IMAGE_MODEL to render this prompt, or take the prompt to the "
                "image tool of your choice. The prompt is the deliverable either way."
            ),
        }

    # Imported here so a missing OpenRouter configuration never affects import time.
    from openai import OpenAI

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"].strip(),
            timeout=IMAGE_TIMEOUT,
            max_retries=0,
        )
        response = client.chat.completions.create(
            model=os.environ["OPENROUTER_IMAGE_MODEL"].strip(),
            messages=[{"role": "user", "content": safe_prompt}],
            extra_body={"modalities": ["image", "text"]},
        )
        data = _extract_image(response.choices[0].message)
    except Exception:
        data = None
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
        "detail": "Rendered by the configured image provider.",
    }
