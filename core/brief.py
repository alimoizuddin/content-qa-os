"""The structured brief.

The old app collected a single free-text box and asked a model to invent the rest.
That is where fabricated metrics come from: the model has a shape to fill and no
material to fill it with, so it makes material up, and the auditor then spends its
time redacting numbers that should never have been generated.

A brief here is the grounding contract. Goal, audience, core idea, and proof are
collected separately, and proof is the load-bearing field: if it is empty, the
generator is told to write [OPEN SLOT] wherever evidence belongs, and approval is
blocked until a human fills it in.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.personas import OPEN_SLOT, PersonaSpec

MAX_FIELD = 2000

GOALS: tuple[str, ...] = (
    "Reach: relatability and engagement",
    "DMs and leads: drive inbound conversation",
    "Both: trust building that earns profile visits and DMs",
    "Authority: establish a position on a contested idea",
    "Save target: engineered to be saved and returned to",
)

TONE_HINTS: tuple[str, ...] = (
    "Match the persona default",
    "Warmer than usual",
    "Sharper than usual",
    "More personal than usual",
    "More technical than usual",
)

OUTPUT_TYPES: dict[str, str] = {
    "post": "LinkedIn post package",
    "carousel": "Branded carousel (PNG slides, PDF, ZIP)",
    "picture": "Picture art direction",
    "calendar": "Four-week content calendar",
}


@dataclass
class ContentBrief:
    """Everything the generator is allowed to build from."""

    persona: str
    goal: str = ""
    audience: str = ""
    core_idea: str = ""
    proof: str = ""
    formats: tuple[str, ...] = ()
    register: str = ""
    tone: str = ""
    pillar: str = ""
    notes: str = ""

    # ------------------------------------------------------------------
    @property
    def has_proof(self) -> bool:
        return bool(self.proof.strip())

    def missing_required(self) -> list[str]:
        """Fields without which generation is not grounded enough to run."""
        missing = []
        if not self.core_idea.strip():
            missing.append("Core idea or insight")
        if not self.audience.strip():
            missing.append("Audience")
        if not self.goal.strip():
            missing.append("Content goal")
        if not self.formats:
            missing.append("At least one output format")
        return missing

    def warnings(self, spec: PersonaSpec) -> list[str]:
        """Things that will not block generation but will degrade the result."""
        notes: list[str] = []
        if not self.has_proof:
            notes.append(
                "No verified proof supplied. Every place the content needs evidence "
                f"will be marked {OPEN_SLOT} and approval will stay blocked until you "
                "fill it in."
            )
        if self.register and self.register not in spec.registers:
            notes.append(
                f"{self.register!r} is not one of {spec.name}'s registers. "
                f"Falling back to {spec.default_register}."
            )
        return notes

    def resolved_register(self, spec: PersonaSpec) -> str:
        if self.register in spec.registers:
            return self.register
        return spec.default_register

    def to_prompt(self, spec: PersonaSpec) -> str:
        """The brief as the model sees it."""
        proof = self.proof.strip()
        if proof:
            evidence = (
                "Verified proof supplied for this piece. You may use these facts and "
                "nothing beyond them:\n" + proof
            )
        else:
            evidence = (
                "No proof was supplied for this piece. You may use the persona's verified "
                f"fact list, and nowhere else. Wherever the writing wants evidence that is "
                f"not in that list, write {OPEN_SLOT} verbatim instead of inventing "
                "anything. Do not write around the gap and do not soften it."
            )

        lines = [
            f"Goal: {self.goal.strip()}",
            f"Audience: {self.audience.strip()}",
            f"Core idea: {self.core_idea.strip()}",
        ]
        if self.pillar:
            lines.append(f"Content pillar: {self.pillar}")
        if self.tone and not self.tone.startswith("Match"):
            lines.append(f"Tone adjustment: {self.tone}")
        if self.notes.strip():
            lines.append(f"Additional context: {self.notes.strip()}")
        lines.extend(("", evidence))
        return "\n".join(lines)

    def truncated(self) -> "ContentBrief":
        """A copy with every free-text field clamped, so one paste cannot blow the context."""
        return ContentBrief(
            persona=self.persona,
            goal=self.goal[:200],
            audience=self.audience[:MAX_FIELD],
            core_idea=self.core_idea[:MAX_FIELD],
            proof=self.proof[:MAX_FIELD],
            formats=self.formats,
            register=self.register[:100],
            tone=self.tone[:100],
            pillar=self.pillar[:200],
            notes=self.notes[:MAX_FIELD],
        )
