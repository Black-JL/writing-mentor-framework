# Writing Mentor Framework

This folder is the framework itself, not a place to review work.

- To review work: install with `install/Install-Writing-Mentor.cmd` (Windows) or
  `install/install.sh` (macOS), then type `/mentor` in Claude Code inside the folder
  that holds the writers' files. See README.md.
- `skills/mentor/SKILL.md` — the `/mentor` command (the installer copies it to
  `~/.claude/skills/mentor/` with this folder's path filled in).
- `skills/feedback/SKILL.md` — runs a review batch.
- `skills/feedback/review-one-writer.md` — what each writer's reviewer does.
- `skills/feedback/scripts/` — extraction, chart rendering, grouping, Word copies.
- `tests/run_tests.py` — checks the scripts on made-up sample files.
- `specs/` — how changes are planned (CONSTITUTION.md has the standing rules).

Never put real writers' work, names or grades in this repository.
