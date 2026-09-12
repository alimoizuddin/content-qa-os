# Handoff

Where this project stands, and how to pick it up without being told anything.

Read `CLAUDE.md` first. It holds the rules. This file holds the state.

---

## What this is

A local Streamlit app that turns one idea into a checked, publishable LinkedIn
package for three real people. Its purpose is not writing. Its purpose is refusing
to publish things that are not true. It was built for the MUST Company 5-Day Remote
AI OS Sprint Quest.

## Where it stands

**The build is finished and the submission is assembled.** 188 tests pass, and
GitHub's check passes on every commit. The evaluation replays with no API key at
all, which is what the Quest requires.

Measured on 20 cases with `anthropic/claude-opus-5`, judged by a scorer that shares
no code with the app:

| Arm | What it is | Unsafe published | Serious violations | Normal briefs shipped |
| --- | --- | --- | --- | --- |
| studio | the app | **0** | **0** | 6 of 7 |
| engine | the same rules as text, nothing enforcing them | 3 | 3 | 7 of 7 |
| baseline | the same model asked plainly | 16 | 46 | 5 of 5 |

The three engine flags were read by hand: one is a real catch, one is the scorer
misreading a refusal, one sits in a planning note that never reaches LinkedIn. The
fair claim is **one genuine catch in twenty**, and every document says so.

## What is left, and it belongs to Ali

His personal checklist is `private/My_Checklist.pdf`, which is not in git. The
short version:

1. Submit the five deliverables on the Match Hire page, then message Janeth.
2. Change the Mesh key. The old one was pasted into a chat.

Done on 12 September 2026: the collaboration note is signed, Minimax is described
as what it was, the demo video is linked, the consent line is chosen, and the
repository is public so reviewers need no invitation.

Two things were raised and never settled, and neither blocks the submission. The
demo video runs to seven and a half minutes where the brief asks for five. And the
demo line "I am not a programmer" could say instead that he has no coding
background but builds software by directing AI, which is both truer and better
suited to the role.

## Decisions that should not be reopened without a reason

- **Adding a person stays a code change.** A self-serve form would break a stated
  non-goal. `START_HERE.md` Part 3b is the written procedure and a test proves a
  fourth person works end to end once registered.
- **The repository is public**, since 12 September 2026, on Ali's instruction, with
  Isshita's and Rakhee's agreement recorded in `directive.md`. Two of the three
  people are real, so treat everything here as published the moment it is pushed.
  Nothing private about anyone goes in without their say-so.
- **The scorer never imports from the app.** It has caught the app twice.
- **No em dashes anywhere.** A test enforces it across the repository.
- **20 evaluation cases, not the 8 to 12 the brief asks for.** The extra ones are
  adversarial and are where every important failure was found. `directive.md` says
  this openly.

## Where everything lives

| What | Where |
| --- | --- |
| The rules for working here | `CLAUDE.md` |
| Setup from nothing, and adding a person | `START_HERE.md`, `START_HERE.pdf` |
| The case study | `directive.md`, `summary.pdf` |
| The evaluation | `docs/EVALUATION.md`, `evals/` |
| What the AI did and what Ali kept | `docs/AI_COLLABORATION.md` |
| Day to day operation | `docs/RUNBOOK.md` |
| Document builders | `tools/`, with `tools/README.md` |
| Ali's personal documents | `private/`, git ignored |
| Keys | `.env`, git ignored, never committed |
| Approved posts, run log | `data/`, git ignored |

## How to pick this up in a new session

```bash
python -m pytest -q          # 188 tests
python -m evals.run_evals    # replays the saved run, no key, no cost
```

Then read `CLAUDE.md`, then this file. The git log is written to be read: every
commit message says what changed and why, including the mistakes. `git log --stat`
is the honest history of this project.

If a document looks stale, check whether it is generated. `summary.pdf`,
`START_HERE.pdf`, and both Loom scripts are built by scripts, listed in
`tools/README.md` and in `CLAUDE.md`.
