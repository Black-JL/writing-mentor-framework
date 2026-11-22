# Constitution — Writing Mentor Framework

Standing rules every spec is checked against. Each rule cites where it came from.
Changing this file needs Jared's OK.

## Purpose
Let a mentor have Claude Code review written work (documents, spreadsheets, charts)
and produce two-part feedback: Reviewer Notes for the mentor, Writer Feedback for the
writer. Must work for a mentor on macOS or Windows who does not use GitHub.
(README; Jared 2026-11-22: colleague on Windows, uses Cursor + Claude.)

## Non-negotiables
- Writers' files and all feedback output never enter git. `.gitignore` covers
  `submissions/` and feedback folders; don't weaken it. (.gitignore; README Privacy)
- Writer Feedback shows evidence and asks questions; it does not hand over the fix.
  (README "Feedback in two parts"; skills/feedback/SKILL.md Tier 2)
- Attribution to Scott Cunningham's Referee 2 protocol stays in the README. (README)

## Human gates (Claude proposes, Jared does/approves)
- Merging a spec branch into `main` / pushing `main`. (spec skill; Jared asked for the
  2026-11-22 push explicitly)
- Publishing a GitHub release, and sending anything to the colleague. (global CLAUDE.md: outward-facing actions)

## Data rules
- No real writers' work, names, or grades in the repo, in specs, in tests, or in CI.
  Test with made-up sample files only. (spec skill rules; global privacy rules)
- Documentation tells the mentor plainly that file contents go to Anthropic, and to
  check their organization's policy first. (README Privacy, 2026-11-22)

## How work flows
- Default /spec tiers: Tier 2 for features, Tier 1 for small changes, none for
  doc edits. (Jared 2026-11-22: "Default as-is")
- Build in a worktree under `~/GitHub/`, never in the main checkout. (spec skill;
  see Known traps)
- **Evidence for Windows behavior = a GitHub Actions job on a Windows runner** that
  installs the tools and runs the scripts on sample files. It cannot run Claude, so
  anything Claude does is checked on the Mac. (Jared 2026-11-22)

## Style and naming
- Plain language, no hype, no AI/tool jargon in anything the mentor reads. (global
  CLAUDE.md "Plain Language")
- Mentor / writer (mentee) language. No references to Canvas or to students in the
  README. (Jared 2026-11-22: "drop references to Canvas and students. Keep the
  mentor-mentee language")
- Commands: `python` on Windows, `python3` on macOS. (2026-11-22 Windows work)

## Known traps
- The main checkout lives in `~/Documents/A-B/`, and iCloud Documents sync appears to
  be on. A `.git` folder in a synced folder can be corrupted. (global CLAUDE.md
  "never put a .git directory inside a synced folder")
- Claude Code finds project skills only in `.claude/skills/<name>/SKILL.md`, not
  `skills/`. (code.claude.com/docs/en/skills, checked 2026-11-22)
- On Windows, winget installs of poppler and Tesseract may not be on PATH; scripts
  find them through `skills/feedback/scripts/_tools.py`.
- Windows console output piped to Claude is cp1252; scripts call `utf8_console()`.
