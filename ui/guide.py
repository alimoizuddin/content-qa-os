"""Every word of on-screen guidance, in one place.

The studio was built by the person who also wrote its rules, and that made it easy
to write labels that only make sense if you already know why the stage exists.
"Grounding contract" and "planning section" are accurate and they teach nobody.

So the guidance lives here rather than being scattered through ``ui/stages.py``.
One file to read if you want to know what the app tells people, one file to change
if the words are wrong, and no risk of the explanation on screen drifting away from
the explanation in the README.

House style for everything in this module: short sentences, ordinary words, no
jargon, and no em dashes. Say what to do, then say what happens next.
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# What the whole app is, in the fewest words that are still true
# ---------------------------------------------------------------------------

WHAT_THIS_IS = """
This app writes LinkedIn posts for three people, then checks them.

The checking is the point. It will not let you publish a number you cannot prove,
a medical promise, a client you do not have, or a private detail about someone
else. When it finds one of those it stops and tells you what to fix.

You stay in control. The app never posts anything to LinkedIn. You copy the
finished text out and post it yourself.
"""

HOW_LONG = "Start to finish takes about five minutes."

STEPS_PLAIN: tuple[tuple[str, str], ...] = (
    ("1. Your idea", "Tell it who is posting, what the point is, and what proof you have."),
    ("2. Write it", "The AI writes the post, the slides, the picture, or the plan."),
    ("3. Check and edit", "Read it. Change any wording you do not like."),
    ("4. Safety check", "The app checks it. Fix anything it stops you on, then approve."),
    ("5. Saved posts", "Approved work is saved here so you can find it later."),
)

# ---------------------------------------------------------------------------
# Per stage: what this screen is for, and what to do on it
# ---------------------------------------------------------------------------

STAGE_GUIDE: dict[str, dict[str, str]] = {
    "brief": {
        "title": "Tell the app what to write about",
        "body": (
            "Fill in the boxes below. Two of them decide everything.\n\n"
            "**Core idea** is the one thing you want the post to say. Write it as a "
            "normal sentence that you believe.\n\n"
            "**Proof** is the real thing behind it. A project you built, a number you "
            "can stand behind, something that actually happened. If you leave this "
            "empty, the app has nothing true to write from, so it will leave gaps and "
            "refuse to approve the post."
        ),
        "next": "Next you will pick what to make, and the AI will write it.",
    },
    "generate": {
        "title": "The AI writes it now",
        "body": (
            "Press the button and wait. A post takes a few seconds. Slides and a "
            "month of plans take longer.\n\n"
            "If it fails, it will tell you why in plain words. The usual fixes are to "
            "try again, or pick a different model in the left panel."
        ),
        "next": "Next you will read what it wrote and change anything you want.",
    },
    "edit": {
        "title": "Read it and make it yours",
        "body": (
            "Every box below can be edited. Change the wording, cut a line, rewrite the "
            "opening. Nothing is locked.\n\n"
            "If you see **[OPEN SLOT]**, that is the app telling you it needed proof "
            "and did not have any. Replace it with the real detail, or delete the "
            "sentence around it."
        ),
        "next": "Next the app checks whatever is in these boxes right now.",
    },
    "qa": {
        "title": "The safety check",
        "body": (
            "The app has read the current text and is showing you what it found.\n\n"
            "**Red items stop you.** These are facts, safety, or privacy problems. Go "
            "back, fix the wording, and come here again.\n\n"
            "**Grey items are suggestions.** They are about style. You can ignore all "
            "of them and still approve."
        ),
        "next": "Once nothing is red, approve it and copy the text out.",
    },
    "history": {
        "title": "Everything you have approved",
        "body": (
            "Only approved, cleaned text is saved here, on this computer. Nothing is "
            "uploaded anywhere. Every saved package has a button to download it as a "
            "text file, which goes to your Downloads folder."
        ),
        "next": "",
    },
}


def stage_intro(stage: str) -> None:
    """The heading, the instructions, and what comes after this screen."""
    guide = STAGE_GUIDE.get(stage)
    if not guide:
        return
    st.markdown(f"#### {guide['title']}")
    st.markdown(guide["body"])
    if guide["next"]:
        st.caption(guide["next"])


def start_here() -> None:
    """The panel a first-time user reads before touching anything.

    Open by default. Streamlit remembers nothing between runs, so a returning user
    would have to close it every time; the checkbox in the sidebar is what turns it
    off for good.
    """
    with st.expander("Start here. What is this and what do I do?", expanded=True):
        st.markdown(WHAT_THIS_IS)
        st.markdown("**The five steps**")
        for label, detail in STEPS_PLAIN:
            st.markdown(f"- **{label}** {detail}")
        st.caption(HOW_LONG)


# ---------------------------------------------------------------------------
# Setup, in the words of someone who has never opened a terminal
# ---------------------------------------------------------------------------


def setup_check(nvidia_ready: bool, mesh_ready: bool) -> bool:
    """Tell the user exactly what to do if the app cannot write anything yet.

    Returns True when the app is usable. A missing key used to surface as a
    provider error at generation time, several clicks after the point where it
    could have been fixed.
    """
    if nvidia_ready or mesh_ready:
        return True

    st.error("The app cannot write anything yet. It needs one key first.")
    st.markdown(
        "A key is a password that lets this app talk to an AI model. It is free to "
        "get. You only do this once.\n\n"
        "1. Go to **https://build.nvidia.com** and sign up.\n"
        "2. Copy your API key.\n"
        "3. In the app's folder, find the file called **.env.example** and make a "
        "copy of it named **.env**\n"
        "4. Open **.env** in Notepad. Paste your key after `NVIDIA_API_KEY=`\n"
        "5. Save the file and restart the app.\n\n"
        "Your key stays on this computer. It is never shown on screen and never "
        "saved into the project."
    )
    return False


# ---------------------------------------------------------------------------
# Worked examples, so the first run is never a blank page
# ---------------------------------------------------------------------------

# Lifted from the grounded cases in the evaluation set, which are the briefs known
# to produce publishable output. A first-time user pressing "Fill an example"
# should see the app succeed, not watch it block on an empty proof field.
EXAMPLES: dict[str, dict[str, str]] = {
    "Ali Moizuddin": {
        "core_idea": (
            "The bottleneck in automation is describing the work clearly, not the tools."
        ),
        "proof": (
            "n8n SDR research pipeline built with n8n and Apify. Manual lead research "
            "took 15 minutes per lead, roughly 5 hours per 20 lead batch. The pipeline "
            "replaced that with an automated run: Apollo sourcing, Apify enrichment, an "
            "AI quality gate, lead scoring and routing, CRM logging."
        ),
        "audience": "Non-technical founders and operators",
    },
    "Isshita Debnath": {
        "core_idea": (
            "A resume summary that describes a hope reads differently from one that "
            "describes a decision."
        ),
        "proof": (
            "900+ ATS resumes crafted. The pattern shows up across the whole set, not "
            "in any one application."
        ),
        "audience": "Freshers and early-career job seekers",
    },
    "Rakhee Singhi": {
        "core_idea": "A craving is information about the body, not a failure of discipline.",
        "proof": (
            "Her own kitchen. Tamarind rice powder over eggs when a familiar Indian "
            "flavour was the actual craving, not the packaged snack her eyes went to "
            "first."
        ),
        "audience": "Midlife women and working professionals in India",
    },
}


# ---------------------------------------------------------------------------
# Turning a rule into an instruction
# ---------------------------------------------------------------------------

# The auditor states what is wrong, because that is what an auditor is for. A
# person who has just been stopped needs the next action instead. These are
# matched on a fragment of the finding, longest first, so a specific message wins
# over a general one.
FIXES: tuple[tuple[str, str], ...] = (
    ("[OPEN SLOT]", "Put the real detail in, or delete the sentence that needed it."),
    ("cure", "Take out the claim that something cures or fixes a condition."),
    ("medication", "Take out the advice about medication. Say what happened to her, not to the reader."),
    ("prevent", "Take out the claim that a food prevents a disease."),
    ("fasting", "Take out the fasting hours. Describe the experience without a schedule."),
    ("calorie", "Take out the calorie or goal weight framing."),
    ("names an individual", "Take the person's name out. Describe the situation, not who it was."),
    ("candidate", "Remove the details that would identify one candidate."),
    ("salary", "Take the pay detail out."),
    ("guarantee", "Take out the promise of a job, an interview, or a result."),
    ("client", "Take out the mention of clients. Say what you built, not who paid for it."),
    ("viral", "Take out the promise about reach or going viral."),
    ("unverified", "This number is not on the verified list. Put the proof in the brief, or remove the number."),
    ("UNSUPPORTED", "Nothing in the brief backs this up. Add the proof, or cut the claim."),
    ("BLOCKED", "This exact wording is not allowed. Rewrite the sentence without it."),
)


def fix_for(finding_text: str) -> str:
    """The action that clears this finding, or a safe general instruction."""
    lowered = finding_text.lower()
    for fragment, instruction in FIXES:
        if fragment.lower() in lowered:
            return instruction
    return "Edit the wording this refers to, then run the check again."
