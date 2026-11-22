---
name: writing-mentor-batch
description: Run a Writing Mentor review over every writer in a prepared folder — one fresh reviewer per writer, then Word copies and a summary. Usually started by /mentor.
---

# Running a review batch

This file runs the batch. What each reviewer does is in `review-one-writer.md` (same
folder). `FRAMEWORK` below is the folder that contains `skills/`; `PY` is the Python
command `/mentor` gave you (or `python3` on macOS / `python` on Windows).

Write everything the mentor reads in plain language: say what happened and where the
files are. No tool jargon.

## 1. Make sure the folder is prepared

Look for the manifest: `<output folder>/_work/manifest.json` with a `prepared` entry.

If it is missing (for example, a folder set up with the old `wmf init`), prepare it:

```bash
PY "FRAMEWORK/skills/feedback/scripts/prepare_review.py" group --submissions submissions \
   --out feedback --assignment assignment.md --rubric rubric.md [--concepts course_concepts.md]
```

Show the mentor the grouping it prints and ask them to confirm it. Then:

```bash
PY "FRAMEWORK/skills/feedback/scripts/prepare_review.py" run --manifest feedback/_work/manifest.json
```

Tell the mentor about any file marked `skipped` or `failed`, and why, before you go on.

## 2. Review each writer with a fresh agent

Read the manifest. For each writer, start one agent (Agent/Task tool,
`subagent_type: "general-purpose"`). Run 3 at a time: send 3 agent calls in one message,
wait for all of them, then the next 3. If you hit rate limits, drop to 1 at a time.

Fill this prompt from the manifest. List the files explicitly: the reviewer must not
search folders.

```
You are reviewing one writer's work for a mentor, using the Writing Mentor Framework.
Read and follow FRAMEWORK/skills/feedback/review-one-writer.md exactly.

Writer: {writer}
Write your feedback to: {output_dir}/{writer}.md  (this one file only)

Assignment (text): {input_text.assignment}
Rubric (text): {input_text.rubric}
Course concepts (text): {input_text.concepts or "none given — use general principles"}
Writing references: FRAMEWORK/skills/feedback/references/

This writer's files (read ONLY these):
  Extracted text: {review.extracted, one per line}
  Chart images: {review.charts, one per line, or "none"}
  Original files (open only if an extract is cut off or failed): {review.originals}
  Extraction notes: {review.report}
Prior feedback for a resubmission: {review.prior_feedback or "none"}
Similarity reports: {similarity files, or "none"}

Do not open any other file in the submissions or feedback folders.
When done, reply with one line: the total score, and the single biggest concern.
```

Collect each agent's one-line reply.

## 3. Check every feedback file

For each writer, confirm `{output_dir}/{writer}.md` exists and contains both
`SECTION A` and `SECTION B`. Rerun a writer once if not. If it fails again, tell the
mentor which writer and move on.

## 4. Word copies of the Writer Feedback

```bash
PY "FRAMEWORK/skills/feedback/scripts/make_writer_docx.py" "{output_dir}"
```

This makes `{writer} - Writer Feedback.docx` (Section B only) next to each `.md` file.

## 5. Summary

Start one more agent to write `{output_dir}/FEEDBACK_SUMMARY.md`. It reads every
writer's `.md` file in the output folder (and nothing else) and writes:

```markdown
# Feedback summary — [assignment name]

## Scores
| Writer | [each rubric criterion, with its points] | Total |
|---|---|---|
(highest total first)

**Mean** X · **Median** X · **Range** X–X · **Standard deviation** X

## One paragraph per writer
### [Writer] — [total]/[rubric total]
[Main strength, biggest concern, anything notable.]

## Issues that came up for several writers
1. [issue] — [how many writers]
```

For a resubmission round, add a column for the change from the earlier score.

## 6. Tell the mentor

- How many writers were reviewed, and any that failed.
- Where the files are: the `.md` files (both sections), the Word files (Writer Feedback
  only, ready to send), and the summary.
- Any files that could not be read, and that the reviewer worked without them.
- Reminder: Section A of each `.md` file is for them only.
