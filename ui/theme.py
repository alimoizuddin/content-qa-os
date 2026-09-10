"""Studio chrome: CSS, the stage stepper, and small presentational helpers.

Streamlit's defaults are fine for a dashboard and wrong for a studio. This module
does three things: it tightens the spacing so a long package does not feel like a
form, it tints the interface with the selected persona's accent so the brand you
are writing for is visible while you write, and it renders a real stage stepper so
the workflow reads as a sequence rather than a scroll.

All styling is injected once per run. Nothing here touches content or QA.
"""
from __future__ import annotations

import html

import streamlit as st

from core.personas import PersonaSpec

# Plain words, because the person reading them has not been told what a "brief"
# or a "QA pass" is and should not have to be.
STAGES: tuple[tuple[str, str], ...] = (
    ("brief", "1. Your idea"),
    ("generate", "2. Write it"),
    ("edit", "3. Check and edit"),
    ("qa", "4. Safety check"),
    ("history", "5. Saved posts"),
)


def _mix(hex_colour: str, alpha: float) -> str:
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def inject_css(spec: PersonaSpec) -> None:
    accent = spec.visual.accent
    deep = spec.visual.accent_deep
    st.markdown(
        f"""
        <style>
        :root {{
            --accent: {accent};
            --accent-deep: {deep};
            --accent-soft: {_mix(accent, 0.12)};
            --accent-line: {_mix(accent, 0.30)};
        }}

        .block-container {{ padding-top: 2.2rem; padding-bottom: 5rem; max-width: 1180px; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        #MainMenu, footer {{ visibility: hidden; }}

        h1, h2, h3 {{ letter-spacing: -0.015em; }}
        h1 {{ font-size: 1.9rem !important; font-weight: 700; }}

        /* Stage stepper */
        .stepper {{ display: flex; gap: 6px; margin: 0 0 1.6rem 0; flex-wrap: wrap; }}
        .step {{
            flex: 1 1 0; min-width: 128px; padding: 10px 14px;
            border-radius: 10px; border: 1px solid var(--accent-line);
            font-size: 0.82rem; font-weight: 600; letter-spacing: 0.01em;
            display: flex; align-items: center; gap: 8px; opacity: 0.55;
        }}
        .step .n {{
            width: 20px; height: 20px; border-radius: 999px; flex: 0 0 20px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 0.7rem; border: 1px solid currentColor;
        }}
        .step.active {{
            opacity: 1; background: var(--accent-soft);
            border-color: var(--accent); color: var(--accent);
        }}
        .step.done {{ opacity: 0.85; }}
        .step.done .n {{ background: var(--accent); border-color: var(--accent); color: #fff; }}

        /* Cards */
        .card {{
            border: 1px solid var(--accent-line); border-radius: 14px;
            padding: 18px 20px; margin-bottom: 14px;
        }}
        .card h4 {{ margin: 0 0 6px 0; font-size: 0.95rem; }}
        .card p {{ margin: 0; font-size: 0.85rem; opacity: 0.75; line-height: 1.5; }}

        /* Persona identity strip */
        .identity {{
            border-left: 3px solid var(--accent); padding: 2px 0 2px 14px;
            margin-bottom: 1.2rem;
        }}
        .identity .name {{ font-weight: 700; font-size: 1.05rem; }}
        .identity .role {{ font-size: 0.85rem; color: var(--accent); font-weight: 600; }}
        .identity .line {{ font-size: 0.84rem; opacity: 0.7; margin-top: 4px; }}

        /* Swatches */
        .swatches {{ display: flex; gap: 6px; margin-top: 10px; }}
        .swatch {{ width: 26px; height: 26px; border-radius: 7px; border: 1px solid rgba(128,128,128,0.35); }}

        /* Findings */
        .finding {{
            border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
            font-size: 0.84rem; line-height: 1.5;
            border-left: 3px solid transparent;
        }}
        .finding.block {{ border-left-color: #d9534f; background: rgba(217,83,79,0.09); }}
        .finding.review {{ border-left-color: #d99b34; background: rgba(217,155,52,0.09); }}
        .finding.lint {{ border-left-color: #6c8ebf; background: rgba(108,142,191,0.09); }}

        .stButton > button[kind="primary"] {{
            background: var(--accent); border-color: var(--accent);
        }}
        .stButton > button[kind="primary"]:hover {{
            background: var(--accent-deep); border-color: var(--accent-deep);
        }}
        div[data-testid="stMetricValue"] {{ font-size: 1.4rem; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def stepper(current: str) -> None:
    keys = [key for key, _ in STAGES]
    position = keys.index(current) if current in keys else 0
    chunks = []
    for index, (key, label) in enumerate(STAGES):
        state = "active" if index == position else ("done" if index < position else "")
        chunks.append(
            f'<div class="step {state}"><span class="n">{index + 1}</span>'
            f"<span>{html.escape(label)}</span></div>"
        )
    st.markdown(f'<div class="stepper">{"".join(chunks)}</div>', unsafe_allow_html=True)


def identity_strip(spec: PersonaSpec) -> None:
    st.markdown(
        f'<div class="identity">'
        f'<div class="name">{html.escape(spec.name)}</div>'
        f'<div class="role">{html.escape(spec.title)}</div>'
        f'<div class="line">{html.escape(spec.positioning)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def swatches(spec: PersonaSpec) -> None:
    v = spec.visual
    chips = "".join(
        f'<div class="swatch" style="background:{c}" title="{c}"></div>'
        for c in (v.background, v.accent, v.accent_deep, v.ink, v.muted)
    )
    st.markdown(f'<div class="swatches">{chips}</div>', unsafe_allow_html=True)


def finding(text: str, kind: str = "lint") -> None:
    st.markdown(
        f'<div class="finding {kind}">{html.escape(text)}</div>', unsafe_allow_html=True
    )


def card(title: str, body: str) -> None:
    st.markdown(
        f'<div class="card"><h4>{html.escape(title)}</h4><p>{html.escape(body)}</p></div>',
        unsafe_allow_html=True,
    )
