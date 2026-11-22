#!/usr/bin/env python3
"""
Checks the scripts against made-up sample files. No Claude, no real writers' work.

    python tests/run_tests.py            # uses the Python running it
    WMF_CHART_TOOLS=none python tests/run_tests.py   # skip chart rendering

Prints PASS/FAIL per check; exits 1 if any check fails.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / 'skills' / 'feedback' / 'scripts'
sys.path.insert(0, str(HERE))
from make_samples import build  # noqa: E402

results = []


def check(name, ok, detail=''):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f'  — {detail}' if detail and not ok else ''))


def py(*args, cwd=None):
    env = dict(os.environ, PYTHONIOENCODING='')  # use the platform default, like a real run
    r = subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', env=env)
    return r.returncode, r.stdout + r.stderr


def main():
    tmp = Path(tempfile.mkdtemp(prefix='wmf-test-'))
    root = build(tmp / 'Review Folder')  # a space in the path on purpose
    sub = root / 'submissions'

    # 1. dependency check runs and prints without encoding errors
    code, out = py(SCRIPTS / 'check_dependencies.py')
    check('check_dependencies runs', 'Traceback' not in out, out[-400:])

    # 2. grouping
    code, out = py(SCRIPTS / 'prepare_review.py', 'group', '--submissions', sub, '--out', root / 'feedback',
                   '--assignment', root / 'assignment.docx', '--rubric', root / 'rubric.pdf', cwd=root)
    check('group exits 0', code == 0, out)
    manifest_path = root / 'feedback' / '_work' / 'manifest.json'
    m = json.loads(manifest_path.read_text(encoding='utf-8'))
    check('three writers found', sorted(m['writers']) == ['lindqvist', 'okafor', 'rivera'], str(sorted(m['writers'])))
    riv = m['writers'].get('rivera', {})
    check('older workbook version set aside',
          any('4999' in f for f in riv.get('older_versions', [])) and not any('4999' in f for f in riv.get('files', [])),
          json.dumps(riv))

    # 3. run (extract + render + gitignore)
    code, out = py(SCRIPTS / 'prepare_review.py', 'run', '--manifest', manifest_path, cwd=root)
    check('run exits 0 despite a damaged file', code == 0, out[-800:])
    check('damaged file reported, not crashed', 'failed    [lindqvist] lindqvist_LATE_1003_5006_broken.xlsx' in out, out)
    check('old .doc/.xls reported or extracted',
          all(any(s in out for s in (f'extracted [okafor] {n}', f'skipped   [okafor] {n}', f'failed    [okafor] {n}'))
              for n in ('okafor_1002_5004_old.doc', 'okafor_1002_5005_old.xls')), out)
    m = json.loads(manifest_path.read_text(encoding='utf-8'))
    wdir = root / 'feedback' / '_work' / 'writers'

    xl = (wdir / 'rivera' / 'extracted' / 'rivera_1001_5002_model.xlsx.txt').read_text(encoding='utf-8')
    check('every sheet under its own name', '[Sheet] Data' in xl and '[Sheet] Calc' in xl
          and xl.index('A1=Year | B1=Nominal GDP') < xl.index('[Sheet] Calc'), xl[:600])
    check('formulas carry cell addresses', 'C2: =Data!B2/Data!C2' in xl, xl)
    check('copied-down formulas shown', 'C3: =Data!B3/Data!C3' in xl and 'C4: =Data!B4/Data!C4' in xl, xl)
    check('chart data ranges listed', 'Data!$B$2:$B$4' in xl and 'Real GDP by year' in xl, xl)
    check('non-English characters intact', 'São Paulo método' in xl, xl)

    doc = (wdir / 'rivera' / 'extracted' / 'rivera_1001_5001_report.docx.txt').read_text(encoding='utf-8')
    check('Word paragraphs kept whole', 'Real GDP grew 10 percent between 2021 and 2023.' in doc, doc)
    check('accents and dashes intact', 'Müller’s café' in doc and '—' in doc, doc)

    pdf = (wdir / 'okafor' / 'extracted' / 'okafor_1002_5003_essay.pdf.txt')
    check('PDF text extracted', pdf.exists() and 'real GDP rose 10 percent' in pdf.read_text(encoding='utf-8'),
          pdf.read_text(encoding='utf-8')[:300] if pdf.exists() else 'missing')

    inputs = m.get('input_text', {})
    check('assignment and rubric converted to text', 'assignment' in inputs and 'rubric' in inputs, json.dumps(inputs))

    review = m['writers']['rivera'].get('review', {})
    others = [f for f in review.get('extracted', []) + review.get('originals', [])
              if 'okafor' in f or 'lindqvist' in f]
    check("a writer's file list holds only that writer's files", review and not others, json.dumps(review)[:500])

    gi = (root / '.gitignore').read_text(encoding='utf-8')
    check('.gitignore covers feedback and submissions', 'feedback/' in gi and 'submissions/' in gi, gi)
    check('feedback folder ignores itself', (root / 'feedback' / '.gitignore').read_text().strip() == '*')

    if os.environ.get('WMF_CHART_TOOLS', '').lower() != 'none':
        charts = review.get('charts', [])
        check('chart images rendered (if a renderer is installed)', bool(charts) or 'not rendered' in json.dumps(review),
              json.dumps(review.get('report')))

    # 4. subfolders (resubmission rounds) are read
    code, out = py(SCRIPTS / 'extract_submission_text.py', '--input', root / 'rounds', '--out', tmp / 'rounds-out')
    check('files inside round1/ and round2/ found', 'round1' in out and 'round2' in out and code == 0, out)

    # 5. Word copy of the Writer Feedback
    fb = root / 'feedback' / 'rivera.md'
    fb.write_text('# Rivera - Feedback\n\n---\n# SECTION A: REVIEWER NOTES\n## (For the mentor only)\n---\n'
                  'Secret technical note C15.\n\n---\n# SECTION B: WRITER FEEDBACK\n## (Share this section with the writer)\n---\n\n'
                  '## Summary\nGood start with **clear** numbers.\n\n| Criterion | Score |\n|---|---|\n| Data | 8/10 |\n\n'
                  '- Check whether your figures are real or nominal.\n', encoding='utf-8')
    code, out = py(SCRIPTS / 'make_writer_docx.py', root / 'feedback')
    out_docx = root / 'feedback' / 'rivera - Writer Feedback.docx'
    ok = code == 0 and out_docx.exists()
    text = ''
    if ok:
        from docx import Document
        d = Document(out_docx)
        text = '\n'.join(p.text for p in d.paragraphs) + '\n'.join(c.text for t in d.tables for r in t.rows for c in r.cells)
    check('Word copy made', ok, out)
    check('Word copy has Writer Feedback only', ok and 'Secret technical note' not in text and 'real or nominal' in text
          and '8/10' in text, text[:400])

    print(f'\n{sum(results)}/{len(results)} checks passed')
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
