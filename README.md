# Writing Mentor Framework

A structured framework for providing rigorous feedback on written work. Goes beyond surface-level review to validate data, check internal and external consistency, and deliver two-tier feedback for reviewers and writers.

## What This Framework Does

The Writing Mentor Framework provides **comprehensive validation and teaching-focused feedback** on written work and analytical submissions.

### Data Validation & Consistency Checking

When submissions include multiple components (document + spreadsheet, raw data + analysis, embedded charts), the framework validates the entire data pipeline:

- **Chart-to-formula matching**: Renders Excel charts and matches them to underlying formulas
- **Cross-file consistency**: Verifies that numbers in the document match the spreadsheet calculations
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

**Tier 2: Writer Feedback** (For Writer/Author)
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

When working with writer submissions, enabling Canvas Anonymous mode before downloading reduces identifiable information in filenames. Full compliance with institutional policies depends on your specific context and vendor agreements.

The framework functions correctly with either anonymized or standard Canvas filenames.

## Installation

**One-time setup** — Add the `wmf` command to your PATH:

```bash
# Clone or download the framework to a permanent location
git clone https://github.com/Black-JL/writing-mentor-framework.git ~/writing-mentor-framework

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export PATH="$HOME/writing-mentor-framework/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Now you can use `wmf init` from any folder.

## Quick Start

**For each new class:**

```bash
# 1. Go to your class folder (or create a new one)
cd /path/to/my-class
# or: mkdir my-economics-class && cd my-economics-class

# 2. Initialize the framework
wmf init

# 3. Drop in your files:
#    - assignment.md (your assignment requirements)
#    - rubric.md (your evaluation criteria)
#    - submissions/ (writer work: DOCX, PDF, XLSX)

# 4. Open Claude Code
claude

# 5. Type: /feedback
```

That's it. Claude will check dependencies, extract submissions, and generate two-tier feedback.

---

**Alternative: Manual Setup**

If you prefer not to install the `wmf` command:

```bash
python ~/writing-mentor-framework/scripts/init_project.py --target /path/to/class
```

**Alternative: Full Copy (for single use or offline)**

1. **Copy this folder** to your project location
2. **Replace `assignment.md`** with the assignment or assignment requirements
3. **Replace `rubric.md`** with your evaluation criteria
4. **(Recommended) Edit `skills/feedback/references/course_concepts.md`** with domain concepts
5. **Place submissions** in the `submissions/` folder
6. **Ask Claude to review** the submissions

## Folder Structure

### Framework Installation

```
writing-mentor-framework/
├── README.md                      # This file
├── CLAUDE.md                      # Instructions for Claude Code
├── bin/
│   └── wmf                        # CLI tool (add to PATH)
├── scripts/
│   └── init_project.py            # Initialize new class folders
├── templates/
│   ├── CLAUDE.md.minimal          # Minimal CLAUDE.md template
│   └── skills/feedback/SKILL.md    # /feedback skill template
├── skills/
│   ├── feedback/
│   │   ├── SKILL.md               # Detailed feedback workflow
│   │   ├── scripts/               # Extraction utilities
│   │   │   ├── check_dependencies.py
│   │   │   ├── extract_submission_text.py
│   │   │   ├── render_xlsx_excel.py
│   │   │   ├── render_xlsx_quicklook.py
│   │   │   └── render_xlsx.py
│   │   └── references/
│   │       ├── economical_writing_principles.md
│   │       └── course_concepts.md
│   └── code-audit/
│       └── SKILL.md               # Code review skill
├── wmf-config.yaml.example        # Config file template
├── assignment.md                  # Template assignment
├── rubric.md                      # Template rubric
├── submissions/                   # Template folder
├── turnitin/                      # Template folder
└── .gitignore
```

### Class Folder (After `wmf init`)

When you run `wmf init`, it creates:

```
My-Class/
├── wmf-config.yaml        # Points to central framework
├── CLAUDE.md              # Instructions for Claude Code
├── assignment.md          # ← DROP IN your requirements
├── rubric.md              # ← DROP IN your criteria
├── course_concepts.md     # Your domain concepts (optional)
├── submissions/           # ← DROP IN writer work
├── turnitin/              # Similarity reports (optional)
└── skills/
    └── feedback/
        └── SKILL.md       # /feedback command (auto-installed)
```

The `/feedback` skill is automatically installed, so you can just type `/feedback` in Claude Code.

## Setup Details

### Required Files

**`assignment.md`** - The requirements for the assignment
- Include all required sections/components
- Include formatting requirements
- Include any resources provided

**`rubric.md`** - Your evaluation criteria
- Define each criterion with point values
- Describe what excellent, competent, and developing work looks like
- Include total points if applicable

### Recommended File

**`skills/feedback/references/course_concepts.md`** - Domain-specific concepts for assumption validation

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

The framework will **automatically check** for required dependencies on first run and provide platform-specific install guidance. It detects your operating system and available package managers.

**Required:**
- `olefile` — Python package for old Office formats
- `poppler` — PDF text extraction (provides `pdftotext`)
- `tesseract` — OCR for scanned PDFs

**What happens without these?**
- Without olefile: Cannot read older .doc/.xls formats (pre-2007)
- Without poppler: Cannot extract text from PDF files
- Without tesseract: Cannot OCR scanned/image-based PDFs

The framework still works for supported file types even with missing dependencies.

**Manual install by platform:**

| Platform | Package Manager | Commands |
|----------|-----------------|----------|
| macOS | Homebrew | `brew install poppler tesseract` |
| Ubuntu/Debian | apt | `sudo apt-get install poppler-utils tesseract-ocr` |
| Fedora | dnf | `sudo dnf install poppler-utils tesseract` |
| Windows | Chocolatey | `choco install poppler tesseract` |
| Windows | Scoop | `scoop install poppler tesseract` |
| All | pip | `pip install olefile` |

Or let the framework prompt you — it will detect what's missing, explain what each dependency does, and show the exact commands for your system.

## Usage

Open Claude Code in the project folder and ask:

```
Review the submissions in the submissions folder
```

Or:

```
Provide feedback on all submissions
```

## How the Framework Works

1. **Extracts text and formulas** from all submission files (including OCR for scanned PDFs, embedded Excel objects)
2. **Renders Excel charts** as images for visual review
3. **Maps data pathways**: Raw data → Calculations → Charts → Claims in document
4. **Validates internal consistency**: Do formulas match charts? Do written claims match spreadsheet values?
5. **Audits assumptions**: Checks against course concepts and economic/statistical principles
6. **Attempts external verification**: Uses APIs (FRED, World Bank, etc.) to verify cited data when possible
7. **Evaluates against the rubric** with scores for each criterion
8. **Provides two-tier feedback**:
   - **Reviewer Notes**: Complete technical audit for instructor
   - **Writer Feedback**: Teaching-focused guidance for the author

### Performance Note

**The framework takes time to run** — expect several minutes per submission for thorough review. However, it's designed to be reliable:

- **One agent per submission**: Each writer's work is reviewed by a separate agent with fresh context
- **No context accumulation**: Because each agent starts clean, the conversation history doesn't grow unbounded
- **Parallel batching**: Submissions are reviewed in parallel batches (default: 3 at a time) for speed

This architecture means the framework **won't time out or hit context window limits**, even with large classes. You can start it and walk away — it will work through all submissions reliably.

### Class Summary Report

After all individual reviews complete, the framework automatically generates `feedback/CLASS_SUMMARY.md` — a single file containing:

- **Score table** (all students, sorted highest to lowest)
- **Class statistics** (mean, median, range)
- **One-paragraph summaries** per student (key strength, biggest concern, score)
- **Common issues** across the class

This gives the instructor an at-a-glance view without opening 20+ individual files.

**Parallelism settings** (in `wmf-config.yaml`):

| Setting | Use Case |
|---------|----------|
| `max_parallel_agents: 1` | Sequential mode — use if you experience rate limits or errors |
| `max_parallel_agents: 3` | Default — good balance of speed and reliability |
| `max_parallel_agents: 5-10` | Large classes with hundreds of submissions |

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

## Centralized Setup Details

The centralized setup (Option A in Quick Start) keeps framework code separate from class data.

### Benefits

- **Single source of truth**: Updates to the framework apply to all classes
- **Smaller class folders**: Each class only contains assignment-specific files
- **Cleaner separation**: Framework code lives separately from class data

### Config File Reference

The `wmf-config.yaml` file controls how the framework operates. See `wmf-config.yaml.example` for all options:

```yaml
# Path to the framework installation
framework_path: ~/writing-mentor-framework

# Assignment files (in this folder)
assignment: assignment.md
rubric: rubric.md
course_concepts: course_concepts.md  # or null

# Submission handling
submissions:
  folder: submissions
  rounds:
    enabled: false  # Set true for multi-round reviews

# Output folders
output:
  extracted: feedback_extracted
  rendered: feedback_rendered
  feedback: feedback

# Review settings
review:
  max_parallel_agents: 3  # 1=sequential, 3=default, 5-10=large classes
  compare_to_round: null  # For resubmission comparisons
```

### Multi-Round Reviews

For assignments with resubmissions:

1. Enable rounds in config: `submissions.rounds.enabled: true`
2. Organize submissions: `submissions/round1/`, `submissions/round2/`, etc.
3. Set comparison: `review.compare_to_round: 1` (for round 2 reviews)

The framework automatically:
- Extracts track changes from DOCX files to show what writers modified
- Compares current work to prior feedback
- Provides both standalone scores and improvement assessments

---

## Customization

### Adding Domain-Specific Concepts (Recommended)

Edit `course_concepts.md` (in your class folder, or `skills/feedback/references/course_concepts.md` if using the full copy approach) to include:
- Key principles from your field (economics, statistics, etc.)
- Common analytical errors to flag
- Correct approaches for typical assignments
- This file enhances the assumption auditing capability

### Modifying the Feedback Format

Edit `skills/feedback/SKILL.md` to:
- Change the output format
- Add or remove feedback sections
- Adjust the two-tier structure
- Modify the mentor voice

### Adjusting Writing Standards

Edit `skills/feedback/references/economical_writing_principles.md` to:
- Emphasize different writing principles
- Add discipline-specific writing guidance
- Adjust the level of writing feedback
