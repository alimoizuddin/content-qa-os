# Operator Runbook

For the person running this day to day. The README says what it does. This says
what to do when it misbehaves.

---

## Starting it

```bash
cd content_qa_os
venv\Scripts\activate
python -m streamlit run app.py
```

It opens at `http://127.0.0.1:8501`. It only listens on this machine. Nobody else
can reach it, including on the same network.

To stop it: `Ctrl+C` in the terminal window.

---

## Daily use, in one line each

1. Pick the person in the left sidebar.
2. Fill in the brief. **The proof box is the important one.**
3. Generate.
4. Edit anything you want to change.
5. Run QA. Fix whatever it blocks on.
6. Approve. It saves to local history.
7. Copy the post, download the carousel, publish it yourself on LinkedIn.

---

## The messages you will see, and what to do

### "The provider could not complete this request"

The internet connection or the provider is having a problem. Wait a minute and
press Generate again.

### "That model has reached end of life and is no longer served"

NVIDIA switched the model off. Pick a different one from the Model dropdown in the
sidebar. Then press **Check models are still served** to see which others are
affected.

### "That model is not available to this account"

Same fix. Different model.

### "The provider rejected the API key"

Your key in `.env` is wrong, expired, or missing. Get a new one from
build.nvidia.com and replace the line in `.env`. You must restart the app after
editing `.env`.

### "Rate limited by the provider"

Too many requests too fast. Wait a couple of minutes.

### "The model returned a response that did not match the required structure, twice"

The model could not produce the right shape. In order:

1. Try again once. This is often random.
2. Shorten the brief, especially the proof box.
3. Switch to a different model in the sidebar.

### "[OPEN SLOT] still present in: post"

The system removed a number it could not verify. You have two choices, and both
are fine:

- **You know the real number.** Put it in the proof box in the brief and generate
  again. Anything in the proof box is treated as verified for that piece.
- **There is no real number.** Delete the sentence. This is usually the right
  answer.

You cannot approve until every open slot in publishable copy is dealt with. Open
slots in a *calendar* are fine and do not block; that is the calendar telling you
what proof you still need.

### A red BLOCKED message about a medical or confidentiality claim

The system found something that must not be published under that person's name.

**Do not try to work around it.** Rewrite the sentence. If you believe the block is
wrong, that is a rule change, not an override, and it belongs in
`core/personas.py` after a conversation with the person it protects.

### Style warnings in blue

Advice only. Cliches, em dashes, engagement bait, too many hashtags. They never
stop you approving. Ignore them if you disagree.

---

## Things that look broken and are not

**The picture package gives a text prompt, not a picture.** Correct, unless you
have set up an image provider. NVIDIA's text service cannot return images. The
prompt is a deliverable on its own; hand it to any image tool.

**The author slide shows initials instead of a face.** No portrait uploaded for
that person yet. Upload one in the sidebar. It is stored on this machine only.

**Generating takes 30 to 60 seconds.** Normal. A calendar takes longest.

**The slides did not change after I edited the text.** Press **Render slides**
again. It says when they are out of date.

---

## Maintenance

### Every month or so

Press **Check models are still served** in the sidebar. Providers retire models on
a schedule. This tells you before a generation fails.

### After changing a prompt or a person's rules

Re-run the evaluation and see if anything got worse:

```bash
python -m evals.run_evals --live --record
```

This costs money and takes about 20 minutes. It calls the provider 40 times.

To re-check without spending anything, using the last saved run:

```bash
python -m evals.run_evals
```

**Reading the exit code:**

| Code | Meaning |
| --- | --- |
| 0 | Everything behaved as expected |
| 2 | Something that must not publish did, or a normal brief got blocked. **Look at it before shipping anything.** |
| 1 | The harness could not run at all |

### Before sharing the folder with anyone

Your API key lives in `.env`. It is excluded from git, so it is not in the
repository. But **if you zip the folder, the key goes with it.** Delete `.env`
first, or send the repository link instead.

---

## Where things are

| What | Where |
| --- | --- |
| Your API key | `.env`. Never committed |
| What each person is allowed to claim | `core/personas.py` |
| The rules that block publishing | `core/personas.py`, in each person's `safety_rules` |
| Approved work | `data/history.db`. Local only |
| Portraits | `assets/portraits/`. Local only |
| Test cases | `evals/cases.json` |
| Last evaluation run | `evals/results/latest.json` |

---

## Changing the rules

**To let a person claim a new fact:** add it to their `star_facts` in
`core/personas.py`, with the number tokens it allows. Then re-run the tests.

**To move a claim from "not verified" to "verified":** it must come out of
`pending_verification` and into `star_facts`, and only when you have the source in
writing. This is the one change that should never be made quickly.

**To add a new safety rule:** add a `SafetyRule` to that person's list. Then add a
case to `evals/cases.json` that the rule should catch, and re-record. A rule with
no test is a rule that will quietly stop working.

After any change:

```bash
python -m pytest -q
python -m evals.run_evals
```
