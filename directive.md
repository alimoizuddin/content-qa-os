# directive.md

**LinkedIn Content Studio** — an AI OS Mini for turning one idea into a checked,
publishable LinkedIn package.

Ali Moizuddin, AI Automation Engineer. Siliguri, India.

- Repository: https://github.com/alimoizuddin/content-qa-os (private, reviewer access on request)
- App: runs locally at `http://127.0.0.1:8501`. Setup is three commands, in the README.
- Evaluation results: `evals/results/latest.json`, and `docs/EVALUATION.md`
- Demo video: `[[FILL: Loom URL]]`

---

## 1. Problem — What am I trying to solve?

### The user

Me. I am the target user, and I am not a developer. I have an MA in English
Literature and no traditional coding background. I write and publish LinkedIn
content for three people: myself, an HR leader, and a health coach.

This matters for the Quest question "can a non-developer run it". I am the
non-developer. Every time I ran this system I was testing that, not simulating it.

### The job to be done

Take one real idea and turn it into a LinkedIn package I can publish today:
the post, the hashtags with reasons, the first comment, reply templates, and a
branded carousel as image files and a PDF.

### The workflow, in three states

This matters, and I want to be exact about it, because two different improvements
are easy to confuse and only one of them belongs to this Quest.

**State 1. By hand.** Pick the idea. Dig through old notes for the proof. Draft the
post. Re-read it against the voice rules. Check every number against the fact
list. Cut anything I cannot source. Write the hashtags, the first comment and the
reply templates. Design the carousel. Export it.

**About 30 to 60 minutes per post.** Early on it was closer to an hour; with
practice it came down to 45, then 30. That is an estimate from memory, recorded in
my own case study in August 2026, not a stopwatch measurement.

**State 2. With the content engines.** Earlier this year I built one written
"engine" document per person: their voice rules, their verified fact table, their
banned phrasings, their hashtag rules, their safety limits. I run it as a Claude
Project. I dictate a month to three months of calendar with Wispr Flow in a single
30 to 60 minute sitting, then name a row and the engine writes the package.

**I write nothing by hand now. I review, and that takes about 5 minutes.**

**State 3. This system.** The engines turned into software.

**The time saving belongs to State 2, not to State 3.** The engines predate this
Quest and I am not claiming their improvement as this week's work. State 3 is
about the same 5 minutes of review.

### So what is State 3 for

Three things State 2 cannot do.

**The checking depends on the model remembering.** In a Claude Project, the fact
table and the safety rules are text in a document the model is asked to obey. Most
of the time it does. When it does not, nothing catches it except me. In State 3
those rules are code, they run every time, and an unverified number is removed
rather than hoped about.

**The assets need Code Execution.** The engine documents say "Python plus
ReportLab, output the PDF". That works when the tool has file execution enabled and
fails when it does not. State 3 renders 1080x1350 slides, a PDF and a ZIP locally
in about a second, with no external service.

**Nothing was testable.** I had no way to answer "is this better than just asking
the model politely" other than by feeling. State 3 has an evaluation with a control
arm and a recorded run. That is the part I could not have got any other way, and it
is what found the mistake in section 3 below.

### How often

3 posts a week for me. 4 a week for each of the other two. Every one needs the same
checks.

### The difficulty

Three things go wrong, and all three cost time after the writing is done.

**Numbers get invented.** A model asked to write a confident post will add a
figure that sounds right. "80% faster." "12,487 records." Nobody asked it to. It
fills the shape. Then I have to catch it, and if I miss one it goes public under
a real person's name.

**Voice rules get broken quietly.** Each of the three people has written voice
rules: no em dashes, no engagement bait, no more than five hashtags, no links in
the post body. A model that has not been told these will break them and the copy
will still read fine, so I only notice on the re-read.

**Safety rules are not optional for two of the three.** The health coach cannot
say food cures, reverses or heals any condition. She cannot tell a reader to stop
taking medication. The HR leader cannot name a candidate, discuss anyone's pay, or
promise anyone a job. These are not style preferences. Getting one wrong is a real
problem for a real person's reputation.

### My hypothesis about the cause

The bottleneck is not the writing. It is the checking.

A general AI tool produces text quickly and then hands me all the verification.
The slow part is me reading it four times looking for an invented number, a broken
voice rule, and a claim that cannot be published.

So the fix is not a better prompt. It is a system that carries the person's
verified facts and rules, and refuses to let unchecked work reach the publish step.

### Scope

**In scope.** Three people. Four output types: post package, carousel, picture
art direction, four-week calendar. One local app. One approval gate.

**Out of scope, deliberately.**

- Posting to LinkedIn. No API, no scheduling, no automation of the publish step.
  A human presses publish, always.
- Adding new people. Three is the set. Adding a fourth is a code change and that
  is the honest state of it.
- Analytics or reach measurement. I cannot measure LinkedIn reach honestly inside
  five days, so I do not claim it.
- Generating images of people. The picture package produces art direction, and a
  raster only if an image provider is configured.

### How this differs from the reference scenario

The reference scenario is request intake: missing information, wrong
classification, and delayed handoffs. This is not that.

There is no ticket queue here, no classification step, and no handoff between
teams. The recurring work is **content production**, and the bottleneck is
**verification before publication**, not routing. The domain, the failure modes,
and the fix are all different.

---

## 2. Priority — Why solve this first?

### Frequency

3 posts a week for me, 4 a week for each of the other two people. Every one needs
the same checks. It is the most repeated piece of work I do.

### Cost of the errors

The three failure modes are not equal, and that shaped what I built.

| Failure | How often it happened before | What it costs |
| --- | --- | --- |
| Invented number | Almost every draft, at least once | Rework, and public damage if missed |
| Broken voice rule | Frequent | Reads generic. The whole point was that it should not |
| Medical or confidentiality claim | Rare | The largest cost of the three. A real person's professional standing |

The last row is why the safety layer blocks instead of warning. A warning in an
editable box gets copied by accident. A redaction cannot be.

### What I compared it against

**Keeping the manual process.** Works, and does not scale past one person. Every
extra person adds the same checking time again.

**Simple ChatGPT use with a long pasted prompt.** This is what I actually did
before, and it is the honest comparison. It is fast and it produces text that
looks right. I measured it as a control arm, and it published a serious violation
on 13 of the 15 briefs it managed to answer. Details in section 5.

**Building a full posting automation.** Rejected. It would take longer than five
days, and it automates the wrong step. The writing was never the slow part.

### Feasibility

The system is one local app, one model provider, and no external services. It
runs on my machine with one API key. That was reachable in the time available,
which a posting integration was not.

---

## 3. Approach — What I did, and what I checked

### The key hypothesis

If the person's verified facts and rules live in the system rather than in a
pasted prompt, then the checking work moves from me to the software, and the
output quality stops depending on whether I remembered to paste the right thing.

### What I actually did, in order

**1. Read the source documents properly.** I have three written "engine"
documents, one per person, built earlier this year. They contain the voice rules,
the verified fact tables, the banned phrasings, the hashtag rules, and the safety
limits. I treated these as the source of truth and pulled the persona
specifications out of them by hand.

Two things came out of that read that I did not expect, and both are in the system
now:

- Two claims I have used about myself are not in my own source document. The
  first prize is real, but the document does not tie it to any specific project.
  And a transcription hours-and-accuracy figure appears nowhere in any of the ten
  documents. **The system now refuses to write either of them** and says why. They
  sit in a "believed but not verified" list.
- The health coach's document has no colours, no fonts and no slide sizes in it at
  all. I derived her visual style from her own brand banners, and the system labels
  it as derived rather than pretending it was specified.

**2. Rebuilt the app around one persona specification.** Before this week I had a
working prototype: about 1,200 lines that generated text and audited it. The
safety instinct in it was right. The structure was not. Persona details were
spread across four files, so adding a person meant four edits and forgetting one
crashed the app.

I am stating this plainly because it matters for honesty: **the prototype existed
before the Quest. The rebuild happened during it.** What I am claiming is the
rebuild and the evidence, not a from-nothing build. `docs/CASE_STUDY.md` lists
every change and why.

**3. Built the evaluation last, and it changed the system.** This is the part I
would keep if I could keep only one. Details in section 4.

**4. Checked the fact tables against the newest source, and found a real
mistake.** The persona specifications were built from the engine documents. My
LinkedIn engine document is dated 18 July 2026. My master profile, which carries a
running verified-facts log, is dated 29 August 2026 and is newer.

The app was shipping a figure I had publicly withdrawn. On 3 August 2026 I
disclosed that "prospect research went from about 10 hours a week to about 3, a 70
percent reduction" was invented. My profile records the retraction and the
canonical replacement. The engine document predates it, so the app was built with
the retracted figure listed as a **verified fact**, inside the system whose entire
purpose is refusing invented figures.

Two claims went the other way. I had marked "300+ hours of multilingual audio at
95%+ accuracy" and the attribution of the Be10x prize to the Agentic SDR
Personalization Engine as unverified, on the strength of the engine document alone.
The profile confirms both. They are facts now.

My own profile already records this exact lesson from a previous occurrence: *"The
stale claims were living in CODE, where nobody was reading them. When a fact
changes, grep the pipeline as well as the profile."* It happened again, in a new
codebase, four days later.

The fixes: the persona file now states which source wins on facts, the withdrawn
figure is a banned phrasing rather than a fact, there is a test that fails if it
returns, and there is an evaluation case that asks for it directly.

### What I gave to AI, and what I kept

| Given to AI | Kept by me |
| --- | --- |
| Writing the Python | Choosing what the system refuses to do |
| Turning my source documents into persona specifications | Deciding which claims are verified and which are not |
| Writing the evaluation harness | Deciding what counts as a failure |
| Drafting the documentation | Every judgement about the three real people's reputations |

Full detail in `docs/AI_COLLABORATION.md`.

### Where AI was wrong and I corrected it

Three worth naming, because they are the ones a reader should not have to take on
trust.

- The first model list it built contained a model that had been switched off two
  weeks earlier. The first real run failed. Every model in the list has now been
  called and confirmed working, and the app has a button that re-checks them.
- It first hid every provider error behind one generic sentence. That meant a
  switched-off model and a dropped internet connection looked identical, and the
  only useful instruction — pick a different model — was invisible. Errors are now
  sorted into a clear sentence, without ever showing the raw error text.
- It wrote a safety rule that missed the plural. "My migraines vanished" was not
  caught because the rule expected "migraine". The independent scorer caught it.
  That is exactly why the scorer shares no code with the thing it scores.

---

## 4. Solution — What it is, and what I checked

### The flow

```
Brief  ->  Generate  ->  Edit and preview  ->  QA and approve  ->  History
```

Five steps, in a fixed order. You cannot approve something you have not generated,
and the check always runs on whatever is in the boxes at that moment, not on what
the model first produced.

**1. Brief.** Pick the person. Fill in the goal, the audience, the core idea, and
the proof. Proof is the field that matters: any number you type there is treated
as verified for that piece. Leave it empty and the system writes `[OPEN SLOT]`
wherever evidence belongs, and refuses to approve until you deal with it.

**2. Generate.** One call per output type. Two tries each: the request, then one
corrective retry if the answer did not fit the required shape. No third try.

**3. Edit and preview.** Every part of the package is its own editable box. The
carousel renders into real 1080x1350 slides you can look at, with a PDF and a ZIP
to download.

**4. QA and approve.** Two layers.
   - *Lint* is advice. Cliches, em dashes, engagement bait, too many hashtags. It
     never blocks. Style is a judgement and the writer gets the last word.
   - *Audit* blocks. Unverified numbers, inflated versions of true claims, and the
     person's own safety rules. An unverified number is **replaced** with
     `[OPEN SLOT]`, not just flagged, because a flagged number in an editable box
     gets pasted by accident.

**5. History.** Only approved, cleaned text is saved, in a local database file.
Briefs, raw model output, error messages and API keys are never written to it.

### Human decision points

| Point | Who decides |
| --- | --- |
| Which idea, and what proof backs it | Human |
| Whether an open slot gets a real number or the sentence gets cut | Human |
| Whether to accept a style warning or ignore it | Human |
| Whether a safety block is correct | The system. It cannot be overridden in the app |
| Publishing to LinkedIn | Human, outside the app entirely |

### Data and tool connections

Two, and both are real, not simulated.

- **NVIDIA NIM**, over its OpenAI-compatible API, for all text generation. This is
  the only required provider. Models are restricted to a checked list; an
  environment variable cannot smuggle in one that is not on it.
- **Local file and image rendering**, using Pillow, for the carousel slides, the
  PDF, and the ZIP. No image service. No remote fonts. The font is included in the
  repository so the slides look the same on any machine.

Optional and clearly marked as optional: **OpenRouter**, for extra text models and
for turning the picture prompt into an actual image. Without it, everything except
the raster image still works.

### Configuration and secrets

Keys live in a local `.env` file, which is listed in `.gitignore` and is not in
the repository. `.env.example` shows the shape with no real values. I checked:
`git ls-files` does not list `.env` or the history database.

### Failure handling

- Two tries per generation, then a clear message. Never a third.
- Provider errors are sorted into a plain sentence that says what to do. The raw
  error text is never shown, because it can contain a web address, a request id,
  or part of a key.
- Every request has a time limit.
- If the model returns JSON with a trailing comma, the system repairs it rather
  than throwing the whole package away.
- If no portrait has been uploaded, the author slide falls back to an initials
  mark rather than leaving a hole.
- If no image provider is set up, the picture package returns the art direction
  prompt and **says so**. It never presents a prompt as if it were an image.

### What is not built

- No posting to LinkedIn.
- No fourth persona without a code change.
- No reach or engagement measurement.
- One grounded brief in seven still needs a person to delete a number the model
  added on its own. The check is right; the writing is wrong. This is measured,
  not estimated. See section 5.

### How to reproduce it

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.lock
copy .env.example .env
```

Put an NVIDIA key in `.env`, then:

```bash
python -m streamlit run app.py
```

To re-run the evaluation without spending anything:

```bash
python -m evals.run_evals
```

Full instructions in `README.md`. Operator instructions in `docs/RUNBOOK.md`.

---

## 5. Expected Outcome — What changes, and what I actually measured

### What I measured, and what I did not

**Measured, with a recorded run anyone can repeat:** how the full system compares
against simple AI use, on 20 written test cases. Every model response is saved to
the repository, so the numbers can be re-derived rather than believed.

**Not measured:** my own before-and-after time, under a stopwatch. My manual
timings are recollection. I have labelled them as estimates and I am not treating
them as evidence.

**Not measured:** LinkedIn reach, engagement, or business outcome. Five days is not
enough to claim that, so I do not.

### The comparison

Two arms. Both use the same model, the same required output shape, and the same
two attempts.

- **Studio**: the full system. Person's facts and rules in the prompt, plus the
  check and the approval gate.
- **Control**: the same model, told clearly who it is writing for and what to
  write, and nothing else. No fact list, no rules, no check, no gate. This is a
  fair version of "just use ChatGPT well", not a weak one.

The scorer that judges both arms shares no code with the app. If it used the app's
own checking code, the app would score perfectly by definition and the number
would mean nothing.

**20 test cases**: 7 normal ones that should publish cleanly, 12 that ask for
something that must not be published, and 1 with no evidence at all. Each carries
a written reason for existing.

### Results

Model: `nvidia/nemotron-3-super-120b-a12b`.

| | Studio | Control (simple AI use) |
| --- | --- | --- |
| Produced a usable result | **19 of 20** | 14 of 20 |
| Published something unpublishable | **0** | **11** |
| Serious violations that reached the page | **0** | **41** |
| Normal briefs that came out ready to publish | 4 of 6 | 5 of 5 |

What the control published, unprompted: a fasting schedule with exact hours, a
named candidate, a superlative with its qualifier removed, "zero human oversight",
"CAC to zero", "my clients" when I have none, and **the figure I publicly withdrew
as invented**.

That last one is the case I would point a reviewer at. Case A12 asks for it
directly. The control wrote it. The system refused.

The control is also worse at the mechanical job. It failed to produce a usable
result on 6 of 20 briefs against 1 for the studio. Being told the rules helps a
model follow the required shape as well as the policy.

These numbers move between runs, because generation is not deterministic. Across
three recorded runs the studio shipped 1, then 0, then 0 unsafe results, and its
grounded-brief pass rate was 2/5, then 6/7, then 4/6. **The safety result has held
at or near zero every time. The usability result is noisy and I am not going to
pretend otherwise.** One run is not a trend.

### What the evaluation changed

The first run scored worse: 17 of 20 produced, 1 unpublishable thing shipped,
and only 2 of 5 normal briefs came out clean. Five fixes came from reading the
failures:

| Fix | Why | Effect |
| --- | --- | --- |
| Repair a trailing comma before giving up | A complete package was thrown away over one character | Recovered a case |
| Ignore blank lines in the body, loosen list limits | Good packages rejected for having 4 reply templates instead of 3 | 17 of 20 to 20 of 20 |
| Tell the model explicitly not to invent numbers | It was adding figures, the check was correctly removing them, and that blocked approval | 2 of 5 to 5 of 7 |
| A first-person exemption no longer applies when the sentence speaks to the reader | A post kept every medication sentence in the first person and still told the reader their daily pill might be unnecessary | The one unpublishable thing, closed |
| Separate planning notes from publishable copy | The calendar is *told* to mark missing proof, and the gate then blocked on those marks. A correct calendar could never be approved | 5 of 7 to 6 of 7 |

Two of these could not have been found by the unit tests, because both needed a
real generated calendar to exist first.

A sixth fix came from outside the harness and the harness then confirmed it: the
fact-table correction in section 3. After it, replaying the old recordings turned
six calendar entries red, because the model had written the withdrawn figure into
the calendar back when the app's own fact table said it was verified. Correct a
fact, replay, and yesterday's output is correctly rejected. That is the loop
doing its job.

### Metrics table

| Metric | Current state and evidence | Observed experiment and conditions | Target and assumptions | Next measurement, owner, timing |
| --- | --- | --- | --- | --- |
| Unpublishable content reaching a draft | Simple AI use: 11 of 14 answered briefs. Measured | 20 cases, 2 arms, 1 model, recorded and replayable | 0. Achieved in all three runs | Re-run after any prompt change. Me. Every change |
| Usable result produced | Simple AI use: 14 of 20. Measured | Same run | 19 of 20. Near target | Same |
| Normal briefs ready to publish with no human fix | 4 of 6. Measured, and noisy: 2/5, 6/7, 4/6 across three runs | Same run | 6 of 6. Not reached | Same |
| My time per post and carousel | By hand: 30 to 60 minutes. With the engines: about 5 minutes of review. **Both are estimates from memory, not stopwatch measurements, and the improvement belongs to the engines rather than to this app** | Not measured under this system | About 5 minutes of review, unchanged. This system is not aimed at speed | Stopwatch on the next 5 posts. Me. Next 2 weeks |
| Adoption | Not measured. The system is 1 week old | Not measured | Used for every post across 3 people | Count of approved packages in the local history. Me. Week 2 |
| LinkedIn reach or engagement | Not measured, and out of scope | Not measured | No target set | Not planned inside this window |

### What would make me stop or change this

- If the check blocks more than 2 in 7 normal briefs, it is too strict to use and
  the prompt needs work before the rules do.
- If anything unpublishable gets through again, the safety layer is the priority
  over every feature.
- If I stop using it for a fortnight, the honest conclusion is that the manual
  process was fine and I should retire this.

### The next two weeks

1. Time myself properly on five real posts, so the time claim becomes a measurement
   rather than a memory.
2. Close the last blocking case: the model still occasionally adds a number the
   brief did not give it.
3. Have one person who is not me open it cold and get to a finished carousel
   without asking me anything.
4. Re-run the evaluation after each change, because the recorded run makes that
   free.

---

## Publication consent

`[[FILL: choose one and delete the other]]`

I consent to publication on MUST Hunt if selected.

I do not consent to publication on MUST Hunt.
