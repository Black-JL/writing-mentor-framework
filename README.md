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

- A Mac, or a PC with Windows 10 or 11
- A Claude Pro or Max plan, used through Claude Code: in Cursor or VS Code (the Claude Code extension), in the Claude desktop app's Code tab, or in a terminal
- Optional: Microsoft Excel or LibreOffice, so the review can see charts as pictures. Without either, it still reads every formula, value and chart data range.

The installer adds everything else.

## Install

### Windows

1. Download **[Install-Writing-Mentor.cmd](https://github.com/Black-JL/writing-mentor-framework/releases/latest/download/Install-Writing-Mentor.cmd)**.
2. Double-click it. Windows will say "Windows protected your PC", because the file comes from the internet and isn't from a known publisher. Click **More info**, then **Run anyway**.
3. Windows may also ask for permission while programs install. Click **Yes**.

It installs what is missing (Git, Python, poppler for PDFs, Tesseract for scanned pages, Claude Code), puts the framework in your user folder under `writing-mentor-framework`, and adds the `/mentor` command to Claude Code. It needs winget, which comes with current Windows; if your computer is managed by your organization and winget is blocked, ask IT to install "App Installer".

### Mac

Open Terminal and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/Black-JL/writing-mentor-framework/main/install/install.sh | bash
```

It needs [Homebrew](https://brew.sh). It installs poppler, Tesseract, Python and Claude Code if missing, puts the framework in `~/writing-mentor-framework`, and adds the `/mentor` command.

### Updating

Run the installer again. It updates the framework and skips programs that are already installed.

## Use it

1. Put the assignment, the rubric, and the writers' files in one folder. Word, PDF, Excel and text files all work. The writers' files can sit in a subfolder.
2. Open that folder in Cursor (File → Open Folder), then open the Claude Code panel. Or open it in the Claude desktop app's Code tab.
3. Type **`/mentor`**.

Claude then asks you, one question at a time:
- which file is the assignment, and which is the rubric (or you can paste them)
- where the writers' files are
- whether there is a file of course principles to check against (optional)
- whether this is a first submission or a revision; for a revision, where the earlier feedback is

It shows you which files it thinks belong to which writer and asks you to confirm or correct the grouping. If a writer handed in the same file twice, it reviews the newest. Before it starts, it reminds you that the files' contents go to Anthropic to be read, and waits for your yes.

When it finishes, the `feedback` folder holds, for each writer:
- `<writer>.md` with both sections: Reviewer Notes (for you) and Writer Feedback
- `<writer> - Writer Feedback.docx` with only the Writer Feedback, ready to send after you read it

plus `FEEDBACK_SUMMARY.md`: all scores, mean, median and range, one paragraph per writer, and the issues several writers share.

### Resubmissions

Run `/mentor` on the revised files and answer "revision". Give it the earlier feedback folder. Each writer's review then checks which earlier points were addressed, reads tracked changes, and gives both a standalone score and the change from last time. The results go to `feedback-round2` (or the round you give).

### Course principles (recommended)

A short file of the principles your field expects makes the assumption checks sharper. Without it, the review still covers writing, structure, internal consistency and data. For example:

```markdown
## GDP comparisons
- Comparisons over time need real (inflation-adjusted) GDP, not nominal
- Comparisons across countries need PPP adjustment or a common currency
- Countries of different sizes need per-capita figures

## Statistical claims
- Correlation does not show causation
- Claims of significance need an appropriate test
```

### What files it reads

- PDFs, including scanned pages (read with OCR)
- Word files (.docx; old .doc with LibreOffice), including spreadsheets pasted into them, tracked changes, comments and footnotes
- Excel workbooks (.xlsx; old .xls with LibreOffice): every sheet, every formula with its cell address, and the cells each chart is drawn from
- Data, code and text files (.csv, .txt, .py, .R, .do, .ipynb, ...)
- Similarity reports (files with "turnitin" or "similarity" in the name)

A file it can't read is reported to you by name, and the review goes ahead without it.

## How a review runs

1. Pulls text and formulas from every file (OCR for scanned PDFs, embedded Excel included)
2. Renders Excel charts as images, using Excel, then LibreOffice, then Quick Look (macOS), whichever is installed
3. Maps each number's path: raw data → calculation → chart → claim
4. Checks that formulas match charts and that the text matches the spreadsheet
5. Checks assumptions against your course principles and general economic and statistical principles
6. Tries to confirm cited public data through its API
7. Scores each rubric criterion
8. Writes the Reviewer Notes and the Writer Feedback

**Each writer is reviewed separately.** A fresh review is started for each writer and given only that writer's files, so one review can't color the next. Three run at once. Expect several minutes per writer. Because each review starts clean, a large batch won't run out of context, and you can leave it running.

## Privacy

Claude Code sends the contents of the files to Anthropic to be read. Before you run a review, confirm that your organization allows this for the work you're reviewing. If names shouldn't be sent, remove them from the files and file names first; the review works the same either way.

Each writer's work is reviewed separately, and each review is given only that writer's files. `/mentor` adds a `.gitignore` to the folder so that, if the folder is ever put in Git, the writers' files and the feedback stay out of it.

## Changing how it works

- **What each review checks, and the feedback format:** `skills/feedback/review-one-writer.md`
- **How a batch runs** (how many at once, the summary): `skills/feedback/SKILL.md`
- **The questions `/mentor` asks:** `skills/mentor/SKILL.md` (run the installer again after changing it)
- **Writing standards:** `skills/feedback/references/economical_writing_principles.md`, `peer.md`, `orwell.md`

## Framework files

```
writing-mentor-framework/
├── install/
│   ├── Install-Writing-Mentor.cmd   # Windows setup (double-click)
│   ├── install.ps1                  # what the Windows setup runs
│   └── install.sh                   # Mac setup
├── skills/
│   ├── mentor/SKILL.md              # the /mentor command
│   ├── feedback/
│   │   ├── SKILL.md                 # runs a batch of reviews
│   │   ├── review-one-writer.md     # what each review does, and its format
│   │   ├── references/              # writing principles, example course principles
│   │   └── scripts/                 # reading files, charts, grouping, Word copies
│   └── code-audit/SKILL.md          # review of code handed in with the writing
├── tests/                           # checks on made-up sample files
└── specs/                           # how changes are planned
```

For developers: `python tests/run_tests.py` checks the scripts on made-up files. GitHub runs the same checks on Windows and Mac, including both installers, on every push.

## Attribution

Created by **Jared Black**.

Parts of the systematic review approach are adapted from **Scott Cunningham's Referee 2 protocol** ([MixtapeTools](https://github.com/scunning1975/MixtapeTools)):

- Systematic checklists for consistent coverage
- Severity tiers (Major Concerns / Minor Concerns / Suggestions)
- The "Questions for Reflection" section (adapted from "Questions for Authors")
- The executive summary structure
- The code audit skill (adapted from the Code Audit and Replication Package Audit)

The two-part feedback, the data checks, the assumption audit, external API checks, the teaching approach, the demanding-but-generous mentor voice, the economical writing principles, the one-agent-per-writer review, and the file extraction scripts are original to this framework.
