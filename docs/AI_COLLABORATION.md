# AI Collaboration Note

> **Ali: read this before submitting and correct anything that is not true.**
> It was drafted from what happened in the build sessions. The blanks have now been
> filled in from what you actually said and did, and every one of those is marked
> **Confirm** so you can check it rather than take it on trust. Only you can sign
> this. Change anything that overstates what you did.

## Tools used, and what each did

| Tool | Role |
| --- | --- |
| Claude (Opus), in Claude Code | Wrote the application code, the tests, and the evaluation harness. Read the three source engine documents and turned them into persona specifications. Drafted this documentation. |
| NVIDIA NIM (`nemotron-3-super-120b-a12b`) | A model the application can call. Used for the earlier two arm evaluation runs. |
| Mesh API (`anthropic/claude-opus-5`) | The default writer in the application now, and the model all three arms of the current evaluation ran against. |
| Claude Projects | Where my three written engine documents run. This is the system this app replaces, and the third arm of the evaluation measures it. |
| Wispr Flow | Voice dictation. I dictate a month to three months of content calendar in a single sitting rather than typing it. |
| ChatGPT | General use, over a long period. It is the tool the control arm of the evaluation stands in for. |

> **Confirm:** these three are taken from your own description of your workflow.
> Add anything else you used during this week, in particular anything you used to
> check the AI's work rather than to produce it. Remove anything you did not
> actually use for this project.

Note the two different roles. Claude built the system. NIM is *inside* the system.
They are not the same job and the evaluation only measures the second one.

## What I delegated

- All Python. The application, the interface, the tests, the evaluation harness.
- Reading three long source documents and pulling the persona rules out of them.
- Writing the safety rules as patterns.
- Writing this documentation.

## What I kept

- **Choosing the problem.** Which recurring work to fix, and why the checking step
  was the bottleneck rather than the writing.
- **What the system refuses to do.** No posting to LinkedIn. No overriding a safety
  block from inside the app. A human always presses publish.
- **Which claims count as verified.** This is the decision the whole system rests
  on, and it is not delegable. See the next section.
- **What counts as a failure.** The evaluation labels say "this must not be
  published". That is a human judgement about three real people's reputations.
- **Which provider the app runs on.** I moved it from OpenRouter to Mesh API and
  made Claude the writer, so that the strongest model I have access to does the
  writing while my own rules do the blocking.
- **That the comparison had to be measured, not asserted.** When I asked whether
  this app was actually better than my Claude Project, the honest answer was that
  nobody had tested it. I asked for the test to be built and run rather than accept
  an opinion, including the possibility that it would show the app was not worth it.
- **That the submission would not invent a test user.** I was told a real external
  user was needed. I checked the brief myself. It says a proxy user is acceptable
  and that access to real customers is not required. I am the non-developer this
  is built for, so I used it and produced the numbers.
- **How this is written.** Plain words and short sentences, in the documents and in
  the app. If a person cannot understand the warning, the warning has not worked.

> **Confirm:** all four are from decisions you made in the build sessions. Cut any
> you would rather not claim.

## How I checked what the AI produced

**I ran it.** Not as a demonstration. I am the non-developer this system is built
for, and I used the app end to end: filled in a brief, generated, looked at the
slides, and read the results. Things that only show up in real use showed up.

**I built a judge that shares no code with the thing it judges.** The evaluation
scorer imports nothing from the application. If it used the app's own checking
code, the app would score perfectly by definition. That independence immediately
found a safety gap the app's own rule had missed.

**I ran it against the real provider, not a mock.** The offline test suite passed
before every one of the failures below surfaced. It now stands at 178 tests, and it
still would not have caught most of them. Mocked tests prove the plumbing works.
They do not prove the provider works.

**I made it prove the structure was worth it.** The evaluation runs a control arm:
the same model, asked politely, with none of the structure. If the structure
bought nothing, that comparison would have said so.

## Results I rejected or corrected

These are the ones a reader should not have to take on trust.

**A model list containing a switched-off model.** The AI assembled the allowed
model list from plausible-looking names. One had reached end of life two weeks
earlier and the first real run failed. I had every model called and confirmed
working, and had a button added that re-checks the list against what is actually
being served.

**Error messages that hid the only useful information.** The first version put
every provider failure behind one generic sentence. A switched-off model and a
dropped connection looked identical, and "pick a different model" was invisible.
Errors are now sorted into a clear instruction. The raw error text is still never
shown, because it can contain a web address, a request id, or part of a key.

**A safety rule that missed a plural.** "My migraines vanished" was not caught,
because the rule expected "migraine". The independent scorer found it.

**A safety exemption with no limit on it.** The rule permitting the coach's own
history let through a post that kept every medication sentence in the first person
and then told the reader their daily pill might be unnecessary. I had the exemption
cancelled by any sentence that speaks to the reader.

**A gate that contradicted its own instruction.** The calendar is told to mark
missing proof with `[OPEN SLOT]`. The gate then blocked on those marks, so a
correct calendar could never be approved. Underneath was a plain programming
mistake: an empty list is treated as false in Python, so a clean result was thrown
away and recalculated.

**A retracted figure of my own, shipping as a verified fact.** This is the one
that matters, and I found it by pointing the AI at the right source document
rather than the convenient one.

The persona rules were built from my LinkedIn engine document, dated 18 July 2026.
My master profile carries a running verified-facts log and is dated 29 August 2026.
On 3 August 2026 I had disclosed that "prospect research went from about 10 hours a
week to about 3, a 70 percent reduction" was a figure I invented. The profile
records the retraction. The engine document predates it.

So the app was built with a claim I had publicly withdrawn, listed as a **verified
fact**, inside the system whose entire purpose is refusing invented figures.

It is now a banned phrasing, its real replacement is the fact, there is a test that
fails if it comes back, and there is an evaluation case that asks for it directly
and checks the system refuses.

**Three failures that only a real provider could show.** Switching the writer to
Claude turned every case in a live evaluation run into "did not generate". The
newest Claude models reject a sampling setting that the older one ignored, and it
was written into the code at the point of use rather than recorded against the
model. Underneath that were two more: responses were being cut off part way
because the size limit had been set for a smaller model, and the app blamed the
user for it by saying "shorten your brief"; and when the provider account ran out
of credit, the app reported it as "check your connection", which was the one thing
it was not.

**The judge itself, scoring refusals as offences.** This is the correction I would
point a reviewer at second, after the retracted figure.

The first three arm run reported that my Claude Project published eight unsafe
posts. Reading them by hand showed that six were the model doing exactly the right
thing and saying so out loud. "I will not tell anyone to come off their tablets"
was scored as an instruction to come off tablets. Three further cases were marked
as publishing an unverified figure because the post mentioned four in the
afternoon, and the clock rule only recognised a time if it had minutes in it.

The corrected number is three, and on inspection only one of those three is
genuine. So the fair claim is one real catch in twenty cases, and that is what the
documents say. The uncorrected eight appears nowhere as a result.

I am recording this because the wrong number was the flattering one. It made my app
look better than it is, and if nobody had opened the cases it would have gone into
this submission.

**Two claims I had wrongly quarantined.** I had told the AI to treat "300+ hours of
multilingual audio at 95%+ accuracy" and the attribution of my Be10x prize to the
Agentic SDR Personalization Engine as unverified, because the engine document does
not carry them. My master profile confirms both. They are facts now.

The general lesson is one my own profile already records from a previous
occurrence: *"The stale claims were living in CODE, where nobody was reading them.
When a fact changes, grep the pipeline as well as the profile."* It happened again,
in a new codebase, four days later. The persona file now states in writing which
source wins when two disagree.

If asked which decision mattered most, it is this one. It was easier to leave the
number in.

## What I would say about my own understanding

I did not write the code and I am not going to pretend otherwise. I have an MA in
English Literature and no traditional programming background.

What I did was direct it, run it, read the parts that carry the decisions, and
push back when something was wrong. Three times that pushing back changed the
outcome. I refused a claim that the Quest required an external test user, and I was
right. I asked for the comparison against my own Claude Project to be measured
rather than asserted, and the measurement came back more modest than the
assumption. And I pointed the work at my master profile instead of the older
engine document, which is how the retracted figure was found.

The four files I can explain are `core/personas.py`, which holds what each of the
three people is allowed to claim, `core/auditor.py`, which holds the checks that
stop a post, `core/studio.py`, which holds the approval gate, and
`evals/scoring.py`, which is the judge and deliberately shares no code with any of
the others. I can explain what each one decides and why it is separate. I could not
sit down and write them from an empty file.

What I understand well is the part that is actually mine: what these three people
may and may not say in public, and what it costs when that goes wrong.

> **Confirm:** this is drafted from what happened. Read the four files named above
> before you sign it, and cut anything you would not be comfortable being
> questioned on in an interview. Understating this is safer than overstating it.
