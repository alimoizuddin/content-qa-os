# CLAUDE.md

Rules for working in this repository. Read before changing anything.

The README explains what the app does. This file explains what will break if you
get it wrong.

---

## What this is

A local Streamlit app that turns one idea into a checked, publishable LinkedIn
package for three named people. Its purpose is not writing. **Its purpose is
refusing to publish things that are not true.**

Every design decision follows from that. If a change makes the app faster or nicer
but weakens the refusal, the change is wrong.

---

## The rule that matters most

**A number or claim enters `star_facts` only when a dated source states it. When
two sources disagree, the newest verified-facts log wins.**

For Ali that is `Ali_Moizuddin_Master_Profile.docx` (29 August 2026), **not** his
LinkedIn engine document (18 July 2026).

This is not theoretical. This app shipped a figure Ali publicly withdrew on
3 August 2026 as invented, listed as a verified fact, because it was built from the
older document. His own profile already records the lesson from a previous
occurrence of the same mistake:

> "The stale claims were living in CODE, where nobody was reading them. When a
> fact changes, grep the pipeline as well as the profile."

**Before adding or editing any fact in `core/personas.py`:**

1. Find it in the newest source. Not a plausible-sounding memory of it.
2. If you cannot find it, it goes in `pending_verification`, not `star_facts`.
3. If it is the wrong version of a true claim, add it to that fact's
   `banned_inflations`.
4. Add a test. A fact with no test is a fact that will quietly rot.

---

## Things that must not change without a very good reason

| Rule | Why |
| --- | --- |
| `evals/scoring.py` imports nothing from `core` | If the judge shares code with the thing it judges, the studio scores perfectly by definition and every number in the repo becomes meaningless |
| Unverified numbers are **replaced**, not flagged | A flagged number in an editable box gets pasted into LinkedIn by accident. A hole cannot be |
| Safety findings block. Lint findings never block | Voice is a judgement and the writer gets the last word. A medical claim is not a judgement |
| No override button in the app for a safety block | If a block is wrong, that is a rule change made in `core/personas.py`, in conversation with the person it protects |
| QA runs on the current edit-field contents | Otherwise you can generate something clean and paste something dangerous in afterwards |
| Dashes are removed when the text is written, in `normalise` | Doing it only at the safety check left them in the boxes people edit and copy from, reply templates included. Ali found that by using the app |
| Two generation attempts, never three | A model that has failed a schema twice fails a third time with a longer wait |
| Provider response bodies are never displayed | They can carry a URL, a request id, or part of a key. Status codes are classified into a safe sentence instead |
| The app never posts to LinkedIn | A human presses publish, always |
| The `engine` arm gets the studio's prompt and no gate | It is the control for "would a Claude Project have caught this". Give it a weaker prompt and the comparison flatters the studio for free |
| Replay never needs an API key | The Quest requires the evaluation to be reproducible without a paid model. Replay checks the allowlist only, never key availability. When it did check keys, CI passed while the studio arm measured nothing |
| `core/runlog.py` writes only `ALLOWED_FIELDS` | A log that can accept any keyword will eventually be handed a brief, a generated post, or a key |

---

## Style

**No em dashes or en dashes.** Anywhere. Not in the app, not in generated content,
not in documentation, not in commit messages. All three personas ban them and Ali
bans them in anything he sends under his own name. Use commas, colons, periods or
parentheses. A test enforces this across the repository; `core/linter.py`,
`evals/scoring.py` and one fixture in `tests/test_studio.py` are exempt because
they need the characters in order to match them.

Write documentation in plain words and short sentences. Ali is the reader and he
has asked for this directly.

---

## After you change anything

```bash
python -m pytest -q          # 188 tests, all must pass
python -m evals.run_evals    # replays the saved run, no key, no cost
```

**If you changed a prompt, a persona specification, or a model, the saved
recordings are stale.** Replaying them measures the old prompt. Re-record:

```bash
python -m evals.run_evals --live --record --model anthropic/claude-opus-5
```

That costs money and takes about 20 minutes. With three arms it calls the provider
at least 60 times, and more when an arm needs its second attempt.

**Check the balance on the account first.** A live run that drains an account
part-way through does not stop. It records the cases that succeeded and reports
every case after the 402 as a failure, which looks exactly like a broken system
until you read the error. This has already happened once.

**Exit codes.** 0 is clean. 2 means a human must look: either something that should
not publish did, or a normal brief was blocked. 1 means the harness could not run,
including an arm that has recordings and replayed to nothing. CI fails the build
only when the studio published something unsafe, and raises a warning for an
over-strict block, which is the known cost of the gate.

**Some documents are generated. Rebuild them or they lie.**

```bash
python docs/build_summary.py        # summary.pdf, a Quest deliverable
python docs/build_start_here.py     # START_HERE.pdf, from START_HERE.md
```

`docs/LOOM_SCRIPT.md` and `docs/Loom_Rehearsal_Script.docx` are built together by
`tools/build_rehearsal.js`, which shares its spoken lines with Ali's personal
speaker script through `tools/loom_parts.js`. Edit the lines there, not in the
generated files. See `tools/README.md`.

---

## Layout

```
app.py                 shell only: page config, sidebar, stage router
core/personas.py       the single source of truth for all three people
core/brief.py          the structured brief
core/prompts.py        prompt construction, one builder per output type
core/providers.py      NVIDIA and Mesh, allowlisted
core/generator.py      two-attempt structured generation, then normalise
core/schemas.py        output shapes, deliberately tolerant
core/linter.py         style, advisory, and the one dash stripper
core/auditor.py        facts and safety, blocking
core/studio.py         sections, QA orchestration, the approval gate
core/carousel.py       slide rendering, PDF, ZIP
core/imagegen.py       optional raster generation, through Mesh
core/history.py        local SQLite, plus package_as_text for downloads
core/runlog.py         content-free run log, data/logs/runs.jsonl
run.bat, run.sh        one-step launchers for non-developers
START_HERE.md          setup from nothing, and how to add a person
docs/build_*.py        the generators for summary.pdf and START_HERE.pdf
ui/                    theme, the five stages, and every word of on-screen help
evals/                 the harness, the cases, the recordings
```

Persona details live in **one** place. Before this rebuild they were spread across
four, and forgetting one crashed the app. Do not spread them again.

---

## Gotchas

**Never write regex or escapes through a shell heredoc.** The shell eats
backslashes. It has cost this project real time twice: once it wrote literal
backspace bytes into `core/auditor.py`, and once it turned an escape sequence
for a dash back into the character itself. Use the Write or Edit tools, or a patch script written
with them.

**Adding a person touches three places, not one.** The spec and the registry in
`core/personas.py`, the hand-transcribed numbers in `evals/scoring.py`, and at least
two cases in `evals/cases.json`, because a test requires every person to appear in
both directions. `START_HERE.md` Part 3b is the written procedure, and a test proves
a fourth person works end to end once registered.

**Schema limits are looser than publishing limits on purpose.** Five hashtags and
three reply templates are what ships; `generator.normalise` trims to that. The same
function caps a carousel at eight slides, the limit in the brief, keeping the cover
and the closing slide.

**An empty list is falsy in Python.** `qa_result.get("blocking_flags") or ...`
treated a clean result as absent and recomputed it down the wrong path. There is a
test asserting on the empty case specifically. Do not remove it.

**A time of day is not a metric.** "4 pm" was read as an unverified number and
redacted, which blocked a clean post. Times are now skipped by position, so a time
can never license the same digit elsewhere in the text. The scorer had the same bug
and the same fix.

**Models get retired.** Every model in the allowlist was called and confirmed
working. Providers switch them off on a schedule. The sidebar has a **Check the AI
models still work** button.

**Per model request differences belong in `core/providers.py`.** Reasoning models
need thinking turned off. Claude Opus 5 and Sonnet 5 reject `temperature` with a
400. Both are declared on `ModelOption` rather than special-cased at a call site,
because both are properties of the model. A temperature hardcoded at the call site
is what turned a whole live evaluation run into "did not generate" and looked like
a schema bug.

**Reasoning models spend the whole budget thinking.** The allowlist marks which
ones need `chat_template_kwargs: {"thinking": false}`. They also need a generous
`MAX_TOKENS`: a budget tuned for a smaller model ran out mid-string, and the app
blamed the brief for it.

**The vendored font is not optional.** `assets/fonts/Inter.ttf` must exist or the
slides silently degrade to a bitmap face. CI fails if it is missing.

---

## Never

- Commit `.env`, `data/history.db`, `data/logs/`, or anything in
  `assets/portraits/`.
- Read anything out of the Google Drive corpus at runtime. Persona specs are
  distilled by hand; the corpus contains raw exports, private media, third-party
  personal data and contact details, none of which belong in an app.
- Put another person's private details into a persona, a test case, or a document
  without their say-so. Two of the three people here are real and did not write
  this code.
- Move a claim from `pending_verification` to `star_facts` quickly. That is the one
  change that should always be slow.
- Present a generated art-direction prompt as if it were an image.
- Promise reach, engagement, or virality anywhere, in code or in documentation.
