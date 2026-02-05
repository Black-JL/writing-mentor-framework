# Grading Template

A reusable template for grading student submissions with Claude Code. Provides substantive feedback that teaches clear thinking and effective writing.

## Attribution

This grading template was created by **Jared Black**.

Portions of the systematic evaluation approach are adapted from **Scott Cunningham's Referee 2 protocol** ([MixtapeTools](https://github.com/scunning1975/MixtapeTools)), specifically:

- **Systematic checklists** for consistent evaluation coverage (Analysis Quality, Evidence Quality, Structure & Logic)
- **Severity tiering** (Major Concerns / Minor Concerns / Suggestions)
- **"Questions for Reflection"** section (adapted from "Questions for Authors")
- **Executive summary** structure
- **Code audit skill** (adapted from the Code Audit and Replication Package Audit)

The pedagogical approach, feedback voice ("demanding but generous mentor"), economical writing principles integration, isolated grading workflow, file extraction pipeline, Turnitin integration, and Canvas compatibility are original to this template.

## FERPA Compliance

Enabling Canvas Anonymous Grading before downloading submissions reduces identifiable information in filenames. However, full FERPA compliance when using AI grading tools depends on your institution's policies, vendor agreements, and whether submissions contain identifying information in their content.

The grading workflow functions correctly with either anonymized or standard Canvas filenames.

## Quick Start

1. **Copy this folder** to your assignment location
3. **Replace `assignment.md`** with the actual assignment instructions
4. **Replace `rubric.md`** with your grading rubric
5. **Place student submissions** in the `submissions/` folder
6. **Ask Claude to grade** the submissions

## Folder Structure

```
Grading-Template/
├── CLAUDE.md              # Instructions for Claude Code (don't modify)
├── assignment.md          # ← REPLACE with your assignment instructions
├── rubric.md              # ← REPLACE with your grading rubric
├── submissions/           # ← PUT student files here
├── turnitin/              # ← OPTIONAL: Turnitin similarity reports
├── skills/
│   └── grading/
│       ├── SKILL.md       # Detailed grading workflow (don't modify)
│       ├── scripts/       # Text extraction utilities
│       │   ├── extract_submission_text.py
│       │   ├── render_xlsx_excel.py
│       │   └── render_xlsx_quicklook.py
│       └── references/
│           ├── economical_writing_principles.md  # Writing evaluation guide
│           └── course_concepts.md                # ← OPTIONAL: course-specific concepts
└── README.md
```

## Setup Details

### Required Files

**`assignment.md`** - The assignment instructions students received
- Include all required sections/components
- Include formatting requirements
- Include any resources provided to students

**`rubric.md`** - Your grading rubric
- Define each criterion with point values
- Describe what excellent, competent, and poor work looks like
- Include total points and grade scale if applicable

### Optional Files

**`turnitin/`** - Turnitin similarity reports
- Place exported Turnitin reports here (or in `submissions/` with "turnitin" in the filename)
- The grading agent checks for reports and incorporates findings into feedback
- Feedback explains what matches mean (benign vs. concerning) and teaches proper citation practices
- If no reports are present, grading proceeds without Turnitin integration

**`skills/grading/references/course_concepts.md`** - Course-specific concepts
- Key terminology and definitions
- Frameworks students should apply
- Common errors to watch for
- Delete this file if not needed

### Submissions Folder

Put all student submission files in `submissions/`. Supported formats:
- PDF documents
- Word documents (.docx, .doc)
- Excel workbooks (.xlsx, .xls)
- Plain text files

## Dependencies

Install these before grading:

```bash
# Python package for old Office formats
pip install olefile

# PDF text extraction and rendering
brew install poppler

# OCR fallback for image-based PDFs
brew install tesseract
```

## Usage

Open Claude Code in the assignment folder and ask:

```
Grade the submissions in the submissions folder
```

Or use the grading agent directly:

```
Use the grading agent to evaluate all student submissions
```

## What the Grading Agent Does

1. **Extracts text** from all submission files (including OCR for scanned PDFs)
2. **Renders Excel charts** as images for visual review
3. **Checks for Turnitin reports** and incorporates similarity findings if present
4. **Evaluates against the rubric** with scores for each criterion
5. **Provides teaching-focused feedback:**
   - What the student did well
   - 2-3 issues with explanations of WHY they matter
   - Writing quality feedback (clarity, active verbs, concreteness)
   - Turnitin review with citation guidance (if reports provided)
   - Required revisions prioritized by impact
   - Optional enhancements for excellent work
6. **Writes a grading report** as a timestamped markdown file

## Feedback Philosophy

The grading agent writes feedback as a demanding but generous mentor would:

- **Explains WHY issues matter**, not just that they exist
- **Connects errors to conceptual gaps** so students understand what they're missing
- **Treats writing quality as a professional skill**, not pedantic grammar policing
- **Prepares students for tough questions** if they'll present their work
- **Prioritizes concrete fixes** so students know exactly what to improve

## Writing Evaluation

All feedback applies the principles from `economical_writing_principles.md`:

- Active verbs over nominalization
- Concrete examples over abstractions
- Plain language over jargon
- Natural voice over bureaucratic prose

Writing feedback focuses on WHY clear writing matters professionally—unclear writing suggests unclear thinking to employers, clients, and colleagues.

## Customization

### Adding Course-Specific Concepts

Edit `skills/grading/references/course_concepts.md` to include:
- Key terminology from your course
- Frameworks students should apply
- Common misconceptions to address

### Modifying the Feedback Format

Edit `skills/grading/SKILL.md` to:
- Change the output format
- Add or remove feedback sections
- Adjust the mentor voice

### Adjusting Writing Standards

Edit `skills/grading/references/economical_writing_principles.md` to:
- Emphasize different writing principles
- Add discipline-specific writing guidance
- Adjust the level of writing feedback
