#!/usr/bin/env python3
"""
Save the Writer Feedback section (Section B) of each feedback file as a Word file
the mentor can send to the writer. The Reviewer Notes are left out.

    python make_writer_docx.py feedback/            # every .md in the folder
    python make_writer_docx.py feedback/rivera.md   # one file

Writes "<name> - Writer Feedback.docx" next to each .md file.
"""
import re
import sys
from pathlib import Path

from _tools import utf8_console

SECTION_B = re.compile(r'^#\s*SECTION B\b', re.IGNORECASE)
SKIP_FILES = {'FEEDBACK_SUMMARY.md'}
INLINE = re.compile(r'(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)')


def section_b(md):
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if SECTION_B.match(line.strip()):
            body = lines[i + 1:]
            # drop the "(Share this section...)" subtitle and rule lines right after the heading
            while body and (not body[0].strip() or body[0].strip() == '---'
                            or body[0].lstrip('#').strip().startswith('(')):
                body.pop(0)
            return body
    return None


def add_runs(par, text):
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith('**') and piece.endswith('**'):
            par.add_run(piece[2:-2]).bold = True
        elif piece.startswith('`') and piece.endswith('`'):
            par.add_run(piece[1:-1]).font.name = 'Courier New'
        elif piece.startswith('*') and piece.endswith('*') and len(piece) > 2:
            par.add_run(piece[1:-1]).italic = True
        else:
            par.add_run(piece)


def convert(md_path):
    from docx import Document

    body = section_b(md_path.read_text(encoding='utf-8'))
    if body is None:
        return None, 'no "SECTION B" heading found'
    doc = Document()
    title = md_path.stem.replace('_', ' ').replace('-', ' ').title()
    doc.add_heading(f'Feedback for {title}', level=1)

    table_rows = []

    def flush_table():
        rows = [r for r in table_rows if not set(r.replace('|', '').strip()) <= set('-: ')]
        if rows:
            cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
            width = max(len(c) for c in cells)
            t = doc.add_table(rows=len(cells), cols=width)
            t.style = 'Table Grid'
            for i, row in enumerate(cells):
                for j, val in enumerate(row):
                    par = t.cell(i, j).paragraphs[0]
                    add_runs(par, val)
                    if i == 0:
                        for run in par.runs:
                            run.bold = True
        table_rows.clear()

    for line in body:
        s = line.rstrip()
        if s.strip().startswith('|'):
            table_rows.append(s)
            continue
        flush_table()
        st = s.strip()
        if not st or st == '---':
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', st)
        if m:
            level = min(len(m.group(1)), 3)
            doc.add_heading(m.group(2).strip(), level=max(level, 2) if level == 1 else level)
        elif re.match(r'^[-*]\s+', st):
            add_runs(doc.add_paragraph(style='List Bullet'), re.sub(r'^[-*]\s+', '', st))
        elif re.match(r'^\d+[.)]\s+', st):
            add_runs(doc.add_paragraph(style='List Number'), re.sub(r'^\d+[.)]\s+', '', st))
        else:
            add_runs(doc.add_paragraph(), st)
    flush_table()

    out = md_path.with_name(f'{md_path.stem} - Writer Feedback.docx')
    doc.save(out)
    return out, 'ok'


def main():
    utf8_console()
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    target = Path(sys.argv[1])
    files = sorted(p for p in target.glob('*.md') if p.name not in SKIP_FILES) if target.is_dir() else [target]
    bad = 0
    for f in files:
        out, note = convert(f)
        if out:
            print(f'made   {out.name}')
        else:
            bad += 1
            print(f'missed {f.name}  ({note})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
