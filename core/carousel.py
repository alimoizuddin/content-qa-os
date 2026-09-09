"""Branded carousel rendering: real 1080x1350 slides, a PDF, and a ZIP.

The carousel is the part of this studio that has to be genuinely good, because a
carousel that is only slide copy in a text box is a note-to-self, not a deliverable.
Everything here runs locally with Pillow: no image service, no network, no remote
font. NVIDIA-only configuration produces the full asset set.

Layout notes worth knowing before editing:

- 1080x1350 is 4:5 portrait, the highest vertical occupancy on a phone, and it is
  what the source engines specify. LinkedIn applies the first page's dimensions to
  the whole document, so every slide is the same size, always.
- Type is auto-fitted rather than fixed. A headline the model wrote eleven words
  long shrinks to fit its box instead of running off the canvas, which is what the
  previous renderer did silently.
- The author lockup places the portrait to the LEFT of the name so the subject's
  gaze points into the copy rather than off the slide. That is the one piece of
  art direction every source engine agrees on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from core.fonts import ASSETS, load
from core.personas import PersonaSpec
from core.schemas import CarouselDraft

WIDTH, HEIGHT = 1080, 1350
MARGIN = 88
CONTENT_W = WIDTH - MARGIN * 2

PORTRAIT_DIR = ASSETS / "portraits"

Colour = str


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Greedy wrap. A single word longer than the box is left to overflow rather
    than hyphenated: it is a signal that the copy needs editing, not the layout."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if _measure(draw, trial, font)[0] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    sizes: range,
    weight: str,
    leading: float,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Largest size in ``sizes`` whose wrapped text fits the box.

    ``sizes`` is searched from the top down, so the first fit is the biggest one.
    If nothing fits, the smallest size is used and the caller gets text that is
    tight rather than text that is missing.
    """
    smallest = None
    for size in sorted(sizes, reverse=True):
        font = load(size, weight)
        lines = wrap(draw, text, font, max_width)
        line_height = int(size * leading)
        if smallest is None:
            smallest = (font, lines, line_height)
        if len(lines) * line_height <= max_height:
            return font, lines, line_height
    size = min(sizes)
    font = load(size, weight)
    return font, wrap(draw, text, font, max_width), int(size * leading)


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: Colour,
    line_height: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: Colour,
    tracking: int = 4,
) -> int:
    """Letter-spaced small caps. Pillow has no tracking, so characters are placed
    one at a time. Used only for eyebrows, which are short."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += _measure(draw, char, font)[0] + tracking
    return x


# ---------------------------------------------------------------------------
# Portraits
# ---------------------------------------------------------------------------


def portrait_slug(persona_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", persona_name.lower()).strip("-")


def portrait_path(persona_name: str) -> Path | None:
    """The stored portrait for this persona, if one has been uploaded.

    Portraits live in the app's own assets directory and are put there by the
    person using the studio. Nothing is ever read from the source corpus: a
    portrait is deliberate branding the user supplies, not private media the app
    goes looking for.
    """
    slug = portrait_slug(persona_name)
    for suffix in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = PORTRAIT_DIR / f"{slug}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def circular_portrait(path: Path, diameter: int, ring: Colour | None = None) -> Image.Image | None:
    """A portrait cropped to a circle, with an optional brand-coloured ring."""
    try:
        source = Image.open(path).convert("RGB")
    except Exception:
        return None

    side = min(source.size)
    left = (source.width - side) // 2
    top = int((source.height - side) * 0.35)  # bias upward: faces sit above centre
    top = max(0, min(top, source.height - side))
    source = source.crop((left, top, left + side, top + side)).resize(
        (diameter, diameter), Image.LANCZOS
    )

    mask = Image.new("L", (diameter * 4, diameter * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter * 4 - 1, diameter * 4 - 1), fill=255)
    mask = mask.resize((diameter, diameter), Image.LANCZOS)

    canvas_size = diameter + 16
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    if ring:
        ImageDraw.Draw(canvas).ellipse((0, 0, canvas_size - 1, canvas_size - 1), fill=ring)
    canvas.paste(source, (8, 8), mask)
    return canvas


# ---------------------------------------------------------------------------
# Slide chrome
# ---------------------------------------------------------------------------


@dataclass
class Theme:
    background: Colour
    panel: Colour
    ink: Colour
    accent: Colour
    accent_deep: Colour
    muted: Colour
    on_accent: Colour
    mode: str

    @classmethod
    def from_spec(cls, spec: PersonaSpec) -> "Theme":
        v = spec.visual
        return cls(
            background=v.background,
            panel=v.panel,
            ink=v.ink,
            accent=v.accent,
            accent_deep=v.accent_deep,
            muted=v.muted,
            on_accent=v.on_accent,
            mode=v.mode,
        )


def _base(theme: Theme, glow: bool = False) -> Image.Image:
    """A blank slide. ``glow`` adds a soft off-canvas accent bloom for cover and
    CTA slides, which is what stops a flat colour field reading as a template."""
    image = Image.new("RGB", (WIDTH, HEIGHT), theme.background)
    if not glow:
        return image

    layer = Image.new("RGB", (WIDTH, HEIGHT), theme.background)
    ImageDraw.Draw(layer).ellipse(
        (WIDTH - 260, -320, WIDTH + 520, 460), fill=theme.accent_deep
    )
    layer = layer.filter(ImageFilter.GaussianBlur(160))
    opacity = 0.30 if theme.mode == "dark" else 0.16
    return Image.blend(image, layer, opacity)


def _footer(
    draw: ImageDraw.ImageDraw,
    theme: Theme,
    index: int,
    total: int,
    momentum: str = "",
) -> None:
    if momentum:
        font = load(30, "semibold")
        draw.text((MARGIN, HEIGHT - 148), momentum, font=font, fill=theme.accent)

    # Progress rule: filled to the current slide, so the reader knows where they are.
    track_y = HEIGHT - 96
    track_w = 280
    draw.rounded_rectangle(
        (MARGIN, track_y, MARGIN + track_w, track_y + 6), radius=3, fill=theme.muted
    )
    filled = int(track_w * index / total)
    draw.rounded_rectangle(
        (MARGIN, track_y, MARGIN + filled, track_y + 6), radius=3, fill=theme.accent
    )

    number = load(34, "bold")
    label = f"{index:02d} / {total:02d}"
    width = _measure(draw, label, number)[0]
    draw.text((WIDTH - MARGIN - width, track_y - 16), label, font=number, fill=theme.muted)


def _eyebrow(draw: ImageDraw.ImageDraw, theme: Theme, text: str, colour: Colour) -> None:
    draw.rounded_rectangle((MARGIN, 118, MARGIN + 78, 124), radius=3, fill=theme.accent)
    draw_tracked(
        draw,
        text.upper()[:52],
        (MARGIN, 152),
        load(26, "semibold"),
        colour,
        tracking=5,
    )


def _author_lockup(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    theme: Theme,
    spec: PersonaSpec,
    y: int,
    diameter: int,
    name_size: int,
    tagline_size: int,
) -> None:
    """Portrait left, name and tagline right. The recognition anchor of the deck."""
    x = MARGIN
    path = portrait_path(spec.name)
    portrait = circular_portrait(path, diameter, theme.accent) if path else None

    if portrait is not None:
        image.paste(portrait, (x, y), portrait)
        text_x = x + portrait.width + 36
    else:
        # No portrait uploaded: an accent monogram disc keeps the lockup composed
        # instead of leaving a hole where a face should be.
        draw.ellipse((x, y, x + diameter, y + diameter), fill=theme.accent)
        initials = "".join(part[0] for part in spec.name.split()[:2]).upper()
        font = load(int(diameter * 0.42), "bold")
        w, h = _measure(draw, initials, font)
        draw.text(
            (x + (diameter - w) / 2, y + (diameter - h) / 2 - diameter * 0.08),
            initials,
            font=font,
            fill=theme.on_accent,
        )
        text_x = x + diameter + 36

    text_y = y + int(diameter * 0.22)
    draw.text((text_x, text_y), spec.name, font=load(name_size, "bold"), fill=theme.accent)
    tagline_font = load(tagline_size, "regular")
    lines = wrap(draw, spec.tagline or spec.title, tagline_font, WIDTH - text_x - MARGIN)
    draw_lines(
        draw,
        lines[:2],
        (text_x, text_y + int(name_size * 1.25)),
        tagline_font,
        theme.ink,
        int(tagline_size * 1.3),
    )


# ---------------------------------------------------------------------------
# Slide types
# ---------------------------------------------------------------------------


def render_cover(spec: PersonaSpec, theme: Theme, title: str, slide, total: int) -> Image.Image:
    """Cover slide.

    Laid out bottom-up from the author badge so a long headline can never run into
    the lockup. Whatever vertical space is left after the headline is what the
    supporting line gets, and if that is not enough the line is dropped rather
    than overlapped.
    """
    image = _base(theme, glow=True)
    draw = ImageDraw.Draw(image)

    _eyebrow(draw, theme, spec.title, theme.accent)

    badge_top = HEIGHT - 330
    content_bottom = badge_top - 60

    font, lines, lh = fit(
        draw, slide.headline, CONTENT_W, 470, range(54, 114, 2), "bold", 1.12
    )
    end = draw_lines(draw, lines, (MARGIN, 320), font, theme.ink, lh)

    remaining = content_bottom - (end + 90)
    if slide.body and remaining >= 60:
        body_font, body_lines, body_lh = fit(
            draw, slide.body, CONTENT_W - 40, remaining, range(28, 42, 1), "regular", 1.42
        )
        draw.rounded_rectangle(
            (MARGIN, end + 46, MARGIN + 64, end + 52), radius=3, fill=theme.accent
        )
        draw_lines(draw, body_lines, (MARGIN, end + 86), body_font, theme.muted, body_lh)

    _author_lockup(image, draw, theme, spec, badge_top, 104, 32, 24)
    _footer(draw, theme, 1, total, slide.momentum)
    return image


def render_content(
    spec: PersonaSpec,
    theme: Theme,
    title: str,
    slide,
    index: int,
    total: int,
    emphasis: bool = False,
) -> Image.Image:
    image = _base(theme)
    draw = ImageDraw.Draw(image)

    _eyebrow(draw, theme, title, theme.muted)

    if emphasis:
        # The recap slide gets a panel: it is the one built to be screenshotted.
        # On a dark ground a fill alone is nearly invisible, so it also gets a hairline.
        draw.rounded_rectangle(
            (MARGIN - 28, 290, WIDTH - MARGIN + 28, HEIGHT - 230),
            radius=28,
            fill=theme.panel,
            outline=theme.accent if theme.mode == "dark" else None,
            width=2 if theme.mode == "dark" else 0,
        )
        headline_ink = theme.on_accent if theme.mode == "light" else theme.accent
        body_ink = theme.on_accent if theme.mode == "light" else theme.ink
        inset = 24
    else:
        headline_ink = theme.ink
        body_ink = theme.muted
        inset = 0

    font, lines, lh = fit(
        draw, slide.headline, CONTENT_W - inset * 2, 300, range(46, 84, 2), "bold", 1.14
    )
    top = 350 + inset
    end = draw_lines(draw, lines, (MARGIN + inset, top), font, headline_ink, lh)

    accent_rule = theme.accent if not emphasis else headline_ink
    draw.rounded_rectangle(
        (MARGIN + inset, end + 40, MARGIN + inset + 96, end + 46), radius=3, fill=accent_rule
    )

    body_font, body_lines, body_lh = fit(
        draw,
        slide.body,
        CONTENT_W - inset * 2,
        HEIGHT - (end + 120) - 240,
        range(32, 48, 1),
        "regular",
        1.45,
    )
    draw_lines(draw, body_lines, (MARGIN + inset, end + 88), body_font, body_ink, body_lh)

    _footer(draw, theme, index, total, slide.momentum)
    return image


def render_cta(spec: PersonaSpec, theme: Theme, title: str, slide, total: int) -> Image.Image:
    image = _base(theme, glow=True)
    draw = ImageDraw.Draw(image)

    _eyebrow(draw, theme, title, theme.muted)

    font, lines, lh = fit(
        draw, slide.headline, CONTENT_W, 300, range(50, 92, 2), "bold", 1.14
    )
    end = draw_lines(draw, lines, (MARGIN, 300), font, theme.ink, lh)

    body_font, body_lines, body_lh = fit(
        draw, slide.body, CONTENT_W, 240, range(32, 46, 1), "regular", 1.45
    )
    draw_lines(draw, body_lines, (MARGIN, end + 56), body_font, theme.muted, body_lh)

    draw.rounded_rectangle((MARGIN, HEIGHT - 452, WIDTH - MARGIN, HEIGHT - 448), radius=2, fill=theme.accent)
    _author_lockup(image, draw, theme, spec, HEIGHT - 392, 200, 46, 30)
    _footer(draw, theme, total, total)
    return image


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_slides(spec: PersonaSpec, carousel: CarouselDraft) -> list[Image.Image]:
    theme = Theme.from_spec(spec)
    total = len(carousel.slides)
    images: list[Image.Image] = []
    for index, slide in enumerate(carousel.slides, start=1):
        if index == 1:
            images.append(render_cover(spec, theme, carousel.title, slide, total))
        elif index == total:
            images.append(render_cta(spec, theme, carousel.title, slide, total))
        else:
            images.append(
                render_content(
                    spec,
                    theme,
                    carousel.title,
                    slide,
                    index,
                    total,
                    emphasis=index == total - 1,
                )
            )
    return images


def build_carousel_assets(spec: PersonaSpec, carousel: CarouselDraft) -> dict[str, object]:
    """PNG bytes per slide, one PDF, and a ZIP containing both.

    The PDF is written from the rendered images, which is exactly what LinkedIn
    document posts display. That keeps one typography path instead of two, so the
    PDF cannot drift from the preview.
    """
    images = render_slides(spec, carousel)

    pngs: list[bytes] = []
    for image in images:
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        pngs.append(buffer.getvalue())

    pdf = BytesIO()
    images[0].save(
        pdf, format="PDF", save_all=True, append_images=images[1:], resolution=150.0
    )

    archive = BytesIO()
    slug = portrait_slug(spec.name)
    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for index, png in enumerate(pngs, start=1):
            zip_file.writestr(f"{slug}-slide-{index:02d}.png", png)
        zip_file.writestr(f"{slug}-carousel.pdf", pdf.getvalue())
        zip_file.writestr(
            "slide-copy.txt",
            "\n\n".join(
                f"Slide {i}\nHeadline: {s.headline}\nBody: {s.body}\n"
                f"Design: {s.design_note}\nMomentum: {s.momentum or '(none)'}"
                for i, s in enumerate(carousel.slides, start=1)
            ),
        )

    return {
        "slides": pngs,
        "pdf": pdf.getvalue(),
        "zip": archive.getvalue(),
        "count": len(pngs),
    }
