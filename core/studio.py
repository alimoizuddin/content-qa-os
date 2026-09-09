"""Section formatting, QA orchestration, and the approval gate.

The unit this module works in is a *section*: one independently editable block of
text with a stable key, a human label, and a note on what it is for. The UI renders
one editable field per section, QA runs per section, and history stores sections.
That is what makes "edit one hashtag without retyping the reasoning" possible, and
it is what lets the linter apply the body-link rule to the post and not to the
comment where a link belongs.

The approval gate re-runs the full audit over whatever text is actually in the
fields at the moment approve is pressed, not over what the model originally
produced. Anything else would let a person generate a clean package, paste a
medical claim into the box, and approve it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.auditor import audit_content, blocking
from core.linter import lint_text
from core.personas import OPEN_SLOT, PersonaSpec
from core.schemas import CarouselDraft, ContentCalendar, PicturePrompt, PostDraft


@dataclass(frozen=True)
class Section:
    key: str
    label: str
    text: str
    help: str = ""
    multiline: bool = True
    copyable: bool = False  # the blocks meant to be pasted straight into LinkedIn


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------


def post_sections(spec: PersonaSpec, data: dict[str, Any]) -> list[Section]:
    post = PostDraft.model_validate(data)
    body = "\n\n".join([post.hook, *post.body_lines, post.takeaway])
    if post.question:
        body = f"{body}\n\n{post.question}"

    tags = " ".join(post.hashtags)
    notes = "\n".join(
        f"{tag} : {note}" for tag, note in zip(post.hashtags, post.hashtag_notes)
    ) or "\n".join(post.hashtag_notes)

    return [
        Section(
            "post",
            "LinkedIn post",
            body,
            "The clean copy-paste block. Hashtags are appended on publish, so they are "
            "kept separate here and editable on their own.",
            copyable=True,
        ),
        Section("hashtags", "Hashtags", tags, spec.hashtag_rule, multiline=False, copyable=True),
        Section(
            "hashtag_notes",
            "Why each hashtag",
            notes,
            "Working notes. These never go into the post itself.",
        ),
        Section(
            "keywords",
            "Keyword strategy",
            " . ".join(post.keywords),
            "Terms this piece carries so the ranking model keeps classifying this "
            "account in one lane. Consistency builds topical authority. It is not a "
            "reach lever and it guarantees nothing.",
            multiline=False,
        ),
        Section(
            "keyword_rationale",
            "Keyword reasoning",
            post.keyword_rationale,
            "Why these terms fit this piece and this audience.",
        ),
        Section(
            "comment_a",
            "First comment (golden hour)",
            post.comment_a,
            "Posted by the author within about five minutes. This is where a link "
            "belongs, never the post body.",
            copyable=True,
        ),
        Section(
            "comment_b",
            spec.surfaces.second_comment_label,
            post.comment_b,
            spec.surfaces.second_comment_rule,
            copyable=True,
        ),
        Section(
            "repost_caption",
            spec.surfaces.repost_label,
            post.repost_caption,
            spec.surfaces.repost_rule,
            copyable=True,
        ),
        Section(
            "reply_templates",
            "Reply templates",
            "\n".join(post.reply_templates),
            "Three replies to adapt fast during the golden hour. Reply speed and reply "
            "substance are both ranking inputs.",
        ),
        Section(
            "publish_window",
            "Recommended publishing window",
            post.publish_window or spec.publish.window,
            f"{spec.name} publishes on {', '.join(spec.publish.days)}. "
            f"{spec.publish.notes}",
            multiline=False,
        ),
    ]


# ---------------------------------------------------------------------------
# Carousel, calendar, picture
# ---------------------------------------------------------------------------


def carousel_sections(spec: PersonaSpec, data: dict[str, Any]) -> list[Section]:
    carousel = CarouselDraft.model_validate(data)
    sections = [
        Section("carousel_title", "Carousel title", carousel.title,
                "Shown as a header above the document on LinkedIn. Benefit led, four to "
                "seven words.", multiline=False)
    ]
    for index, slide in enumerate(carousel.slides, start=1):
        sections.append(
            Section(
                f"slide_{index}",
                f"Slide {index}",
                f"{slide.headline}\n{slide.body}",
                f"Line one is the headline, the rest is body copy. "
                f"Design direction: {slide.design_note}"
                + (f" Momentum: {slide.momentum}" if slide.momentum else ""),
            )
        )
    return sections


def carousel_from_sections(data: dict[str, Any], edited: dict[str, str]) -> CarouselDraft:
    """Rebuild a carousel from edited text so the render reflects the edits."""
    carousel = CarouselDraft.model_validate(data)
    slides = []
    for index, slide in enumerate(carousel.slides, start=1):
        raw = edited.get(f"slide_{index}", f"{slide.headline}\n{slide.body}")
        head, _, body = raw.partition("\n")
        slides.append(
            slide.model_copy(
                update={
                    "headline": head.strip() or slide.headline,
                    "body": body.strip() or slide.body,
                }
            )
        )
    return carousel.model_copy(
        update={"title": edited.get("carousel_title", carousel.title).strip() or carousel.title,
                "slides": slides}
    )


def calendar_sections(spec: PersonaSpec, data: dict[str, Any]) -> list[Section]:
    calendar = ContentCalendar.model_validate(data)
    sections = []
    for week in (1, 2, 3, 4):
        entries = [e for e in calendar.entries if e.week == week]
        block = "\n\n".join(
            "\n".join(
                (
                    f"{e.pillar} . {e.content_format} . {e.goal}",
                    f"Hook: {e.hook_angle}",
                    f"Anchored to: {e.target_asset}",
                    f"CTA: {e.cta}",
                    f"Evidence needed: {e.evidence or 'none beyond the anchor'}",
                )
            )
            for e in entries
        )
        sections.append(
            Section(f"week_{week}", f"Week {week}", block, "Four entries. Formats rotate.")
        )
    return sections


def picture_sections(spec: PersonaSpec, data: dict[str, Any]) -> list[Section]:
    picture = PicturePrompt.model_validate(data)
    sections = [
        Section("picture_prompt", "Art direction prompt", picture.prompt,
                "Hand this to an image tool or a designer. It is a deliverable on its own.")
    ]
    if picture.alt_text:
        sections.append(
            Section("picture_alt", "Alt text", picture.alt_text,
                    "Describes the image for a screen reader.", multiline=False)
        )
    return sections


SECTION_BUILDERS = {
    "post": post_sections,
    "carousel": carousel_sections,
    "calendar": calendar_sections,
    "picture": picture_sections,
}


def build_sections(spec: PersonaSpec, output_type: str, data: dict[str, Any]) -> list[Section]:
    try:
        return SECTION_BUILDERS[output_type](spec, data)
    except KeyError:
        raise ValueError(f"Unknown output type: {output_type!r}") from None


def delivery_text(sections: list[Section]) -> str:
    """The whole package as one labelled block, for copying out in one go."""
    return "\n\n".join(f"{s.label.upper()}\n{s.text}" for s in sections if s.text.strip())


# ---------------------------------------------------------------------------
# QA and approval
# ---------------------------------------------------------------------------


def run_qa(spec: PersonaSpec, sections: dict[str, str], proof: str = "") -> dict[str, Any]:
    """Lint then audit every section. Returns cleaned text and both flag sets."""
    cleaned: dict[str, str] = {}
    lint_flags: list[str] = []
    audit_flags: list[str] = []

    for key, text in sections.items():
        linted = lint_text(text, spec, section=key)
        audited = audit_content(spec, linted["cleaned_text"], proof=proof, section=key)
        cleaned[key] = audited["audited_text"]
        lint_flags.extend(f"{key}: {flag}" for flag in linted["flags"])
        audit_flags.extend(f"{key}: {flag}" for flag in audited["flags"])

    return {
        "outputs": cleaned,
        "lint_flags": lint_flags,
        "audit_flags": audit_flags,
        "blocking_flags": [f for f in audit_flags if not f.split(": ", 1)[-1].startswith("REVIEW")],
    }


def approve_package(qa_result: dict[str, Any]) -> dict[str, Any]:
    """The gate. Every reason it refuses is returned, not just the first."""
    reasons: list[str] = []

    open_slots = [k for k, v in qa_result["outputs"].items() if OPEN_SLOT in v]
    if open_slots:
        reasons.append(
            f"{OPEN_SLOT} still present in: {', '.join(open_slots)}. Supply the real "
            "evidence or remove the claim."
        )

    blocked = qa_result.get("blocking_flags") or blocking(qa_result["audit_flags"])
    if blocked:
        reasons.append(f"{len(blocked)} blocking finding(s) must be resolved.")

    return {
        "approved": not reasons,
        "reason": " ".join(reasons),
        "reasons": reasons,
        "blocking_flags": blocked,
    }
