---
name: mentor
description: Review writers' work with the Writing Mentor Framework. Asks where the assignment, rubric and writers' files are, then gives each writer two-part feedback (notes for the mentor, feedback for the writer). Use when the user types /mentor or asks to review, grade or give feedback on submissions with the writing mentor.
---

# /mentor — set up and run a review

FRAMEWORK = `{{FRAMEWORK}}`
PY = `{{PYTHON}}`

(If those two lines still show curly-brace placeholders, this file was not installed by
the installer. Tell the user to run the installer, and stop.)

You are guiding a mentor who may not use the command line or GitHub. Ask one thing at a
time. Use plain words: "your rubric", "the writers' files", "the feedback folder". Never
mention manifests, scripts, agents, prompts or other tool terms. Call the people whose work is reviewed "writers" and their files "their work",
not "students" or "submissions", unless the user uses those words first. Use the AskUserQuestion
tool for each question when it is available, with your best guess as the first option.

## 0. Check the tools (quietly)

Run `PY "FRAMEWORK/skills/feedback/scripts/check_dependencies.py"`. If it reports
missing items, tell the user in one or two sentences what is missing and that running
the installer again will add it. Charts are optional: if only chart images are
unavailable, say so and continue.

## 1. Look before asking

List the current folder (two levels deep, names only; skip hidden folders and any
existing `feedback*` folders). Guess from the names which file is the assignment, which
is the rubric, which folder or files are the writers' work, and whether a course
concepts file exists. Do not open the writers' files.

## 2. Ask, one question at a time

1. **Assignment.** "Which file has the assignment instructions?" Offer your guess, other
   likely files, and "I'll paste it". Word, PDF, text or Markdown are all fine. If
   pasted, save it to `feedback/_work/inputs/assignment-pasted.md` and use that file.
2. **Rubric.** Same, for the rubric. A rubric is required; if there is none, offer to
   help write a short one from the assignment, and get their approval of it first.
3. **Writers' files.** "Where are the writers' files?" Offer the folder you found, "all
   the other files in this folder", or "somewhere else" (they give the path).
4. **Course principles (optional).** "Is there a file of course principles the analysis
   should follow (for example, 'use real GDP for comparisons over time')?" Options:
   your guess, "No — use general principles", "I'll paste some".
5. **Resubmission?** "Is this a first submission or a revision?" If a revision, ask for
   the folder with the earlier feedback (offer any `feedback*` folders you saw) and the
   round number. The output folder becomes `feedback-round{N}`; otherwise `feedback`.

If the output folder already contains feedback, ask whether to replace it or use a new
folder name (`feedback-2`, ...). Never delete earlier feedback without a yes.

## 3. Group the files by writer, and confirm

```bash
PY "FRAMEWORK/skills/feedback/scripts/prepare_review.py" group \
  --submissions "<writers' files folder or files>" --out "<output folder>" \
  --assignment "<file>" --rubric "<file>" [--concepts "<file>"] \
  [--prior-feedback "<earlier feedback folder>" --round N]
```

Show the result as a short list: each writer and their files, older versions that will
be skipped, and files not matched to anyone. Ask: "Does this match who handed in what?"
If not, ask what to change, edit `<output folder>/_work/manifest.json` accordingly
(move file paths between writers' `files` lists, add or rename writers), and show the
list again.

## 4. Say what will happen, and wait

Tell the user, in about five lines:
- how many writers will be reviewed, and that each gets a separate, fresh review
- that the contents of these files are sent to Anthropic (the company that makes
  Claude) to be read, and that they should check this is allowed for this work
- that it takes several minutes per writer, and they can leave it running
- where the results will go

Ask: "Start the review?" Do nothing more until they say yes.

## 5. Prepare the files

```bash
PY "FRAMEWORK/skills/feedback/scripts/prepare_review.py" run --manifest "<output folder>/_work/manifest.json"
```

If any file is `skipped` or `failed`, tell the user which and why in plain words (for
example, "one spreadsheet is damaged and couldn't be opened; its reviewer will note
that"), then continue.

## 6. Run the review

Read `FRAMEWORK/skills/feedback/SKILL.md` and follow it from step 2, using FRAMEWORK and
PY above.

## 7. Finish

Tell the user where everything is, using full paths:
- one `.md` file per writer, with Section A (for them only) and Section B (for the writer)
- one Word file per writer with only the Writer Feedback, ready to send
- `FEEDBACK_SUMMARY.md` with all scores and common issues

Offer to open the summary. Remind them to read each Word file before sending it.
