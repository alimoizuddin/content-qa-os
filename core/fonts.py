"""Font resolution for the slide renderer.

The previous renderer hardcoded ``C:/Windows/Fonts/segoeui.ttf`` and fell back to
Pillow's built-in bitmap face when that path did not exist. CI runs on Linux, so
every carousel test passed against a fallback font and real typography was never
exercised. Slides that looked designed locally rendered as tiny bitmap text in the
one place that was supposed to be checking them.

Inter is vendored under ``assets/fonts/`` for that reason: one variable font file,
Open Font Licence, identical output on every machine. Weights come from the
variation axes, so there is one file rather than four. If the vendored file is
missing the resolver still degrades gracefully, but ``vendored_font_available()``
lets the app say so out loud instead of quietly shipping worse slides.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT_DIR = ASSETS / "fonts"
VENDORED = FONT_DIR / "Inter.ttf"

# Weight names as Inter exposes them, mapped to the numeric axis value used when
# named instances are unavailable.
WEIGHTS: dict[str, int] = {
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
    "black": 900,
}

# Searched in order when the vendored file is absent. Each entry is a family that
# exists by default on that platform.
_SYSTEM_CANDIDATES: tuple[Path, ...] = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
)


def vendored_font_available() -> bool:
    return VENDORED.is_file()


def _font_path() -> Path | None:
    if VENDORED.is_file():
        return VENDORED
    for candidate in _SYSTEM_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=256)
def load(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    """A font at this size and weight.

    Cached, because the previous renderer re-read the TTF from disk once per line
    of text and it showed.
    """
    path = _font_path()
    if path is None:
        return ImageFont.load_default(size=size)

    try:
        font = ImageFont.truetype(str(path), size=size)
    except OSError:
        return ImageFont.load_default(size=size)

    axis = WEIGHTS.get(weight, 400)
    if axis == 400:
        return font

    # Variable font: ask for the named instance, then fall back to the raw axis,
    # then accept regular weight rather than failing a render over a font detail.
    try:
        font.set_variation_by_name(weight.capitalize())
        return font
    except Exception:
        pass
    try:
        axes = font.get_variation_axes()
        values = []
        for spec in axes:
            name = (spec.get("name") or b"").decode(errors="ignore").lower() if isinstance(spec.get("name"), bytes) else str(spec.get("name", "")).lower()
            if "weight" in name:
                values.append(axis)
            else:
                values.append(spec.get("default", spec.get("minimum", 0)))
        font.set_variation_by_axes(values)
    except Exception:
        pass
    return font
