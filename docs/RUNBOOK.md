# Operator Runbook

For the person running this day to day. The README says what it does. This says
what to do when it misbehaves.

---

## Starting it

Double-click **`run.bat`** in the project folder. On macOS or Linux, run
`./run.sh`.

The first time, it sets itself up, which takes a few minutes once, and opens a
settings file in Notepad. Paste your NVIDIA key after `NVIDIA_API_KEY=`, save,
close Notepad, and double-click `run.bat` again.

After that it just starts. A black window opens and your browser opens the app at
`http://127.0.0.1:8501`. It only listens on this machine. Nobody else can reach
it, including on the same network.

To stop it: close the black window.

---

## Daily use, in one line each

1. **Who is posting?** Pick the person in the left panel.
2. **1. Your idea.** Fill in the form. **The proof box is the important one.**
3. **2. Write it.** Press **Generate**.
4. **3. Check and edit.** Change anything you want. Every box is editable.
5. **4. Safety check.** Press **Check it for problems**. Fix anything red.
6. Press **Approve and save it**. It is saved on this computer.
7. Copy the post, download the carousel, and publish it yourself on LinkedIn.

---

## Where your files go

| What | Where |
| --- | --- |
| Carousel PDF and ZIP, picture | Your browser's **Downloads** folder, when you press a download button |
| Approved posts | `data/history.db` on this computer. **5. Saved posts** has a button to download each one as a text file |
| Run log: timings and outcomes, never any content | `data/logs/runs.jsonl` |
| Author photos | `assets/portraits/` |
| Your API keys | `.env` |

None of these are uploaded anywhere, and none are committed to git.

---

## The messages you will see, and what to do

### "The provider could not complete this request"

The internet connection or the provider is having a problem. Wait a minute and
press **Generate** again.

### "The provider account is out of credit"

The Mesh account behind that key has run out of money. Top it up, or choose an
**NVIDIA NIM** model under **Which AI should write it?** in the left panel.

### "The model ran out of room before it finished writing, twice"

The answer was cut off before it was complete. Ask for fewer things at once, for
example a post without the carousel, or choose another model.

### "That model has reached end of life and is no longer served"

The provider switched the model off. Pick a different one under **Which AI should
write it?** in the left panel. Then press **Check the AI models still work** to
see which others are affected.

### "That model is not available to this account"

Same fix. Different model.

### "The provider rejected the API key"

Your key in `.env` is wrong, expired, or missing. Get a new one and replace the
line in `.env`. Close the black window and double-click `run.bat` again after
editing `.env`.

### "Rate limited by the provider"

Too many requests too fast. Wait a couple of minutes.

### "The model returned a response that did not match the required structure, twice"

The model could not produce the right shape. In order:

1. Try again once. This is often random.
2. Shorten the brief, especially the proof box.
3. Switch to a different model in the left panel.

### "[OPEN SLOT] still present in: post"

The system removed a number it could not verify. You have two choices, and both
are fine:

- **You know the real number.** Put it in the proof box and generate again.
  Anything in the proof box is treated as verified for that piece.
- **There is no real number.** Delete the sentence. This is usually the right
  answer.

You cannot approve until every open slot in publishable copy is dealt with. Open
slots in a *calendar* are fine and do not block; that is the calendar telling you
what proof you still need.

### A red message about a medical or confidentiality claim

The system found something that must not be published under that person's name.
The line under it, **What to do:**, says how to fix it.

**Do not try to work around it.** Rewrite the sentence. If you believe the block is
wrong, that is a rule change, not an override, and it belongs in
`core/personas.py` after a conversation with the person it protects.

### Grey style suggestions

Advice only. Cliches, engagement bait, too many hashtags. They never stop you
approving. Ignore them if you disagree. Em dashes are not on this list any more:
they are removed automatically the moment the text is written.

---

## Things that look broken and are not

**The picture package gives a text prompt, not a picture.** Correct, unless a Mesh
key is set in `.env`. NVIDIA's text service cannot return images. The prompt is a
deliverable on its own; hand it to any image tool.

**The author slide shows initials instead of a face.** No photo uploaded for that
person yet. Upload one in the left panel. It is stored on this machine only.

**Writing takes 30 to 60 seconds.** Normal. A calendar takes longest. **5. Saved
posts** shows the typical time from the run log.

**The slides did not change after I edited the text.** Press **Render slides**
again. It says when they are out of date.

**A carousel came back with 8 slides when the model wrote more.** Correct. The
limit is 6 to 8. The cover and the closing slide are kept and the middle is
trimmed.

---

## Maintenance

### Every month or so

Press **Check the AI models still work** in the left panel. Providers retire
models on a schedule. This tells you before a generation fails.

### After changing a prompt or a person's rules

Re-run the evaluation and see if anything got worse:

```bash
python -m evals.run_evals --live --record
```

This costs money and takes about 20 minutes. With three arms it calls the provider
at least 60 times. Check the account has credit first: a run that runs out part
way through reports every case after that point as a failure.

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

Your API keys live in `.env`. It is excluded from git, so it is not in the
repository. But **if you zip the folder, the keys go with it.** Delete `.env`
first, or send the repository link instead.

---

## Where things are

| What | Where |
| --- | --- |
| Your API keys | `.env`. Never committed |
| What each person is allowed to claim | `core/personas.py` |
| The rules that block publishing | `core/personas.py`, in each person's `safety_rules` |
| Approved work | `data/history.db`. Local only |
| Run log | `data/logs/runs.jsonl`. Local only |
| Photos | `assets/portraits/`. Local only |
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
