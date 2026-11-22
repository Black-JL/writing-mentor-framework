#!/usr/bin/env python3
"""
Prepare a review: group the files by writer, then extract and render everything.

Step 1 — propose a grouping (reads only file names):
    python prepare_review.py group --submissions <folder or files...> --out feedback \
        --assignment <file> --rubric <file> [--concepts <file>] \
        [--prior-feedback <folder>] [--round N]
  Writes <out>/_work/manifest.json and prints the grouping for the mentor to check.
  The manifest can be edited (move files between writers) before step 2.

Step 2 — extract and render:
    python prepare_review.py run --manifest feedback/_work/manifest.json
  Extracts text for every file, renders Excel charts, converts the assignment,
  rubric and course concepts to text, writes a .gitignore, prints one line per file,
  and adds each writer's file list to the manifest.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from _tools import utf8_console
from extract_submission_text import extract_file, iter_files

# Export-style names: writer_[LATE_]userid_fileid_originalname
EXPORT = re.compile(r'^(?P<writer>[A-Za-z][A-Za-z0-9-]*?)(?:_LATE)?_(?P<uid>\d+)_(?P<fid>\d+)_(?P<orig>.+)$',
                    re.IGNORECASE)
SIMILARITY = re.compile(r'turnitin|similarity', re.IGNORECASE)
RESUBMIT_SUFFIX = re.compile(r'-\d+(?=\.[^.]+$)')


def slug(name):
    s = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-._')
    return s or 'writer'


def collect(paths):
    """All files under the given paths, as (absolute path, path relative to its root)."""
    out = []
    for p in paths:
        p = Path(p).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f'Not found: {p}')
        out += [(f.resolve(), rel) for f, rel in iter_files(p)]
    return out


def group_files(files):
    """Return ({writer: {files, older_versions, similarity}}, method, unmatched)."""
    writers, unmatched = {}, []

    def entry(name):
        return writers.setdefault(name, {'files': [], 'older_versions': [], 'similarity': []})

    matches = [(f, rel, EXPORT.match(f.name)) for f, rel in files]
    hits = sum(1 for *_, m in matches if m)
    if files and hits / len(files) >= 0.6:
        method = 'file names (writer_id_id_name pattern)'
        newest = {}
        for f, rel, m in matches:
            if not m:
                unmatched.append(str(f))
                continue
            w = m.group('writer').lower()
            if SIMILARITY.search(m.group('orig')):
                entry(w)['similarity'].append(str(f))
                continue
            key = (w, RESUBMIT_SUFFIX.sub('', m.group('orig')).lower())
            newest.setdefault(key, []).append((int(m.group('fid')), f))
        for (w, _), versions in newest.items():
            versions.sort()
            entry(w)['files'].append(str(versions[-1][1]))
            entry(w)['older_versions'] += [str(f) for _, f in versions[:-1]]
        return writers, method, unmatched

    nested = [(f, rel) for f, rel in files if len(rel.parts) >= 2]
    if files and len(nested) == len(files):
        method = 'one folder per writer'
        for f, rel in files:
            e = entry(rel.parts[0])
            (e['similarity'] if SIMILARITY.search(f.name) else e['files']).append(str(f))
        return writers, method, unmatched

    method = 'one file per writer (no naming pattern found; please check)'
    for f, rel in files:
        if SIMILARITY.search(f.name):
            unmatched.append(str(f))
        else:
            entry(f.stem)['files'].append(str(f))
    return writers, method, unmatched


def cmd_group(args):
    out = Path(args.out).expanduser().resolve()
    work = out / '_work'
    work.mkdir(parents=True, exist_ok=True)
    files = collect(args.submissions)
    inputs = {k: str(Path(v).expanduser().resolve()) if v else None
              for k, v in (('assignment', args.assignment), ('rubric', args.rubric),
                           ('concepts', args.concepts))}
    input_paths = {v for v in inputs.values() if v}
    files = [(f, rel) for f, rel in files if str(f) not in input_paths
             and out not in f.parents]
    writers, method, unmatched = group_files(files)
    manifest = {
        'version': 1,
        'created': datetime.now().isoformat(timespec='seconds'),
        'output_dir': str(out),
        'project_dir': str(Path.cwd().resolve()),
        'submissions': [str(Path(p).expanduser().resolve()) for p in args.submissions],
        'inputs': inputs,
        'round': args.round,
        'prior_feedback': str(Path(args.prior_feedback).expanduser().resolve()) if args.prior_feedback else None,
        'grouping_method': method,
        'writers': {slug(k): v for k, v in sorted(writers.items())},
        'unmatched': unmatched,
    }
    (work / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f'Grouped by: {method}')
    print(f'{len(manifest["writers"])} writer(s):')
    for name, w in manifest['writers'].items():
        print(f'  {name}')
        for f in w['files']:
            print(f'      {Path(f).name}')
        for f in w['older_versions']:
            print(f'      (older version, not reviewed) {Path(f).name}')
        for f in w['similarity']:
            print(f'      (similarity report) {Path(f).name}')
    if unmatched:
        print('Not matched to a writer:')
        for f in unmatched:
            print(f'      {Path(f).name}')
    print(f'\nManifest: {work / "manifest.json"}')
    return 0


def write_gitignore(manifest):
    """Keep writers' files and all review output out of git."""
    root = Path(manifest['project_dir'])
    lines = ['# Writing Mentor: writers\' files and review output stay out of git']
    for p in [manifest['output_dir']] + manifest['submissions']:
        p = Path(p)
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            continue  # outside this folder; nothing to ignore here
        if rel in ('', '.'):
            rel = '*'
        lines.append(rel + ('/' if p.is_dir() and rel != '*' else ''))
    gi = root / '.gitignore'
    existing = gi.read_text(encoding='utf-8').splitlines() if gi.exists() else []
    new = [ln for ln in lines if ln not in existing]
    if new:
        with gi.open('a', encoding='utf-8') as fh:
            if existing and existing[-1].strip():
                fh.write('\n')
            fh.write('\n'.join(new) + '\n')
    (Path(manifest['output_dir']) / '.gitignore').write_text('*\n', encoding='utf-8')
    return gi


def cmd_run(args):
    import render_charts

    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    out = Path(manifest['output_dir'])
    work = out / '_work'
    counts = {'extracted': 0, 'skipped': 0, 'failed': 0}
    renderers = render_charts.methods()

    # Assignment, rubric, course concepts
    inputs_dir = work / 'inputs'
    manifest['input_text'] = {}
    for key, src in manifest['inputs'].items():
        if not src:
            continue
        status, note = extract_file(Path(src), inputs_dir / f'{key}.txt', work)
        counts[status] += 1
        print(f'{status:9} [{key}] {Path(src).name}  ({note})')
        if status == 'extracted':
            manifest['input_text'][key] = str(inputs_dir / f'{key}.txt')

    for name, w in manifest['writers'].items():
        wdir = work / 'writers' / name
        if wdir.exists():
            shutil.rmtree(wdir)  # no leftovers from an earlier run
        review = {'originals': w['files'] + w['similarity'], 'extracted': [], 'charts': [],
                  'prior_feedback': None, 'report': []}
        for src in w['files'] + w['similarity']:
            src = Path(src)
            target = wdir / 'extracted' / f'{src.name}.txt'
            status, note = extract_file(src, target, wdir)
            counts[status] += 1
            review['report'].append(f'{status}: {src.name} ({note})')
            print(f'{status:9} [{name}] {src.name}  ({note})')
            if target.exists():
                review['extracted'].append(str(target))
        # Charts: workbooks handed in, plus workbooks pasted into Word files
        books = [Path(f) for f in w['files'] if Path(f).suffix.lower() in ('.xlsx', '.xlsm')]
        books += sorted((wdir / 'extracted' / 'embedded').glob('*.xlsx'))
        for book in books:
            if not renderers:
                review['report'].append(f'charts not rendered: {book.name} (no Excel or LibreOffice)')
                continue
            used, errors = render_charts.render_file(book, wdir / 'charts', renderers)
            msg = f'rendered with {used}' if used else 'charts not rendered: ' + '; '.join(errors)
            review['report'].append(f'{book.name}: {msg}')
            print(f'{"charts":9} [{name}] {book.name}  ({msg})')
        review['charts'] = [str(p) for p in sorted((wdir / 'charts').glob('*.png'))] if (wdir / 'charts').exists() else []
        if manifest.get('prior_feedback'):
            prior = Path(manifest['prior_feedback']) / f'{name}.md'
            review['prior_feedback'] = str(prior) if prior.exists() else None
        w['review'] = review

    gi = write_gitignore(manifest)
    manifest['prepared'] = datetime.now().isoformat(timespec='seconds')
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n{counts['extracted']} extracted, {counts['skipped']} skipped, {counts['failed']} failed")
    if not renderers:
        print('Chart images skipped: no Excel or LibreOffice found. Formulas and chart data ranges were still read.')
    print(f'.gitignore updated: {gi}')
    return 0


def main():
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('group')
    g.add_argument('--submissions', nargs='+', required=True)
    g.add_argument('--out', default='feedback')
    g.add_argument('--assignment')
    g.add_argument('--rubric')
    g.add_argument('--concepts')
    g.add_argument('--prior-feedback')
    g.add_argument('--round', type=int)
    r = sub.add_parser('run')
    r.add_argument('--manifest', required=True)
    args = ap.parse_args()
    return cmd_group(args) if args.cmd == 'group' else cmd_run(args)


if __name__ == '__main__':
    sys.exit(main())
