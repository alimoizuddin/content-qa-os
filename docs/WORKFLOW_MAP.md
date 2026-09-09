# Workflow map

The work before, and the work now.

> `[[Ali: the timings below are blank on purpose. Fill them in from memory and
> label them as estimates. Do not guess precisely. "About 40 minutes" is more
> honest than "38 minutes" and reads better.]]`

---

## Before: producing one LinkedIn package by hand

```mermaid
flowchart TD
    A[Trigger: a post is due<br/>3 to 4 times a week, per person] --> B[Pick the idea<br/>from the calendar]
    B --> C[Find the real proof<br/>dig through notes and old projects]
    C --> D[Draft the post<br/>by hand, or ChatGPT with a long pasted prompt]
    D --> E{Re-read against<br/>the voice rules}
    E -->|breaks a rule| D
    E -->|passes| F{Check every number<br/>against the fact list}
    F -->|cannot source it| D
    F -->|all sourced| G{Safety check<br/>medical / confidentiality}
    G -->|breach| D
    G -->|clear| H[Write hashtags,<br/>first comment, replies]
    H --> I[Design the carousel slides]
    I --> J[Export slides to PDF]
    J --> K[Publish on LinkedIn]

    style E fill:#f8d7da,stroke:#c00
    style F fill:#f8d7da,stroke:#c00
    style G fill:#f8d7da,stroke:#c00
```

**The three red boxes are the bottleneck.** Not the drafting. Each one is a manual
re-read of the whole piece, looking for a different kind of problem, and each one
can send you back to the start.

| Step | Who does it | Time | Notes |
| --- | --- | --- | --- |
| Pick the idea | Human | `[[FILL]]` | |
| Find the proof | Human | `[[FILL]]` | The digging step |
| Draft | Human, or AI with a pasted prompt | `[[FILL]]` | |
| **Voice re-read** | Human | `[[FILL]]` | Loops back |
| **Number check** | Human | `[[FILL]]` | Loops back |
| **Safety check** | Human | `[[FILL]]` | Loops back |
| Hashtags, comments, replies | Human | `[[FILL]]` | |
| Carousel design | Human | `[[FILL]]` | |
| Export | Human | `[[FILL]]` | |
| **Total** | | `[[FILL]]` | Estimate from memory |

### Exceptions in the old process

- **The proof does not exist.** Realised halfway through drafting. Either the post
  gets rewritten around a different angle or it gets dropped.
- **A number cannot be sourced.** Same outcome: rewrite or cut.
- **The safety issue is found late**, after the carousel is already designed. Then
  the slides get redone too.

---

## Now: the same package through the studio

```mermaid
flowchart TD
    A[Trigger: a post is due] --> B[Brief<br/>person, goal, audience, idea, PROOF]
    B --> C[Generate<br/>2 attempts, then it stops]
    C --> D[Edit and preview<br/>every part editable, slides render]
    D --> E{QA}
    E -->|style advice| F[Ignore or fix.<br/>Never blocks]
    E -->|unverified number| G[Replaced with OPEN SLOT.<br/>Blocks]
    E -->|safety breach| H[Blocked.<br/>No override in the app]
    F --> I{Approve}
    G -->|human supplies proof<br/>or cuts the sentence| D
    H -->|human rewrites| D
    I --> J[Saved to local history]
    J --> K[Human publishes on LinkedIn]

    style G fill:#f8d7da,stroke:#c00
    style H fill:#f8d7da,stroke:#c00
    style I fill:#d4edda,stroke:#0a0
    style K fill:#d4edda,stroke:#0a0
```

**What moved.** The three manual re-reads became one automatic check. The human
work that remains is the work that needs judgement: choosing the idea, supplying
the proof, and deciding whether a flagged sentence gets a real number or gets cut.

**What did not move.** Publishing. A human still presses publish on LinkedIn,
every time, outside the app.

| Step | Who does it | Notes |
| --- | --- | --- |
| Brief | Human | The proof box is the grounding contract |
| Generate | System | 2 attempts maximum |
| Edit | Human | Optional |
| Style check | System | Advice only |
| Fact check | System | Removes unverified numbers. Blocks |
| Safety check | System | Blocks. Cannot be overridden in the app |
| Resolve a block | Human | Supply proof, or cut the sentence |
| Approve | Human | Only possible when nothing blocks |
| Carousel slides and PDF | System | Local, about one second |
| Publish | Human | Outside the app |

---

## Where a human must still decide

| Decision | Why it stays human |
| --- | --- |
| Which idea, and what proof it rests on | This is the thinking. The system has no view on it |
| Whether an open slot gets a real number or the sentence gets cut | Only a person knows if the number exists |
| Whether to accept a style warning | Voice is a judgement |
| Whether a safety block is correct | The system holds the line. Changing it is a rule change, made outside the app, in conversation with the person it protects |
| Publishing | Always |

---

## Input variation the system has to handle

| Variation | How it is handled |
| --- | --- |
| Brief with full proof | Normal path |
| Brief with no proof | Open slots inserted, approval blocked, stated up front in the brief screen |
| Brief asking for something unpublishable | Blocked at QA. Tested by 13 of the 20 evaluation cases |
| Three different people with three different rule sets | One persona specification per person. The checker reads the rules from it, so a new person cannot silently skip a guardrail |
| A person with no numbers in their evidence at all | Handled. Evidence can be a real remembered moment. Tested by case G04 |
| Model returns malformed JSON | Repaired if it is a trailing comma. Otherwise one corrective retry, then a clear message |
| Model is switched off by the provider | Named in the error, with instructions to pick another. A sidebar button checks the whole list |
| No image provider configured | The picture package returns art direction and says so. It never presents a prompt as an image |
| No portrait uploaded | The author slide falls back to an initials mark |
