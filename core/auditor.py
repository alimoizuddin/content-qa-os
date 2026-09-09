"""Fact and safety audit. This is the layer that blocks publication.

Three things it does, in order:

1. Runs the persona's safety rules. These come from the ``PersonaSpec`` rather than
   from ``if persona_name == "..."`` branches, so adding a persona cannot silently
   skip a domain guardrail. A safety flag is critical and blocks approval.
2. Checks banned inflations: the specific wrong version of a right claim, recorded
   next to the claim it inflates.
3. Redacts unverified numbers. Every numeric token in the text is checked against
   the tokens the persona's verified facts license, plus anything supplied as proof
   in the brief. An unlicensed number is replaced with [OPEN SLOT], which blocks
   approval until a person resolves it.

The redaction is deliberately blunt: an unverified number is replaced, not merely
flagged, because a flagged number in an editable text area gets copied to LinkedIn
by accident and a redacted one cannot.
"""
from __future__ import annotations

import re
from typing import Any

from core.personas import OPEN_SLOT, PersonaSpec

NUMBER_PATTERN = re.compile(
    r"(?<![\w.$])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s?%\+?|\+|x)?(?![\w.-])"
)

# Numbers that are structure, not claims: "Week 4", "Slide 6", "Day 2", ordinals.
_STRUCTURAL = re.compile(
    r"\b(?:week|slide|day|step|part|phase|point|no\.?|number)\s*#?\s*(\d+)\b", re.IGNORECASE
)
# Clock times inside a publishing window are not metrics.
_CLOCK = re.compile(r"\b\d{1,2}[:.]\d{2}\s*(?:AM|PM)?\b", re.IGNORECASE)
# A sentence that addresses the reader is instruction, whatever else is in it.
# The evaluation harness found a post whose every medication sentence carried a
# first-person marker, and whose takeaway still told the reader their daily pill
# might be unnecessary. First-person history earns the exemption; turning to the
# reader takes it away again.
_SECOND_PERSON = re.compile(
    r"\byou\b|\byour\b|\byou'?re\b|\byours\b|\breaders?\b|\banyone\b",
    re.IGNORECASE,
)

# Sentence boundaries, also treating a line break as one: these texts are written
# in one-line paragraphs, where a newline is a full stop. Honorifics are excluded
# so "Mr. Sharma" stays in one piece and the confidentiality rule can see it.
_SENTENCE = re.compile(
    r"(?<!\bMr\.)(?<!\bMs\.)(?<!\bDr\.)(?<!\bMrs\.)(?<!\bSt\.)(?<=[.!?])\s+|\n+"
)


def _structural_tokens(text: str) -> set[str]:
    tokens = set(_STRUCTURAL.findall(text))
    for match in _CLOCK.finditer(text):
        tokens.update(NUMBER_PATTERN.findall(match.group(0)))
    return tokens


def _normalise(token: str) -> str:
    return token.replace(" ", "").rstrip("+x").rstrip("%").strip()


def licensed_numbers(spec: PersonaSpec, proof: str = "") -> set[str]:
    """Numeric tokens this persona may use, plus anything the brief supplied.

    Proof text supplied in the brief is trusted, because a person typed it
    deliberately as evidence for this specific piece. That is the escape hatch that
    keeps the auditor from being an obstacle: to use a new number, state it as proof.
    """
    licensed = {_normalise(t) for t in spec.verified_numbers}
    if proof:
        licensed.update(_normalise(t) for t in NUMBER_PATTERN.findall(proof))
    return {t for t in licensed if t}


def audit_content(
    spec: PersonaSpec,
    text: str,
    proof: str = "",
    section: str = "",
) -> dict[str, Any]:
    """Audit one block of text. Returns the redacted text and its flags."""
    flags: list[str] = []
    audited = text

    # 1. Persona safety rules, matched sentence by sentence so an exemption in one
    #    sentence cannot excuse a breach in another.
    sentences = _SENTENCE.split(audited)
    for rule in spec.safety_rules:
        for sentence in sentences:
            match = re.search(rule.pattern, sentence, flags=re.IGNORECASE)
            if not match:
                continue
            exempt = (
                rule.exempt
                and re.search(rule.exempt, sentence, flags=re.IGNORECASE)
                and not _SECOND_PERSON.search(sentence)
            )
            if exempt:
                continue
            prefix = "BLOCKED" if rule.severity == "critical" else "REVIEW"
            flags.append(f"{prefix}: {rule.message} Found: {match.group(0).strip()!r}")
            break

    # 2. Banned inflations of otherwise-true claims.
    for inflation in spec.banned_claims:
        if inflation.lower() in audited.lower():
            flags.append(
                f"BLOCKED: {inflation!r} is the inflated version of a real claim. "
                "Use the verified wording."
            )

    # 3. Unverified numbers.
    licensed = licensed_numbers(spec, proof)
    structural = _structural_tokens(audited)
    seen: set[str] = set()

    for token in NUMBER_PATTERN.findall(audited):
        bare = _normalise(token)
        if not bare or bare in seen:
            continue
        seen.add(bare)
        if bare in structural or bare in licensed:
            continue
        flags.append(
            f"UNVERIFIED: {token.strip()!r} is not in the verified fact list and was not "
            f"supplied as proof. Replaced with {OPEN_SLOT}."
        )
        audited = re.sub(
            rf"(?<![\w.]){re.escape(token.strip())}(?![\w.])", OPEN_SLOT, audited
        )

    return {
        "original_text": text,
        "audited_text": audited,
        "flags": flags,
        "passed": not flags,
        "section": section,
    }


def blocking(flags: list[str]) -> list[str]:
    """The subset of audit flags that must stop an approval."""
    return [f for f in flags if not f.startswith("REVIEW")]
