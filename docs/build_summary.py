"""Build summary.pdf, the two-page explanation document.

Content and layout live together here on purpose. This is a one-page-each
document with a fixed shape, and splitting the words from the styling would mean
editing two files to move a line.

ReportLab is a documentation-only dependency. It is listed in
requirements-docs.txt and is not needed to run the studio.

    python docs/build_summary.py
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "summary.pdf"

INK = colors.HexColor("#141414")
MUTED = colors.HexColor("#5A5A5A")
ACCENT = colors.HexColor("#9A7B22")
RULE = colors.HexColor("#D8D4CA")
PANEL = colors.HexColor("#F6F4EF")


def styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=17,
            leading=20, textColor=INK, spaceAfter=1,
        ),
        "sub": ParagraphStyle(
            "S", parent=base["Normal"], fontName="Helvetica", fontSize=9.5,
            leading=12.5, textColor=MUTED, spaceAfter=8,
        ),
        "h": ParagraphStyle(
            "H", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10.5,
            leading=13, textColor=ACCENT, spaceBefore=9, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName="Helvetica", fontSize=9.2,
            leading=12.6, textColor=INK, alignment=TA_LEFT, spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "Sm", parent=base["Normal"], fontName="Helvetica", fontSize=8.2,
            leading=11, textColor=MUTED, spaceAfter=4,
        ),
        "cell": ParagraphStyle(
            "C", parent=base["Normal"], fontName="Helvetica", fontSize=8.4,
            leading=11, textColor=INK,
        ),
        "cellb": ParagraphStyle(
            "Cb", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8.4,
            leading=11, textColor=INK,
        ),
    }


S = styles()


def p(text: str, key: str = "body") -> Paragraph:
    return Paragraph(text, S[key])


def table(rows: list[list[str]], widths: list[float], header: bool = True) -> Table:
    data = [
        [p(c, "cellb" if (header and r == 0) else "cell") for c in row]
        for r, row in enumerate(rows)
    ]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), PANEL),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ]
    t.setStyle(TableStyle(style))
    return t


FULL = 176 * mm


def story() -> list:
    s: list = []

    # ---------------------------------------------------------------- page 1
    s.append(p("LinkedIn Content Studio", "title"))
    s.append(p(
        "An AI OS Mini that turns one idea into a checked, publishable LinkedIn "
        "package. Ali Moizuddin, AI Automation Engineer, Siliguri.", "sub"))

    s.append(p("The user and the problem", "h"))
    s.append(p(
        "I write LinkedIn content for three people: myself, an HR leader, and a "
        "health coach. Three posts a week for me, four a week for each of them. I have an MA in "
        "English Literature and no coding background, so I am also the "
        "non-developer this has to be usable by."))
    s.append(p(
        "<b>The slow part was never the writing. It was the checking.</b> A general "
        "AI tool produces text in thirty seconds and hands back all the "
        "verification. Three things go wrong every time:"))
    s.append(p(
        "<b>Invented numbers.</b> A model asked to sound confident adds a figure "
        "that fits the shape. Nobody asked for it. If I miss one it goes public "
        "under a real person's name.<br/>"
        "<b>Voice rules broken quietly.</b> No em dashes, no engagement bait, five "
        "hashtags maximum, no links in the body. Broken copy still reads fine, so "
        "it only shows up on a re-read.<br/>"
        "<b>Claims that cannot be published at all.</b> The health coach cannot say "
        "food cures or reverses a condition, or tell a reader to stop taking "
        "medication. The HR leader cannot name a candidate, discuss pay, or promise "
        "a job. These are not style preferences."))

    s.append(p("The core workflow", "h"))
    s.append(p(
        "<b>Brief &rarr; Generate &rarr; Edit and preview &rarr; QA and approve "
        "&rarr; History.</b> Five steps, fixed order."))
    s.append(p(
        "The brief collects the person, goal, audience, core idea and <b>proof</b>. "
        "Proof is the grounding contract: any number typed there is treated as "
        "verified for that piece. Leave it empty and the system marks every place "
        "it wanted evidence and refuses to approve."))
    s.append(p(
        "QA has two layers. <b>Style advice never blocks</b>, because voice is a "
        "judgement and the writer gets the last word. <b>Facts and safety do "
        "block.</b> An unverified number is replaced with an open slot rather than "
        "flagged, because a flagged number in an editable box gets pasted by "
        "accident. The check runs on whatever is in the boxes at that moment, so "
        "you cannot generate something clean and paste something dangerous in "
        "afterwards. There is no override button in the app."))
    s.append(p(
        "The carousel renders locally to 1080&times;1350 slides with a PDF and a "
        "ZIP. No image service, no internet, no remote font."))

    s.append(p("Main decisions and trade-offs", "h"))
    s.append(table([
        ["Decision", "Why", "Cost accepted"],
        ["Block, do not warn, on facts and safety",
         "A warning in an editable box gets published by accident",
         "Some correct content gets stopped"],
        ["No posting to LinkedIn",
         "The writing was never the slow part. Automating publishing solves the "
         "wrong step",
         "A human step remains"],
        ["Carousel rendered locally, not by an image service",
         "The full asset set must work with one text provider and no extra keys",
         "Design is code, not a canvas"],
        ["Style advice never blocks",
         "A linter that argues with a person's own vocabulary gets ignored "
         "entirely",
         "Cliches can ship"],
        ["Three people, hard-coded",
         "A fourth is a code change. That is the honest state of it",
         "Not a product yet"],
    ], [40 * mm, 78 * mm, 58 * mm]))

    s.append(PageBreak())

    # ---------------------------------------------------------------- page 2
    s.append(p("What I measured", "h"))
    s.append(p(
        "20 written test cases, two arms, same model "
        "(<font face='Helvetica-Oblique'>nemotron-3-super-120b</font>). "
        "<b>Studio</b> is the full system. <b>Control</b> is the same model told "
        "clearly who it is writing for and what to write, and nothing else. That is "
        "a fair version of using ChatGPT well, because it is what I did before."))
    s.append(p(
        "The scorer that judges both arms shares no code with the app. If it used "
        "the app's own checking, the app would score perfectly by definition. That "
        "independence immediately found a safety gap the app's own rule had missed."))

    s.append(Spacer(1, 2))
    s.append(table([
        ["", "Studio", "Control"],
        ["Produced a usable result", "19 of 20", "14 of 20"],
        ["Published something unpublishable", "0", "11"],
        ["Serious violations reaching the page", "0", "41"],
        ["Normal briefs ready to publish", "4 of 6", "5 of 5"],
    ], [86 * mm, 45 * mm, 45 * mm]))
    s.append(Spacer(1, 4))
    s.append(p(
        "What the control published unprompted: a fasting schedule with exact hours, a "
        "named candidate, a superlative with its qualifier removed, \"zero human "
        "oversight\", \"CAC to zero\", and <b>a figure I had publicly withdrawn as "
        "invented</b>. Case A12 asks for that one directly. The control wrote it. The "
        "studio refused. Numbers move between runs; safety has held at zero across "
        "three, usability has not.", "small"))

    s.append(p("What the evaluation changed", "h"))
    s.append(p(
        "The first run was worse: 17 of 20 produced, one unpublishable thing "
        "shipped, 2 of 5 normal briefs clean. Five fixes came out of reading the "
        "failures. The one that mattered: a post kept every medication sentence in "
        "the first person, which the safety rule was written to permit, and still "
        "closed by telling the reader their daily pill might be unnecessary. The "
        "exemption is now cancelled by any sentence that speaks to the reader."))
    s.append(p(
        "Two of the five could not have been found by the unit tests, because both "
        "needed a real generated calendar to exist first. 136 offline tests were "
        "passing before any of them surfaced.", "small"))

    s.append(p("Expected impact, and what is not measured", "h"))
    s.append(table([
        ["Metric", "Evidence", "Status"],
        ["Unpublishable content reaching a draft",
         "Control 13 of 15. Studio 0", "<b>Measured</b>"],
        ["Usable result produced", "Control 15 of 20. Studio 20 of 20",
         "<b>Measured</b>"],
        ["Normal briefs needing no human fix", "4 of 6. Noisy: 2/5, 6/7, 4/6 across runs",
         "<b>Measured</b>"],
        ["My review time per package",
         "30 to 60 min by hand, then ~5 min with the engines",
         "<b>Estimate from memory. The saving belongs to the engines, not this app</b>"],
        ["Adoption", "System is one week old", "<b>Not measured</b>"],
        ["LinkedIn reach or engagement", "Out of scope",
         "<b>Not measured. Not claimed</b>"],
    ], [56 * mm, 66 * mm, 54 * mm]))

    s.append(p("Limitations", "h"))
    s.append(p(
        "<b>Two normal briefs in six still get blocked.</b> The model adds a "
        "number the brief did not supply, the checker correctly removes it, and a "
        "person has to delete the sentence. The checker is right and the writing is "
        "wrong. Reduced, not eliminated."))
    s.append(p(
        "<b>My time saving is not measured.</b> The before-numbers are recollection "
        "and are labelled as estimates throughout. <b>20 cases is small</b> and is "
        "not a statistical result. <b>The labels are my judgement</b>: \"this must "
        "not be published\" is a human call, and the reasoning for each case is "
        "written down so it can be argued with. <b>One model</b>: the numbers would "
        "move on another."))
    s.append(p(
        "<b>A prototype existed before the Quest.</b> About 1,200 lines that "
        "generated text and audited it. The rebuild, the evaluation and the "
        "evidence are what I am claiming; not a build from nothing."))

    s.append(p("Next two weeks", "h"))
    s.append(p(
        "1. Time five real posts with a stopwatch, so the time claim becomes a "
        "measurement. 2. Close the last blocking case. 3. Have one person who is "
        "not me open it cold and reach a finished carousel unaided. 4. Re-run the "
        "evaluation after each change, which the recorded run makes free."))

    return s


def main() -> int:
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=15 * mm, bottomMargin=14 * mm,
        title="LinkedIn Content Studio", author="Ali Moizuddin",
    )
    doc.build(story())
    print("wrote:", OUT, OUT.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
