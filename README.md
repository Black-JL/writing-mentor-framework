# Writing Mentor Framework

A structured framework for providing substantive feedback on written work. Teaches clear thinking and effective writing through systematic evaluation and mentor-style guidance.

## Attribution

This framework was created by **Jared Black**.

Portions of the systematic evaluation approach are adapted from **Scott Cunningham's Referee 2 protocol** ([MixtapeTools](https://github.com/scunning1975/MixtapeTools)), specifically:

- **Systematic checklists** for consistent evaluation coverage (Analysis Quality, Evidence Quality, Structure & Logic)
- **Severity tiering** (Major Concerns / Minor Concerns / Suggestions)
- **"Questions for Reflection"** section (adapted from "Questions for Authors")
- **Executive summary** structure
- **Code audit skill** (adapted from the Code Audit and Replication Package Audit)

The pedagogical approach, feedback voice ("demanding but generous mentor"), economical writing principles integration, isolated review workflow, file extraction pipeline, Turnitin integration, and Canvas compatibility are original to this framework.

## What This Framework Does

The Writing Mentor Framework provides structured, teaching-focused feedback on papers and written submissions. It acts as a demanding but generous mentor—the kind who pushes you to think more clearly and write more effectively, while explaining *why* improvements matter.

**Core capabilities:**
- Systematic evaluation using checklists for consistent coverage
- Feedback organized by severity (Major Concerns → Minor Concerns → Suggestions)
- Location-specific comments pointing to exact passages
- Questions for reflection that prompt deeper thinking
- Writing quality assessment based on principles of economical writing
- Support for processing multiple papers with isolated context per submission

## Privacy Considerations

When working with student submissions, enabling Canvas Anonymous mode before downloading reduces identifiable information in filenames. Full compliance with institutional policies depends on your specific context and vendor agreements.

The framework functions correctly with either anonymized or standard Canvas filenames.

## Quick Start

1. **Copy this folder** to your project location
2. **Replace `assignment.md`** with the assignment or paper requirements
3. **Replace `rubric.md`** with your evaluation criteria
4. **Place submissions** in the `submissions/` folder
5. **Ask Claude to review** the submissions

## Folder Structure

```
Writing-Mentor-Framework/
├── CLAUDE.md              # Instructions for Claude Code (don't modify)
├── assignment.md          # ← REPLACE with assignment/paper requirements
├── rubric.md              # ← REPLACE with your evaluation criteria
├── submissions/           # ← PUT papers here
├── turnitin/              # ← OPTIONAL: Similarity reports
├── skills/
│   └── grading/
│       ├── SKILL.md       # Detailed feedback workflow (don't modify)
│       ├── scripts/       # Text extraction utilities
│       │   ├── extract_submission_text.py
│       │   ├── render_xlsx_excel.py
│       │   └── render_xlsx_quicklook.py
│       └── references/
│           ├── economical_writing_principles.md  # Writing evaluation guide
│           └── course_concepts.md                # ← OPTIONAL: domain-specific concepts
└── README.md
```

## Setup Details

### Required Files

**`assignment.md`** - The requirements for the paper or assignment
- Include all required sections/components
- Include formatting requirements
- Include any resources provided

**`rubric.md`** - Your evaluation criteria
- Define each criterion with point values
- Describe what excellent, competent, and developing work looks like
- Include total points if applicable

### Optional Files

**`turnitin/`** - Similarity reports
- Place exported reports here (or in `submissions/` with "turnitin" in the filename)
- The framework incorporates findings into feedback
- Feedback explains what matches mean (benign vs. concerning) and teaches proper citation practices
- If no reports are present, review proceeds without similarity integration

**`skills/grading/references/course_concepts.md`** - Domain-specific concepts
- Key terminology and definitions
- Frameworks that should be applied
- Common errors to watch for
- Delete this file if not needed

### Submissions Folder

Place all papers in `submissions/`. Supported formats:
- PDF documents
- Word documents (.docx, .doc)
- Excel workbooks (.xlsx, .xls)
- Plain text files

## Dependencies

Install these before use:

```bash
# Python package for old Office formats
pip install olefile

# PDF text extraction and rendering
brew install poppler

# OCR fallback for image-based PDFs
brew install tesseract
```

## Usage

Open Claude Code in the project folder and ask:

```
Review the submissions in the submissions folder
```

Or:

```
Provide feedback on all papers in submissions
```

## How the Framework Works

1. **Extracts text** from all submission files (including OCR for scanned PDFs)
2. **Renders Excel charts** as images for visual review
3. **Checks for similarity reports** and incorporates findings if present
4. **Evaluates against the rubric** with scores for each criterion
5. **Provides structured, teaching-focused feedback:**
   - Executive summary (overall assessment)
   - What the writer did well
   - 2-3 development areas with explanations of WHY they matter
   - Writing quality feedback (clarity, active verbs, concreteness)
   - Questions for reflection
   - Major concerns, minor concerns, and suggestions (severity-tiered)
   - Similarity review with citation guidance (if reports provided)
6. **Writes feedback** as a markdown file for each submission

## Feedback Philosophy

The framework provides feedback as a demanding but generous mentor would:

- **Explains WHY issues matter**, not just that they exist
- **Connects errors to conceptual gaps** so writers understand what they're missing
- **Treats writing quality as a professional skill**, not pedantic grammar policing
- **Prepares writers for tough questions** they might face presenting their work
- **Prioritizes concrete improvements** so writers know exactly what to do next

## Writing Evaluation

All feedback applies the principles from `economical_writing_principles.md`:

- Active verbs over nominalization
- Concrete examples over abstractions
- Plain language over jargon
- Natural voice over bureaucratic prose

Writing feedback focuses on WHY clear writing matters professionally—unclear writing suggests unclear thinking to readers, whether they're employers, clients, colleagues, or reviewers.

## Customization

### Adding Domain-Specific Concepts

Edit `skills/grading/references/course_concepts.md` to include:
- Key terminology from your field
- Frameworks that should be applied
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
