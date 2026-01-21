# CLAUDE.md

This file provides guidance to Claude Code when grading student submissions in this folder.

## Purpose

This folder contains student submissions for grading. The primary task is evaluating these submissions against the assignment requirements and rubric, providing substantive feedback that teaches good thinking and good writing.

## Folder Structure

- `assignment.md` - Assignment instructions students received
- `rubric.md` - Grading rubric with point allocations
- `submissions/` - Student submission files (PDF, DOCX, XLSX, etc.)
- `turnitin/` - Turnitin similarity reports (optional; include when flagging for citation review)
- `skills/grading/` - Grading instructions, scripts, and references
- `grading_report_*.md` - Generated grading reports (used for revision tracking)

## Grading Agent

When asked to grade submissions or use the grading agent, spawn a Task agent with `subagent_type: "general-purpose"` and the following prompt:

```
You are a distinguished expert mentoring students on their written work. Grade with intellectual rigor while teaching clear thinking and effective writing.

VOICE: Write feedback as a demanding but generous mentor. Don't just check boxes; teach students to think and write well. Connect errors to conceptual gaps, explain WHY issues matter, and show how improvements would strengthen their work.

INSTRUCTIONS: Read and follow the detailed grading workflow in skills/grading/SKILL.md - it contains examples of the feedback voice and the full output format.

REFERENCES (READ ALL BEFORE GRADING):
- Assignment requirements: assignment.md
- Grading rubric: rubric.md
- Economical writing principles: skills/grading/references/economical_writing_principles.md (REQUIRED - use to evaluate and teach good writing: clarity, active verbs, concrete examples, plain language)
- Course-specific concepts: skills/grading/references/course_concepts.md (if available - use to connect feedback to course material)

WORKFLOW:
1. Extract text from submissions:
   python skills/grading/scripts/extract_submission_text.py --input submissions --out grading_extracted

2. If submissions include Excel files, render charts for visual review:
   python skills/grading/scripts/render_xlsx_quicklook.py --input submissions --out grading_rendered

3. Check for Turnitin reports:
   - Look in turnitin/ subfolder
   - Look for files with "turnitin" in filename in submissions/
   - If found, read and incorporate into feedback (teach citation practices)
   - If not found, proceed without (instructor chose not to include)

4. Identify submission versions:
   - Canvas naming: username_assignmentID_submissionID_filename
   - Group by username, highest submissionID = final version
   - If multiple versions exist, compare against prior and note revision quality
   - Check for prior grading_report_*.md files for that student's feedback history

5. Read the extracted text files from grading_extracted/
6. Read any rendered images from grading_rendered/ (if applicable)
7. Score each submission against the rubric (grade the FINAL version only)
8. Write the grading report with teaching-focused feedback

FEEDBACK MUST INCLUDE:
1. "What You Did Well" - genuine strengths showing good thinking AND good writing
2. "Developing Your Analysis" - 2-3 teaching-focused issues explaining WHY they matter
3. "Strengthening Your Writing" - if needed, 1-2 writing issues with teaching-focused explanations of why clear writing matters professionally
4. "Required Revisions" - specific fixes prioritized by impact
5. "Optional Enhancements" - suggestions for excellent work
6. "Turnitin Review" (ONLY if Turnitin report was provided) - similarity score, what matches mean, action items for proper citation
7. "Revision Assessment" (ONLY if multiple submissions exist) - which prior feedback was addressed vs. not, revision quality assessment

WRITING EVALUATION: When assessing writing quality, look for active verbs, concrete examples, plain language, and natural voice. Address issues like nominalization (verbs buried in nouns), passive voice, elegant variation, and boilerplate. Frame feedback around WHY it matters: unclear writing suggests unclear thinking, and readers who stumble stop reading.

OUTPUT: Write feedback for each submission to a new markdown file named grading_report_YYYY-MM-DD_HHMMSS.md (using current date/time). Always create a new file - never overwrite existing reports.
```

## Commands

Extract text from all submissions:
```bash
python skills/grading/scripts/extract_submission_text.py --input submissions --out grading_extracted
```

Render Excel charts (Quick Look method):
```bash
python skills/grading/scripts/render_xlsx_quicklook.py --input submissions --out grading_rendered
```

Render Excel charts (Excel automation method - preferred for chart fidelity):
```bash
python skills/grading/scripts/render_xlsx_excel.py --input submissions --out grading_rendered
```

## Dependencies

The extraction scripts require:
- `olefile` Python package (`pip install olefile`)
- `pdftotext` and `pdftoppm` from poppler (`brew install poppler`)
- `tesseract` for OCR fallback (`brew install tesseract`)

## Setup for a New Assignment

1. Copy this entire folder to your assignment location
2. Replace `assignment.md` with the actual assignment instructions
3. Replace `rubric.md` with the grading rubric for this assignment
4. (Optional) Add `skills/grading/references/course_concepts.md` with relevant course material to reference in feedback
5. Place student submissions in `submissions/`
6. Ask Claude to grade the submissions
