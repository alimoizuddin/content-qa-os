"""Ali's personal checklist of what is left, as a colourful printable PDF."""
import pathlib

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PRIVATE = pathlib.Path(__file__).resolve().parent.parent / "private"
PRIVATE.mkdir(exist_ok=True)
OUT = str(PRIVATE / "My_Checklist.pdf")

NAVY, GOLD = colors.HexColor("#1F3864"), colors.HexColor("#C9A84C")
INK, MUTED, WHITE = colors.HexColor("#1B1F2A"), colors.HexColor("#5B6472"), colors.white
GROUPS = [
    ("Before you record", colors.HexColor("#2F6FDB"), colors.HexColor("#EAF1FD")),
    ("Record your video", colors.HexColor("#1E9E6A"), colors.HexColor("#E6F6EE")),
    ("Finish and submit", colors.HexColor("#7B4FD6"), colors.HexColor("#F1EBFC")),
]

W = A4[0] - 32 * mm


def st(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


TITLE = st("t", fontName="Helvetica-Bold", fontSize=12, leading=16)
HOW = st("h", fontSize=10, leading=14)
WHY = st("w", fontSize=9, leading=12.5, textColor=MUTED)

ITEMS = [
    # group, title, how, why
    (0, "Decide about Isshita and Rakhee",
     "Pick one. <b>Option 1:</b> get a short written yes from each of them, then tell "
     "Claude to add one line to directive.md saying they agreed. <b>Option 2:</b> tell "
     "Claude to swap them for made-up people.",
     "The brief says do not submit real personal data, and exposed personal data is on "
     "its fail list. Rakhee's weight and age history is in the project."),
    (0, "Change your Mesh key",
     "Go to meshapi.ai. Make a new key and delete the old one. Open the <b>.env</b> file "
     "in the project folder with Notepad. Paste the new key after <b>MESH_API_KEY=</b> "
     "and save.",
     "The old key was pasted into a chat. The app needs a working key for your video."),
    (0, "Read your AI Collaboration Note",
     "Open <b>docs/AI_COLLABORATION.md</b>. Wherever it says <b>Confirm</b>, check it is "
     "true. Tell Claude anything you want changed.",
     "It is your statement about your own work. Only you can sign it."),
    (0, "Read the four files you say you can explain",
     "core/personas.py, core/auditor.py, core/studio.py and evals/scoring.py. Read what "
     "each one decides. You do not need to understand every line.",
     "Your note says you can explain them. A reviewer may ask."),
    (0, "Optional, but strong: let a friend try it",
     "Give a friend <b>START_HERE.pdf</b> and the folder. Let them set it up with no help "
     "from you. Write down anything they got stuck on and tell Claude.",
     "Nobody but you has run it cold. This is the best proof a handoff works."),
    (1, "Practise with My Loom Script",
     "Read it out loud once. Then click through once without talking. Then do one full "
     "run with a timer. Aim for under five and a half minutes.",
     "Say it in your own words. Do not practise more than this."),
    (1, "Get the screen ready",
     "Close WhatsApp, email and Slack. Double-click <b>run.bat</b>. Pick <b>Rakhee "
     "Singhi</b>. Open <b>summary.pdf</b> in another window.",
     "Nothing should pop up while you record."),
    (1, "Record the video",
     "In Loom choose <b>Screen only</b> and <b>Full screen</b>. Record. Two takes at most.",
     "The second take is usually the best one."),
    (1, "Copy the Loom link", "Copy the share link Loom gives you.", ""),
    (2, "Put the Loom link in directive.md",
     "Easiest: send the link to Claude. Or open directive.md and replace <b>ALI: paste "
     "the Loom URL here after recording.</b> with your link.", ""),
    (2, "Choose your consent line",
     "At the very end of directive.md there are two lines about MUST Hunt. Keep one and "
     "delete the other. Easiest: tell Claude which one.", "This is your decision."),
    (2, "Give the reviewers access on GitHub",
     "Ask Janeth which GitHub username to add. Then on GitHub open your project, click "
     "<b>Settings</b>, then <b>Collaborators</b>, then <b>Add people</b>, and type it in.",
     "The project is private. Without access they cannot run it."),
    (2, "Submit the five deliverables on the Match Hire page",
     "<b>1. Working system:</b> https://github.com/alimoizuddin/content-qa-os<br/>"
     "<b>2. Evaluation package:</b> docs/EVALUATION.md and evals/results/latest.json<br/>"
     "<b>3. Case study:</b> directive.md and summary.pdf<br/>"
     "<b>4. AI Collaboration Note:</b> docs/AI_COLLABORATION.md<br/>"
     "<b>5. Demo video:</b> your Loom link", ""),
    (2, "Tell Janeth you have submitted",
     "Send her a short message on LinkedIn saying the Quest is submitted.", ""),
]


class Box(Flowable):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour

    def wrap(self, aw, ah):
        return 16, 16

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.colour)
        c.setLineWidth(1.6)
        c.setFillColor(WHITE)
        c.roundRect(0, 0, 15, 15, 3, stroke=1, fill=1)


class Header(Flowable):
    def wrap(self, aw, ah):
        return W, 40 * mm

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, W, 40 * mm, 10, stroke=0, fill=1)
        c.setFillColor(GOLD)
        c.rect(0, 40 * mm - 6, W, 6, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(12 * mm, 24 * mm, "Your checklist")
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(12 * mm, 16 * mm, "What is left for you, in order. Tick each box when it is done.")
        c.setFillColor(colors.HexColor("#DCE3EF"))
        c.setFont("Helvetica", 10)
        c.drawString(12 * mm, 9 * mm, f"{len(ITEMS)} things. Everything else is already done and on GitHub.")


class Band(Flowable):
    def __init__(self, text, colour, count):
        super().__init__()
        self.text, self.colour, self.count = text, colour, count

    def wrap(self, aw, ah):
        return W, 11 * mm

    def draw(self):
        c = self.canv
        c.setFillColor(self.colour)
        c.roundRect(0, 0, W, 11 * mm, 6, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13.5)
        c.drawString(5 * mm, 3.6 * mm, self.text)
        c.setFont("Helvetica", 10)
        c.drawRightString(W - 5 * mm, 3.8 * mm, self.count)


story = [Header(), Spacer(1, 5 * mm)]
tip = Table([[Paragraph(
    '<font color="#D98A0B"><b>Changing a file.</b></font>  The easiest way is to tell '
    "Claude what to change. Or change it on GitHub: open the file, click the pencil, "
    "change it, then click <b>Commit changes</b>.", HOW)]], colWidths=[W])
tip.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4DE")),
    ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor("#D98A0B")),
    ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story += [tip, Spacer(1, 5 * mm)]

number = 0
for g, (name, colour, tint) in enumerate(GROUPS):
    items = [it for it in ITEMS if it[0] == g]
    first = True
    for _, title, how, why in items:
        number += 1
        content = [Paragraph(f'<font color="{colour.hexval().replace("0x", "#")}">{number}.</font>  {title}', TITLE),
                   Spacer(1, 2), Paragraph(how, HOW)]
        if why:
            content += [Spacer(1, 2), Paragraph(f"<i>Why: {why}</i>", WHY)]
        row = Table([[Box(colour), content]], colWidths=[10 * mm, W - 10 * mm])
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), tint if number % 2 else WHITE),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE2EA")),
        ]))
        if first:
            story.append(KeepTogether([Band(name, colour, f"{len(items)} steps"), Spacer(1, 3), row]))
            first = False
        else:
            story.append(KeepTogether([row]))
    story.append(Spacer(1, 5 * mm))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.line(16 * mm, 11 * mm, A4[0] - 16 * mm, 11 * mm)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, 7 * mm, "Your checklist   |   MUST Company Quest")
    canvas.drawRightString(A4[0] - 16 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm,
                  bottomMargin=16 * mm, title="Your checklist", author="Ali Moizuddin").build(
    story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
