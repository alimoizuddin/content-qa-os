"""LinkedIn Content Studio. Private, local, NVIDIA NIM first.

This file is the shell: page configuration, session state, the sidebar, and the
stage router. Everything that produces or checks content lives under ``core/``, and
everything that draws a stage lives under ``ui/``. Keeping the shell thin is what
lets the whole workflow be driven from tests without a provider.
"""
from __future__ import annotations

import streamlit as st

from core.carousel import PORTRAIT_DIR, portrait_path, portrait_slug
from core.fonts import vendored_font_available
from core.personas import PERSONA_NAMES, get_persona
from core.providers import (
    available_models,
    check_live_catalogue,
    has_mesh_key,
    has_nvidia_key,
    provider_status,
)
from ui import stages
from ui.guide import setup_check, start_here
from ui.theme import STAGES, identity_strip, inject_css, stepper, swatches

st.set_page_config(
    page_title="LinkedIn Content Studio",
    page_icon=":material/stylus_note:",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULTS = {
    "stage": "brief",
    "show_guide": True,
    "persona": PERSONA_NAMES[0],
    "brief": None,
    "package": {},
    "edits": {},
    "qa": None,
    "carousel_assets": None,
    "picture": None,
    "catalogue": None,
    "failures": {},
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def _save_portrait(persona: str, uploaded) -> None:
    """Store a persona portrait in the app's own assets directory.

    Portraits are supplied by the person using the studio. Nothing is ever read
    out of a source corpus or an archive folder.
    """
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    for existing in PORTRAIT_DIR.glob(f"{portrait_slug(persona)}.*"):
        existing.unlink(missing_ok=True)
    suffix = "." + (uploaded.name.rsplit(".", 1)[-1].lower() or "png")
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
    (PORTRAIT_DIR / f"{portrait_slug(persona)}{suffix}").write_bytes(uploaded.getbuffer())


def sidebar() -> None:
    with st.sidebar:
        st.markdown("### Studio")
        persona = st.selectbox("Who is posting?", PERSONA_NAMES, key="persona")
        spec = get_persona(persona)

        st.caption(spec.title)
        swatches(spec)

        st.divider()
        st.markdown("**Connection**")
        for status in provider_status():
            mark = "Ready" if status["ready"] else ("Missing" if status["required"] else "Off")
            st.markdown(f"`{mark}` **{status['provider']}**")
            st.caption(status["detail"])

        models = available_models()
        labels = [m["label"] for m in models]
        chosen = st.selectbox(
            "Which AI should write it?",
            labels,
            key="model_label",
            help="The one at the top is the recommended default. Any of them will work.",
        )
        selected = next(m for m in models if m["label"] == chosen)
        st.session_state["provider"] = selected["provider"]
        st.session_state["model"] = selected["model"]

        if st.button("Check the AI models still work", key="check_models", width="stretch"):
            st.session_state["catalogue"] = check_live_catalogue()
        catalogue = st.session_state.get("catalogue")
        if catalogue:
            (st.success if catalogue["ok"] else st.warning)(catalogue["detail"])
            for model in catalogue["missing"]:
                st.caption(f"Retired: {model}")

        st.divider()
        st.markdown("**Photo for the slides**")
        current = portrait_path(persona)
        if current:
            st.image(str(current), width=104)
            st.caption("This appears on the cover slide and the last slide.")
        else:
            st.caption(
                "No photo yet. The slides will use initials instead until you add one. "
                "Your photo stays on this computer."
            )
        uploaded = st.file_uploader(
            "Add a photo",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"portrait_{portrait_slug(persona)}",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            _save_portrait(persona, uploaded)
            st.session_state["carousel_assets"] = None
            st.rerun()

        st.divider()
        st.markdown("**Go to a step**")
        for key, label in STAGES:
            if st.button(label, key=f"nav_{key}", width="stretch"):
                st.session_state["stage"] = key
                st.rerun()

        st.divider()
        st.checkbox(
            "Show the help panel",
            key="show_guide",
            help="Turn this off once you know your way around.",
        )

        if not vendored_font_available():
            st.warning(
                "The Inter font file is missing from assets/fonts. The slides will still "
                "render, but they will use a different typeface and will not match."
            )

        st.caption(
            "This app runs only on your computer. The only thing that ever leaves it is "
            "the writing request you send to the AI. Your key, your photo and your "
            "saved posts stay here."
        )


def main() -> None:
    sidebar()
    spec = get_persona(st.session_state["persona"])
    inject_css(spec)

    st.title("LinkedIn Content Studio")
    identity_strip(spec)

    # A missing key used to surface as a provider error several clicks later, at
    # generation time, which is the worst possible moment to learn about it.
    if not setup_check(has_nvidia_key(), has_mesh_key()):
        return

    stepper(st.session_state["stage"])

    if st.session_state.get("show_guide", True):
        start_here()

    router = {
        "brief": stages.stage_brief,
        "generate": stages.stage_generate,
        "edit": stages.stage_edit,
        "qa": stages.stage_qa,
        "history": stages.stage_history,
    }
    router.get(st.session_state["stage"], stages.stage_brief)(spec)


main()
