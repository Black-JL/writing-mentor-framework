# Setup wizard, one set of instructions, and the data-loss fixes

- **ID:** 2026-11-22-setup-wizard  ·  **Tier:** 2
- **Status:** Approved (Jared, "do it", 2026-11-22) — Building
- **Branch / worktree:** spec/2026-11-22-setup-wizard at ~/GitHub/writing-mentor-framework-wizard

## Goal
A mentor who does not use GitHub or the command line (first user: Jared's colleague on
Windows, who works in Cursor and has Claude) installs the framework once by
double-clicking one file, then runs a review by typing `/mentor` and answering a few
questions about where his files are. At the same time, fix the bugs that lose or
overwrite data, merge the four disagreeing copies of the instructions into one, and
tighten privacy.

## Who uses it and how
1. Jared sends him a link to the GitHub release page. He downloads
   `Install-Writing-Mentor.cmd` (Mac: `Install-Writing-Mentor.command`), double-clicks
   it, and on Windows clicks "More info → Run anyway".
2. The installer says what it will install, installs what is missing (Python, Git,
   poppler, Tesseract, Claude Code, Python packages), downloads the framework as a zip,
   adds the `/mentor` command, runs the dependency check, and says what to do next.
   Running it again updates the framework.
3. He opens the folder that holds the writers' files in Cursor, opens the Claude Code
   panel (or the Claude desktop app's Code tab), and types `/mentor`.
4. Claude asks, one step at a time: where the assignment instructions are, where the
   rubric is (Word, PDF or text), which files are the writers' submissions (it shows
   how it grouped the files by writer and asks him to confirm), whether there are
   course principles, and whether this is a resubmission round. It says that file
   contents go to Anthropic, shows a short plan, and waits for "go".
5. A `feedback` folder appears next to his files: per writer, one .md file with both
   sections and one Word file with only the Writer Feedback, ready to send; plus a
   summary across all writers.

## In scope / Out of scope
- In:
  - Installers for Windows (`.cmd`) and Mac (`.command`), published as GitHub Release assets
  - Global `/mentor` skill in `~/.claude/skills/mentor/`
  - Instructions merged into two files: one that runs the batch, one that reviews one writer
  - Extraction fixes: no crash on one bad file; every sheet kept under its own name;
    formulas with cell addresses; copied-down formulas; say when output is cut;
    .doc/.xls handled or reported; a printed result per file; olefile optional;
    subfolders (rounds) read; .docx paragraphs kept whole
  - Resubmission rounds made to work
  - Privacy: .gitignore in every review folder; each writer's reviewer gets only that
    writer's files; no references to Jared's private tools in the public repo
  - Word copy of the Writer Feedback
  - Windows test job on GitHub Actions
  - README rewritten around the installer and `/mentor`
- Removed: `bin/wmf`, `bin/wmf.cmd`, `scripts/init_project.py`, `templates/`,
  `wmf-config.yaml.example`, root `assignment.md`/`rubric.md` templates, the leftover
  command-line entry points of the three `render_xlsx*` scripts
- Out (deliberately):
  - A signed `.exe` (yearly certificate cost; `.cmd` does the job)
  - Running Claude inside the test job (needs an account; checked on Mac)
  - Changing how a review judges the work (rubric scoring, mentor voice, two sections)
  - Automatic name removal before review (possible later; Jared's `redactor` skill exists)

## Acceptance checks
- [ ] A1 — On the GitHub Windows runner, the Windows installer runs start to finish
  unattended, and the dependency check then reports every tool found.
- [ ] A2 — Running the installer a second time succeeds and updates the framework.
- [ ] A3 — On the Windows runner and the Mac, extraction of made-up sample files gives:
  every sheet under its own name; formulas with cell addresses (e.g. `Calc!D15`);
  copied-down formulas; non-English characters intact; a .doc and an .xls either
  extracted or reported; one deliberately broken file reported while the rest still
  extract; files inside `round1/` and `round2/` subfolders found.
- [ ] A4 — On the Mac, `/mentor` appears in the Cursor Claude Code panel and in the
  Claude desktop app's Code tab. In a folder of made-up samples, with the assignment
  and rubric as Word/PDF, it asks the questions, shows the writer grouping, waits for
  "go", and produces per writer one .md (both sections) and one .docx (Writer Feedback
  only), plus the summary.
- [ ] A5 — `/mentor` states that file contents are sent to Anthropic before it starts.
- [ ] A6 — Each writer's reviewer is given only that writer's files (visible in the
  prompt the batch file builds).
- [ ] A7 — A resubmission run on made-up round 1 and round 2 samples compares round 2
  with round 1 feedback.
- [ ] A8 — The review folder gets a .gitignore covering submissions, similarity
  reports, extracted text, rendered charts and feedback.
- [ ] A9 — `grep` finds no `jared-voice`, `Research-Project-Flow`, Canvas or student
  references in the repo, outside the attribution and economics quotes.
- [ ] A10 — The Mac installer runs on Jared's Mac and installs `/mentor`.
- [ ] A11 — README describes the installer and `/mentor` first, in plain language,
  with the Windows warning step.

## Assumptions
- The repo is public, so the installers can download the framework zip with no
  account. ✅ verified (`gh repo view` → PUBLIC, 2026-11-22)
- `irm https://claude.ai/install.ps1 | iex` installs Claude Code on Windows without
  admin; Git for Windows is optional. ✅ verified (code.claude.com/docs/en/setup).
  The installer still installs Git, because review steps run as bash commands.
- Personal skills live in `~/.claude/skills/<name>/SKILL.md`. ✅ verified (docs). The
  desktop app's Code tab reading them is not in official docs → checked by hand in A4.
- GitHub's `windows-2025` runner has winget. — secondary sources; the test job prints
  `winget --version` first and fails if absent.
- After a winget install, the same window doesn't see the new program on PATH; the
  installer finds Python by full path. — checked in A1.
- On Mac, Homebrew needs admin and can't run unattended; if it is missing the
  installer stops and says how to install it. — design choice, no question needed.
- The Word copy is made with the `python-docx` package, which the installers add. —
  design choice.
- Existing folders set up with `wmf init` keep working because the script paths they
  reference don't move. — checked by running one old folder's commands after the change.
- Writers' files may be named by any learning system; `/mentor` proposes a grouping
  by writer and asks him to confirm instead of assuming one naming scheme. — from
  review item 4 (inferred, not tested against real exports).

## Decisions (from Clarify)
| # | Question | Answer | Who / date |
|---|---|---|---|
| D1 | Spec workflow for this project | Default tiers | Jared 2026-11-22 |
| D2 | Evidence for Windows | GitHub Actions Windows job | Jared 2026-11-22 |
| D3 | Which Claude he uses | Support both Cursor panel and desktop Code tab | Jared 2026-11-22 |
| D4 | How he gets it | One installer file he double-clicks | Jared 2026-11-22 |
| D5 | Where he downloads it | GitHub Release asset (`releases/latest/download/…`), `.cmd` not `.exe` | Jared 2026-11-22 |
| D6 | Extra fixes in scope | Data-loss bugs, one set of instructions, privacy, resubmission rounds | Jared 2026-11-22 |
| D7 | Old `wmf init` and config | Remove | Jared 2026-11-22 |
| D8 | Output | `feedback` folder; .md per writer + Word copy of Writer Feedback | Jared 2026-11-22 |
| D9 | Mac installer | Yes | Jared 2026-11-22 |

## Constitution rules this touches
- Data rules: made-up sample files only, in tests and CI
- Human gates: merge to main; publishing the release; sending the link to the colleague
- Non-negotiables: writers' files never in git (A8); Writer Feedback doesn't hand over fixes
- Style: plain language, mentor/writer terms
