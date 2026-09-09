"""The five stages of the studio.

Each function renders one stage and owns its slice of session state. The order is
deliberate and enforced: you cannot approve a package you have not generated, and
the QA stage always re-audits the text currently in the edit fields rather than
the text the model produced. That ordering is the product, not decoration.
"""
from __future__ import annotations

import hashlib
from typing import Any

import streamlit as st

from core import history
from core.brief import GOALS, OUTPUT_TYPES, TONE_HINTS, ContentBrief
from core.carousel import build_carousel_assets, portrait_path
from core.generator import generate_bundle
from core.imagegen import create_picture, image_provider_configured
from core.personas import OPEN_SLOT, PersonaSpec
from core.schemas import ContentCalendar, PicturePrompt
from core.studio import (
    Section,
    approve_package,
    build_sections,
    carousel_from_sections,
    delivery_text,
    run_qa,
)
from ui.theme import card, finding, swatches

ORDER = ("post", "carousel", "picture", "calendar")


def goto(stage: str) -> None:
    st.session_state["stage"] = stage
    st.rerun()


def _current_brief() -> ContentBrief:
    return st.session_state.get("brief") or ContentBrief(persona=st.session_state["persona"])


def _edited_sections(output_type: str) -> dict[str, str]:
    """Whatever is in the edit fields right now for one output type."""
    package = st.session_state["package"].get(output_type)
    if not package:
        return {}
    edits = st.session_state["edits"].get(output_type, {})
    return {s.key: edits.get(s.key, s.text) for s in package["sections"]}


def all_edited_sections() -> dict[str, str]:
    merged: dict[str, str] = {}
    for output_type in st.session_state["package"]:
        for key, value in _edited_sections(output_type).items():
            merged[f"{output_type}.{key}"] = value
    return merged


# ---------------------------------------------------------------------------
# 1. Brief
# ---------------------------------------------------------------------------


def stage_brief(spec: PersonaSpec) -> None:
    st.subheader("1. Brief")
    st.caption(
        "The brief is the grounding contract. Everything the generator writes has to "
        "come from here or from the verified fact list. The proof field is the one that "
        "decides whether you get publishable content or a set of open slots."
    )

    existing = _current_brief()
    pillar_options = [""] + [f"{p.key} {p.name}" for p in spec.pillars]

    with st.form("brief_form"):
        left, right = st.columns([3, 2])

        with left:
            core_idea = st.text_area(
                "Core idea or insight",
                key="core_idea",
                value=existing.core_idea,
                height=110,
                placeholder="The one thing this piece argues. Write it as a sentence you believe.",
            )
            proof = st.text_area(
                "Verified proof, project, experience, or asset",
                key="proof",
                value=existing.proof,
                height=140,
                placeholder=(
                    "The real material this is anchored to. A project, a number you can "
                    "stand behind, a moment that actually happened. Numbers you put here "
                    "are treated as verified for this piece."
                ),
                help=(
                    "Leave this empty and every place the writing needs evidence will be "
                    f"marked {OPEN_SLOT}, and approval stays blocked until you fill it in."
                ),
            )
            notes = st.text_area(
                "Anything else the writer should know",
                key="notes",
                value=existing.notes,
                height=80,
                placeholder="Optional. Constraints, a phrase to include, a angle to avoid.",
            )

        with right:
            goal = st.selectbox("Content goal", GOALS, key="goal")
            audience = st.text_input(
                "Audience",
                key="audience",
                value=existing.audience or spec.audience,
                help="Who this is written at. The persona default is prefilled.",
            )
            pillar = st.selectbox("Content pillar", pillar_options, key="pillar")
            register = st.selectbox(
                "Register", list(spec.registers), key="register",
                help=" | ".join(f"{k}: {v}" for k, v in spec.registers.items()),
            )
            tone = st.selectbox("Tone", TONE_HINTS, key="tone")
            formats = st.multiselect(
                "Outputs to produce",
                list(OUTPUT_TYPES),
                default=["post", "carousel"],
                key="formats",
                format_func=lambda key: OUTPUT_TYPES[key],
            )

        submitted = st.form_submit_button("Save brief and continue", type="primary")

    if submitted:
        brief = ContentBrief(
            persona=spec.name,
            goal=goal,
            audience=audience,
            core_idea=core_idea,
            proof=proof,
            formats=tuple(formats),
            register=register,
            tone=tone,
            pillar=pillar,
            notes=notes,
        )
        missing = brief.missing_required()
        if missing:
            st.error("Still needed: " + ", ".join(missing) + ".")
            return
        st.session_state["brief"] = brief
        st.session_state["package"] = {}
        st.session_state["edits"] = {}
        st.session_state["qa"] = None
        goto("generate")

    with st.expander("What this persona is allowed to claim"):
        st.markdown("**Verified facts.** Only these, plus whatever you put in the proof field.")
        for fact in spec.star_facts:
            st.markdown(f"- {fact.claim}")
        if spec.pending_verification:
            st.markdown("**Believed but not verified. The studio will not write these.**")
            for item in spec.pending_verification:
                st.markdown(f"- {item}")


# ---------------------------------------------------------------------------
# 2. Generate
# ---------------------------------------------------------------------------


def stage_generate(spec: PersonaSpec) -> None:
    brief = st.session_state.get("brief")
    st.subheader("2. Generate")

    if brief is None:
        st.info("Write the brief first.")
        if st.button("Back to the brief", key="gen_back_empty"):
            goto("brief")
        return

    for note in brief.warnings(spec):
        st.warning(note)

    left, right = st.columns([3, 2])
    with left:
        card("Core idea", brief.core_idea)
        card("Proof", brief.proof or "None supplied. Open slots will be inserted.")
    with right:
        card("Goal", brief.goal)
        card("Audience", brief.audience)
        card(
            "Producing",
            ", ".join(OUTPUT_TYPES[f] for f in brief.formats),
        )

    columns = st.columns([1, 1, 4])
    with columns[0]:
        run = st.button("Generate", type="primary", key="generate_button")
    with columns[1]:
        if st.button("Edit brief", key="gen_back"):
            goto("brief")

    if not run:
        if st.session_state["package"]:
            st.success("A package is already generated.")
            if st.button("Go to editing", key="gen_to_edit"):
                goto("edit")
        return

    provider = st.session_state["provider"]
    model = st.session_state["model"]

    with st.spinner("Writing the package. The post is written first, then the assets."):
        result = generate_bundle(brief, list(brief.formats), provider, model)

    package: dict[str, Any] = {}
    for output_type, outcome in result["outputs"].items():
        if not outcome["success"]:
            continue
        data = outcome["data"]
        package[output_type] = {
            "data": data,
            "sections": build_sections(spec, output_type, data),
            "attempts": outcome["attempts"],
        }

    st.session_state["package"] = package
    st.session_state["edits"] = {}
    st.session_state["qa"] = None
    st.session_state["carousel_assets"] = None
    st.session_state["picture"] = None
    # Stored rather than only rendered here: a partial bundle jumps straight to the
    # edit stage, and an error drawn on this screen would vanish with it.
    st.session_state["failures"] = dict(result["failures"])

    for output_type, message in result["failures"].items():
        st.error(f"{OUTPUT_TYPES[output_type]}: {message}")

    if package:
        goto("edit")


# ---------------------------------------------------------------------------
# 3. Edit and preview
# ---------------------------------------------------------------------------


def stage_edit(spec: PersonaSpec) -> None:
    st.subheader("3. Edit and preview")
    package = st.session_state["package"]

    if not package:
        st.info("Nothing generated yet.")
        if st.button("Go to generate", key="edit_back_empty"):
            goto("generate")
        return

    st.caption(
        "Every field below is yours to change. Whatever is in these boxes when you press "
        "approve is what gets audited and what gets saved."
    )

    for output_type, message in (st.session_state.get("failures") or {}).items():
        st.error(f"{OUTPUT_TYPES[output_type]} was not produced. {message}")

    present = [t for t in ORDER if t in package]
    tabs = st.tabs([OUTPUT_TYPES[t] for t in present])

    for tab, output_type in zip(tabs, present):
        with tab:
            _render_editor(spec, output_type)
            if output_type == "carousel":
                _render_carousel_assets(spec)
            elif output_type == "picture":
                _render_picture(spec)
            elif output_type == "calendar":
                _render_calendar_table(output_type)

    st.divider()
    columns = st.columns([1, 1, 4])
    with columns[0]:
        if st.button("Run QA", type="primary", key="edit_to_qa"):
            goto("qa")
    with columns[1]:
        if st.button("Regenerate", key="edit_regenerate"):
            st.session_state["package"] = {}
            goto("generate")


def _render_editor(spec: PersonaSpec, output_type: str) -> None:
    package = st.session_state["package"][output_type]
    edits = st.session_state["edits"].setdefault(output_type, {})

    for section in package["sections"]:
        widget_key = f"edit_{output_type}_{section.key}"
        current = edits.get(section.key, section.text)
        if section.multiline:
            height = max(90, min(340, 34 + 22 * current.count("\n")))
            value = st.text_area(
                section.label, value=current, key=widget_key, help=section.help, height=height
            )
        else:
            value = st.text_input(
                section.label, value=current, key=widget_key, help=section.help
            )
        edits[section.key] = value
        if OPEN_SLOT in value:
            st.caption(f"Contains {OPEN_SLOT}. Approval is blocked until this is resolved.")

    with st.expander("Copy the whole package as one block"):
        rebuilt = [
            Section(s.key, s.label, edits.get(s.key, s.text), s.help, s.multiline, s.copyable)
            for s in package["sections"]
        ]
        st.code(delivery_text(rebuilt), language=None)


def _carousel_fingerprint(sections: dict[str, str]) -> str:
    joined = "|".join(f"{k}={v}" for k, v in sorted(sections.items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _render_carousel_assets(spec: PersonaSpec) -> None:
    st.divider()
    st.markdown("#### Slides")

    edited = _edited_sections("carousel")
    fingerprint = _carousel_fingerprint(edited)
    cached = st.session_state.get("carousel_assets")

    columns = st.columns([1, 3])
    with columns[0]:
        render = st.button("Render slides", type="primary", key="render_slides")
    with columns[1]:
        if cached is not None and cached.get("fingerprint") != fingerprint:
            st.caption("These slides are older than your edits. Render again to update them.")

    # Rendered on first view so selecting a carousel visibly produces slides, then
    # re-rendered on demand once the copy has been edited.
    if render or cached is None:
        with st.spinner("Rendering 1080 x 1350 slides"):
            draft = carousel_from_sections(
                st.session_state["package"]["carousel"]["data"], edited
            )
            cached = build_carousel_assets(spec, draft)
            cached["fingerprint"] = fingerprint
            st.session_state["carousel_assets"] = cached

    if portrait_path(spec.name) is None:
        st.caption(
            f"No portrait uploaded for {spec.name}, so the author slide uses an initials "
            "mark. Upload one in the sidebar to get the full lockup."
        )

    grid = st.columns(3)
    for index, png in enumerate(cached["slides"]):
        with grid[index % 3]:
            st.image(png, caption=f"Slide {index + 1}", width="stretch")

    download = st.columns(2)
    with download[0]:
        st.download_button(
            "Download LinkedIn PDF",
            data=cached["pdf"],
            file_name="carousel.pdf",
            mime="application/pdf",
            width="stretch",
            key="download_pdf",
        )
    with download[1]:
        st.download_button(
            "Download ZIP (slides plus PDF)",
            data=cached["zip"],
            file_name="carousel-assets.zip",
            mime="application/zip",
            width="stretch",
            key="download_zip",
        )


def _render_picture(spec: PersonaSpec) -> None:
    st.divider()
    st.markdown("#### Image")

    if not image_provider_configured():
        st.info(
            "No image provider is configured, so this package is the art-direction prompt "
            "only. That prompt is a deliverable: it goes to a designer or an image tool "
            "unchanged. Set OPENROUTER_API_KEY and OPENROUTER_IMAGE_MODEL to render it here."
        )
        return

    if st.button("Render image", key="render_image"):
        prompt = _edited_sections("picture").get(
            "picture_prompt",
            PicturePrompt.model_validate(
                st.session_state["package"]["picture"]["data"]
            ).prompt,
        )
        with st.spinner("Asking the image provider"):
            st.session_state["picture"] = create_picture(spec, prompt)

    result = st.session_state.get("picture")
    if not result:
        return
    if result["image_bytes"]:
        st.image(result["image_bytes"], width="stretch")
        st.download_button(
            "Download image",
            data=result["image_bytes"],
            file_name="picture.png",
            mime="image/png",
            key="download_image",
        )
    else:
        st.warning(result["detail"])


def _render_calendar_table(output_type: str) -> None:
    st.divider()
    st.markdown("#### Calendar grid")
    calendar = ContentCalendar.model_validate(
        st.session_state["package"][output_type]["data"]
    )
    st.dataframe(
        [
            {
                "Week": e.week,
                "Pillar": e.pillar,
                "Format": e.content_format,
                "Hook angle": e.hook_angle,
                "Anchored to": e.target_asset,
                "CTA": e.cta,
                "Goal": e.goal,
                "Evidence": e.evidence or "-",
            }
            for e in calendar.entries
        ],
        width="stretch",
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# 4. QA and approve
# ---------------------------------------------------------------------------


def stage_qa(spec: PersonaSpec) -> None:
    st.subheader("4. QA and approve")
    package = st.session_state["package"]

    if not package:
        st.info("Nothing to check yet.")
        if st.button("Go to generate", key="qa_back_empty"):
            goto("generate")
        return

    brief = _current_brief()
    sections = all_edited_sections()
    qa = run_qa(spec, sections, proof=brief.proof)
    verdict = approve_package(qa)
    st.session_state["qa"] = qa

    metrics = st.columns(4)
    metrics[0].metric("Sections checked", len(sections))
    metrics[1].metric("Blocking", len(verdict["blocking_flags"]))
    metrics[2].metric("Advisory", len(qa["audit_flags"]) - len(verdict["blocking_flags"]))
    metrics[3].metric("Style notes", len(qa["lint_flags"]))

    if verdict["approved"]:
        st.success("Clean. Nothing is blocking this package.")
    else:
        for reason in verdict["reasons"]:
            st.error(reason)

    if qa["audit_flags"]:
        st.markdown("#### Facts and safety")
        for flag in qa["audit_flags"]:
            finding(flag, "review" if ": REVIEW" in flag else "block")

    if qa["lint_flags"]:
        st.markdown("#### Style and voice")
        st.caption("Advisory. These never block approval on their own.")
        for flag in qa["lint_flags"]:
            finding(flag, "lint")

    with st.expander("Sanitised text that would be saved"):
        for key, value in qa["outputs"].items():
            st.markdown(f"**{key}**")
            st.code(value, language=None)

    st.divider()
    columns = st.columns([1, 1, 3])
    with columns[0]:
        approve = st.button(
            "Approve and save",
            type="primary",
            disabled=not verdict["approved"],
            key="approve_button",
        )
    with columns[1]:
        if st.button("Back to editing", key="qa_back"):
            goto("edit")

    if approve and verdict["approved"]:
        package_id = history.save_approved_package(
            persona=spec.name,
            outputs=qa["outputs"],
            provider=st.session_state["provider"],
            model=st.session_state["model"],
            output_types=list(package),
        )
        st.success(f"Saved locally as package #{package_id}.")


# ---------------------------------------------------------------------------
# 5. History
# ---------------------------------------------------------------------------


def stage_history(spec: PersonaSpec) -> None:
    st.subheader("5. History")
    st.caption(
        "Approved, sanitised text only. Briefs, raw model output, provider errors, and "
        "keys are never written to this database."
    )

    only_this = st.checkbox(
        f"Only {spec.name}", value=True, key="history_filter_persona"
    )
    packages = history.list_approved_packages(persona=spec.name if only_this else "")

    if not packages:
        st.info("Nothing approved yet.")
        return

    for entry in packages:
        label = (
            f"#{entry['id']} . {entry['created_at']} . {entry['persona']} . "
            f"{entry['output_types'] or 'package'}"
        )
        with st.expander(label):
            st.caption(f"{entry['provider']} . {entry['model']}")
            for key, value in entry["outputs"].items():
                st.markdown(f"**{key}**")
                st.code(value, language=None)
