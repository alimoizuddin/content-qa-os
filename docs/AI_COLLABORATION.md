# AI Collaboration Note

> **Ali: read this before submitting and correct anything that is not true.**
> It was drafted from what happened in the build session. Only you know what you
> did outside it, and only you can sign it. Places needing your input are marked
> `[[FILL]]`.

## Tools used, and what each did

| Tool | Role |
| --- | --- |
| Claude (Opus), in Claude Code | Wrote the application code, the tests, and the evaluation harness. Read the three source engine documents and turned them into persona specifications. Drafted this documentation. |
| NVIDIA NIM (`nemotron-3-super-120b-a12b`) | The model the application itself calls to generate content. Also the model both arms of the evaluation ran against. |
| `[[FILL: anything else you used — ChatGPT, Gemini, Perplexity, n8n? Say what for.]]` | |

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
- `[[FILL: anything else you decided that is not on this list]]`

## How I checked what the AI produced

**I ran it.** Not as a demonstration. I am the non-developer this system is built
for, and I used the app end to end: filled in a brief, generated, looked at the
slides, and read the results. Things that only show up in real use showed up.

**I built a judge that shares no code with the thing it judges.** The evaluation
scorer imports nothing from the application. If it used the app's own checking
code, the app would score perfectly by definition. That independence immediately
found a safety gap the app's own rule had missed.

**I ran it against the real provider, not a mock.** 136 offline tests passed
before any of the following surfaced. Mocked tests prove the plumbing works. They
do not prove the provider works.

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

`[[FILL: your honest answer. Suggested shape below — rewrite it in your own words,
and do not claim more than is true.]]`

I did not write the code. I directed it, ran it, read the parts that carry the
decisions, and corrected it when it was wrong. The four files I can explain are
`core/personas.py` (what each person is allowed to claim), `core/auditor.py` (the
checks that block), `core/studio.py` (the approval gate), and `evals/scoring.py`
(the independent judge). `[[FILL: adjust once you have read them]]`
