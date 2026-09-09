"""Structured output schemas.

These are the contract between the model and the rest of the studio. Every field
is independently editable in the UI, so the schema shape is also the shape of the
edit surface: splitting ``hashtags`` from ``hashtag_notes`` exists so a person can
change one hashtag without retyping the reasoning for the other four.

Bounds are deliberately generous where personas differ. One persona writes under
150 words in a strict 1-3-1; another writes 900 to 1,600 characters across five to
twelve paragraphs. A schema tight enough for one would reject the other, so
per-persona limits are enforced by the linter, which can explain itself, rather
than by Pydantic, which can only fail.
"""
from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, Field, field_validator, model_validator


class PostDraft(BaseModel):
    """A complete publishing package for one post."""

    hook: str = Field(min_length=1, max_length=500)
    body_lines: list[str] = Field(min_length=2, max_length=20)
    takeaway: str = Field(min_length=1, max_length=500)
    question: str = Field(default="", max_length=300)

    # These ceilings are deliberately looser than the publishing rules. Five
    # hashtags and three reply templates are what ships, and `generator.normalise`
    # trims to exactly that. Enforcing the publishing limit here instead throws an
    # otherwise-complete package away over a count, which is what the evaluation
    # harness caught: a grounded brief produced nothing twice because the model
    # wrote four reply templates rather than three.
    keywords: list[str] = Field(default_factory=list, max_length=12)
    keyword_rationale: str = Field(default="", max_length=800)
    hashtags: list[str] = Field(default_factory=list, max_length=10)
    hashtag_notes: list[str] = Field(default_factory=list, max_length=10)

    comment_a: str = Field(default="", max_length=800)
    comment_b: str = Field(default="", max_length=800)
    repost_caption: str = Field(default="", max_length=800)
    reply_templates: list[str] = Field(default_factory=list, max_length=8)
    publish_window: str = Field(default="", max_length=120)

    # There is deliberately no validator pairing hashtag_notes with hashtags. A
    # model that returns four notes for three tags has produced usable content with
    # a cosmetic mismatch, and rejecting it costs a whole retry to fix something
    # `generator.normalise` repairs for free.

    @field_validator("body_lines", mode="before")
    @classmethod
    def _drop_blank_paragraphs(cls, value):
        """Empty entries are the model drawing a blank line, not a paragraph.

        Section assembly already joins paragraphs with a blank line between them,
        so these carry no information and only push a good package over the length
        ceiling. The evaluation harness found a post rejected for having 25
        "paragraphs", 13 of which were empty strings.
        """
        if isinstance(value, list):
            return [v.strip() for v in value if isinstance(v, str) and v.strip()]
        return value


class CarouselSlide(BaseModel):
    headline: str = Field(min_length=1, max_length=90)
    body: str = Field(min_length=1, max_length=300)
    design_note: str = Field(min_length=1, max_length=300)
    momentum: str = Field(default="", max_length=60)


class CarouselDraft(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    slides: list[CarouselSlide] = Field(min_length=6, max_length=10)


class CalendarEntry(BaseModel):
    week: int = Field(ge=1, le=4)
    pillar: str = Field(min_length=1, max_length=120)
    content_format: str = Field(min_length=1, max_length=60)
    hook_angle: str = Field(min_length=1, max_length=400)
    target_asset: str = Field(min_length=1, max_length=200)
    cta: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=120)
    evidence: str = Field(default="", max_length=300)


class ContentCalendar(BaseModel):
    entries: list[CalendarEntry] = Field(min_length=16, max_length=16)

    @model_validator(mode="after")
    def _four_per_week(self):
        if Counter(e.week for e in self.entries) != Counter({1: 4, 2: 4, 3: 4, 4: 4}):
            raise ValueError("The calendar must contain four entries for each of four weeks.")
        return self

    @model_validator(mode="after")
    def _formats_rotate(self):
        """No week may be one format repeated four times.

        A calendar reading "carousel, carousel, carousel, carousel" is not a
        calendar, it is one idea with four dates on it. Every source engine
        prescribes a deliberate rotation, so this is enforced rather than asked for.
        """
        for week in (1, 2, 3, 4):
            formats = {
                e.content_format.strip().lower() for e in self.entries if e.week == week
            }
            if len(formats) < 2:
                raise ValueError(
                    f"Week {week} uses a single format for all four entries. Formats must "
                    "rotate across posts, carousels, stories, and proof-led content."
                )
        return self


class PicturePrompt(BaseModel):
    prompt: str = Field(min_length=40, max_length=1600)
    alt_text: str = Field(default="", max_length=300)


OUTPUT_SCHEMAS: dict[str, type[BaseModel]] = {
    "post": PostDraft,
    "carousel": CarouselDraft,
    "calendar": ContentCalendar,
    "picture": PicturePrompt,
}
