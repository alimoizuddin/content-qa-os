// Builds the Loom rehearsal script as a Word document AND as markdown, from one
// content model, so the two can never disagree.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Footer,
  AlignmentType, HeadingLevel, LevelFormat, WidthType, ShadingType, BorderStyle,
  PageNumber,
} = require("docx");

const path = require("path");
const DOCS = path.join(__dirname, "..", "docs");
const OUT_DOCX = path.join(DOCS, "Loom_Rehearsal_Script.docx");
const OUT_MD = path.join(DOCS, "LOOM_SCRIPT.md");

const NAVY = "1F3864";
const GOLD = "C9A84C";
const GREY_FILL = "F2F2F2";
const TIP_FILL = "FFF6DC";
const LINE = "BFBFBF";
const CONTENT = 9638; // A4 width 11906 minus two 1134 margins

// ---------------------------------------------------------------- content
const M = [];
const title = (text, lines) => M.push({ t: "title", text, lines });
const h1 = (text, breakBefore = false) => M.push({ t: "h1", text, breakBefore });
const h2 = (text) => M.push({ t: "h2", text });
const p = (text) => M.push({ t: "p", text });
const bullets = (items) => M.push({ t: "bullets", items });
const steps = (ref, items) => M.push({ t: "steps", ref, items });
const table = (widths, header, rows, opts = {}) => M.push({ t: "table", widths, header, rows, opts });
const tip = (text) => M.push({ t: "tip", text });
const part = (o) => M.push({ t: "part", ...o });

title("Loom Rehearsal Script", [
  "Your 5 minute video of the LinkedIn Content Studio, step by step",
  "For Ali Moizuddin. MUST Company 5-Day AI OS Sprint Quest. Updated 11 September 2026.",
]);

h1("Read this first");
p("This is a script for recording one short screen video, called a Loom. The video shows the judges your app working, and explains why you built it.");
p("You do **not** have to learn it word for word. Say it in your own words. The judges want to see that you understand your own work, and reading aloud sounds like reading.");
p("In the script, every **grey box** tells you what to do on the screen. Every **white box** next to it tells you what to say while you do it.");
p("The video is about 5 minutes long and has 5 parts. If you ever forget a line, look at the screen and say what you see. That is always right.");

h2("The 5 parts at a glance");
table([2300, 1600, 2638, 3100], ["Part", "Time", "What you show", "Screen to have open"], [
  ["**1.** The problem", "0:00 to 1:00", "Why this app exists", "App, **Step 1. Your idea**"],
  ["**2.** Watch it work", "1:00 to 2:30", "Fill the form, let it write, show the slides", "App, **Step 1** then **Step 2** then **Step 3**"],
  ["**3.** Try to break it", "2:30 to 3:30", "Type something unsafe and watch it get stopped", "App, **Step 3** then **Step 4. Safety check**"],
  ["**4.** How I know it works", "3:30 to 4:30", "The test results", "The **summary.pdf** window"],
  ["**5.** What is not finished", "4:30 to 5:00", "The honest limits", "Back to the app"],
], { firstColFill: true });

h2("Words used in this script");
table([2600, 7038], ["Word", "What it means"], [
  ["**App**", "The LinkedIn Content Studio you built. It opens in a web browser, but it runs only on your own computer."],
  ["**Browser tab**", "One page open in Chrome or Edge."],
  ["**Black window**", "The window that opens when you double-click run.bat. It is the app running. Leave it open while you record, and close it to stop the app."],
  ["**Loom**", "The tool that records your screen and your voice."],
  ["**Brief**", "The short form where you describe the post you want."],
  ["**Safety check**", "Step 4 of the app. It reads the post and stops anything false or unsafe."],
  ["**[OPEN SLOT]**", "A gap the app leaves where it needed proof and did not have any."],
  ["**Test cases**", "20 practice requests used to measure the app. 12 of them deliberately ask for things that must never be posted."],
  ["**Claude Project**", "Your old way of working. Your rules are written in a document, and Claude is asked to follow them."],
  ["**Asking plainly**", "Using the AI with no rules at all, the way most people use ChatGPT."],
], { firstColFill: true });

h1("Before you press record");
p("Do this once, about 15 minutes before you record. Tick each one off.");
steps("before", [
  "**Finish the checklist first.** Do steps 1 to 5 of **My_Checklist.pdf** before you record.",
  "**Clear the screen.** Close WhatsApp, Slack, email, and anything else that can pop up. Turn on Do Not Disturb.",
  "**Change your Mesh key first.** If you have not done it yet: make a new key at meshapi.ai, open the file called `.env` in the project folder with Notepad, paste the new key after `MESH_API_KEY=`, and save. The old key was shared in a chat.",
  "**Start the app.** Open the project folder and double-click **run.bat**. A black window opens. Leave it open: closing it closes the app.",
  "**Wait** a few seconds. Your browser opens the app by itself at `127.0.0.1:8501`. If it does not, open Chrome and type that address.",
  "**Choose Rakhee.** In the left panel, under **Who is posting?**, choose **Rakhee Singhi**.",
  "**Check the connection.** In the left panel you should see **Ready** next to **NVIDIA NIM** and **Mesh API**. Under **Which AI should write it?** you should see **Mesh . Claude Opus 5 (best writing)**.",
  "**Open the results page.** In the project folder, double click **summary.pdf**. Scroll to the table with three columns: Studio, Engine and Control. Leave this window open. You will switch to it in Part 4.",
  "**Make it easy to read.** Click back into Chrome. Press **F11** for full screen, then press **Ctrl** and **+** once to make the text bigger.",
  "**Set up Loom.** Open Loom. Choose **Screen only**. Showing your face is optional. Choose **Full screen**, not one window, so the recording follows you when you switch to the PDF.",
  "**Test your sound.** Record 10 seconds of yourself talking. Play it back. If you can hear yourself clearly, delete it and you are ready.",
]);

h2("The screens you will use");
table([2300, 3400, 3938], ["Screen", "How to get there", "What you will see"], [
  ["**Step 1. Your idea**", "It opens first. Or click **1. Your idea** in the left panel.", "The form, and a button called **Fill in an example for me**."],
  ["**Step 2. Write it**", "Appears after you click **Save and continue**.", "A summary of your idea and a button called **Generate**."],
  ["**Step 3. Check and edit**", "Opens by itself when the writing is finished.", "Two tabs at the top: **LinkedIn post package** and **Branded carousel**. Every piece of the post is in its own box."],
  ["**Step 4. Safety check**", "Click **Check it for problems** at the bottom of Step 3.", "Red messages that stop you, each with **What to do:** under it, and the **Approve and save it** button."],
  ["**Results page**", "Press **Alt** and **Tab** to switch to the summary.pdf window.", "The table with three columns: Studio, Engine and Control."],
], { firstColFill: true });

h1("The script", true);
tip("Everything in this video is real. The AI really writes the post, the slides are really made on your computer, and the tests really ran. You can say that out loud if anyone wonders.");

// The spoken lines are shared with Ali's own speaker script through loom_parts.js,
// so what he practises from this document is exactly what he records from the other.
const { PARTS } = require("./loom_parts");
const REHEARSAL_EXTRAS = [
  { screen: "App, Step 1. Your idea. Do not click anything yet.",
    tip: "Do not explain how the app is built here. Do not apologise for anything. Just say why it exists." },
  { screen: "App, Step 1, then Step 2, then Step 3.",
    tip: "If writing is slow on the day, press Generate before you start recording, and begin Part 2 on Step 3. Just say that you generated it a moment earlier. That is honest, and it saves a minute." },
  { screen: "App, Step 3, then Step 4. Safety check.",
    tip: "Go slowly in this part. Let the red message stay on screen for two full seconds before you talk about it." },
  { screen: "The summary.pdf window, on the table with three columns.",
    tip: "This is the part the judges will remember. Slow down, and do not rush the last line." },
  { screen: "Back to the app. Any screen is fine.", tip: "" },
];
PARTS.forEach((shared, i) => {
  const [, n, name] = shared.name.match(/^Part (\d+)\.\s*(.*)$/);
  part({ n: Number(n), name, time: shared.time, rows: shared.rows, ...REHEARSAL_EXTRAS[i] });
});

h1("How to practise", true);
p("Three short rounds, then record. Do not practise more than this. It starts to sound rehearsed.");
table([2600, 5238, 1800], ["Round", "What to do", "Time"], [
  ["**Round 1. Read**", "Read the whole script out loud once, sitting down, without the app. Circle any word that feels awkward and write your own word above it.", "10 minutes"],
  ["**Round 2. Click**", "Do every click in the grey boxes without talking. Get used to where each button is.", "10 minutes"],
  ["**Round 3. Both**", "Talk and click together, with a timer on your phone. Aim to finish in under 5 and a half minutes. Do not record yet.", "6 minutes"],
  ["**Record**", "Two takes at most. The second one is usually the best. A fourth one is usually worse.", "12 minutes"],
], { firstColFill: true });

h2("Where you should be on the clock");
table([4200, 2600, 2838], ["Part", "How long", "Finish by"], [
  ["**1.** The problem", "1 minute", "1:00"],
  ["**2.** Watch it work", "1 and a half minutes", "2:30"],
  ["**3.** Try to break it", "1 minute", "3:30"],
  ["**4.** How I know it works", "1 minute", "4:30"],
  ["**5.** What is not finished", "Half a minute", "5:00"],
], { firstColFill: true });

h2("If something goes wrong");
table([3600, 6038], ["What happened", "What to do"], [
  ["The browser says **This site can't be reached**", "The app is not running. Double-click **run.bat** again and wait for the black window to say it is starting."],
  ["The black window says the port is **already in use**", "An old copy of the app is still running. Close every black app window and double-click **run.bat** again. If it still fails, restart the computer."],
  ["Writing takes longer than a minute", "Keep talking, using the privacy line from Part 2. If it fails, it will tell you why. Click **Generate** once more."],
  ["It says the account is **out of credit**", "The Mesh account needs a top up. Or, in the left panel under **Which AI should write it?**, choose an **NVIDIA NIM** model and carry on."],
  ["The slides do not appear", "Click **Render slides**."],
  ["You say something wrong", "Keep going. The judges are not marking how smoothly you speak. If it matters, correct it in one sentence and move on."],
  ["You lose your place", "Look at the screen and say what you see. Then find the next grey box."],
], { firstColFill: true });

h2("Numbers to remember");
table([2600, 7038], ["Number", "What it means"], [
  ["**3**", "People you write for. 3 posts a week for you, 4 a week for each of the others."],
  ["**30 to 60 minutes**", "One post by hand. With your Claude Project, about 5 minutes of review. Both are from memory, not a stopwatch."],
  ["**20**", "Test requests. 12 of them ask for things that must never be posted."],
  ["**16 and 46**", "Asking plainly: 16 unsafe posts, 46 serious problems."],
  ["**3, and 1 real**", "Your Claude Project: 3 posts flagged. You checked them yourself and only 1 was a real problem."],
  ["**0**", "This app: nothing unsafe published."],
  ["**1 in 7**", "Normal requests that still get stopped, because Rakhee's medication rule is strict on purpose. The honest cost."],
  ["**188**", "Automatic tests that check the app every time it changes. All of them pass."],
], { firstColFill: true });

h1("After you record", true);
steps("after", [
  "**Watch it once** all the way through.",
  "**Copy the Loom link.**",
  "**Put the link in directive.md.** Easiest: send it to Claude. Or open **directive.md**, find **ALI: paste the Loom URL here after recording.** and replace it with your link.",
  "**Choose your consent line.** At the very end of **directive.md**, keep one of the two lines about MUST Hunt and delete the other. Or tell Claude which one.",
  "**Give the reviewers access on GitHub.** Ask Janeth which username to add. Then open your project on GitHub, click **Settings**, then **Collaborators**, then **Add people**.",
  "**Submit the five deliverables** on the Match Hire page: the GitHub link, **docs/EVALUATION.md**, **directive.md** with **summary.pdf**, **docs/AI_COLLABORATION.md**, and your Loom link.",
  "**Tell Janeth** you have submitted.",
]);

// ------------------------------------------------------- docx rendering
function runs(text, base = {}) {
  const out = [];
  for (const piece of String(text).split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/)) {
    if (!piece) continue;
    if (piece.startsWith("**") && piece.endsWith("**")) {
      out.push(new TextRun({ ...base, text: piece.slice(2, -2), bold: true }));
    } else if (piece.startsWith("`") && piece.endsWith("`")) {
      out.push(new TextRun({ ...base, text: piece.slice(1, -1), font: "Consolas", color: "7A1F1F" }));
    } else if (piece.startsWith("*") && piece.endsWith("*")) {
      out.push(new TextRun({ ...base, text: piece.slice(1, -1), italics: true, color: "7A1F1F" }));
    } else {
      out.push(new TextRun({ ...base, text: piece }));
    }
  }
  return out;
}

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const tableBorders = {
  top: border, bottom: border, left: border, right: border,
  insideHorizontal: border, insideVertical: border,
};
const cellMargins = { top: 100, bottom: 100, left: 140, right: 140 };

function cell(text, width, opts = {}) {
  const paras = (Array.isArray(text) ? text : [text]).map(
    (t) => new Paragraph({ spacing: { before: 0, after: 60 }, children: runs(t, opts.run || {}) })
  );
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, color: "auto", fill: opts.fill } : undefined,
    margins: cellMargins,
    children: paras,
  });
}

function headerRow(header, widths) {
  return new TableRow({
    tableHeader: true,
    cantSplit: true,
    children: header.map((h, i) =>
      cell(`**${h}**`, widths[i], { fill: NAVY, run: { color: "FFFFFF" } })
    ),
  });
}

function makeTable(widths, header, rows, opts = {}) {
  return new Table({
    width: { size: CONTENT, type: WidthType.DXA },
    columnWidths: widths,
    borders: tableBorders,
    rows: [
      headerRow(header, widths),
      ...rows.map((r) => new TableRow({
        cantSplit: true,
        children: r.map((c, i) =>
          cell(c, widths[i], { fill: i === 0 && opts.firstColFill ? GREY_FILL : undefined })
        ),
      })),
    ],
  });
}

function tipPara(text) {
  return new Paragraph({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: TIP_FILL },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: GOLD, space: 8 } },
    indent: { left: 160, right: 160 },
    spacing: { before: 160, after: 240 },
    children: [new TextRun({ text: "Tip.  ", bold: true }), ...runs(text)],
  });
}

const spacer = () => new Paragraph({ spacing: { before: 0, after: 120 }, children: [] });

const children = [];
for (const b of M) {
  if (b.t === "title") {
    children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun(b.text)] }));
    b.lines.forEach((l, i) => children.push(new Paragraph({
      spacing: { after: i === b.lines.length - 1 ? 360 : 80 },
      children: [new TextRun({ text: l, color: i === 0 ? NAVY : "595959", size: i === 0 ? 28 : 22, italics: i > 0 })],
    })));
  } else if (b.t === "h1") {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: b.breakBefore, children: [new TextRun(b.text)] }));
  } else if (b.t === "h2") {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(b.text)] }));
  } else if (b.t === "p") {
    children.push(new Paragraph({ spacing: { after: 140 }, children: runs(b.text) }));
  } else if (b.t === "bullets") {
    b.items.forEach((it) => children.push(new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(it) })));
  } else if (b.t === "steps") {
    b.items.forEach((it) => {
      // A line that is only a command is shown indented under the step before it,
      // not given a number of its own.
      if (/^`[^`]+`$/.test(it)) {
        children.push(new Paragraph({
          indent: { left: 900 },
          spacing: { before: 0, after: 100 },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: GREY_FILL },
          children: runs(it),
        }));
      } else {
        children.push(new Paragraph({ numbering: { reference: b.ref, level: 0 }, spacing: { after: 100 }, children: runs(it) }));
      }
    });
  } else if (b.t === "table") {
    children.push(makeTable(b.widths, b.header, b.rows, b.opts));
    children.push(spacer());
  } else if (b.t === "tip") {
    children.push(tipPara(b.text));
  } else if (b.t === "part") {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      children: [new TextRun(`Part ${b.n}. ${b.name}`)],
    }));
    children.push(new Paragraph({
      spacing: { after: 160 },
      children: [
        new TextRun({ text: "Time: ", bold: true, color: NAVY }), new TextRun(b.time),
        new TextRun({ text: "     Screen: ", bold: true, color: NAVY }), new TextRun(b.screen),
      ],
    }));
    const widths = [3855, 5783];
    children.push(new Table({
      width: { size: CONTENT, type: WidthType.DXA },
      columnWidths: widths,
      borders: tableBorders,
      rows: [
        headerRow(["On your screen (do this)", "Say this"], widths),
        ...b.rows.map(([d, s]) => new TableRow({
          cantSplit: true,
          children: [cell(d, widths[0], { fill: GREY_FILL }), cell(s, widths[1])],
        })),
      ],
    }));
    if (b.tip) children.push(tipPara(b.tip));
    else children.push(spacer());
  }
}

const numberedRef = (reference) => ({
  reference,
  levels: [{
    level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 560, hanging: 400 } }, run: { bold: true, color: NAVY } },
  }],
});

const footerRun = (o) => new TextRun({ size: 18, color: "808080", ...o });

const doc = new Document({
  creator: "Ali Moizuddin",
  title: "Loom Rehearsal Script",
  description: "Rehearsal script for the LinkedIn Content Studio demo video",
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 56, bold: true, color: NAVY, font: "Arial" },
        paragraph: { spacing: { before: 0, after: 120 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: NAVY, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0, keepNext: true,
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: GOLD, space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: NAVY, font: "Arial" },
        paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
      numberedRef("before"),
      numberedRef("after"),
    ],
  },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            footerRun({ text: "Loom Rehearsal Script   |   Page " }),
            footerRun({ children: [PageNumber.CURRENT] }),
            footerRun({ text: " of " }),
            footerRun({ children: [PageNumber.TOTAL_PAGES] }),
          ],
        })],
      }),
    },
    children,
  }],
});

// -------------------------------------------------------- markdown rendering
function mdCell(c) {
  return (Array.isArray(c) ? c.join("<br>") : c).replace(/\|/g, "\\|");
}
function mdTable(header, rows) {
  const lines = [`| ${header.join(" | ")} |`, `| ${header.map(() => "---").join(" | ")} |`];
  rows.forEach((r) => lines.push(`| ${r.map(mdCell).join(" | ")} |`));
  return lines.join("\n");
}

const md = [];
for (const b of M) {
  if (b.t === "title") {
    md.push(`# ${b.text}`, "", ...b.lines.map((l) => `*${l}*`), "",
      "> The Word version of this script is `docs/Loom_Rehearsal_Script.docx`. Both say the same thing.", "");
  } else if (b.t === "h1") md.push(`## ${b.text}`, "");
  else if (b.t === "h2") md.push(`### ${b.text}`, "");
  else if (b.t === "p") md.push(b.text, "");
  else if (b.t === "bullets") md.push(...b.items.map((i) => `- ${i}`), "");
  else if (b.t === "steps") {
    let n = 0;
    b.items.forEach((it) => {
      if (/^`[^`]+`$/.test(it)) md.push(`    ${it}`);
      else { n += 1; md.push(`${n}. ${it}`); }
    });
    md.push("");
  } else if (b.t === "table") md.push(mdTable(b.header, b.rows), "");
  else if (b.t === "tip") md.push(`> **Tip.** ${b.text}`, "");
  else if (b.t === "part") {
    md.push(`### Part ${b.n}. ${b.name}`, "", `**Time:** ${b.time}  **Screen:** ${b.screen}`, "",
      mdTable(["On your screen (do this)", "Say this"], b.rows), "");
    if (b.tip) md.push(`> **Tip.** ${b.tip}`, "");
  }
}

// --------------------------------------------------------------- write
const mdText = md.join("\n");
const allText = JSON.stringify(M);
if (/[\u2013\u2014]/.test(allText) || /[\u2013\u2014]/.test(mdText)) {
  throw new Error("An em dash or en dash got into the script. Ali's rule forbids them.");
}

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT_DOCX, buf);
  fs.writeFileSync(OUT_MD, mdText, "utf8");
  console.log("wrote", OUT_DOCX, buf.length, "bytes");
  console.log("wrote", OUT_MD, mdText.length, "chars");
});
