# LinkedIn Content Studio

A private, local content studio for three LinkedIn personas. It takes a grounded
brief and produces a publishable package: the post with its hashtags, keywords and
engagement blocks, a branded carousel rendered as real 1080x1350 slides with a
LinkedIn-ready PDF and a ZIP, art direction for a picture, and a four-week calendar.
Nothing is approved until it has passed a fact and safety audit.

NVIDIA NIM is the default and the only required provider. Mesh API is optional and
adds the Anthropic catalogue plus picture rendering.

## Run it

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.lock
copy .env.example .env
```

On macOS or Linux use `source venv/bin/activate` and `cp .env.example .env`.

Put your NVIDIA key in `.env`, then:

```bash
python -m streamlit run app.py
```

It binds to `127.0.0.1` only, with XSRF and CORS protection on and Streamlit error
details hidden from the browser. Nothing leaves the machine except the prompts you
generate with.

## The workflow

Five stages, in order, and the order is enforced.

1. **Brief.** Persona, goal, audience, core idea, and proof. Proof is the field that
   matters: numbers you put there are treated as verified for that piece. Leave it
   empty and the studio writes `[OPEN SLOT]` wherever evidence belongs, and blocks
   approval until you resolve it.
2. **Generate.** One provider call per output type, two attempts each: the request,
   then one corrective retry. Provider failures are classified into an actionable
   sentence; the raw response body is never shown.
3. **Edit and preview.** Every part of the package is its own editable field. The
   carousel renders to slides you can see, with PDF and ZIP downloads.
4. **QA and approve.** The audit runs over whatever is in the fields *now*, not over
   what the model produced. Open slots, unverified numbers, inflated claims, and
   persona safety breaches all block approval. Style notes never do.
5. **History.** Approved, sanitised text only, in local SQLite.

## What each package contains

**Post.** The clean copy-paste block, hashtags with a line on why each one fits,
keyword strategy with its reasoning, the golden-hour first comment, a second-wave
comment, a repost or resurface caption, three reply templates, and the publishing
window. Hashtags are kept out of the post body so you can edit them separately.

**Carousel.** Six to ten slides following the arc the source engines prescribe:
cover, tension, the turn, framework, recap, call to action. Each slide carries a
headline, phone-readable body, a specific visual direction, and a momentum phrase.
Rendered as 1080x1350 PNGs plus a PDF and a ZIP, entirely locally. The recap slide
gets a panel treatment because it is the one built to be screenshotted, and the
final slide carries the author lockup: portrait to the left of the name, so the
subject's gaze points into the copy.

**Picture.** A detailed art-direction prompt bound to the persona palette and the
safety rules. If an image provider is configured it is also rendered. If not, you
get the prompt, and the studio says so rather than pretending a prompt is an image.

**Calendar.** Sixteen entries across four weeks, four per week, each with a pillar,
a format, a hook angle, the real asset it is anchored to, a CTA, a goal, and the
evidence still required. Formats are required to rotate: a week that is four
carousels is rejected by the schema.

## Author portraits

Upload a portrait per persona in the sidebar. It is stored under
`assets/portraits/`, gitignored, and used on the cover badge and the author slide.
Without one, the lockup falls back to an initials mark rather than leaving a hole.
Portraits are yours to supply; the studio never reads media out of a source folder.

## Honesty layer

This is the part worth understanding before you rely on the output.

- **Verified facts only.** Each persona has a fact list. A number that is not on it,
  and was not supplied as proof in the brief, is replaced with `[OPEN SLOT]` rather
  than merely flagged, because a flagged number in an editable box gets pasted by
  accident.
- **Inflations are named.** Each fact records the specific wrong version of itself,
  so "10,000 students taught" passes and "10,000 people transformed by me" does not.
- **Unsourced claims are quarantined.** Two claims commonly attached to this work do
  not appear in the canonical source engine: the attribution of the Be10x first
  prize to a specific project, and "300+ transcription hours at 95%+ accuracy". The
  prize itself is verified; the attribution is not. Both sit in
  `pending_verification`, which means the studio will not write them and will tell
  you why. Supply a source and move them into `star_facts`.
- **Domain safety fails closed.** Claims of cure, reversal, healing, disease
  prevention, medication changes, fasting protocols, and restriction framing are
  blocked outright for the health persona. Named individuals, private compensation,
  internal data, and outcome guarantees are blocked for the HR persona. Rules carry
  an exemption clause so first-person history stays writable while instruction does
  not: "I wanted to stop depending on daily pills" passes, "you can stop your
  medication" does not.
- **No promises of reach.** Keywords and hashtags are described as classification
  and consistency signals. Nothing in the studio claims they cause virality.

## Provider configuration

| Variable | Required | Effect |
| --- | --- | --- |
| `NVIDIA_API_KEY` | Yes | Enables generation. |
| `MESH_API_KEY` | No | Adds Claude models to the sidebar and turns on picture rendering. Without it they are not offered at all. |
| `DEFAULT_MODEL` | No | Which allowlisted model the sidebar starts on. A Mesh model here is ignored unless `MESH_API_KEY` is also set, so the app never defaults to something it cannot call. Unknown values are ignored, not fatal. |
| `NVIDIA_MODEL` | No | Older name for the same thing, still honoured. `DEFAULT_MODEL` wins when both are set. |
| `MESH_IMAGE_MODEL` | No | Which image model renders the picture package. Defaults to a fast, cheap one. |

Models are allowlisted. An environment variable cannot introduce one that is not on
the list. Requests have a bounded timeout and at most one transport retry.

Reasoning models are marked as such in the allowlist and are asked to skip their
chain of thought, because otherwise they spend the entire token budget on it before
reaching the JSON.

**Models get retired.** Every allowlisted model was called and confirmed working, but
NVIDIA ends support on a schedule. The sidebar has a **Check models are still served**
button that compares the allowlist against the live catalogue and names anything that
has gone. A retired model otherwise fails at generation time, and the studio will say
so and tell you to pick another.

**On sampling.** The newest Anthropic models reject a `temperature` parameter with
a 400 rather than ignoring it. That is declared per model in the allowlist, not
handled at the call site, because it is a property of the model.

**Known limitation.** NVIDIA NIM's text endpoint does not return rasters, so a
generated picture needs a Mesh key. Everything else, the carousel included, works
NVIDIA-only, and without any image provider the picture package still returns its
art-direction prompt, which is a deliverable in its own right.

## Does the structure earn its keep

The evaluation has three arms, not two:

| Arm | Prompt | Enforcement |
| --- | --- | --- |
| `studio` | the full persona specification | linter, auditor, approval gate |
| `engine` | **the same full specification** | none |
| `baseline` | a competent generic request | none |

The middle one is the interesting control. It is what a written engine document run
as a Claude Project actually is: every rule present, stated clearly, and nothing but
the model's own compliance enforcing them. Comparing `studio` against `engine`
isolates one variable, which is whether the rules are text or code. Comparing
against `baseline` only ever answered the easier question.

There is an evaluation harness in `evals/`, and it exists because a test suite
cannot answer that question. Twenty labelled briefs run through two arms: the full
studio, and a control that is the same model with the same schema and none of the
structure. The scorer imports nothing from `core`, so the studio cannot mark its
own homework.

Latest run, `anthropic/claude-opus-5`, 10 September 2026:

| arm | generated | unsafe ships | serious violations shipped | safety | usability |
| --- | --- | --- | --- | --- | --- |
| studio | 20/20 | **0** | **0** | 100% | 6/7 |
| engine | 20/20 | 3 | 3 | 85% | 7/7 |
| control | 18/20 | **16** | **47** | 11% | 5/5 |

The control publishes fasting protocols with durations, "zero human oversight",
"CAC to zero", a superlative with its qualifier dropped, a named candidate, and a
figure Ali had publicly retracted as invented. The studio publishes none of them,
and pays for it with one grounded brief in seven that needs a person to resolve an
open slot first.

**The engine arm is the honest headline, and it is a modest one.** Given the same
rules as text, Claude Opus 5 obeyed them almost perfectly on its own. The gap
between stating the rules and enforcing them is real but small on this model.
Against a generic prompt the gap is enormous.

The three flags against the engine arm were read by hand, because three is small
enough to check and a number nobody has checked is not evidence. One is a real
catch: it invites a reader who takes daily medication to message about food, which
is the exact move Rakhee's rules forbid. One is a scorer artifact, a refusal it
still misreads ("Someone asked me for a testimonial. I do not have one."). One is
in a planning note that never reaches LinkedIn. Call it **one genuine catch in
twenty cases**, not three.

```bash
python -m evals.run_evals                 # replay the recorded run, no credits
python -m evals.run_evals --live --record # call the provider and re-record
```

Exit code 2 means a case that must not ship did, or a grounded brief was blocked.
A human has to look. See `evals/README.md` for what changed between runs and why.

## Verify

```bash
python -m pip check
python -m compileall -q app.py core ui tests
python -m pytest -q
python -m evals.run_evals
pip-audit -r requirements.lock
```

The test suite runs entirely offline against a fake provider and never spends
credits. It covers every output type, mixed bundles, empty selection, schema retry
success and failure, provider error redaction, carousel PNG, PDF and ZIP rendering,
the NVIDIA-only image fallback, Mesh gating in both directions, approval
blocking, every persona safety rule, and the full UI flow through Streamlit's
`AppTest`.

## Layout

```
app.py                 shell: page config, sidebar, stage router
core/personas.py       the single source of truth for all three personas
core/brief.py          the structured brief
core/prompts.py        prompt construction, one builder per output type
core/providers.py      NVIDIA and Mesh, allowlisted
core/generator.py      two-attempt structured generation
core/schemas.py        output schemas
core/linter.py         style lint, advisory
core/auditor.py        fact and safety audit, blocking
core/studio.py         sections, QA orchestration, the approval gate
core/carousel.py       slide rendering, PDF, ZIP
core/fonts.py          font resolution
core/imagegen.py       optional raster generation
core/history.py        local SQLite
ui/theme.py            studio chrome
ui/stages.py           the five stages
assets/fonts/          vendored Inter (SIL Open Font Licence)
```

## Documents

| File | What it is |
| --- | --- |
| `directive.md` | The main submission document. Problem, priority, approach, solution, expected outcome |
| `summary.pdf` | Two-page overview. Rebuild it with `python docs/build_summary.py` |
| `docs/EVALUATION.md` | The evaluation package: cases, results, failure analysis, before and after |
| `docs/AI_COLLABORATION.md` | What AI did, what I kept, what I rejected |
| `docs/WORKFLOW_MAP.md` | The workflow before and after, and where a human still decides |
| `docs/RUNBOOK.md` | Operator guide. What to do when it misbehaves |
| `docs/CASE_STUDY.md` | Rebuild notes: what changed from the prototype and why |
| `docs/LOOM_SCRIPT.md` | Script for the demo recording |
| `evals/README.md` | How the evaluation works and why the scorer is independent |

Persona specifications are distilled by hand from the canonical engine document for
each person. The source corpus is never read at runtime, and no raw export, profile,
archive, private media, or contact detail is reproduced in the app. See
`docs/source-corpus-audit.json` for which document is canonical for whom, and
`docs/CASE_STUDY.md` for what the rebuild changed and why.
