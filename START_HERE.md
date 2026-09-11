# Start Here

A simple guide to setting up the LinkedIn Content Studio from nothing, using it, and
adding a new person to it.

You do not need to know how to code for Parts 1 and 2.

---

## What this app does

It helps you write LinkedIn posts. Then it checks them.

It will not let you post a number you cannot prove, a health promise, or a private
detail about someone else. When it finds one, it stops and tells you how to fix it.

It never posts anything by itself. You copy the words and post them yourself.

## What you need

- A Windows computer. A Mac works too; see the end of Part 1.
- The internet.
- About 20 minutes the first time.

---

## Part 1. Set it up

### Step 1. Install Python

Python is a free program the app needs to run.

1. Go to https://www.python.org/downloads/
2. Click the big yellow **Download Python** button.
3. Open the file you downloaded.
4. **Important:** at the bottom of the first screen, tick the box that says
   **Add python.exe to PATH**.
5. Click **Install Now**. Wait until it says it has finished.

### Step 2. Get the app folder

Ask the person who looks after the app for the folder. Or download it yourself:

1. Open the project page on GitHub. It is private, so you need to be given access
   first.
2. Click the green **Code** button, then **Download ZIP**.
3. Find the ZIP in your Downloads folder. Right click it and choose **Extract All**.
4. Open the new folder. You should see a file called **run.bat**.

### Step 3. Get your free key

A key is like a password that lets the app talk to the AI. It is free.

1. Go to https://build.nvidia.com and sign up.
2. Find your API key and click **Copy**.

Never share your key. Never put it in a chat, an email, or a screenshot.

### Step 4. Start it for the first time

1. Double-click **run.bat**.
2. A black window opens. Let it work. The first time takes a few minutes.
3. Notepad opens a file called `.env`.
4. Find the line `NVIDIA_API_KEY=`. Click just after the `=` sign and paste your
   key: press **Ctrl** and **V**.
5. Save: press **Ctrl** and **S**. Close Notepad.

If Windows shows a blue box that says it protected your PC, and you got the folder
from the person who looks after the app, click **More info** and then **Run anyway**.
It appears because the file is new to your computer.

### Step 5. Start it for real

1. Double-click **run.bat** again.
2. Wait a few seconds. Your web browser opens the app.
3. Keep the black window open while you use the app. Closing it stops the app.

That is it. Next time, you only do Step 5.

**On a Mac:** open the Terminal app, go into the folder, and type `./run.sh`.
Everything else is the same.

**Want better writing and pictures?** You can add a Mesh key the same way, on the
line `MESH_API_KEY=`. Mesh costs money. The app works without it.

---

## Part 2. Use it

The app has five steps. You can see them along the top.

1. **Your idea.** Choose who is posting on the left. Say what the post is about. In
   the **Proof** box, write the real thing behind it: something that happened, or a
   number you can prove. Not sure what to write? Click **Fill in an example for
   me**.
2. **Write it.** Click **Generate**. Wait up to a minute.
3. **Check and edit.** Read it. Change any words you like.
4. **Safety check.** Click **Check it for problems**. If something is red, read the
   **What to do** line under it and fix it. Then click **Approve and save it**.
5. **Saved posts.** Everything you approved is kept here. Click **Download as a
   text file** to get a copy.

### Where your files go

| What | Where it goes |
| --- | --- |
| Slides (PDF and ZIP) and pictures | Your **Downloads** folder |
| Posts you approved | Inside the app, in Step 5. Download them from there |

### If something goes wrong

| What you see | What to do |
| --- | --- |
| The browser cannot reach the site | The app is not running. Double-click **run.bat** |
| "The provider rejected the API key" | Your key is wrong. Paste it again in `.env`, save, close the black window, and double-click **run.bat** |
| "Out of credit" | On the left, under **Which AI should write it?**, choose an **NVIDIA NIM** one |
| A red message about health or privacy | The app is protecting someone. Change the words. You cannot skip it, and that is on purpose |
| Anything else | Read `docs/RUNBOOK.md`, or ask the person who looks after the app |

---

## Part 3. Add a new person

Right now the app writes for three people. You can add yourself, or anyone who has
said yes to being added.

It happens in two parts. **You fill in a form.** Then **the person who looks after
the app adds you.** That takes them about an hour. It is careful work on purpose,
because the app uses these answers to decide what you are allowed to say in public.

### 3a. Fill in this form (you)

Copy these questions into an email or a document, and answer them. Short answers are
fine.

1. Your full name, the way you want it on your posts.
2. Your job title, exactly as it should appear.
3. In one sentence, what you do.
4. Who you want to read your posts.
5. Three to five topics you post about.
6. How you sound. Pick a few words, for example: warm, direct, funny, calm.
7. Words you like to use.
8. Words you never want to use.
9. **Facts about you that you can prove.** For each one, say where it is written down
   and when. For example: "Trained 500 people. It is on my certificate, March 2025."
   The app only lets you use numbers that are on this list. If you cannot prove it,
   leave it out.
10. Things you must never say in public. For example: health promises, or private
    details about clients.
11. Hashtags you use, and any you never use.
12. Your two brand colours, if you have them. Or just say something like "dark and
    gold" or "light and green".
13. How many times a week you post, and the best time of day.
14. A photo for your slides. This one is optional.

Only write things about yourself that you are happy to have in the app. Never write
someone else's private details.

### 3b. Add the person (the person who looks after the app)

This part means editing code. Go slowly. The tests at the end check every step.

1. Open `core/personas.py` in a text editor.
2. Find the line that starts `RAKHEE = PersonaSpec(`. Copy everything from that line
   down to its matching closing bracket `)`. That bracket sits on its own line, just
   above a comment block that says `# Registry`.
3. Paste the copy just above that `# Registry` comment. Change the first word from
   `RAKHEE` to the new person's name in capitals, for example `SAM`.
4. In the copy, replace Rakhee's details with the form answers: `name`, `title`,
   `audience`, `pillars` (topics), `use_words`, `never_words`, the hashtags,
   `visual` (colours), `publish` (days and times), `star_facts` (the facts they can
   prove, each with the numbers it allows), `pending_verification` (things believed
   but not yet proven), and `safety_rules` (things they must never say).
5. In the `PERSONAS` line, add the new name to the list:
   `(ALI, ISSHITA, RAKHEE, SAM)`.
6. Open `evals/scoring.py`. In `LICENSED_NUMBERS`, add the new person with the
   numbers from their proven facts, typed out by hand. That is on purpose: the
   checker that marks the app must never copy from the app.
7. Open `evals/cases.json`. Add at least two test cases for the new person: one
   normal post that should pass, and one that asks for something they must never
   say. Copy an existing case and change it.
8. Run the tests. In the project folder, in Command Prompt, type
   `venv\Scripts\python -m pytest -q`. They must all pass. If one fails, its message
   tells you what is missing.
9. Record each new test case once, with the same model as the others. This needs the
   Mesh key in `.env`, and costs a little money:
   `venv\Scripts\python -m evals.run_evals --live --record --model anthropic/claude-opus-5 --case YOUR_CASE_ID`
10. Refresh the results for every case, which is free:
    `venv\Scripts\python -m evals.run_evals`
11. Close the black window and double-click **run.bat**. The new person is now in the
    **Who is posting?** list.

One of the tests proves that a new person works from start to finish once they are
added: they appear in the app, the writing works, the checks run, and their slides
render. So if you follow these steps and every test passes, the app works for them.
