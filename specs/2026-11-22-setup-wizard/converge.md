# Converge — 2026-11-22-setup-wizard

Evidence produced in the 2026-11-22 session. Made-up sample files only.

| Check | Verdict | Evidence |
|---|---|---|
| A1 Windows installer unattended, all tools found | ✅ | GitHub run 45053927596 (ef7c2db), job `windows` on windows-2025: first run installed poppler, Tesseract, Claude Code; "Setup finished."; check_dependencies "✓ All dependencies are installed". Earlier run 45052169999 failed: runner had pdftotext without pdftoppm → fixed in T-C1. |
| A2 Second install updates | ✅ | Same run: second install printed "already installed" for every program and "Setup finished." Mac: second `install.sh` on Jared's Mac replaced the old `bin/`, `templates/` files. |
| A3 Extraction on Windows + Mac | ✅ | `tests/run_tests.py` 23/23 on windows-2025, macos-15 (run 45053927596) and Jared's Mac: every sheet named, `C3: =Data!B3/Data!C3` (copied-down), chart ranges, `São Paulo método`, damaged file reported, round1/round2 found. |
| A4 /mentor appears and runs end to end | ✅ partly / ⚠️ | ✅ a fresh `claude -p "/mentor"` session in a sample folder found the installed skill, asked the 5 questions, showed the grouping (older version set aside), waited for yes, and wrote rivera/okafor/lindqvist `.md` + `- Writer Feedback.docx` + FEEDBACK_SUMMARY.md (session aaaddffd…, $2.42). Word copy checked: no Section A text. ⚠️ not yet seen in the Cursor panel or the desktop app's Code tab: Jared to check by hand. |
| A5 Privacy notice before starting | ✅ | Both runs: "the contents of these files … are sent to Anthropic … Start the review?" and no extraction until "Yes". |
| A6 Each reviewer gets only one writer's files | ✅ | run_tests check "a writer's file list holds only that writer's files"; batch prompt lists files explicitly. |
| A7 Resubmission compares with round 1 | ✅ | Round-2 run (session fef44bac…, $1.74): `feedback-round2/rivera.md` "Revision assessment" table item by item; caught the false claim "My chart now shows real GDP"; round 1 folder untouched. |
| A8 .gitignore | ✅ | run_tests: root `.gitignore` has `feedback/`, `submissions/`; `feedback/.gitignore` = `*`. |
| A9 No private-tool / Canvas / student references | ✅ | `grep -rniE "jared-voice|Research-Project-Flow|canvas"` → none; "student" only inside quoted examples in `peer.md` and `economical_writing_principles.md`. |
| A10 Mac installer on Jared's Mac | ✅ | `install.sh` (WMF_SOURCE=branch) → "Setup finished.", `~/.claude/skills/mentor/SKILL.md` with real paths. |
| A11 README | ✅ | README "Install" (Windows download link + "More info → Run anyway", Mac one line) and "Use it" (/mentor questions, outputs). |

## Found during converge and fixed
- T-C1 Windows installer detected poppler by pdftotext; now pdftoppm.
- T-C2 Excel on Mac never worked (AppleScript `PDF` → `PDF file format`); quits Excel if it opened it; LibreOffice profile in temp; OCR cut-off per page (one-page rubric was OCR'd).
- T-C3 Time limits on outside programs (Quick Look hung on the Mac test machine).
- /mentor used "students" unprompted → told to say "writers".

## Not tested
- Quitting Excel when the script opened it: Excel was already open on Jared's Mac, so only the "leave it open" path ran.
- Excel chart rendering on Windows (no Excel on the test machine).
- The release download link: no release published yet (human gate).
- A real learning-system export's file names.

## Built but not in the spec
- Chart titles, types and data ranges listed in spreadsheet extracts (supports the chart-vs-formula check).
- Mac installer is a one-line Terminal command, not a `.command` file (D10, needs Jared's OK).
