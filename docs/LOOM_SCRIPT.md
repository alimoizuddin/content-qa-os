# Loom Rehearsal Script

*Your 5 minute video of the LinkedIn Content Studio, step by step*
*For Ali Moizuddin. MUST Company 5-Day AI OS Sprint Quest. Updated 11 September 2026.*

> The Word version of this script is `docs/Loom_Rehearsal_Script.docx`. Both say the same thing.

## Read this first

This is a script for recording one short screen video, called a Loom. The video shows the judges your app working, and explains why you built it.

You do **not** have to learn it word for word. Say it in your own words. The judges want to see that you understand your own work, and reading aloud sounds like reading.

In the script, every **grey box** tells you what to do on the screen. Every **white box** next to it tells you what to say while you do it.

The video is about 5 minutes long and has 5 parts. If you ever forget a line, look at the screen and say what you see. That is always right.

### The 5 parts at a glance

| Part | Time | What you show | Screen to have open |
| --- | --- | --- | --- |
| **1.** The problem | 0:00 to 1:00 | Why this app exists | App, **Step 1. Your idea** |
| **2.** Watch it work | 1:00 to 2:30 | Fill the form, let it write, show the slides | App, **Step 1** then **Step 2** then **Step 3** |
| **3.** Try to break it | 2:30 to 3:30 | Type something unsafe and watch it get stopped | App, **Step 3** then **Step 4. Safety check** |
| **4.** How I know it works | 3:30 to 4:30 | The test results | The **summary.pdf** window |
| **5.** What is not finished | 4:30 to 5:00 | The honest limits | Back to the app |

### Words used in this script

| Word | What it means |
| --- | --- |
| **App** | The LinkedIn Content Studio you built. It opens in a web browser, but it runs only on your own computer. |
| **Browser tab** | One page open in Chrome or Edge. |
| **Black window** | The window that opens when you double-click run.bat. It is the app running. Leave it open while you record, and close it to stop the app. |
| **Loom** | The tool that records your screen and your voice. |
| **Brief** | The short form where you describe the post you want. |
| **Safety check** | Step 4 of the app. It reads the post and stops anything false or unsafe. |
| **[OPEN SLOT]** | A gap the app leaves where it needed proof and did not have any. |
| **Test cases** | 20 practice requests used to measure the app. 12 of them deliberately ask for things that must never be posted. |
| **Claude Project** | Your old way of working. Your rules are written in a document, and Claude is asked to follow them. |
| **Asking plainly** | Using the AI with no rules at all, the way most people use ChatGPT. |

## Before you press record

Do this once, about 15 minutes before you record. Tick each one off.

1. **Finish the checklist first.** Do steps 1 to 5 of **My_Checklist.pdf** before you record.
2. **Clear the screen.** Close WhatsApp, Slack, email, and anything else that can pop up. Turn on Do Not Disturb.
3. **Change your Mesh key first.** If you have not done it yet: make a new key at meshapi.ai, open the file called `.env` in the project folder with Notepad, paste the new key after `MESH_API_KEY=`, and save. The old key was shared in a chat.
4. **Start the app.** Open the project folder and double-click **run.bat**. A black window opens. Leave it open: closing it closes the app.
5. **Wait** a few seconds. Your browser opens the app by itself at `127.0.0.1:8501`. If it does not, open Chrome and type that address.
6. **Choose Rakhee.** In the left panel, under **Who is posting?**, choose **Rakhee Singhi**.
7. **Check the connection.** In the left panel you should see **Ready** next to **NVIDIA NIM** and **Mesh API**. Under **Which AI should write it?** you should see **Mesh . Claude Opus 5 (best writing)**.
8. **Open the results page.** In the project folder, double click **summary.pdf**. Scroll to the table with three columns: Studio, Engine and Control. Leave this window open. You will switch to it in Part 4.
9. **Make it easy to read.** Click back into Chrome. Press **F11** for full screen, then press **Ctrl** and **+** once to make the text bigger.
10. **Set up Loom.** Open Loom. Choose **Screen only**. Showing your face is optional. Choose **Full screen**, not one window, so the recording follows you when you switch to the PDF.
11. **Test your sound.** Record 10 seconds of yourself talking. Play it back. If you can hear yourself clearly, delete it and you are ready.

### The screens you will use

| Screen | How to get there | What you will see |
| --- | --- | --- |
| **Step 1. Your idea** | It opens first. Or click **1. Your idea** in the left panel. | The form, and a button called **Fill in an example for me**. |
| **Step 2. Write it** | Appears after you click **Save and continue**. | A summary of your idea and a button called **Generate**. |
| **Step 3. Check and edit** | Opens by itself when the writing is finished. | Two tabs at the top: **LinkedIn post package** and **Branded carousel**. Every piece of the post is in its own box. |
| **Step 4. Safety check** | Click **Check it for problems** at the bottom of Step 3. | Red messages that stop you, each with **What to do:** under it, and the **Approve and save it** button. |
| **Results page** | Press **Alt** and **Tab** to switch to the summary.pdf window. | The table with three columns: Studio, Engine and Control. |

## The script

> **Tip.** Everything in this video is real. The AI really writes the post, the slides are really made on your computer, and the tests really ran. You can say that out loud if anyone wonders.

### Part 1. The problem

**Time:** 0:00 to 1:00  **Screen:** App, Step 1. Your idea. Do not click anything yet.

| On your screen (do this) | Say this |
| --- | --- |
| Step 1 of the app. Do not click anything. | I write LinkedIn posts for three people. Me, an HR leader called Isshita, and a health coach called Rakhee. |
| Stay still. | A post used to take me half an hour to an hour. I already fixed that with a set of rules I run in Claude. Now I just check each post. About five minutes. |
| Stay still. | But checking is the risky part. The AI is only asked to follow my rules. Sometimes it does not. |
| Stay still. | And some mistakes really hurt. Rakhee can never say food cures an illness. Isshita can never name a job candidate. None of us can use a number we cannot prove. |
| Stay still. | I am not a programmer. I studied English Literature. So this app has to be simple enough for me. |

> **Tip.** Do not explain how the app is built here. Do not apologise for anything. Just say why it exists.

### Part 2. Watch it work

**Time:** 1:00 to 2:30  **Screen:** App, Step 1, then Step 2, then Step 3.

| On your screen (do this) | Say this |
| --- | --- |
| Click **Fill in an example for me**. | This is the form. Who is posting, what the post is about, and the proof. The proof is the real thing behind the post. |
| Point at the **Proof** box. | Any number I write here counts as proven. If I leave it empty, the app leaves a gap and will not let me approve. |
| Click **Save and continue**. Then click **Generate**. | Now the AI writes it, using Rakhee's rules. It gets two tries. If both fail, it tells me why, in plain words. |
| Wait for it to finish. | Everything runs on my own computer. Only the writing request goes out. My key and my posts stay here. |
| Step 3 opens. Scroll down slowly. | Here is the whole post. Hashtags, with a reason for each one. A first comment. Replies. I can change any word. |
| Click the **Branded carousel** tab. Scroll through the slides. | These slides are real pictures, made on my computer, in Rakhee's colours. |
| Click **Download LinkedIn PDF**. | And here is the PDF, ready for LinkedIn. It goes to my Downloads folder. |

> **Tip.** If writing is slow on the day, press Generate before you start recording, and begin Part 2 on Step 3. Just say that you generated it a moment earlier. That is honest, and it saves a minute.

### Part 3. Try to break it

**Time:** 2:30 to 3:30  **Screen:** App, Step 3, then Step 4. Safety check.

| On your screen (do this) | Say this |
| --- | --- |
| Click the **LinkedIn post package** tab. Click in the **LinkedIn post** box. Press **Ctrl** and **A**. Type: *This programme cures thyroid disease.* | Now let me try to break it. I will type something Rakhee must never say. |
| Click **Check it for problems**. | It checks what is in the boxes right now. So nobody can sneak something in later. |
| Step 4 opens. Point at the red message, then at **What to do**. | Stopped. It tells me what is wrong, and exactly how to fix it. |
| Point at the grey **Approve and save it** button. | And I cannot approve it. There is no way around it. That is on purpose. |
| Click **Back to editing**. Press **Ctrl** and **A** in the post box. Type: *I have coached 5,000 women through their cravings.* Click **Check it for problems**. | One more. A number I just made up. |
| Click **See exactly what would be saved**. Point at **[OPEN SLOT]**. | It takes the number out and leaves a gap. You cannot copy a gap by mistake. |

> **Tip.** Go slowly in this part. Let the red message stay on screen for two full seconds before you talk about it.

### Part 4. How I know it works

**Time:** 3:30 to 4:30  **Screen:** The summary.pdf window, on the table with three columns.

| On your screen (do this) | Say this |
| --- | --- |
| Press **Alt** and **Tab** to open **summary.pdf**. Point at the table. | I did not want to just say it works. So I tested it. Twenty tests. Twelve of them ask for things that must never be posted. |
| Point at the three columns, one by one. | Three ways, same AI. Asking it plainly. My old Claude rules. And this app. |
| Point at **Control**. | Asked plainly, the AI posted something unsafe sixteen times. Forty-six serious problems. It even used a number I had publicly taken back. |
| Point at **Studio**. | This app: zero. |
| Point at **Engine**. | Now the honest part. My old Claude rules did almost as well. Three posts were flagged. I checked each one myself. Only one was a real problem. So the app wins big over asking plainly, and only a little over my own rules. |
| Keep pointing at the table. | One more thing. The first time I checked, my own checker was wrong. It counted the AI saying no as a mistake. I fixed it and kept the smaller number, even though the bigger one made me look better. |

> **Tip.** This is the part the judges will remember. Slow down, and do not rush the last line.

### Part 5. What is not finished

**Time:** 4:30 to 5:00  **Screen:** Back to the app. Any screen is fine.

| On your screen (do this) | Say this |
| --- | --- |
| Press **Alt** and **Tab** to go back to the app. | What is not finished. One normal post in seven still gets stopped. The AI added a kind line telling people to talk to their doctor about their medicine. Rakhee's rule says never talk to readers about their medicine, so the app stops it. Changing that is Rakhee's choice. |
| Stay still. | I have not timed myself with a stopwatch yet. My times are from memory, and I say so everywhere. |
| Stay still. | In the next two weeks: time five real posts, ask Rakhee about that rule, and have someone else try the app without my help. |
| Stop recording. | Thank you. |

## How to practise

Three short rounds, then record. Do not practise more than this. It starts to sound rehearsed.

| Round | What to do | Time |
| --- | --- | --- |
| **Round 1. Read** | Read the whole script out loud once, sitting down, without the app. Circle any word that feels awkward and write your own word above it. | 10 minutes |
| **Round 2. Click** | Do every click in the grey boxes without talking. Get used to where each button is. | 10 minutes |
| **Round 3. Both** | Talk and click together, with a timer on your phone. Aim to finish in under 5 and a half minutes. Do not record yet. | 6 minutes |
| **Record** | Two takes at most. The second one is usually the best. A fourth one is usually worse. | 12 minutes |

### Where you should be on the clock

| Part | How long | Finish by |
| --- | --- | --- |
| **1.** The problem | 1 minute | 1:00 |
| **2.** Watch it work | 1 and a half minutes | 2:30 |
| **3.** Try to break it | 1 minute | 3:30 |
| **4.** How I know it works | 1 minute | 4:30 |
| **5.** What is not finished | Half a minute | 5:00 |

### If something goes wrong

| What happened | What to do |
| --- | --- |
| The browser says **This site can't be reached** | The app is not running. Double-click **run.bat** again and wait for the black window to say it is starting. |
| The black window says the port is **already in use** | An old copy of the app is still running. Close every black app window and double-click **run.bat** again. If it still fails, restart the computer. |
| Writing takes longer than a minute | Keep talking, using the privacy line from Part 2. If it fails, it will tell you why. Click **Generate** once more. |
| It says the account is **out of credit** | The Mesh account needs a top up. Or, in the left panel under **Which AI should write it?**, choose an **NVIDIA NIM** model and carry on. |
| The slides do not appear | Click **Render slides**. |
| You say something wrong | Keep going. The judges are not marking how smoothly you speak. If it matters, correct it in one sentence and move on. |
| You lose your place | Look at the screen and say what you see. Then find the next grey box. |

### Numbers to remember

| Number | What it means |
| --- | --- |
| **3** | People you write for. 3 posts a week for you, 4 a week for each of the others. |
| **30 to 60 minutes** | One post by hand. With your Claude Project, about 5 minutes of review. Both are from memory, not a stopwatch. |
| **20** | Test requests. 12 of them ask for things that must never be posted. |
| **16 and 46** | Asking plainly: 16 unsafe posts, 46 serious problems. |
| **3, and 1 real** | Your Claude Project: 3 posts flagged. You checked them yourself and only 1 was a real problem. |
| **0** | This app: nothing unsafe published. |
| **1 in 7** | Normal requests that still get stopped, because Rakhee's medication rule is strict on purpose. The honest cost. |
| **188** | Automatic tests that check the app every time it changes. All of them pass. |

## After you record

1. **Watch it once** all the way through.
2. **Copy the Loom link.**
3. **Put the link in directive.md.** Easiest: send it to Claude. Or open **directive.md**, find **ALI: paste the Loom URL here after recording.** and replace it with your link.
4. **Choose your consent line.** At the very end of **directive.md**, keep one of the two lines about MUST Hunt and delete the other. Or tell Claude which one.
5. **Give the reviewers access on GitHub.** Ask Janeth which username to add. Then open your project on GitHub, click **Settings**, then **Collaborators**, then **Add people**.
6. **Submit the five deliverables** on the Match Hire page: the GitHub link, **docs/EVALUATION.md**, **directive.md** with **summary.pdf**, **docs/AI_COLLABORATION.md**, and your Loom link.
7. **Tell Janeth** you have submitted.
