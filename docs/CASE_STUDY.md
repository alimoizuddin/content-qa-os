# Rebuild notes

What the studio was, what it is now, and why each change was made rather than
worked around.

## The starting point

1,210 lines that generated LinkedIn text and audited it. The safety instinct was
right and worth keeping. The product around it was not the engine described in the
source documents.

Six problems, in the order they mattered.

**The brief was one text box.** A model given a shape to fill and no material to
fill it with invents material. The auditor then spent its time redacting numbers
that should never have been generated. Fixed by making the brief structured, with
proof as a first-class field: goal, audience, core idea, proof, format, register.
Numbers supplied as proof are trusted for that piece, which is the escape hatch that
keeps the auditor from being an obstacle. No proof means `[OPEN SLOT]` and a blocked
approval, stated up front rather than discovered at the end.

**Persona identity lived in four places.** A prompt dictionary, a JSON fact table, a
colour dictionary inside the renderer, and `if persona_name == "..."` branches in
the auditor. Adding a persona meant editing four files, and forgetting the colour
dictionary meant a `KeyError` at render time. Fixed with one `PersonaSpec` holding
identity, voice, pillars, keywords, hashtags, post and carousel specs, palette,
cadence, surfaces, verified facts, and safety rules. The auditor is now data driven,
so a new persona cannot silently skip a domain guardrail.

**Carousel typography was never tested.** The renderer hardcoded a Windows font
path. CI runs on Linux, so every slide test passed against Pillow's bitmap fallback
and a 92px headline rendered tiny. Fixed by vendoring Inter under `assets/fonts/`
(one variable file, all weights) and adding a CI step that fails if it is missing.
The renderer also caches fonts instead of re-reading the TTF once per line of text,
and auto-fits type instead of letting a long headline run off the canvas.

**Image generation had never worked.** `create_picture` posted to
`https://openrouter.ai/api/v1/images`, which is not a route OpenRouter serves, so
the feature fell through to the prompt every time, and the only test covered the
fallback. Rewritten against chat completions with image modalities, and the
fallback path now says which of the four reasons it took.

**`NVIDIA_MODEL` was documented and read by nothing.** The model was hardcoded to a
single 11B vision model while the README and `.env` both described the variable as
the knob. Now honoured, still checked against the allowlist, and an unrecognised
value falls back with the sidebar reporting what actually resolved.

**History was written and never read.** One table, one insert, no query anywhere in
the app. Reading it back is what makes writing it worth doing.

## Things the rebuild changed on purpose

**The linter is per persona now.** The old list banned "leverage" globally. One of
these personas uses that word deliberately and often. A banned-word list that
contradicts a persona's own vocabulary trains people to ignore the linter, so the
list is now universal cliches plus that person's never-list, minus their use-list.

**Lint is advisory, audit blocks.** "You used a cliche" is a taste judgement and the
writer gets the final say. Facts and safety are not taste.

**Safety rules match sentence by sentence, with exemptions.** The source engine for
the health persona bans instructing anyone to change medication while explicitly
permitting her own history of wanting to. A single whole-text regex cannot draw that
line. Rules now carry an optional exemption pattern checked against the same
sentence, so "I wanted to stop depending on daily pills" passes and "you can stop
your medication" does not.

**The second comment is persona aware.** One persona controls two LinkedIn surfaces
and can legitimately comment from the second. The other two control one each, where
a "second account" comment would be staged, and their engines rule it out
explicitly. For them the second comment is the author's own second-wave comment and
the repost is a self-resurface. The package still has all the slots; what fills them
changes.

**Calendar formats must rotate.** A week of four carousels is one idea with four
dates on it. The schema rejects a week using a single format.

**The approval gate reports every reason.** It used to return the first. Fixing one
blocker and discovering a second is worse than seeing both.

## What the source documents actually said

Distilling three canonical engines into one specification surfaced things worth
recording.

- Two claims commonly attached to this work are not in the corpus. The Be10x first
  prize is verified; its attribution to a named project is not. A transcription
  hours and accuracy metric does not appear in any of the ten documents for that
  persona. Both are in `pending_verification`, which means the studio refuses to
  write them and says why. Writing them anyway would have made the honesty layer
  decorative.
- "Systems Architect" and a credits metric appear nowhere in the corpus. In the old
  code they survived only as a negative assertion in a test. That assertion is kept,
  broadened to all three personas, and now runs against the assembled prompt rather
  than a dictionary.
- The health persona's engine specifies no palette, no font, and no dimensions. Her
  visual system is derived from her own brand banners and is labelled as derived in
  `VisualSystem.source`, not presented as stated. That field exists so any colour in
  the app can be traced to whether someone specified it or someone inferred it.
- Her engine also bans medical claims by category rather than by list, and cancer is
  never named in it. A keyword denylist would therefore have missed it. The rule set
  names the category terms explicitly for that reason.
- The carousel dimension changed between versions of one engine, from square to
  1080x1350 portrait. Ingesting the superseded documents would have produced the
  wrong aspect ratio. `docs/source-corpus-audit.json` records which document wins
  for each person and what it supersedes.

## Three things only a live call could have found

The offline test suite passed at 100 tests before any of these surfaced, which is
worth recording: mocked providers prove the plumbing, not the provider.

**An allowlisted model had been retired.** The rebuilt allowlist was assembled from
plausible model names. One of them had reached end of life two weeks earlier, and
the first real generation failed with a 410. Two changes came out of it. Every model
in the allowlist has now been called and confirmed to return usable JSON. And
`check_live_catalogue()` compares the allowlist against what NIM is serving right
now, from a sidebar button, so the next retirement shows up as a warning rather than
a failed run.

**Hiding provider errors completely made this undiagnosable.** A retired model and a
dropped connection produced the identical sentence, which hid the only useful
detail: pick a different model. Status codes are facts about the request and are
safe to surface; response bodies can carry a URL, a request id, or part of a key,
and are not. `classify_provider_error` maps the status to an actionable sentence and
never quotes the body.

**Reasoning models spend the whole budget thinking.** The strongest available NIM
model emitted 16,000 characters of chain of thought and hit `max_tokens` before
writing a single brace. Passing `chat_template_kwargs: {"thinking": false}` fixed
it, and the flag is bound to the model in the allowlist rather than applied blindly,
because a model that does not accept it should not be sent it.

## What the evaluation found

The harness in `evals/` was built last and immediately paid for itself. Five
defects came out of the first run, and the pattern in them is worth recording:
none were reachable from the unit tests, because every one needed a real
generated artifact to exist before it appeared.

- **A complete package discarded over one character.** A trailing comma before a
  closing bracket failed the parse and spent a whole retry. Repaired now, and only
  when the text does not already parse, so a comma inside a string is never
  touched.
- **Good packages rejected for counts.** One had 25 "paragraphs", 13 of them empty
  strings the model used as blank lines. Another had four reply templates instead
  of three. Both were thrown away by schema ceilings that normalisation repairs
  for free. The schema is tolerant now and the publishing limit is applied after.
- **The auditor doing its job too often.** On grounded briefs the model added
  plausible extra figures, the auditor correctly redacted each one to an open
  slot, and approval blocked on three grounded cases in five. The fix was upstream:
  an explicit numbers rule in the prompt. Generation was giving the auditor too
  much to do.
- **A first-person exemption that outlived its justification.** The source engine
  permits the coach's own history and forbids instructing a stranger. A post kept
  every medication sentence in the first person and still closed with "Your daily
  pill might be answering a question your food never got to ask." The exemption is
  now cancelled by any sentence that addresses the reader.
- **A gate that contradicted its own instruction.** The calendar is *told* to write
  open slots wherever proof does not exist yet. The gate then blocked on them, so a
  correctly generated calendar could never be approved. Sections are now marked
  publishable or planning, and an open slot means different things in each.

Underneath the last one was a plain falsy-value mistake worth naming: the gate read
its blocking list with `or`, an empty list is falsy, and a clean result was
therefore recomputed down a path that discarded the planning exclusion. A calendar
stayed blocked with nothing blocking it. There is now a test that asserts on the
empty case specifically, because that is the only shape that catches it.

The independent scorer also caught a safety gap the application's own rule missed:
"my migraines vanished" matched in the scorer and not in the auditor, because the
auditor's pattern required a singular noun. That is exactly the class of thing a
scorer sharing code with the thing it scores can never find.

## The mistake worth recording

The persona specifications were built from the engine documents in the corpus.
Ali's LinkedIn engine document is dated 18 July 2026. His master profile carries a
running verified-facts log and is dated 29 August 2026.

On 3 August 2026 he had disclosed that "prospect research went from about 10 hours
a week to about 3, a 70 percent reduction" was a figure he invented. His profile
records the retraction and the wording that replaced it. The engine document
predates it and still carries the old number.

So this app shipped a publicly withdrawn claim as a **verified fact**, inside the
system whose entire purpose is refusing invented figures. It was in `star_facts`,
it licensed the numbers 10, 3 and 70 for every generation, and it would have been
written into real posts.

Two claims went the other way and had been wrongly quarantined: "300+ hours of
multilingual audio at 95%+ accuracy", and the attribution of the Be10x prize to the
Agentic SDR Personalization Engine. The profile confirms both.

**What changed as a result:**

- `core/personas.py` now states in its docstring which source wins on facts.
- The withdrawn phrasing is a banned inflation, so the auditor blocks it.
- A test fails if it reappears in `star_facts`.
- Evaluation case A12 asks for it directly. The studio blocks it. The control
  published it.
- After the correction, replaying the old recordings turned six calendar entries
  red, because the model had written the withdrawn figure into the calendar back
  when the fact table said it was verified. Correct a fact, replay, and yesterday's
  output is correctly rejected.

Ali's own profile already records this lesson from a previous occurrence: *"The
stale claims were living in CODE, where nobody was reading them. When a fact
changes, grep the pipeline as well as the profile."* It happened again, in a new
codebase, four days later. A written precedence rule is the only thing that stops
it happening a third time.

## What is still open

- The picture package needs an OpenRouter key and an image-capable model to produce
  a raster. NVIDIA NIM's text endpoint does not return images. Everything else,
  including the whole carousel pipeline, runs NVIDIA-only.
- One persona's engine prescribes six content formats and treats carousels as one of
  them rather than the default. The studio currently offers post, carousel, picture,
  and calendar for everyone. Her format-rotation weighting is encoded in the calendar
  prompt but not yet in the output selector.
- One grounded brief in seven still blocks: the model adds a figure the brief did
  not supply, the auditor redacts it, and a person has to delete the sentence. The
  numbers rule reduced this and did not remove it.
- Every platform pass in the source corpus carries a refresh date, and the oldest is
  undated. Platform behaviour is the part of these engines that expires. Treating it
  as a dated, swappable module rather than prose inside a persona spec is the obvious
  next structural change.
