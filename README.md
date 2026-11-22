# Writing Mentor Framework

A set of instructions and scripts that lets Claude Code review written work the way a demanding but generous mentor would. It reads the documents, spreadsheets and charts a writer hands in, checks that the numbers and claims agree with each other, scores the work against your rubric, and writes feedback in two parts: technical notes for you, the mentor, and teaching-focused feedback for the writer.

## What it does

### Checks the work, not only the prose

When a submission has several parts (a report plus a spreadsheet, raw data plus analysis, charts pasted into a document), the framework traces each number from its source to the claim it supports:

- **Charts against formulas:** turns Excel charts into images and compares them with the formulas behind them.
- **Document against spreadsheet:** checks that numbers in the text match the spreadsheet's calculations.
- **Assumptions:** checks the analysis against the principles of your field. For example, it flags nominal GDP used where real GDP is needed, or a cross-country comparison with no PPP adjustment.
- **Cited data:** when a writer cites a public source, it tries to confirm the figures through that source's API (FRED, World Bank, BLS).

### Feedback in two parts

Each review produces one file with two sections.

**Section A: Reviewer Notes (for the mentor only)**
- Every issue, with its exact location
- The path each number takes: source → calculation → chart → claim
- An assumption table (expected vs. found)
- What external checks were tried and what they found
- How each issue was found

**Section B: Writer Feedback (to share with the writer)**
- Shows the evidence that something is wrong, without handing over the fix
- Points to the area of concern instead of correcting line by line
- Asks questions that lead the writer to find the fix
- The writer learns by doing the correction

**The same issue, written for each reader:**

| Reviewer Notes | Writer Feedback |
|----------------|-----------------|
| "Cell D15 uses `=B15/C15` but C15 contains nominal GDP. FRED confirms series GDP (nominal) was used, not GDPC1 (real)." | "Your GDP comparison shows a pattern, but your data source and your claims don't agree. Check whether your GDP figures are nominal or real; the difference matters here. What adjustment would you need if the data is nominal?" |

### The mentor's stance

- Checks the data and calculations before judging the writing
- Explains why an issue matters, not only that it exists
- Treats clear writing as a professional skill, not grammar policing
- Puts the most important improvements first, sorted as Major Concerns, Minor Concerns and Suggestions
- Ends with questions for the writer to reflect on

Writing feedback follows `economical_writing_principles.md`: active verbs, concrete examples, plain language, a natural voice.

## What you need

- **Claude Code**, signed in with a Claude Pro or Max plan (or an API key). It runs in a terminal, or in Cursor and VS Code through the Claude Code extension.
- **Python 3**
- **poppler** (reads PDFs), **tesseract** (reads scanned PDFs), and the `olefile` Python package (reads old .doc and .xls files)
- **Optional:** Microsoft Excel or LibreOffice, so the review can see charts as pictures. Without either, it still reads every formula and value.

## Install

### macOS

```bash
brew install poppler tesseract
python3 -m pip install olefile
git clone https://github.com/Black-JL/writing-mentor-framework.git ~/writing-mentor-framework
echo 'export PATH="$HOME/writing-mentor-framework/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Install Claude Code from [claude.com/claude-code](https://claude.com/claude-code) if you don't have it.

### Windows 10 or 11

Type these into PowerShell.

1. Install the tools:
   ```powershell
   winget install -e --id Git.Git
   winget install -e --id Python.Python.3.12
   winget install -e --id oschwartz10612.Poppler
   winget install -e --id UB-Mannheim.TesseractOCR
   irm https://claude.ai/install.ps1 | iex
   ```
   Close PowerShell and open it again so it finds the new programs.
2. Download the framework and the Python package it needs:
   ```powershell
   git clone https://github.com/Black-JL/writing-mentor-framework.git "$HOME\writing-mentor-framework"
   python -m pip install olefile
   ```
3. Add the `wmf` command:
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$HOME\writing-mentor-framework\bin", "User")
   ```
   Close PowerShell and open it again.

On Windows the Python command is `python`; on macOS it is `python3`.

### Check the install

```bash
python3 ~/writing-mentor-framework/skills/feedback/scripts/check_dependencies.py
```

On Windows: `python "$HOME\writing-mentor-framework\skills\feedback\scripts\check_dependencies.py"`

It lists anything missing with the install command for your system, and says which tool it will use for chart images.

## Use it

Do this once for each assignment you review.

1. **Set up a folder.** In a terminal, go to the folder (or a new one) and run:
   ```bash
   wmf init
   ```
2. **Add your files:**
   - `assignment.md`: what the assignment asked for
   - `rubric.md`: how you score it
   - `course_concepts.md` (optional but recommended): the principles of your field the analysis should follow
   - `submissions/`: the writers' files (Word, PDF, Excel)
3. **Open Claude Code in that folder.** Either type `claude` in the terminal, or open the folder in Cursor and open the Claude Code panel.
4. **Type `/feedback`.**

Claude checks the tools, pulls the text and formulas out of every file, renders the charts, and then reviews each writer's work. The feedback lands in `feedback/`, one file per writer, plus `feedback/FEEDBACK_SUMMARY.md`.

If you'd rather not install `wmf`, run the setup script directly:

```bash
python3 ~/writing-mentor-framework/scripts/init_project.py --target /path/to/folder
```

### What `wmf init` creates

```
My-Assignment/
├── wmf-config.yaml        # settings, and where the framework is installed
├── CLAUDE.md              # instructions Claude Code reads in this folder
├── assignment.md          # ← replace with your assignment
├── rubric.md              # ← replace with your rubric
├── course_concepts.md     # ← your field's principles (optional)
├── submissions/           # ← put the writers' files here
├── turnitin/              # similarity reports (optional)
└── .claude/skills/feedback/SKILL.md   # the /feedback command
```

The framework itself stays in one place, so an update to it applies to every assignment folder.

## Your input files

**`assignment.md`:** the required sections and components, formatting rules, and any data or readings provided.

**`rubric.md`:** each criterion with its points, and what excellent, competent and developing work looks like.

**`course_concepts.md`:** without it, the review still covers writing, structure, internal consistency and data checks. With it, the review can also catch errors specific to your field. Include key principles, common errors to flag, correct approaches, and terms. For example:

```markdown
## GDP Comparisons
- Comparisons over time need real (inflation-adjusted) GDP, not nominal
- Comparisons across countries need PPP adjustment or a common currency
- Countries of different sizes need per-capita figures

## Statistical Claims
- Correlation does not show causation
- Claims of significance need an appropriate test
```

**`turnitin/` (optional):** put exported similarity reports here. The feedback explains what the matches mean and how to cite properly.

**`submissions/`:** handles
- PDFs, including scanned pages (read with OCR)
- Word documents (.docx, .doc), including Excel objects pasted into them
- Excel workbooks (.xlsx, .xls): formulas read, charts rendered
- Raw data and plain text files

When a writer hands in more than one version, the review uses the latest.

## How a review runs

1. Pulls text and formulas from every file (OCR for scanned PDFs, embedded Excel included)
2. Renders Excel charts as images, using Excel, then LibreOffice, then Quick Look (macOS), whichever is installed
3. Maps each number's path: raw data → calculation → chart → claim
4. Checks that formulas match charts and that the text matches the spreadsheet
5. Checks assumptions against `course_concepts.md` and general economic and statistical principles
6. Tries to confirm cited public data through its API
7. Scores each rubric criterion
8. Writes the Reviewer Notes and the Writer Feedback

**Each writer is reviewed separately.** A fresh Claude agent reviews each writer's work, so one review can't color the next. By default three run at once. Expect several minutes per writer. Because each agent starts clean, a large batch won't run out of context, and you can leave it running.

**The summary.** When every review is done, `feedback/FEEDBACK_SUMMARY.md` lists all scores from highest to lowest, the mean, median and range, one paragraph per writer (main strength, biggest concern, score), and the issues that came up across many submissions.

## Settings

`wmf-config.yaml` in each assignment folder. See `wmf-config.yaml.example` for every option.

```yaml
framework_path: ~/writing-mentor-framework

assignment: assignment.md
rubric: rubric.md
course_concepts: course_concepts.md  # or null

submissions:
  folder: submissions
  rounds:
    enabled: false        # true for assignments with resubmissions

output:
  extracted: feedback_extracted
  rendered: feedback_rendered
  feedback: feedback

review:
  max_parallel_agents: 3  # 1 if you hit rate limits; 5-10 for large batches
  compare_to_round: null  # e.g. 1 when reviewing round 2
```

### Resubmissions

1. Set `submissions.rounds.enabled: true`
2. Put each round in its own folder: `submissions/round1/`, `submissions/round2/`
3. Set `review.compare_to_round: 1` when reviewing round 2

The review then reads the writer's tracked changes, compares the new version with the earlier feedback, and gives both a standalone score and an assessment of how much improved.

## Privacy

Claude Code sends the text of each file to Anthropic for review. Before you run it, confirm that your organization allows this for the work you're reviewing. If names shouldn't be sent, remove them from the files and filenames first; the review works the same either way. The `.gitignore` keeps `submissions/` and all feedback out of git.

## Changing how it works

- **Field-specific checks:** edit `course_concepts.md` in the assignment folder.
- **Feedback format, sections or voice:** edit `skills/feedback/SKILL.md` in the framework.
- **Writing standards:** edit `skills/feedback/references/economical_writing_principles.md`.

## Framework files

```
writing-mentor-framework/
├── bin/
│   ├── wmf                         # wmf command, macOS/Linux
│   └── wmf.cmd                     # wmf command, Windows
├── scripts/init_project.py         # sets up an assignment folder
├── skills/
│   ├── feedback/
│   │   ├── SKILL.md                # the full review instructions
│   │   ├── scripts/
│   │   │   ├── check_dependencies.py
│   │   │   ├── extract_submission_text.py
│   │   │   ├── render_charts.py           # picks Excel / LibreOffice / Quick Look
│   │   │   ├── render_xlsx_excel.py       # Excel (macOS or Windows)
│   │   │   ├── render_xlsx.py             # LibreOffice (any system)
│   │   │   ├── render_xlsx_quicklook.py   # Quick Look (macOS only)
│   │   │   └── _tools.py                  # finds poppler, tesseract, LibreOffice
│   │   └── references/             # writing principles, example course concepts
│   └── code-audit/SKILL.md         # review of code files handed in with the writing
├── templates/                      # templates used by wmf init
├── wmf-config.yaml.example
└── CLAUDE.md                       # instructions for using this folder directly
```

## Attribution

Created by **Jared Black**.

Parts of the systematic review approach are adapted from **Scott Cunningham's Referee 2 protocol** ([MixtapeTools](https://github.com/scunning1975/MixtapeTools)):

- Systematic checklists for consistent coverage
- Severity tiers (Major Concerns / Minor Concerns / Suggestions)
- The "Questions for Reflection" section (adapted from "Questions for Authors")
- The executive summary structure
- The code audit skill (adapted from the Code Audit and Replication Package Audit)

The two-part feedback, the data checks, the assumption audit, external API checks, the teaching approach, the demanding-but-generous mentor voice, the economical writing principles, the one-agent-per-writer review, and the file extraction scripts are original to this framework.
