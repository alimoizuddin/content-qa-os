# Loom Rehearsal Script

*Your 5 minute video of the LinkedIn Content Studio, step by step*
*For Ali Moizuddin. MUST Company 5-Day AI OS Sprint Quest. Updated 10 September 2026.*

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
| **Terminal** | The window where you type a command. You only need it once, to start the app. |
| **Loom** | The tool that records your screen and your voice. |
| **Brief** | The short form where you describe the post you want. |
| **Safety check** | Step 4 of the app. It reads the post and stops anything false or unsafe. |
| **[OPEN SLOT]** | A gap the app leaves where it needed proof and did not have any. |
| **Test cases** | 20 practice requests used to measure the app. 12 of them deliberately ask for things that must never be posted. |
| **Claude Project** | Your old way of working. Your rules are written in a document, and Claude is asked to follow them. |
| **Asking plainly** | Using the AI with no rules at all, the way most people use ChatGPT. |

## Before you press record

Do this once, about 15 minutes before you record. Tick each one off.

1. **Clear the screen.** Close WhatsApp, Slack, email, and anything else that can pop up. Turn on Do Not Disturb.
2. **Check your key.** If you changed your Mesh key since the last time the app ran, open the file called `.env` in the project folder with Notepad. Paste the new key after `MESH_API_KEY=` and save.
3. **Start the app.** Press the Windows key, type **PowerShell**, and press Enter. Type the first line below and press Enter, then the second line and press Enter.
    `cd C:\Users\aalim\content_qa_os`
    `.\venv\Scripts\python -m streamlit run app.py`
4. **Wait** until the window says **You can now view your Streamlit app**. Leave this window open. Closing it closes the app.
5. **Open the app.** Open Chrome. In the address bar type `127.0.0.1:8501` and press Enter. The app does not open by itself, so this step matters.
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
| Stay on **Step 1**. Do not click anything. | I write LinkedIn content for three people. Myself, an HR leader called Isshita, and a health coach called Rakhee. Three posts a week for me, and four a week for each of them. |
| Keep still. | Writing a post by hand used to take me thirty minutes to an hour. I fixed that before this week. I wrote a rulebook for each person and I run it as a Claude Project. Now I only review each post, for about five minutes. |
| Move the mouse over the help panel at the top of the page. | So this week was not about speed. It was about trust. My rulebook is just text that the AI is asked to follow. Most of the time it does. When it does not, nothing catches it except me. |
| Keep still. | And some mistakes really matter. Rakhee must never say a food cures an illness. Isshita must never name a job candidate. And none of us can use a number we cannot prove. |
| Keep still. | I am not a programmer. I have an MA in English Literature. So I am also exactly the kind of person this app has to be simple enough for. |

> **Tip.** Do not explain how the app is built here. Do not apologise for anything. Just say why it exists.

### Part 2. Watch it work

**Time:** 1:00 to 2:30  **Screen:** App, Step 1, then Step 2, then Step 3.

| On your screen (do this) | Say this |
| --- | --- |
| Scroll down a little. Click **Fill in an example for me**. The boxes fill in by themselves. | This is the form. I say who is posting, what the point is, and, most important of all, the proof. The real thing behind the idea. |
| Point at the box called **Your proof. The real thing behind the idea**. | Any number I put in this box counts as proven for this post. If I leave it empty, the app leaves a gap everywhere it needed proof, and it will not let me approve the post until I fill those gaps. |
| Look at **What should it make?** Check that **LinkedIn post package** and **Branded carousel** are both there. Click **Save and continue**. | I will ask for a post and a set of slides. |
| On **Step 2**, click **Generate**. Wait. It takes about 30 seconds to a minute. | Claude is writing this now, following Rakhee's rules. It gets two tries. If both fail, it stops and tells me why in plain words. It never keeps trying forever. |
| Still waiting. | While it works, one thing about privacy. This app runs only on my computer. The only thing that leaves it is the writing request. My key, my photos and my saved posts stay here. |
| **Step 3** opens by itself. Scroll slowly down the post. | Here is the full package. The post, the hashtags with a reason for each one, the first comment, and reply templates. Every piece is its own box, and I can change any word. |
| Click the tab **Branded carousel (PNG slides, PDF, ZIP)**. Scroll through the slides. | These slides are real images, 1080 by 1350 pixels, made on this computer in Rakhee's own colours. No design tool and no internet. |
| Click **Download LinkedIn PDF**. Let the file appear at the bottom of the browser. | And that is a PDF, ready to upload to LinkedIn. |

> **Tip.** If writing is slow on the day, press Generate before you start recording, and begin Part 2 on Step 3. Just say that you generated it a moment earlier. That is honest, and it saves a minute.

### Part 3. Try to break it

**Time:** 2:30 to 3:30  **Screen:** App, Step 3, then Step 4. Safety check.

| On your screen (do this) | Say this |
| --- | --- |
| Click the tab **LinkedIn post package**. Click inside the box called **LinkedIn post**. Press **Ctrl** and **A** to select everything, then type: `This programme cures thyroid disease.` | This is the most important part. Let me try to make it do something dangerous. I am typing a medical claim that Rakhee must never make. |
| Scroll down. Click **Check it for problems**. | It checks whatever is in the boxes right now, not what the AI first wrote. So nobody can sneak something in afterwards. |
| **Step 4** opens. Point at the red message, then at the **What to do:** line under it. | Stopped. It tells me what is wrong, and underneath it tells me exactly what to do about it. |
| Point at the grey **Approve and save it** button. | And the approve button is switched off. There is no override. If I ever think a block is wrong, that is a change to Rakhee's rules, agreed with Rakhee. It is not a click. |
| Click **Back to editing**. In the **LinkedIn post** box, press **Ctrl** and **A**, then type: `I have coached 5,000 women through their cravings.` Click **Check it for problems**. | One more. A number I have just made up. |
| Click **See exactly what would be saved**. Point at **[OPEN SLOT]** where the number used to be. | It does not just warn me. It takes the number out and leaves a gap. A warning can be copied by accident. A gap cannot. |

> **Tip.** Go slowly in this part. Let the red message stay on screen for two full seconds before you talk about it.

### Part 4. How I know it works

**Time:** 3:30 to 4:30  **Screen:** The summary.pdf window, on the table with three columns.

| On your screen (do this) | Say this |
| --- | --- |
| Press **Alt** and **Tab** to switch to **summary.pdf**. Point at the table. | I did not want to just claim this works, so I measured it. Twenty test requests. Twelve of them deliberately ask for things that must never be posted. |
| Point at each column heading, one at a time. | Three ways of doing the same job, with the same AI. Control is just asking plainly. Engine is my old Claude Project, with all my rules written down. Studio is this app, where the rules are checked every single time. |
| Point at the **Control** column. | Asked plainly, the AI published something unsafe 16 times, with 46 serious problems. That includes a figure I had publicly withdrawn as made up. |
| Point at the **Studio** column. | This app published zero. |
| Point at the **Engine** column. | Now the honest part. My Claude Project did nearly as well. The checker flagged three posts, and I read all three myself. Only one was a real problem. So with a strong AI, the app beats my rulebook by a little. Compared with asking plainly, it is a huge difference. |
| Keep pointing at the table. | One more thing. The first time I scored this, it said my Claude Project made eight mistakes. Most of those were the AI correctly refusing, and my checker reading the refusal as the mistake. I fixed the checker and reported the smaller number, even though the bigger one made my app look better. |

> **Tip.** This is the part the judges will remember. Slow down, and do not rush the last line.

### Part 5. What is not finished

**Time:** 4:30 to 5:00  **Screen:** Back to the app. Any screen is fine.

| On your screen (do this) | Say this |
| --- | --- |
| Press **Alt** and **Tab** to go back to the app. | What is not finished. One normal request in seven still gets stopped. The AI added a kind line telling the reader to talk to their doctor about their medication. That line is safe, but Rakhee's rule says never speak to the reader about their medication at all, so the app stops it. Loosening that is Rakhee's decision, not a click. |
| Keep still. | And I have not timed myself with a stopwatch. My before and after times come from memory, and I say so everywhere. |
| Keep still. | In the next two weeks I will time five real posts properly, ask Rakhee whether that one kind of sentence should be allowed, and have someone who is not me use the app without any help. |
| Stop the recording. | Thank you. |

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
| The browser says **This site can't be reached** | The app is not running. Go back to the PowerShell window and type the start command again. Check that you typed `127.0.0.1:8501`. |
| PowerShell says the port is **already in use** | An old copy of the app is still running. Close every PowerShell window, open a new one, and start again. If it still fails, restart the computer. |
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
| **178** | Automatic tests that check the app every time it changes. All of them pass. |

## After you record

1. **Watch it once** all the way through.
2. **Copy the Loom link.**
3. **Paste the link.** Open **directive.md** in the project folder. Find the line that says **ALI: paste the Loom URL here after recording.** and replace it with your link.
4. **Choose the consent line.** At the very end of **directive.md**, delete one of the two lines about MUST Hunt.
5. **Read your AI Collaboration Note.** Open **docs/AI_COLLABORATION.md**, read every line marked **Confirm**, and change anything that is not true.
6. **Submit** the five deliverables.
7. **Change your Mesh key** at meshapi.ai, because the old one was shared in a chat. Then paste the new key into `.env`, so the app keeps working.
