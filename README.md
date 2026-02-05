# Writing Mentor Framework

A structured framework for providing rigorous feedback on written work. Goes beyond surface-level review to validate data, check internal and external consistency, and deliver two-tier feedback for reviewers and writers.

## What This Framework Does

The Writing Mentor Framework provides **comprehensive validation and teaching-focused feedback** on papers and analytical submissions.

### Data Validation & Consistency Checking

When submissions include multiple components (paper + spreadsheet, raw data + analysis, embedded charts), the framework validates the entire data pipeline:

- **Chart-to-formula matching**: Renders Excel charts and matches them to underlying formulas
- **Cross-file consistency**: Verifies that numbers in the paper match the spreadsheet calculations
- **Assumption auditing**: Checks economic/statistical assumptions against course principles (e.g., flagging nominal GDP when real GDP is needed, or missing PPP adjustment for cross-country comparisons)
- **External source verification**: When data sources are cited, attempts to verify via APIs (FRED, World Bank, BLS) that the data pulled matches what was claimed

### Two-Tier Feedback System

The framework produces **two distinct sections** of feedback:

**Tier 1: Reviewer Notes** (For Instructor)
- Complete technical audit with exact locations of issues
- Data pathway mapping (source → calculation → chart → claim)
- Assumption audit tables (expected vs. found)
- External validation attempts and results
- Evidence trail documenting how issues were identified

**Tier 2: Writer Feedback** (For Student/Author)
- Teaching-focused guidance that shows *evidence* something is wrong without giving the exact fix
- Points to areas of concern without line-by-line correction
- Prompts reflection with questions that guide the writer toward discovering the fix themselves
- Helps writers learn by doing the correction work themselves

**Example of the difference:**

| Reviewer Notes | Writer Feedback |
|----------------|-----------------|
| "Cell D15 uses `=B15/C15` but C15 contains nominal GDP. FRED API confirms series GDP (nominal) was used, not GDPC1 (real)." | "Your GDP comparison shows a pattern, but I found an inconsistency between your data source and your claims. Review whether your GDP figures are nominal or real—this distinction matters. What adjustment would be needed if the data is nominal?" |

## Attribution

This framework was created by **Jared Black**.

Portions of the systematic evaluation approach are adapted from **Scott Cunningham's Referee 2 protocol** ([MixtapeTools](https://github.com/scunning1975/MixtapeTools)), specifically:

- **Systematic checklists** for consistent evaluation coverage
- **Severity tiering** (Major Concerns / Minor Concerns / Suggestions)
- **"Questions for Reflection"** section (adapted from "Questions for Authors")
- **Executive summary** structure
- **Code audit skill** (adapted from the Code Audit and Replication Package Audit)

The two-tier feedback system, data validation pipeline, assumption auditing, external API verification, pedagogical approach, feedback voice ("demanding but generous mentor"), economical writing principles integration, isolated review workflow, and file extraction pipeline are original to this framework.

## Privacy Considerations

When working with student submissions, enabling Canvas Anonymous mode before downloading reduces identifiable information in filenames. Full compliance with institutional policies depends on your specific context and vendor agreements.

The framework functions correctly with either anonymized or standard Canvas filenames.

## Quick Start

1. **Copy this folder** to your project location
2. **Replace `assignment.md`** with the assignment or paper requirements
3. **Replace `rubric.md`** with your evaluation criteria
4. **(Recommended) Add `skills/grading/references/course_concepts.md`** with domain concepts for enhanced assumption validation
5. **Place submissions** in the `submissions/` folder
6. **Ask Claude to review** the submissions

## Folder Structure

```
Writing-Mentor-Framework/
├── CLAUDE.md              # Instructions for Claude Code (don't modify)
├── assignment.md          # ← REPLACE with assignment/paper requirements
├── rubric.md              # ← REPLACE with your evaluation criteria
├── submissions/           # ← PUT papers/spreadsheets/data here
├── turnitin/              # ← OPTIONAL: Similarity reports
├── skills/
│   ├── grading/
│   │   ├── SKILL.md       # Detailed feedback workflow (don't modify)
│   │   ├── scripts/       # Text/formula extraction utilities
│   │   │   ├── extract_submission_text.py
│   │   │   ├── render_xlsx_excel.py
│   │   │   └── render_xlsx_quicklook.py
│   │   └── references/
│   │       ├── economical_writing_principles.md  # Writing evaluation guide
│   │       └── course_concepts.md                # ← RECOMMENDED: domain concepts
│   └── code-audit/
│       └── SKILL.md       # Code review skill (auto-invoked when code detected)
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

### Recommended File

**`skills/grading/references/course_concepts.md`** - Domain-specific concepts for assumption validation

This file **enhances** the assumption auditing capability. Without it, the framework still provides full feedback on writing quality, analysis structure, internal consistency, and data validation—it just won't be able to check assumptions against your specific course principles. Include:
- Key economic/statistical principles that submissions should follow
- Common errors to flag (e.g., "comparing nominal values across countries without PPP adjustment")
- Correct approaches for common analytical tasks
- Terminology and definitions

**Example content:**
```markdown
## GDP Comparisons
- Cross-time comparisons require real (inflation-adjusted) GDP, not nominal
- Cross-country comparisons require PPP adjustment or common currency conversion
- Per-capita normalization needed when comparing countries of different sizes

## Statistical Claims
- Correlation does not imply causation
- Statistical significance requires appropriate tests
- Sample size affects reliability of estimates
```

### Optional Files

**`turnitin/`** - Similarity reports
- Place exported reports here (or in `submissions/` with "turnitin" in the filename)
- The framework incorporates findings into feedback
- Feedback explains what matches mean and teaches proper citation practices

### Submissions Folder

Place all submission files in `submissions/`. The framework handles multi-component submissions:
- PDF documents (with OCR for scanned pages)
- Word documents (.docx, .doc) including embedded Excel objects
- Excel workbooks (.xlsx, .xls) - formulas extracted, charts rendered
- Raw data files
- Plain text files

## Dependencies

The framework will **automatically check** for required dependencies on first run and prompt you to install any that are missing.

**Required:**
- `olefile` — Python package for old Office formats
- `poppler` — PDF text extraction (provides `pdftotext`)
- `tesseract` — OCR for scanned PDFs

**Manual install (if needed):**
```bash
pip install olefile
brew install poppler
brew install tesseract
```

Or let the framework prompt you — it will detect what's missing and offer to install.

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

1. **Extracts text and formulas** from all submission files (including OCR for scanned PDFs, embedded Excel objects)
2. **Renders Excel charts** as images for visual review
3. **Maps data pathways**: Raw data → Calculations → Charts → Claims in paper
4. **Validates internal consistency**: Do formulas match charts? Do paper claims match spreadsheet values?
5. **Audits assumptions**: Checks against course concepts and economic/statistical principles
6. **Attempts external verification**: Uses APIs (FRED, World Bank, etc.) to verify cited data when possible
7. **Evaluates against the rubric** with scores for each criterion
8. **Provides two-tier feedback**:
   - **Reviewer Notes**: Complete technical audit for instructor
   - **Writer Feedback**: Teaching-focused guidance for the author

## Feedback Philosophy

The framework provides feedback as a demanding but generous mentor would:

- **Validates before evaluating**: Checks the underlying data and calculations, not just the prose
- **Explains WHY issues matter**, not just that they exist
- **Shows evidence** of problems without giving exact fixes (in writer feedback)
- **Prompts reflection** with questions that guide writers toward solutions
- **Treats writing quality as a professional skill**, not pedantic grammar policing
- **Prioritizes concrete improvements** so writers know what to focus on

## Writing Evaluation

All feedback applies the principles from `economical_writing_principles.md`:

- Active verbs over nominalization
- Concrete examples over abstractions
- Plain language over jargon
- Natural voice over bureaucratic prose

Writing feedback focuses on WHY clear writing matters professionally—unclear writing suggests unclear thinking to readers.

## Customization

### Adding Domain-Specific Concepts (Critical)

Edit `skills/grading/references/course_concepts.md` to include:
- Key principles from your field (economics, statistics, etc.)
- Common analytical errors to flag
- Correct approaches for typical assignments
- This file drives the assumption auditing capability

### Modifying the Feedback Format

Edit `skills/grading/SKILL.md` to:
- Change the output format
- Add or remove feedback sections
- Adjust the two-tier structure
- Modify the mentor voice

### Adjusting Writing Standards

Edit `skills/grading/references/economical_writing_principles.md` to:
- Emphasize different writing principles
- Add discipline-specific writing guidance
- Adjust the level of writing feedback
