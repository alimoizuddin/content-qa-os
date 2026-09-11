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

from core import history, runlog
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
from ui.guide import EXAMPLES, fix_for, stage_intro
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


def all_edited_sections() -> tuple[dict[str, str], set[str]]:
    """Every edit field, and the subset that is a working note rather than copy.

    The second half matters at the gate. An open slot in a post is an unfilled
    claim and must block publication. An open slot in a calendar is the plan
    naming proof you have not gathered yet, which is what a calendar is for.
    """
    merged: dict[str, str] = {}
    planning: set[str] = set()
    for output_type, package in st.session_state["package"].items():
        edits = st.session_state["edits"].get(output_type, {})
        for section in package["sections"]:
            key = f"{output_type}.{section.key}"
            merged[key] = edits.get(section.key, section.text)
            if not section.publishable:
                planning.add(key)
    return merged, planning


# ---------------------------------------------------------------------------
# 1. Brief
# ---------------------------------------------------------------------------


def stage_brief(spec: PersonaSpec) -> None:
    st.subheader("Step 1 of 5. Your idea")
    stage_intro("brief")

    existing = _current_brief()

    # A blank form is the hardest screen in the app for someone who has never used
    # it. One button turns it into a worked example they can edit.
    example = EXAMPLES.get(spec.name)
    if example and st.button(
        "Fill in an example for me",
        key="fill_example",
        help="You can change every word after.",
    ):
        st.session_state["core_idea"] = example["core_idea"]
        st.session_state["proof"] = example["proof"]
        st.session_state["audience"] = example["audience"]
        st.rerun()
    pillar_options = [""] + [f"{p.key} {p.name}" for p in spec.pillars]

    with st.form("brief_form"):
        left, right = st.columns([3, 2])

        with left:
            core_idea = st.text_area(
                "Core idea or insight",
                key="core_idea",
                value=existing.core_idea,
                height=110,
                placeholder="Example: the hard part of automation is describing the work, not the tools.",
            )
            proof = st.text_area(
                "Your proof. The real thing behind the idea",
                key="proof",
                value=existing.proof,
                height=140,
                placeholder=(
                    "A project you built, a number you can stand behind, something that "
                    "actually happened. Any number you write here is treated as proven "
                    "for this post."
                ),
                help=(
                    "This is the most important box on the screen. Leave it empty and the "
                    f"app will write {OPEN_SLOT} wherever it needed proof, and it will not "
                    "let you approve the post until you fill those in."
                ),
            )
            notes = st.text_area(
                "Anything else you want it to know (optional)",
                key="notes",
                value=existing.notes,
                height=80,
                placeholder="A phrase to include, an angle to avoid, a length you want.",
            )

        with right:
            goal = st.selectbox(
                "What do you want this post to do?", GOALS, key="goal"
            )
            audience = st.text_input(
                "Audience",
                key="audience",
                value=existing.audience or spec.audience,
                help="Who you are talking to. Already filled in for this person.",
            )
            pillar = st.selectbox(
                "Which theme does this belong to? (optional)",
                pillar_options,
                key="pillar",
            )
            register = st.selectbox(
                "Which voice should it use?", list(spec.registers), key="register",
                help=" | ".join(f"{k}: {v}" for k, v in spec.registers.items()),
            )
            tone = st.selectbox("How should it sound?", TONE_HINTS, key="tone")
            formats = st.multiselect(
                "What should it make?",
                list(OUTPUT_TYPES),
                default=["post", "carousel"],
                key="formats",
                format_func=lambda key: OUTPUT_TYPES[key],
            )

        submitted = st.form_submit_button("Save and continue", type="primary")

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
            st.error("Please fill these in first: " + ", ".join(missing) + ".")
            return
        st.session_state["brief"] = brief
        st.session_state["package"] = {}
        st.session_state["edits"] = {}
        st.session_state["qa"] = None
        goto("generate")

    with st.expander(f"What {spec.name.split()[0]} is allowed to say"):
        st.markdown(
            "These are the facts the app will let into a post. Anything else has to "
            "come from the proof box above."
        )
        for fact in spec.star_facts:
            st.markdown(f"- {fact.claim}")
        if spec.pending_verification:
            st.markdown(
                "**These are believed but not proven yet, so the app refuses to "
                "write them.**"
            )
            for item in spec.pending_verification:
                st.markdown(f"- {item}")


# ---------------------------------------------------------------------------
# 2. Generate
# ---------------------------------------------------------------------------


def stage_generate(spec: PersonaSpec) -> None:
    brief = st.session_state.get("brief")
    st.subheader("Step 2 of 5. Write it")

    if brief is None:
        st.info("Fill in your idea first.")
        if st.button("Back to step 1", key="gen_back_empty"):
            goto("brief")
        return

    stage_intro("generate")

    for note in brief.warnings(spec):
        st.warning(note)

    left, right = st.columns([3, 2])
    with left:
        card("Core idea", brief.core_idea)
        card(
            "Proof",
            brief.proof
            or "You did not give any. The app will leave gaps you must fill.",
        )
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
    st.subheader("Step 3 of 5. Check and edit")
    stage_intro("edit")
    package = st.session_state["package"]

    if not package:
        st.info("Nothing generated yet.")
        if st.button("Go to generate", key="edit_back_empty"):
            goto("generate")
        return

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
        if st.button("Check it for problems", type="primary", key="edit_to_qa"):
            goto("qa")
    with columns[1]:
        if st.button("Write it again", key="edit_regenerate"):
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

    with st.expander("Copy everything as one block"):
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
    st.caption(
        "Downloads go to your browser's Downloads folder, the same place as anything "
        "else you download."
    )


def _render_picture(spec: PersonaSpec) -> None:
    st.divider()
    st.markdown("#### Image")

    if not image_provider_configured():
        st.info(
            "No image provider is configured, so this package is the art-direction prompt "
            "only. That prompt is a deliverable: it goes to a designer or an image tool "
            "unchanged. Add MESH_API_KEY to your .env file to render it here."
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
        st.caption("Saved to your browser's Downloads folder.")
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
    st.subheader("Step 4 of 5. Safety check")
    package = st.session_state["package"]

    if not package:
        st.info("There is nothing to check yet.")
        if st.button("Go back and write something", key="qa_back_empty"):
            goto("generate")
        return

    stage_intro("qa")

    brief = _current_brief()
    sections, planning = all_edited_sections()
    qa = run_qa(spec, sections, proof=brief.proof, planning=planning)
    verdict = approve_package(qa)
    st.session_state["qa"] = qa

    metrics = st.columns(4)
    metrics[0].metric("Pieces checked", len(sections))
    metrics[1].metric("Must fix", len(verdict["blocking_flags"]))
    metrics[2].metric("Worth a look", len(qa["audit_flags"]) - len(verdict["blocking_flags"]))
    metrics[3].metric("Style notes", len(qa["lint_flags"]))

    if verdict["approved"]:
        st.success("All clear. Nothing is stopping this. You can approve it below.")
    else:
        st.error(
            f"{len(verdict['blocking_flags'])} thing(s) must be fixed before you can "
            "approve this. Each one below tells you what to do."
        )
        for reason in verdict["reasons"]:
            st.caption(reason)

    if qa["audit_flags"]:
        st.markdown("#### Facts, safety and privacy")
        blocking = set(verdict["blocking_flags"])
        for flag in qa["audit_flags"]:
            stops_you = flag in blocking
            finding(flag, "block" if stops_you else "review")
            # The finding says what is wrong. A person who has just been stopped
            # needs the next action, so it is spelled out underneath.
            st.caption(
                f"**What to do:** {fix_for(flag)}"
                if stops_you
                else "This does not stop you. Worth a read."
            )

    if qa["lint_flags"]:
        st.markdown("#### Style suggestions")
        st.caption("You can ignore all of these and still approve.")
        for flag in qa["lint_flags"]:
            finding(flag, "lint")

    with st.expander("See exactly what would be saved"):
        for key, value in qa["outputs"].items():
            st.markdown(f"**{key}**")
            st.code(value, language=None)

    st.divider()
    columns = st.columns([1, 1, 3])
    with columns[0]:
        approve = st.button(
            "Approve and save it",
            type="primary",
            disabled=not verdict["approved"],
            key="approve_button",
        )
    with columns[1]:
        if st.button("Back to editing", key="qa_back"):
            goto("edit")
    with columns[2]:
        if not verdict["approved"]:
            st.caption(
                "The approve button turns on by itself once nothing is red. There is "
                "no way to override it, and that is deliberate."
            )

    if approve and verdict["approved"]:
        package_id = history.save_approved_package(
            persona=spec.name,
            outputs=qa["outputs"],
            provider=st.session_state["provider"],
            model=st.session_state["model"],
            output_types=list(package),
        )
        runlog.log_event(
            "approve", persona=spec.name, package_id=package_id, output_types=list(package)
        )
        st.success(
            f"Saved as package #{package_id}, on this computer only. You can find it any "
            "time in Step 5. Saved posts."
        )
        saved = next(
            (e for e in history.list_approved_packages(persona=spec.name, limit=5)
             if e["id"] == package_id),
            None,
        )
        if saved:
            st.download_button(
                "Download this package as a text file",
                data=history.package_as_text(saved),
                file_name=f"{spec.name.split()[0].lower()}-package-{package_id}.txt",
                mime="text/plain",
                key="download_saved_now",
            )
            st.caption("It goes to your browser's Downloads folder.")


# ---------------------------------------------------------------------------
# 5. History
# ---------------------------------------------------------------------------


def stage_history(spec: PersonaSpec) -> None:
    st.subheader("Step 5 of 5. Saved posts")
    stage_intro("history")
    st.caption(
        "Approved and cleaned text only. Your briefs, the raw AI output, error "
        "messages and your key are never saved here."
    )
    st.caption(
        f"Where it is kept: {history.DEFAULT_HISTORY_PATH}. That file is a small "
        "database, so use the download button on any package below to get a text "
        "file you can open."
    )
    stats = runlog.summary()
    if stats["runs"]:
        st.caption(
            f"Recent writing runs: {stats['worked']} of {stats['runs']} worked, typical "
            f"time {stats['median_seconds']} seconds. The full log is data/logs/runs.jsonl."
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
            st.download_button(
                "Download as a text file",
                data=history.package_as_text(entry),
                file_name=f"{entry['persona'].split()[0].lower()}-package-{entry['id']}.txt",
                mime="text/plain",
                key=f"download_package_{entry['id']}",
            )
