// The spoken lines for Ali's Loom video, shared by both documents that use them:
// build_speaker.js (his own screen-and-words script) and build_rehearsal.js (the
// full rehearsal guide). One source, so what he practises is what he records.
const PARTS = [
  {
    name: "Part 1. The problem", time: "0:00 to 1:00",
    rows: [
      ["Step 1 of the app. Do not click anything.", "I write LinkedIn posts for three people. Me, an HR leader called Isshita, and a health coach called Rakhee."],
      ["Stay still.", "A post used to take me half an hour to an hour. I already fixed that with a set of rules I run in Claude. Now I just check each post. About five minutes."],
      ["Stay still.", "But checking is the risky part. The AI is only asked to follow my rules. Sometimes it does not."],
      ["Stay still.", "And some mistakes really hurt. Rakhee can never say food cures an illness. Isshita can never name a job candidate. None of us can use a number we cannot prove."],
      ["Stay still.", "I am not a programmer. I studied English Literature. So this app has to be simple enough for me."],
    ],
  },
  {
    name: "Part 2. Watch it work", time: "1:00 to 2:30",
    rows: [
      ["Click **Fill in an example for me**.", "This is the form. Who is posting, what the post is about, and the proof. The proof is the real thing behind the post."],
      ["Point at the **Proof** box.", "Any number I write here counts as proven. If I leave it empty, the app leaves a gap and will not let me approve."],
      ["Click **Save and continue**. Then click **Generate**.", "Now the AI writes it, using Rakhee's rules. It gets two tries. If both fail, it tells me why, in plain words."],
      ["Wait for it to finish.", "Everything runs on my own computer. Only the writing request goes out. My key and my posts stay here."],
      ["Step 3 opens. Scroll down slowly.", "Here is the whole post. Hashtags, with a reason for each one. A first comment. Replies. I can change any word."],
      ["Click the **Branded carousel** tab. Scroll through the slides.", "These slides are real pictures, made on my computer, in Rakhee's colours."],
      ["Click **Download LinkedIn PDF**.", "And here is the PDF, ready for LinkedIn. It goes to my Downloads folder."],
    ],
  },
  {
    name: "Part 3. Try to break it", time: "2:30 to 3:30",
    rows: [
      ["Click the **LinkedIn post package** tab. Click in the **LinkedIn post** box. Press **Ctrl** and **A**. Type: *This programme cures thyroid disease.*", "Now let me try to break it. I will type something Rakhee must never say."],
      ["Click **Check it for problems**.", "It checks what is in the boxes right now. So nobody can sneak something in later."],
      ["Step 4 opens. Point at the red message, then at **What to do**.", "Stopped. It tells me what is wrong, and exactly how to fix it."],
      ["Point at the grey **Approve and save it** button.", "And I cannot approve it. There is no way around it. That is on purpose."],
      ["Click **Back to editing**. Press **Ctrl** and **A** in the post box. Type: *I have coached 5,000 women through their cravings.* Click **Check it for problems**.", "One more. A number I just made up."],
      ["Click **See exactly what would be saved**. Point at **[OPEN SLOT]**.", "It takes the number out and leaves a gap. You cannot copy a gap by mistake."],
    ],
  },
  {
    name: "Part 4. How I know it works", time: "3:30 to 4:30",
    rows: [
      ["Press **Alt** and **Tab** to open **summary.pdf**. Point at the table.", "I did not want to just say it works. So I tested it. Twenty tests. Twelve of them ask for things that must never be posted."],
      ["Point at the three columns, one by one.", "Three ways, same AI. Asking it plainly. My old Claude rules. And this app."],
      ["Point at **Control**.", "Asked plainly, the AI posted something unsafe sixteen times. Forty-six serious problems. It even used a number I had publicly taken back."],
      ["Point at **Studio**.", "This app: zero."],
      ["Point at **Engine**.", "Now the honest part. My old Claude rules did almost as well. Three posts were flagged. I checked each one myself. Only one was a real problem. So the app wins big over asking plainly, and only a little over my own rules."],
      ["Keep pointing at the table.", "One more thing. The first time I checked, my own checker was wrong. It counted the AI saying no as a mistake. I fixed it and kept the smaller number, even though the bigger one made me look better."],
    ],
  },
  {
    name: "Part 5. What is not finished", time: "4:30 to 5:00",
    rows: [
      ["Press **Alt** and **Tab** to go back to the app.", "What is not finished. One normal post in seven still gets stopped. The AI added a kind line telling people to talk to their doctor about their medicine. Rakhee's rule says never talk to readers about their medicine, so the app stops it. Changing that is Rakhee's choice."],
      ["Stay still.", "I have not timed myself with a stopwatch yet. My times are from memory, and I say so everywhere."],
      ["Stay still.", "In the next two weeks: time five real posts, ask Rakhee about that rule, and have someone else try the app without my help."],
      ["Stop recording.", "Thank you."],
    ],
  },
];

module.exports = { PARTS };
