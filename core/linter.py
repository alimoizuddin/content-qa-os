"""Deterministic style lint.

The lint layer normalises typography and flags voice problems. It is advisory: a
lint flag never blocks approval on its own, because "you used a cliche" is a taste
judgement and the person writing gets the final say. Facts and safety are the
auditor's job, and those do block.

One correction worth recording. The previous version banned "leverage" globally,
which is a word one of these personas uses deliberately and often. A banned-word
list that contradicts a persona's own vocabulary trains people to ignore the
linter, so the list is now assembled per persona: universal cliches plus that
person's own never-list, minus anything on their use-list.
"""
from __future__ import annotations

import re
from typing import Any

from core.personas import PersonaSpec, banned_words_for

ENGAGEMENT_BAIT: tuple[tuple[str, str], ...] = (
    (r"\bcomment\s+(?:yes|below|[A-Z]{2,})\b", "a comment gate"),
    (r"\bcomment\s+\"?\w+\"?\s+and\s+I(?:'| w)ll\b", "a comment gate"),
    (r"\bdo\s+you\s+agree\b", "'do you agree'"),
    (r"\bthoughts\s*\?", "'thoughts?'"),
    (r"\bagree\s*\?", "'agree?'"),
    (r"\bdrop\s+a\s+comment\b", "'drop a comment'"),
    (r"\blike\s+and\s+share\b", "'like and share'"),
    (r"\btag\s+someone\s+who\b", "'tag someone who'"),
    (r"\blike\s+if\s+you\b", "'like if you'"),
)

# Ranges are normalised to words before dash typography, so "10-15%" becomes
# "10 to 15%" rather than "10 - 15%".
_RANGE = re.compile(r"(?<!\w)(\d+)\s*[-–—]\s*(\d+%?)(?!\w)")
_DASHES = ("—", "–", "--")
_URL = re.compile(r"https?://\S+|\bwww\.\S+")
_STALE_MODEL = re.compile(r"\bGPT-[34](?:\.\d)?\b|\bClaude\s*[23](?:\.\d)?\b", re.IGNORECASE)


def lint_text(text: str, spec: PersonaSpec | None = None, section: str = "") -> dict[str, Any]:
    """Normalise typography and flag voice problems.

    ``section`` is the label of the block being linted, so the body-link rule can
    apply to the post body and not to the first comment, which is exactly where a
    link is supposed to live.
    """
    flags: list[str] = []
    cleaned = text

    ranged = _RANGE.sub(r"\1 to \2", cleaned)
    if ranged != cleaned:
        flags.append("Metric range rewritten in words.")
        cleaned = ranged

    if any(dash in cleaned for dash in _DASHES):
        flags.append("Em dash or en dash replaced. This voice does not use them.")
        for dash in _DASHES:
            cleaned = cleaned.replace(dash, ", ")
        cleaned = re.sub(r"\s*,\s*,\s*", ", ", cleaned)
        cleaned = re.sub(r"\s+,", ",", cleaned)

    if _STALE_MODEL.search(cleaned):
        flags.append("Stale model reference. Name a current model or drop the version.")

    words = banned_words_for(spec) if spec else ()
    allowed = {w.lower() for w in (spec.use_words if spec else ())}
    for word in words:
        if word.lower() in allowed:
            continue
        if re.search(rf"\b{re.escape(word)}\b", cleaned, flags=re.IGNORECASE):
            flags.append(f"Off-voice word: {word!r}.")

    for pattern, label in ENGAGEMENT_BAIT:
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            flags.append(f"Engagement bait: {label}. This pattern is demoted, not rewarded.")

    if section in {"post", "Post", "LinkedIn post"} and _URL.search(cleaned):
        flags.append(
            "Link in the post body. Links belong in the first comment, where they do not "
            "cost reach."
        )

    hashtags = re.findall(r"(?<!\w)#\w+", cleaned)
    if len(hashtags) > 5:
        flags.append(f"{len(hashtags)} hashtags. Never more than five.")
    if spec:
        banned_tags = {t.lower() for t in spec.hashtags_banned}
        for tag in hashtags:
            if tag.lower() in banned_tags:
                flags.append(f"Banned hashtag: {tag}.")

    return {
        "original_text": text,
        "cleaned_text": cleaned,
        "flags": flags,
        "passed": not flags,
    }
