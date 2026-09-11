"""Build START_HERE.pdf, a colourful printable version of START_HERE.md.

The PDF is generated from the Markdown every time, so the two can never say
different things. Edit START_HERE.md, then run:

    python docs/build_start_here.py

ReportLab is a documentation-only dependency, listed in requirements-docs.txt.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "START_HERE.md"
OUT = ROOT / "START_HERE.pdf"

NAVY = colors.HexColor("#1F3864")
GOLD = colors.HexColor("#C9A84C")
INK = colors.HexColor("#1B1F2A")
MUTED = colors.HexColor("#5B6472")
RULE = colors.HexColor("#DDE2EA")
WHITE = colors.white

# One colour per part, so a reader always knows which part they are in.
PART_COLOURS = [
    (colors.HexColor("#2F6FDB"), colors.HexColor("#EAF1FD")),  # Part 1, blue
    (colors.HexColor("#1E9E6A"), colors.HexColor("#E6F6EE")),  # Part 2, green
    (colors.HexColor("#7B4FD6"), colors.HexColor("#F1EBFC")),  # Part 3, purple
]
INTRO_COLOURS = (NAVY, colors.HexColor("#EEF2F8"))

RED = (colors.HexColor("#D64545"), colors.HexColor("#FDECEC"))
AMBER = (colors.HexColor("#D98A0B"), colors.HexColor("#FFF4DE"))
GREEN = (colors.HexColor("#1E9E6A"), colors.HexColor("#E6F6EE"))
BLUE = (colors.HexColor("#2F6FDB"), colors.HexColor("#EAF1FD"))
PURPLE = (colors.HexColor("#7B4FD6"), colors.HexColor("#F1EBFC"))

# Paragraphs that deserve a coloured box, found by how they start.
CALLOUTS = [
    ("Never share your key", "Keep it secret", RED),
    ("Only write things about yourself", "Privacy", RED),
    ("If Windows shows", "If you see a blue box", AMBER),
    ("This part means editing code", "Go slowly", AMBER),
    ("That is it.", "Done", GREEN),
    ("One of the tests proves", "Checked for you", GREEN),
    ("**On a Mac:**", "Mac", BLUE),
    ("**Want better writing", "Optional", PURPLE),
]

PAGE_W, PAGE_H = A4
MARGIN = 16 * mm
WIDTH = PAGE_W - 2 * MARGIN


def style(name: str, **kw) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


BODY = style("body", spaceAfter=6)
SMALL = style("small", fontSize=9.5, leading=13.5)
CELL = style("cell", fontSize=9.5, leading=13)
CELL_HEAD = style("cellhead", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=WHITE)
H2 = style("h2", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY,
           spaceBefore=10, spaceAfter=6)
STEP_TEXT = style("steptext", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=INK)


# --------------------------------------------------------------- Markdown in
def inline(text: str) -> str:
    """Markdown inline marks to ReportLab paragraph markup."""
    codes: list[str] = []

    def keep(match):
        codes.append(match.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(
        r"(https?://[^\s)]+?)([.,]?)(?=\s|$)",
        r'<link href="\1" color="#2F6FDB"><u>\1</u></link>\2',
        text,
    )

    def put(match):
        code = html.escape(codes[int(match.group(1))], quote=False)
        # Short code stays on one line, so "# Registry" never splits after the "#".
        # Long commands still wrap, or they would run off the page.
        if len(code) <= 30:
            code = code.replace(" ", "&nbsp;")
        return f'<font face="Courier-Bold" color="#8A1C1C">{code}</font>'

    return re.sub(r"\x00(\d+)\x00", put, text)


def parse(md: str) -> list[tuple]:
    """Split the Markdown into blocks: headings, paragraphs, lists, tables."""
    lines = md.splitlines()
    blocks: list[tuple] = []
    i = 0
    numbered = re.compile(r"^(\d+)\.\s+(.*)")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
            i += 1
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            i += 1
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            i += 1
        elif line.strip() == "---":
            blocks.append(("hr",))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            blocks.append(("table", rows[0], rows[1:]))
        elif numbered.match(line):
            items: list[list[str]] = []
            while i < len(lines):
                match = numbered.match(lines[i])
                if match:
                    items.append([match.group(1), match.group(2)])
                elif lines[i].startswith("   ") and lines[i].strip() and items:
                    items[-1][1] += " " + lines[i].strip()
                else:
                    break
                i += 1
            blocks.append(("ol", items))
        elif line.startswith("- "):
            bullets: list[str] = []
            while i < len(lines) and (
                lines[i].startswith("- ") or (lines[i].startswith("  ") and lines[i].strip())
            ):
                if lines[i].startswith("- "):
                    bullets.append(lines[i][2:].strip())
                else:
                    bullets[-1] += " " + lines[i].strip()
                i += 1
            blocks.append(("ul", bullets))
        else:
            para = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"^(#|\||---|\d+\.\s|- )", lines[i])
            ):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


# ------------------------------------------------------------ drawn elements
class Cover(Flowable):
    """The coloured title block on page one, with a chip for each part."""

    def __init__(self, title: str, intro: list[str], parts: list[str]):
        super().__init__()
        self.title, self.intro, self.parts = title, intro, parts
        self.height = 78 * mm

    def wrap(self, aw, ah):
        return WIDTH, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, WIDTH, self.height, 10, stroke=0, fill=1)
        c.setFillColor(GOLD)
        c.rect(0, self.height - 6, WIDTH, 6, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 34)
        c.drawString(14 * mm, self.height - 22 * mm, self.title)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(14 * mm, self.height - 30 * mm, "LinkedIn Content Studio")
        y = self.height - 40 * mm
        for line in self.intro:
            p = Paragraph(
                inline(line),
                style("coverp", fontSize=10.5, leading=14.5, textColor=colors.HexColor("#DCE3EF")),
            )
            _, h = p.wrap(WIDTH - 28 * mm, 100)
            p.drawOn(c, 14 * mm, y - h)
            y -= h + 3
        x, chip_w, chip_h, gap = 14 * mm, (WIDTH - 28 * mm - 2 * 5 * mm) / 3, 11 * mm, 5 * mm
        for index, label in enumerate(self.parts[:3]):
            colour, _ = PART_COLOURS[index]
            c.setFillColor(colour)
            c.roundRect(x, 8 * mm, chip_w, chip_h, 5, stroke=0, fill=1)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 10.5)
            c.drawCentredString(x + chip_w / 2, 8 * mm + chip_h / 2 - 3.5, label)
            x += chip_w + gap


class Banner(Flowable):
    """A full-width coloured band that opens each part."""

    def __init__(self, label: str, title: str, colour):
        super().__init__()
        self.label, self.title, self.colour = label, title, colour

    def wrap(self, aw, ah):
        return WIDTH, 16 * mm

    def draw(self):
        c = self.canv
        c.setFillColor(self.colour)
        c.roundRect(0, 0, WIDTH, 16 * mm, 8, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(6 * mm, 10.5 * mm, self.label.upper())
        c.setFont("Helvetica-Bold", 17)
        c.drawString(6 * mm, 4 * mm, self.title)


class Badge(Flowable):
    """A coloured circle with a number in it."""

    def __init__(self, text: str, colour, size: float = 18):
        super().__init__()
        self.text, self.colour, self.size = text, colour, size

    def wrap(self, aw, ah):
        return self.size, self.size

    def draw(self):
        c = self.canv
        c.setFillColor(self.colour)
        c.circle(self.size / 2, self.size / 2, self.size / 2, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(self.size / 2, self.size / 2 - 3.3, self.text)


# ------------------------------------------------------------------ builders
def callout(text: str, title: str, pair) -> Table:
    colour, tint = pair
    body = Paragraph(
        f'<font color="{colour.hexval().replace("0x", "#")}"><b>{title}.</b></font>  {inline(text)}',
        SMALL,
    )
    t = Table([[body]], colWidths=[WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("LINEBEFORE", (0, 0), (0, -1), 4, colour),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def numbered_list(items, pair) -> list:
    colour, tint = pair
    rows = [[Badge(n, colour), Paragraph(inline(text), BODY)] for n, text in items]
    t = Table(rows, colWidths=[9 * mm, WIDTH - 9 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [t]


def bullet_list(items, pair) -> list:
    colour, _ = pair
    hexcol = colour.hexval().replace("0x", "#")
    return [
        Paragraph(f'<font color="{hexcol}"><b>&#9679;</b></font>&nbsp;&nbsp;{inline(text)}', BODY)
        for text in items
    ]


def table(header, rows, pair) -> Table:
    colour, tint = pair
    data = [[Paragraph(inline(h), CELL_HEAD) for h in header]]
    data += [[Paragraph(inline(c), CELL) for c in row] for row in rows]
    first = 0.38 if len(header) == 2 else 1 / len(header)
    widths = [WIDTH * first] + [WIDTH * (1 - first) / (len(header) - 1)] * (len(header) - 1)
    t = Table(data, colWidths=widths, repeatRows=1)
    style_rows = [
        ("BACKGROUND", (0, 0), (-1, 0), colour),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            style_rows.append(("BACKGROUND", (0, r), (-1, r), tint))
    t.setStyle(TableStyle(style_rows))
    return t


def step_heading(text: str, pair) -> Table:
    """ "Step 3. Get your free key" becomes a coloured STEP 3 pill and a title."""
    colour, tint = pair
    match = re.match(r"^(Step \d+|\d+[a-z])\.\s+(.*)", text)
    padding = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if not match:
        # A heading that is not a numbered step: a tinted bar with a coloured edge.
        t = Table([[Paragraph(inline(text), STEP_TEXT)]], colWidths=[WIDTH])
        t.setStyle(TableStyle(padding + [
            ("BACKGROUND", (0, 0), (-1, -1), tint),
            ("LINEBEFORE", (0, 0), (0, -1), 4, colour),
        ]))
        return t
    pill = Paragraph(
        f'<font color="white"><b>{html.escape(match.group(1).upper())}</b></font>',
        style("pill", fontSize=9, leading=12, alignment=1),
    )
    t = Table([[pill, Paragraph(inline(match.group(2)), STEP_TEXT)]],
              colWidths=[22 * mm, WIDTH - 22 * mm])
    t.setStyle(TableStyle(padding + [
        ("BACKGROUND", (0, 0), (0, 0), colour),
        ("BACKGROUND", (1, 0), (1, 0), tint),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.line(MARGIN, 11 * mm, PAGE_W - MARGIN, 11 * mm)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 7 * mm, "Start Here   |   LinkedIn Content Studio")
    canvas.drawRightString(PAGE_W - MARGIN, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build() -> None:
    blocks = parse(SOURCE.read_text(encoding="utf-8"))

    title = next(b[1] for b in blocks if b[0] == "h1")
    first_rule = next(i for i, b in enumerate(blocks) if b[0] == "hr")
    intro = [b[1] for b in blocks[:first_rule] if b[0] == "p"]
    part_titles = [b[1] for b in blocks if b[0] == "h2" and b[1].startswith("Part ")]
    chips = [re.sub(r"^Part (\d+)\.\s*", r"\1   ", t) for t in part_titles]

    story: list = [Cover(title, intro, chips), Spacer(1, 8 * mm)]
    pair = INTRO_COLOURS
    part_index = -1
    pending_heading = None

    def add(flowable):
        nonlocal pending_heading
        if pending_heading is not None:
            story.append(KeepTogether([pending_heading, Spacer(1, 4), flowable]))
            pending_heading = None
        else:
            story.append(flowable)

    for block in blocks[first_rule + 1:]:
        kind = block[0]
        if kind == "hr":
            story.append(Spacer(1, 5 * mm))
        elif kind == "h2":
            text = block[1]
            match = re.match(r"^Part (\d+)\.\s*(.*)", text)
            if match:
                part_index = int(match.group(1)) - 1
                pair = PART_COLOURS[part_index % len(PART_COLOURS)]
                pending_heading = Banner(f"Part {match.group(1)}", match.group(2), pair[0])
            else:
                pending_heading = Paragraph(inline(text), H2)
        elif kind == "h3":
            if pending_heading is not None:
                story.append(pending_heading)
                story.append(Spacer(1, 4))
            pending_heading = step_heading(block[1], pair)
        elif kind == "p":
            text = block[1]
            for start, label, colours in CALLOUTS:
                if text.startswith(start):
                    add(callout(text, label, colours))
                    break
            else:
                add(Paragraph(inline(text), BODY))
            story.append(Spacer(1, 3))
        elif kind == "ol":
            for flowable in numbered_list(block[1], pair):
                add(flowable)
            story.append(Spacer(1, 5))
        elif kind == "ul":
            for flowable in bullet_list(block[1], pair):
                add(flowable)
            story.append(Spacer(1, 4))
        elif kind == "table":
            add(table(block[1], block[2], pair))
            story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=16 * mm,
        title="Start Here", author="Ali Moizuddin",
        subject="Setting up and using the LinkedIn Content Studio",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {OUT} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    build()
