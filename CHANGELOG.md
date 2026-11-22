# Changes

## 2.0.0 — 2026-11-22

Release page: https://github.com/Black-JL/writing-mentor-framework/releases/tag/v2.0.0
Windows installer link (always the newest release):
https://github.com/Black-JL/writing-mentor-framework/releases/latest/download/Install-Writing-Mentor.cmd

### What's new
- **`/mentor` command.** Type it in Claude Code in any folder. It asks where the assignment,
  rubric and writers' files are (Word, PDF or text), shows which files belong to which writer
  for you to confirm, says that file contents go to Anthropic, and waits for your yes.
- **Installers.** Windows: double-click `Install-Writing-Mentor.cmd` (Windows warns once:
  More info → Run anyway). Mac: one line in Terminal (see README). Both install what's
  missing, keep Python packages in a private environment inside the framework folder, and add
  `/mentor`. Running the installer again updates the framework.
- **Word copy of the Writer Feedback** for each writer, ready to send.
- **Resubmissions.** Point `/mentor` at the earlier feedback; each review checks what was
  addressed and gives the change in score. Output goes to `feedback-round<N>`.
- **File reading fixed.** One damaged file no longer stops the run. Every spreadsheet sheet is
  read under its own name, with cell addresses, copied-down formulas, and the cells each chart
  is drawn from. Old .doc/.xls are read with LibreOffice or reported. Word paragraphs stay
  whole; footnotes and headers are read. Short text PDFs are no longer sent to OCR.
- **Charts.** Excel (Mac or Windows), then LibreOffice, then Quick Look (Mac), whichever is
  installed. Every outside program has a time limit.
- **Privacy.** Each writer's review is given only that writer's files. Review folders get a
  `.gitignore`. References to Jared's private tools were removed from the public repo.
- **One set of instructions:** `skills/feedback/SKILL.md` runs a batch;
  `skills/feedback/review-one-writer.md` is what each review does.
- **Removed:** `wmf init`, `wmf.cmd`, `templates/`, `wmf-config.yaml`. Folders set up with
  `wmf init` still work (their script commands are kept as hand-offs).

### Fixed after the release (on `main`, 18aa1e1)
- **Mac: Excel no longer asks "Grant File Access" for every file.** The workbook is copied into
  Excel's own folder (`~/Library/Containers/com.microsoft.Excel/Data`), turned into a PDF
  there, and the PDF is copied back. Windows was not affected. Mac users get this by running
  the installer again.

### Bugs found by testing before release
- Excel chart rendering on Mac had never worked (AppleScript used `PDF` instead of
  `PDF file format`); every chart had come from LibreOffice or Quick Look.
- The Windows installer skipped poppler when another program had installed `pdftotext` alone.
- Quick Look could hang a review on a machine with no screen.
- `wmf init` overwrote existing assignment and rubric files (`--force`).

### How it was tested
- GitHub Actions (`.github/workflows/test.yml`), on every push: Windows (windows-2025) and Mac
  (macos-15) each run their installer twice, then `tests/run_tests.py` (23 checks on made-up
  files). Passing on 2.0.0.
- On Jared's Mac: full `/mentor` runs on made-up samples (3 writers, about $2.40; a round 2
  resubmission for 1 writer, about $1.75). Both caught the planted chart error; round 2 caught a
  false "I fixed the chart" claim.
- Details: `specs/2026-11-22-setup-wizard/converge.md`.

### Not yet tested
- Excel drawing charts on Windows (the test machine has no Excel).
- Quitting Excel afterwards when the script was the one that opened it.
- `/mentor` in the Claude desktop app's Code tab (tested in Claude Code).
- File names from a real learning-system export.
- A first install on a colleague's own Windows PC.

### Making the next release
1. Merge to `main` and check the GitHub Actions run passes on Windows and Mac.
2. Make a Windows-line-ending copy of the installer and publish it:
   ```bash
   python3 -c "from pathlib import Path; t=Path('install/Install-Writing-Mentor.cmd').read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'); Path('/tmp/Install-Writing-Mentor.cmd').write_bytes(t)"
   gh release create vX.Y.Z /tmp/Install-Writing-Mentor.cmd --target main --title "..." --notes "..."
   ```
3. The `.cmd` downloads `install/install.ps1` from `main` each time it runs, so fixes on `main`
   reach Windows users without a new release; a release is needed only when the `.cmd` itself
   changes.
