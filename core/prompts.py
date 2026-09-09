"""Prompt construction, one builder per output type.

This used to live inside the generator as a dict of format strings, which meant
the persona rules and the schema instructions were assembled in the same place the
HTTP call happened. Splitting it out is what makes the prompts testable without a
provider: every function here is pure, takes a spec and a brief, and returns text.

The instructions are written from the source engine documents, so they say things
like "slide 2 must stand alone as a second cover" rather than "write good slides".
Specific instructions are the difference between a model that fills a shape and a
model that follows a method.
"""
from __future__ import annotations

import json

from pydantic import BaseModel

from core.brief import ContentBrief
from core.personas import OPEN_SLOT, PersonaSpec, voice_brief

# Compact key layouts. A small model follows an example layout far more reliably
# than it follows a JSON Schema, so it gets both: the shape first, the schema after.
LAYOUTS: dict[str, str] = {
    "post": (
        '{"hook":"...","body_lines":["...","...","..."],"takeaway":"...","question":"...",'
        '"keywords":["..."],"keyword_rationale":"...","hashtags":["#..."],'
        '"hashtag_notes":["..."],"comment_a":"...","comment_b":"...",'
        '"repost_caption":"...","reply_templates":["...","...","..."],'
        '"publish_window":"..."}'
    ),
    "carousel": (
        '{"title":"...","slides":[{"headline":"...","body":"...",'
        '"design_note":"...","momentum":"..."}]}'
    ),
    "calendar": (
        '{"entries":[{"week":1,"pillar":"...","content_format":"...","hook_angle":"...",'
        '"target_asset":"...","cta":"...","goal":"...","evidence":"..."}]}'
    ),
    "picture": '{"prompt":"...","alt_text":"..."}',
}


def _bullets(items, bullet: str = "- ") -> str:
    return "\n".join(f"{bullet}{item}" for item in items)


def _numbered(items) -> str:
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))


# ---------------------------------------------------------------------------
# Per output type
# ---------------------------------------------------------------------------


def post_instruction(spec: PersonaSpec, brief: ContentBrief) -> str:
    surfaces = spec.surfaces
    if surfaces.count > 1:
        second = (
            f"comment_b is the {surfaces.second_surface} commenting on the post. "
            f"{surfaces.second_comment_rule} "
            f"repost_caption is the {surfaces.second_surface} reposting. {surfaces.repost_rule}"
        )
    else:
        second = (
            f"This person runs a single LinkedIn surface, so there is no second account "
            f"to comment from and inventing one would read as staged. comment_b is "
            f"{surfaces.second_comment_label.lower()}: {surfaces.second_comment_rule} "
            f"repost_caption is {surfaces.repost_label.lower()}: {surfaces.repost_rule}"
        )

    return "\n".join(
        (
            "Write one complete LinkedIn post package.",
            "",
            "hook: the opening lines. " + spec.post.hook_rule,
            "body_lines: the body, one array entry per paragraph. " + spec.post.paragraph_rule,
            "takeaway: the closing line that lands the idea.",
            "question: the closing question. " + spec.post.close_rule,
            "",
            "keywords: three to six terms from this person's keyword bank that genuinely "
            "belong in this piece. Pick the ones the brief actually supports, not the ones "
            "that sound impressive. The available bank is:",
            _bullets(f"{tier}: {', '.join(terms)}" for tier, terms in spec.keyword_tiers.items()),
            "",
            "keyword_rationale: two or three sentences on why these terms fit this piece and "
            "this audience. Explain the discoverability reasoning: consistent topical "
            "vocabulary is how the ranking model learns who the post is for. Never claim "
            "keywords or hashtags cause reach, and never promise virality.",
            "",
            f"hashtags: {spec.hashtag_rule} Draw from these, or propose better ones for this "
            "specific topic. Generic tags are worse than none.",
            f"Broad: {', '.join(spec.hashtags_broad)}",
            f"Niche: {', '.join(spec.hashtags_niche)}",
            f"Theirs: {', '.join(spec.hashtags_owned)}",
            f"Never: {', '.join(spec.hashtags_banned)}",
            "hashtag_notes: exactly one short line per hashtag saying why that tag fits this "
            "post and this audience. Same order as hashtags.",
            "",
            "comment_a: the golden-hour comment, posted by the author within about five "
            "minutes of publishing. Either the transactional link or CTA, which never goes in "
            "the post body, or one real detail the post did not carry. Two to four sentences, "
            "ending on an easy question.",
            f"comment_b: {second}",
            "",
            "reply_templates: exactly three short replies for the golden hour. One that "
            "redirects a bare compliment into a question, one that answers a real question "
            "with a specific, and one that concedes the valid half of a disagreement and "
            "holds the position.",
            f"publish_window: {spec.publish.window}.",
        )
    )


def carousel_instruction(spec: PersonaSpec, brief: ContentBrief) -> str:
    c = spec.carousel
    return "\n".join(
        (
            f"Design a {c.default_slides} slide carousel. Between {c.min_slides} and "
            f"{c.max_slides} is acceptable if the content genuinely needs it. Never pad.",
            "",
            "The post and the carousel are companion pieces, never duplicates. The post "
            "carries the feeling and the hook. The carousel teaches the framework or the "
            "process. If a slide restates the post, replace it.",
            "",
            "Follow this arc, one slide per beat:",
            _numbered(c.arc),
            "",
            "Every slide needs four things:",
            "- headline: three to seven words. Billboard type. It is read at arm's length on "
            "a five-inch screen, so it must work with no other context.",
            "- body: one or two short sentences, phone readable. Never a paragraph.",
            "- design_note: a specific visual direction for this slide. Name a tangible "
            "object, a composition, or a diagram. 'A clean layout' is not a direction. 'A "
            "single frayed rope against negative space, shot from above' is.",
            "- momentum: a short trailing phrase that pulls the reader to the next slide, "
            f"for example {', '.join(repr(m) for m in c.momentum_examples[:2])}. Leave it "
            "empty on the final slide.",
            "",
            "Slide rules:",
            _bullets(c.slide_rules),
            "",
            f"Any figure not in the verified fact list, and not supplied in the brief, is "
            f"written as {OPEN_SLOT}. A slide with an honest gap is fine. A slide with an "
            "invented number is not.",
        )
    )


def calendar_instruction(spec: PersonaSpec, brief: ContentBrief) -> str:
    pillars = _bullets(
        f"{p.key} {p.name} (about {int(p.weight * 100)}% of the block): {p.description}"
        for p in spec.pillars
    )
    return "\n".join(
        (
            "Build a four-week content calendar. Exactly sixteen entries, exactly four per "
            "week, weeks numbered 1 to 4.",
            "",
            "Content pillars for this person, and roughly how much of the block each should "
            "carry:",
            pillars,
            "",
            "Every entry needs:",
            "- week: 1, 2, 3, or 4.",
            "- pillar: one of the pillars above, named exactly.",
            "- content_format: one of post, carousel, framework, proof, photo, or video. "
            "Formats must rotate intelligently. No week may use the same format four times, "
            "and the block as a whole should mix teaching formats with proof-led ones.",
            "- hook_angle: the specific angle, written as a line that could open the post.",
            "- target_asset: the real project, experience, or artifact this entry is anchored "
            f"to. If no real asset exists for an idea, write {OPEN_SLOT} here rather than "
            "inventing a project.",
            "- cta: the single ask for that post. One ask, never a stack of them.",
            "- goal: reach, DMs and leads, both, authority, or save target.",
            f"- evidence: the specific proof needed before this entry can be written. If the "
            f"proof does not exist yet, write {OPEN_SLOT}.",
            "",
            "Ground every entry in the brief and in this person's verified facts. A calendar "
            "of plausible topics they have no material for is worse than a shorter honest one, "
            "so where material is thin, say so through an open slot rather than inventing a "
            "project.",
        )
    )


def picture_instruction(spec: PersonaSpec, brief: ContentBrief) -> str:
    v = spec.visual
    return "\n".join(
        (
            "Write one detailed art-direction prompt for a single editorial image that "
            "accompanies this content.",
            "",
            "prompt: one flowing paragraph, no bullet points inside it. It must name a "
            "tangible real-world object as the metaphor, describe the composition and the "
            "negative space, describe the lighting, and state the palette. Use this palette "
            f"exactly: background {v.background}, accent {v.accent}, type {v.ink}. Aspect "
            "ratio 4:5. Sophisticated and editorial, never stock-photo corporate, never "
            "cartoonish.",
            "",
            "The image is for objects, scenes, and materials only. Never a human face, never "
            "an identifiable person, never text overlays, never a logo, never a chart of "
            "invented data, never anything implying a medical or clinical outcome.",
            "",
            "alt_text: one sentence describing the image for a screen reader.",
        )
    )


INSTRUCTION_BUILDERS = {
    "post": post_instruction,
    "carousel": carousel_instruction,
    "calendar": calendar_instruction,
    "picture": picture_instruction,
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_messages(
    spec: PersonaSpec,
    brief: ContentBrief,
    output_type: str,
    schema: type[BaseModel],
    corrective: bool = False,
) -> list[dict[str, str]]:
    """The two messages sent to the provider.

    The persona and the method go in the system message; the brief goes in the
    user message. Keeping them separate is what lets a brief be edited and
    regenerated without the persona rules drifting.
    """
    try:
        instruction = INSTRUCTION_BUILDERS[output_type](spec, brief)
    except KeyError:
        raise ValueError(f"Unknown output type: {output_type!r}") from None

    correction = (
        "\nYour previous response did not match the required structure. Return valid "
        "JSON this time, with every required key present and every list the required "
        "length.\n"
        if corrective
        else ""
    )

    # The evaluation harness measured this. Without an explicit numbers rule the
    # model garnished grounded briefs with plausible extra figures, every one of
    # which the auditor then redacted to an open slot, which blocked approval on
    # three grounded cases out of five. The fix belongs in the prompt: the auditor
    # was doing its job, the generation was giving it too much to do.
    numbers_rule = (
        "NUMBERS. Do not write any figure that is not either in the verified fact "
        "list above or in the proof supplied with this brief. That includes "
        "percentages, counts, durations, multiples, and money. If a sentence wants "
        "a quantity you have not been given, write the sentence without it. Do not "
        f"estimate, do not round, do not illustrate with an example figure. {OPEN_SLOT} "
        "is always better than a number nobody can stand behind."
    )

    system = "\n".join(
        (
            voice_brief(spec, brief.resolved_register(spec)),
            "",
            numbers_rule,
            "",
            "=" * 60,
            f"TASK: {output_type}",
            "=" * 60,
            instruction,
            correction,
            "",
            "Respond with a single JSON object and nothing else. No preamble, no code "
            "fence, no commentary. Start with { and end with }.",
            f"Key layout: {LAYOUTS[output_type]}",
            "It must validate against this JSON Schema:",
            json.dumps(schema.model_json_schema(), separators=(",", ":")),
        )
    )

    user = f"Create the {output_type} for this brief.\n\n{brief.to_prompt(spec)}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
