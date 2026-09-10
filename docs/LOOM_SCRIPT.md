# Loom script, 5 minutes

Read this, do not memorise it. Say it in your own words. They are assessing
whether you understand your own system, and a read-aloud script sounds like one.

Face camera is not required. Screen only is fine.

**Before you hit record:**

- App running at `http://127.0.0.1:8501`, on the Brief stage, Rakhee selected
- A second browser tab with `evals/results/latest.json` open, or the results table
  from `docs/EVALUATION.md`
- A terminal window ready, in the project folder, venv activated
- Close Slack, WhatsApp, email. Anything that can pop up

---

## 0:00 to 1:00. The problem

**Say, roughly:**

> I write LinkedIn content for three people. Myself, an HR leader, and a health
> coach. Three posts a week for me, four a week for each of them.
>
> By hand a post took me thirty to sixty minutes. I already fixed that: I built a
> written engine per person and I run it as a Claude Project, and now I review for
> five minutes instead of writing. That saving is not what this week was about, and
> I want to be clear about that up front.
>
> What the engine could not do is prove it was safe. The rules live in a document
> the model is asked to obey. Most of the time it does. When it does not, nothing
> catches it except me.
>
> Three things go wrong every time. It invents numbers that sound right. It breaks
> voice rules quietly, so the copy still reads fine. And for two of these three
> people there are things that genuinely cannot be published. The health coach
> cannot say food cures a condition. The HR leader cannot name a candidate or
> promise anyone a job.
>
> I am not a developer. I have an MA in English Literature. So I am also the
> person this has to be usable by.

**Do not:** explain the architecture yet. Do not apologise for scope.

---

## 1:00 to 3:30. The system, running for real

Talk while you click. Do not narrate every field.

**Brief stage.** Fill it in live. Say:

> Person, goal, audience, core idea, and proof. Proof is the one that matters.
> Any number I put in there is treated as verified for this piece. If I leave it
> empty, the system marks every place it wanted evidence and refuses to approve
> until I deal with it.

**Generate.** While it runs, say:

> One call per output. Two tries, then it stops and tells me what happened. Never
> a third.

**Edit and preview.** Scroll the carousel slides.

> Every part is its own editable box. The slides are real 1080 by 1350 images,
> rendered on this machine. No image service, no internet. There is a PDF and a
> ZIP.

Click the PDF download so they see it land.

**Now the important bit. Break it on camera.**

Go to the post text box. Type in a claim that must not publish. For Rakhee:

> This programme cures thyroid disease.

Click **Run QA**.

> That is the part I would keep if I could only keep one thing.

Point at the blocked message. Point at the greyed-out Approve button.

> It checks whatever is in the boxes right now, not what the model first wrote. So
> I cannot generate something clean and then paste something dangerous in
> afterwards. And there is no override button in the app. If I think a block is
> wrong, that is a rule change, not a click.

**Also show a number being removed.** Type a made-up figure into the post. Run QA.

> It does not warn me about an unverified number. It removes it and puts a marker
> there. A warning in an editable box gets copied by accident. A hole cannot be.

---

## 3:30 to 4:30. How I know it is better

Switch to the results table.

> I did not want to claim this was better, so I measured it.
>
> Twenty test cases. Two arms. One is the full system. The other is the same
> model, told clearly who it is writing for and what to write, and nothing else.
> That is a fair version of just using ChatGPT well, because that is what I did
> before.
>
> The judge that scores both shares no code with the app. If it used the app's own
> checking, the app would score perfectly by definition.

Point at the numbers.

> The control published something unpublishable on thirteen of the fifteen briefs
> it managed to answer. Forty-five violations. Including a fasting schedule with
> exact hours, and a made-up figure of twelve thousand four hundred and
> eighty-seven.
>
> The full system published zero.

Then, immediately:

> The first run was worse. Five things came out of reading the failures. One was a
> safety rule that let a post keep every medication sentence in the first person
> and still tell the reader their daily pill might be unnecessary. That got
> through. I fixed it and re-ran.

**This is the most important 20 seconds of the video.** Showing a failure you
found and fixed is worth more than any clean demo.

---

## 4:30 to 5:00. The limitation

Pick one. Say it plainly. Do not soften it.

> The honest limitation is that one normal brief in seven still gets blocked. The
> model adds a number the brief did not give it, the checker correctly removes it,
> and I have to go and delete the sentence. The checker is right. The writing is
> wrong. I reduced it and I did not eliminate it.
>
> And I have not measured my own time saved with a stopwatch. My before-numbers
> are from memory, and I have labelled them as estimates everywhere rather than
> presenting them as results.
>
> Next two weeks: time myself properly on five real posts, close that last case,
> and get someone who is not me to run it cold.

---

## Rules for the recording

- **Do not present anything planned as finished.** If it is not built, say so.
- **Say when something is a simulation.** Nothing here is, so say that too: the
  provider calls are real, the slides are really rendered, the evaluation really
  ran.
- **Do not rehearse it five times.** Two takes. The second one is always better
  and the fourth is always worse.
- If you fumble, keep going. They are not marking your delivery.
