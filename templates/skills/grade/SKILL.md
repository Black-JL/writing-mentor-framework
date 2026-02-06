---
name: grade
description: Review student submissions using the Writing Mentor Framework
user-invocable: true
---

# Grade Submissions

Review all submissions in this folder using the Writing Mentor Framework.

## What This Does

1. Checks for required dependencies (prompts to install if missing)
2. Extracts text from all submissions (DOCX, PDF, XLSX)
3. Renders Excel charts for visual review
4. Reviews each submission with isolated context (prevents bias)
5. Writes two-tier feedback (Reviewer Notes + Writer Feedback)

## Prerequisites

Before running, ensure you have:
- `assignment.md` - Your assignment requirements
- `rubric.md` - Your evaluation criteria
- `submissions/` - Folder containing student work

Optional:
- `course_concepts.md` - Domain concepts for assumption validation
- `turnitin/` - Similarity reports

## Workflow

<workflow>
1. **Read the config** from `wmf-config.yaml` to get the framework path

2. **Check dependencies** by running:
   ```bash
   python {framework_path}/skills/grading/scripts/check_dependencies.py
   ```
   If dependencies are missing, prompt the user to install them before continuing.

3. **Verify required files exist**:
   - `assignment.md` (required)
   - `rubric.md` (required)
   - `submissions/` folder with at least one file (required)

   If any are missing, tell the user what's needed and stop.

4. **Extract text from submissions**:
   ```bash
   python {framework_path}/skills/grading/scripts/extract_submission_text.py --input submissions --out grading_extracted
   ```

5. **Render Excel charts** (if any .xlsx files exist):
   ```bash
   python {framework_path}/skills/grading/scripts/render_xlsx_quicklook.py --input submissions --out grading_rendered
   ```

6. **Read the framework instructions** from `{framework_path}/skills/grading/SKILL.md`

7. **Read reference materials**:
   - `assignment.md`
   - `rubric.md`
   - `{framework_path}/skills/grading/references/economical_writing_principles.md`
   - `course_concepts.md` (if present)

8. **Enumerate submissions** by parsing filenames. Group by username.

9. **Read parallelism setting** from `wmf-config.yaml`: `review.max_parallel_agents` (default: 3)

10. **Process submissions in parallel batches**:
    - For each batch of N submissions (where N = max_parallel_agents):
      - Spawn N Task agents **in a single message** with `subagent_type: "general-purpose"`
      - Each agent follows the isolated review workflow from the framework SKILL.md
      - **Wait for all N to complete** before starting the next batch
    - Each agent writes to `grading_feedback/{username}.md`

11. **Report completion** with summary of submissions reviewed.
</workflow>

## Parallelism Settings

Configure `review.max_parallel_agents` in `wmf-config.yaml`:

| Setting | Use Case |
|---------|----------|
| `1` | Sequential mode — use if you experience rate limits or errors |
| `3` | Default — good balance of speed and reliability |
| `5-10` | Large classes with hundreds of students |

## Multi-Round Reviews

If submissions are organized in rounds (`submissions/round1/`, `submissions/round2/`):

1. Check `wmf-config.yaml` for `submissions.rounds.enabled: true`
2. Use round-specific folders: `grading_extracted_round{N}/`, `grading_feedback_round{N}/`
3. For resubmissions, compare to prior round feedback per config setting

## Output

Feedback files are written to `grading_feedback/` (or `grading_feedback_round{N}/` for rounds).

Each file contains:
- **Section A: Reviewer Notes** - Technical audit for instructor only
- **Section B: Writer Feedback** - Teaching-focused guidance to share with student
