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

**Two claims about myself that the AI would have written and I stopped.** Reading
my own source document properly showed that neither is supported by it. My first
prize is real, but no document ties it to a specific project. And a transcription
hours-and-accuracy figure appears in none of my ten documents. Both now sit in a
"believed but not verified" list, and the system refuses to write either and says
why.

That last one is the decision I would point to if asked which one mattered. It was
easier to leave them in. The whole system is about not doing that.

## What I would say about my own understanding

`[[FILL: your honest answer. Suggested shape below — rewrite it in your own words,
and do not claim more than is true.]]`

I did not write the code. I directed it, ran it, read the parts that carry the
decisions, and corrected it when it was wrong. The four files I can explain are
`core/personas.py` (what each person is allowed to claim), `core/auditor.py` (the
checks that block), `core/studio.py` (the approval gate), and `evals/scoring.py`
(the independent judge). `[[FILL: adjust once you have read them]]`
