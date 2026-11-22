# Plan — 2026-11-22-setup-wizard

## Approach
The installer puts the framework in `~/writing-mentor-framework`, makes a private
Python environment in it (`.venv`, so no PATH or "externally managed" problems), and
writes `~/.claude/skills/mentor/SKILL.md` with the framework and Python paths filled in.
`/mentor` asks the questions, runs `prepare_review.py group` to propose a grouping by
writer, waits for "go", runs `prepare_review.py run` (extract, render, convert inputs,
.gitignore, per-file report), then follows the batch file. The batch file hands each
writer's reviewer an explicit file list from the manifest; each reviewer follows
`review-one-writer.md`. Afterwards `make_writer_docx.py` makes the Word copies and one
agent writes the summary.

## Files touched
| File | Change |
|---|---|
| `install/install.ps1`, `install/Install-Writing-Mentor.cmd` | new: Windows installer |
| `install/install.sh` | new: Mac installer |
| `skills/mentor/SKILL.md` | new: /mentor template (installer fills paths) |
| `skills/feedback/SKILL.md` | rewritten: runs the batch (path kept so old folders work) |
| `skills/feedback/review-one-writer.md` | new: everything one reviewer needs (moved from SKILL.md + CLAUDE.md) |
| `skills/feedback/scripts/prepare_review.py` | new: group + run |
| `skills/feedback/scripts/make_writer_docx.py` | new: Word copy of Section B |
| `skills/feedback/scripts/extract_submission_text.py` | fixes from review items 1, 2, 7, 8, 9 |
| `skills/feedback/scripts/check_dependencies.py` | python-docx; olefile optional |
| `skills/feedback/scripts/render_*.py` | drop unused command-line entry points |
| `skills/feedback/references/peer.md` | drop private-tool reference |
| `CLAUDE.md` | shrink to a pointer |
| `README.md` | installer + /mentor first |
| `tests/make_samples.py`, `tests/run_tests.py` | new: made-up samples + checks |
| `.github/workflows/test.yml` | new: Windows + Mac jobs |
| removed | `bin/`, `scripts/init_project.py`, `templates/`, `wmf-config.yaml.example`, root `assignment.md`/`rubric.md`, `submissions/` |

## Alternatives rejected
| Option | Why not |
|---|---|
| Signed .exe | yearly certificate; stronger antivirus friction unsigned |
| Mac `.command` file | a downloaded `.command` loses its run permission and Gatekeeper blocks it; a one-line Terminal command avoids both (see D10) |
| Install packages into system Python | Homebrew Python refuses (PEP 668); Windows PATH unreliable right after install |
| Keep the config file | almost none of it is read; /mentor asks instead |

## Risks and how they're contained
- winget missing or blocked by school IT → installer stops with a plain message naming what to install by hand.
- Older `wmf init` folders → `skills/feedback/SKILL.md` and script paths stay; checked in T-final.
- Grouping guesses wrong → mentor confirms the grouping before anything runs.

## How each acceptance check will be tested
| Check | Test |
|---|---|
| A1, A2 | GitHub Actions `windows-2025`: run installer twice with `WMF_SOURCE` = checkout; then `check_dependencies.py` exit 0 |
| A3 | `tests/run_tests.py` on both runners and on the Mac |
| A4, A5, A6 | Jared's Mac: run `/mentor` in a scratch folder of made-up samples; read transcript + outputs; open Cursor panel and desktop Code tab and look for /mentor |
| A7 | same, with round 1 feedback then round 2 samples |
| A8 | `tests/run_tests.py` checks the .gitignore lines after `prepare_review.py run` |
| A9 | `grep -rniE "jared-voice|Research-Project-Flow|canvas|student"` over the repo |
| A10 | run `install/install.sh` on Jared's Mac with `WMF_SOURCE` set |
| A11 | read README |
