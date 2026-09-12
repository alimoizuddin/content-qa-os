// Ali's own speaker script: only the screen and the words. Not part of the repo.
// The spoken lines come from loom_parts.js, shared with the rehearsal guide.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Footer,
  AlignmentType, HeadingLevel, WidthType, ShadingType, BorderStyle, PageNumber,
} = require("docx");
const { PARTS } = require("./loom_parts");

const path = require("path");
const PRIVATE = path.join(__dirname, "..", "private");
fs.mkdirSync(PRIVATE, { recursive: true });
const OUT = path.join(PRIVATE, "My_Loom_Script.docx");
const NAVY = "1F3864", GOLD = "C9A84C", GREY = "F2F2F2", LINE = "BFBFBF";
const W = 9638, COLS = [3600, 6038];

function runs(text, base = {}) {
  const out = [];
  for (const piece of String(text).split(/(\*\*[^*]+\*\*|\*[^*]+\*)/)) {
    if (!piece) continue;
    if (piece.startsWith("**")) out.push(new TextRun({ ...base, text: piece.slice(2, -2), bold: true }));
    else if (piece.startsWith("*")) out.push(new TextRun({ ...base, text: piece.slice(1, -1), italics: true, color: "7A1F1F" }));
    else out.push(new TextRun({ ...base, text: piece }));
  }
  return out;
}
const b = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const borders = { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b };
const cell = (text, width, fill, run = {}) => new TableCell({
  width: { size: width, type: WidthType.DXA },
  shading: fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
  margins: { top: 110, bottom: 110, left: 150, right: 150 },
  children: [new Paragraph({ children: runs(text, run) })],
});

const children = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("My Loom Script")] }),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Five minutes. Screen on the left. Words on the right. Say it in your own words.", color: "595959" })] }),
  new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Before you press record")] }),
];
[
  "Double-click **run.bat**. Wait for the app to open in your browser.",
  "On the left, under **Who is posting?**, pick **Rakhee Singhi**.",
  "Open **summary.pdf** in another window, on the table with three columns.",
  "Start Loom: **Screen only**, **Full screen**.",
].forEach((t, i) => children.push(new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: `${i + 1}.  `, bold: true, color: NAVY }), ...runs(t)] })));

PARTS.forEach((part, i) => {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: i > 0 && i % 2 === 0, children: [new TextRun(part.name)] }));
  children.push(new Paragraph({ spacing: { after: 140 }, children: [new TextRun({ text: part.time, color: NAVY, bold: true })] }));
  children.push(new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: COLS, borders,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: [cell("**Screen**", COLS[0], NAVY, { color: "FFFFFF" }), cell("**Say**", COLS[1], NAVY, { color: "FFFFFF" })] }),
      ...part.rows.map(([s, say]) => new TableRow({ cantSplit: true, children: [cell(s, COLS[0], GREY), cell(say, COLS[1])] })),
    ],
  }));
  children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
});

const fr = (o) => new TextRun({ size: 18, color: "808080", ...o });
const doc = new Document({
  creator: "Ali Moizuddin", title: "My Loom Script",
  styles: {
    default: { document: { run: { font: "Arial", size: 26 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 52, bold: true, color: NAVY }, paragraph: { spacing: { after: 100 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 300, after: 60 }, outlineLevel: 0, keepNext: true, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: GOLD, space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [fr({ text: "My Loom Script   |   Page " }), fr({ children: [PageNumber.CURRENT] }), fr({ text: " of " }), fr({ children: [PageNumber.TOTAL_PAGES] })] })] }) },
    children,
  }],
});

if (/[\u2013\u2014]/.test(JSON.stringify(PARTS))) throw new Error("A dash got into the script.");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
