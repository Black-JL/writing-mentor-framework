#!/usr/bin/env python3
"""
Extract text, formulas, chart references, tracked changes and comments from the
files a writer hands in, so a reviewer can read them as plain text.

Handles .docx, .xlsx/.xlsm, .pdf (OCR for scanned pages), plain-text and code files,
and old .doc/.xls when LibreOffice is installed. One bad file never stops the run:
every file gets a printed result line (extracted / skipped / failed).

    python extract_submission_text.py --input submissions --out extracted
"""
import argparse
import io
import re
import shutil
import struct
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from _tools import find_tool, run, tool, utf8_console

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
NS = {'w': W, 's': S, 'c': C}

MAX_ROWS_PER_SHEET = 60
MAX_FORMULAS_PER_SHEET = 400
MAX_TEXT_FILE_CHARS = 200_000

TEXT_SUFFIXES = {'.txt', '.md', '.csv', '.tsv', '.json', '.py', '.r', '.rmd', '.do',
                 '.sas', '.sql', '.ipynb', '.tex', '.html', '.xml', '.yaml', '.yml'}
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.tiff', '.heic', '.webp'}
SUPPORTED = {'.docx', '.xlsx', '.xlsm', '.pdf', '.doc', '.xls'} | TEXT_SUFFIXES


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', errors='replace')


def _q(ns, tag):
    return f'{{{NS[ns]}}}{tag}'


# ---------------------------------------------------------------- Word (.docx)

def _paragraph_text(p, comment_map):
    """Text of one paragraph, runs joined, deleted text left out."""
    parts = []
    for node in p.iter():
        if node.tag == _q('w', 't') and node.text:
            parts.append(node.text)
        elif node.tag == _q('w', 'tab'):
            parts.append('\t')
        elif node.tag in (_q('w', 'br'), _q('w', 'cr')):
            parts.append('\n')
        elif node.tag == _q('w', 'commentRangeStart'):
            cid = node.attrib.get(_q('w', 'id'))
            if cid in comment_map:
                parts.append(f' [COMMENT {cid}] ')
    return ''.join(parts)


def _paragraphs(xml_bytes, comment_map):
    tree = ET.fromstring(xml_bytes)
    out = []
    for p in tree.iter(_q('w', 'p')):
        # Skip paragraphs nested in another paragraph (text boxes); the outer one has them.
        text = _paragraph_text(p, comment_map).strip()
        if text:
            out.append(text)
    return out


def extract_docx(path):
    insertions, deletions, comments, comment_map = [], [], [], {}
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if 'word/comments.xml' in names:
            tree = ET.fromstring(z.read('word/comments.xml'))
            for cm in tree.iter(_q('w', 'comment')):
                cid = cm.attrib.get(_q('w', 'id'))
                author = cm.attrib.get(_q('w', 'author'), 'Unknown')
                text = ' '.join(_paragraph_text(p, {}) for p in cm.iter(_q('w', 'p'))).strip()
                if cid and text:
                    comment_map[cid] = text
                    comments.append((cid, author, text))

        doc = z.read('word/document.xml')
        body = _paragraphs(doc, comment_map)
        tree = ET.fromstring(doc)
        for tag, bucket, text_tag in ((_q('w', 'ins'), insertions, _q('w', 't')),
                                      (_q('w', 'del'), deletions, _q('w', 'delText'))):
            for node in tree.iter(tag):
                text = ''.join(t.text or '' for t in node.iter(text_tag))
                if text.strip():
                    bucket.append((node.attrib.get(_q('w', 'author'), 'Unknown'), text))

        notes = []
        for part in ('word/footnotes.xml', 'word/endnotes.xml'):
            if part in names:
                notes += _paragraphs(z.read(part), {})
        headers = []
        for part in sorted(n for n in names if re.match(r'word/(header|footer)\d*\.xml$', n)):
            headers += _paragraphs(z.read(part), {})

    out = ['=' * 60, 'DOCUMENT TEXT (one paragraph per line)', '=' * 60, '\n'.join(body)]
    if notes:
        out += ['', '=' * 60, 'FOOTNOTES AND ENDNOTES', '=' * 60, '\n'.join(notes)]
    if headers:
        out += ['', '=' * 60, 'HEADERS AND FOOTERS', '=' * 60, '\n'.join(dict.fromkeys(headers))]
    if insertions or deletions:
        out += ['', '=' * 60, 'TRACK CHANGES DETECTED', '=' * 60,
                'The writer handed this in with tracked changes. They show what was modified.']
        for label, items in (('INSERTIONS', insertions), ('DELETIONS', deletions)):
            if items:
                out.append(f'{label} ({len(items)}):')
                for i, (author, text) in enumerate(items[:100], 1):
                    out.append(f'  [{i}] "{text[:300]}" (by {author})')
                if len(items) > 100:
                    out.append(f'  ({len(items) - 100} more not shown)')
    if comments:
        out += ['', '=' * 60, 'COMMENTS IN DOCUMENT', '=' * 60,
                'These may be earlier mentor feedback or the writer\'s own notes.']
        for cid, author, text in comments[:60]:
            out.append(f'  [COMMENT {cid}] {author}: "{text[:500]}"')
        if len(comments) > 60:
            out.append(f'  ({len(comments) - 60} more not shown)')
    return '\n'.join(out)


def _parse_ole10_native(data):
    try:
        pos = 8
        end = data.index(b'\x00', pos)
        filename = data[pos:end].decode('latin1', errors='ignore')
        pos = data.index(b'\x00', end + 1) + 1 + 8
        size = struct.unpack_from('<I', data, pos)[0]
        return filename, data[pos + 4:pos + 4 + size]
    except Exception:
        return None, None


def extract_embedded_from_docx(path, out_dir):
    """Save spreadsheets pasted into a Word file. Returns (saved paths, notes)."""
    saved, notes = [], []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.startswith('word/embeddings/'):
                continue
            base = Path(name).name
            data = z.read(name)
            if base.lower().endswith(('.xlsx', '.xlsm', '.xls')):
                target = out_dir / f'{path.stem}__{base}'
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                saved.append(target)
            elif base.lower().endswith('.bin'):
                try:
                    import olefile
                except ImportError:
                    notes.append(f'{base}: embedded object not read (olefile not installed)')
                    continue
                try:
                    ole = olefile.OleFileIO(io.BytesIO(data))
                    if ole.exists('\x01Ole10Native'):
                        fname, fdata = _parse_ole10_native(ole.openstream('\x01Ole10Native').read())
                        if fdata:
                            target = out_dir / f'{path.stem}__{Path(fname).name if fname else base}'
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(fdata)
                            saved.append(target)
                    ole.close()
                except Exception as exc:
                    notes.append(f'{base}: embedded object not read ({exc})')
    return saved, notes


# ------------------------------------------------------------ Excel (.xlsx)

_CELL = re.compile(r'([A-Z]{1,3})(\d+)$')
_REF = re.compile(r"(?<![A-Za-z_\d.$])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\d(A-Za-z_])")


def _col_num(col):
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def _col_name(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _split(ref):
    m = _CELL.match(ref)
    return _col_num(m.group(1)), int(m.group(2))


def shift_formula(formula, d_col, d_row):
    """Move the relative references in a formula, as Excel does when it is copied."""
    def repl(m):
        c_abs, col, r_abs, row = m.groups()
        new_col = col if c_abs else _col_name(_col_num(col) + d_col)
        new_row = row if r_abs else str(int(row) + d_row)
        return f'{c_abs}{new_col}{r_abs}{new_row}'
    return _REF.sub(repl, formula)


def _rels(z, part):
    folder, name = part.rsplit('/', 1)
    rel_path = f'{folder}/_rels/{name}.rels'
    if rel_path not in z.namelist():
        return {}
    out = {}
    for rel in ET.fromstring(z.read(rel_path)).iter(f'{{{PR}}}Relationship'):
        target = rel.attrib['Target']
        if target.startswith('/'):
            target = target[1:]
        else:
            parts = (folder + '/' + target).split('/')
            stack = []
            for p in parts:
                if p == '..':
                    stack.pop()
                elif p != '.':
                    stack.append(p)
            target = '/'.join(stack)
        out[rel.attrib['Id']] = target
    return out


def _cell_value(c, strings):
    t = c.attrib.get('t')
    v = c.find('s:v', NS)
    if t == 's' and v is not None and v.text is not None:
        i = int(v.text)
        return strings[i] if 0 <= i < len(strings) else ''
    if t == 'inlineStr':
        return ''.join(x.text or '' for x in c.iter(_q('s', 't')))
    if t == 'b' and v is not None:
        return 'TRUE' if v.text == '1' else 'FALSE'
    return v.text if v is not None and v.text is not None else ''


def _chart_summary(z, chart_part):
    tree = ET.fromstring(z.read(chart_part))
    title_el = tree.find('.//c:title', NS)
    a_t = '{http://schemas.openxmlformats.org/drawingml/2006/main}t'
    title = ' '.join(t.text for t in title_el.iter(a_t) if t.text) if title_el is not None else ''
    kinds = sorted({el.tag.split('}')[1] for el in tree.iter() if el.tag.endswith('Chart')
                    and el.tag.startswith(f'{{{C}}}') and el.tag != f'{{{C}}}chart'})
    refs = [f.text for f in tree.iter(_q('c', 'f')) if f.text]
    return title, kinds, refs


def extract_xlsx(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        strings = []
        if 'xl/sharedStrings.xml' in names:
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(_q('s', 'si')):
                strings.append(''.join(t.text or '' for t in si.iter(_q('s', 't'))))

        wb_rels = _rels(z, 'xl/workbook.xml')
        sheets = []
        for sh in ET.fromstring(z.read('xl/workbook.xml')).iter(_q('s', 'sheet')):
            rid = sh.attrib.get(f'{{{R}}}id')
            sheets.append((sh.attrib.get('name', '?'), wb_rels.get(rid)))

        out = [f'FILE: {path.name}', f'SHEETS: {", ".join(n for n, _ in sheets)}']
        chart_lines = []
        for name, part in sheets:
            out += ['', '=' * 60, f'[Sheet] {name}', '=' * 60]
            if not part or part not in names:
                out.append('(sheet contents not found: chart sheet or unusual file)')
                continue
            tree = ET.fromstring(z.read(part))
            shared = {}
            formulas, rows = [], []
            total_rows = 0
            for row in tree.iter(_q('s', 'row')):
                cells = []
                for c in row.findall('s:c', NS):
                    ref = c.attrib.get('r', '')
                    val = _cell_value(c, strings)
                    f = c.find('s:f', NS)
                    formula = None
                    if f is not None:
                        si = f.attrib.get('si')
                        if f.text:
                            formula = f.text
                            if f.attrib.get('t') == 'shared' and si is not None:
                                shared[si] = (ref, f.text)
                        elif f.attrib.get('t') == 'shared' and si in shared and ref:
                            m_ref, m_formula = shared[si]
                            (mc, mr), (cc, cr) = _split(m_ref), _split(ref)
                            formula = shift_formula(m_formula, cc - mc, cr - mr)
                    if formula is not None:
                        formulas.append(f'  {ref}: ={formula}  → {val}')
                    if val != '' or formula is not None:
                        cells.append(f'{ref}={val}')
                if cells:
                    total_rows += 1
                    if len(rows) < MAX_ROWS_PER_SHEET:
                        rows.append('  ' + ' | '.join(cells))
            out.append(f'Formulas ({len(formulas)}), as cell: =formula → value shown in the file:')
            out += formulas[:MAX_FORMULAS_PER_SHEET] or ['  (none)']
            if len(formulas) > MAX_FORMULAS_PER_SHEET:
                out.append(f'  CUT: {len(formulas) - MAX_FORMULAS_PER_SHEET} more formulas not shown. Open the original file to see them.')
            out.append(f'Values (first {MAX_ROWS_PER_SHEET} rows that have content):')
            out += rows or ['  (empty)']
            if total_rows > MAX_ROWS_PER_SHEET:
                out.append(f'  CUT: {total_rows - MAX_ROWS_PER_SHEET} more rows not shown (sheet has {total_rows}).')

            # Charts drawn on this sheet
            for drawing in _rels(z, part).values():
                if 'drawings/' not in drawing or drawing not in names:
                    continue
                for chart in _rels(z, drawing).values():
                    if chart in names and '/charts/' in chart:
                        title, kinds, refs = _chart_summary(z, chart)
                        chart_lines.append(f'  On sheet "{name}": {Path(chart).name}'
                                           f' — type: {", ".join(kinds) or "?"}'
                                           f' — title: {title or "(none)"}')
                        chart_lines += [f'      data from: {r}' for r in refs]
        out += ['', '=' * 60, 'CHARTS (title, type and the cells each series is drawn from)', '=' * 60]
        out += chart_lines or ['  (no charts)']
    return '\n'.join(out)


# ------------------------------------------------------------------- PDF

def extract_pdf(path, work_dir):
    text = run([tool('pdftotext'), '-layout', str(path), '-']).stdout
    if len(re.sub(r'\s+', '', text)) >= 200:
        return text, 'text layer'
    if not find_tool('tesseract') or not find_tool('pdftoppm'):
        return text, 'little text found; OCR not available (tesseract missing)'
    ocr_dir = Path(tempfile.mkdtemp(prefix='ocr_', dir=work_dir))
    try:
        run([tool('pdftoppm'), '-r', '200', '-png', str(path), str(ocr_dir / 'page')])
        pages = []
        for img in sorted(ocr_dir.glob('page-*.png')):
            pages.append(run([tool('tesseract'), str(img), 'stdout']).stdout)
    finally:
        shutil.rmtree(ocr_dir, ignore_errors=True)
    return text + '\n\n[OCR TEXT]\n' + '\n'.join(pages), 'scanned; read with OCR'


# ----------------------------------------------------------- old formats

def convert_with_libreoffice(path, fmt, work_dir):
    """Convert .doc/.xls to .docx/.xlsx with LibreOffice. Returns the new path."""
    soffice = find_tool('soffice')
    if not soffice:
        raise LookupError('needs LibreOffice to read this old format')
    out = Path(tempfile.mkdtemp(prefix='convert_', dir=work_dir))
    profile = out / 'profile'
    run([soffice, '--headless', '--norestore', f'-env:UserInstallation={profile.resolve().as_uri()}',
         '--convert-to', fmt, '--outdir', str(out), str(path)], check=False)
    result = out / f'{path.stem}.{fmt}'
    if not result.exists():
        raise RuntimeError('LibreOffice could not convert it (file may be damaged)')
    return result


# ------------------------------------------------------------ one file

def extract_file(path, out_path, work_dir):
    """Extract one file to out_path. Returns (status, note). Never raises."""
    suffix = path.suffix.lower()
    try:
        if suffix in IMAGE_SUFFIXES:
            return 'skipped', 'image: look at the original file'
        if suffix not in SUPPORTED:
            return 'skipped', f'{suffix or "no extension"} files are not read'
        note = ''
        if suffix in ('.doc', '.xls'):
            try:
                path_to_read = convert_with_libreoffice(path, 'docx' if suffix == '.doc' else 'xlsx', work_dir)
            except LookupError as exc:
                return 'skipped', str(exc)
            suffix = path_to_read.suffix
            note = 'converted with LibreOffice; '
        else:
            path_to_read = path

        if suffix == '.docx':
            text = extract_docx(path_to_read)
            embedded, notes = extract_embedded_from_docx(path_to_read, out_path.parent / 'embedded')
            for emb in embedded:
                text += f'\n\n[SPREADSHEET PASTED INTO THE DOCUMENT: {emb.name}]\n'
                try:
                    text += extract_xlsx(emb) if emb.suffix.lower() != '.xls' else '(old .xls; not read)'
                except Exception as exc:
                    text += f'(could not read it: {exc})'
            for n in notes:
                text += f'\n[NOTE] {n}'
            note += f'{len(embedded)} pasted spreadsheet(s)' if embedded else 'text'
        elif suffix in ('.xlsx', '.xlsm'):
            text = extract_xlsx(path_to_read)
            note += 'formulas, values, charts'
        elif suffix == '.pdf':
            if not find_tool('pdftotext'):
                return 'skipped', 'needs poppler (pdftotext) to read PDFs'
            text, how = extract_pdf(path, out_path.parent)
            note += how
        else:
            raw = path.read_text(encoding='utf-8', errors='replace')
            text = raw[:MAX_TEXT_FILE_CHARS]
            if len(raw) > MAX_TEXT_FILE_CHARS:
                text += f'\n\nCUT: {len(raw) - MAX_TEXT_FILE_CHARS} more characters not shown.'
            note += 'plain text'
        write_text(out_path, text)
        return 'extracted', note
    except Exception as exc:
        write_text(out_path, f'EXTRACTION FAILED for {path.name}: {exc}\nRead the original file directly.')
        return 'failed', str(exc) or exc.__class__.__name__


def iter_files(in_path):
    if in_path.is_file():
        yield in_path, Path(in_path.name)
        return
    for p in sorted(in_path.rglob('*')):
        if p.is_file() and not p.name.startswith(('.', '~$')):
            yield p, p.relative_to(in_path)


def main():
    utf8_console()
    parser = argparse.ArgumentParser(description='Extract text from submitted files.')
    parser.add_argument('--input', required=True, help='File or folder (subfolders included)')
    parser.add_argument('--out', required=True, help='Folder for the extracted text')
    args = parser.parse_args()

    in_path, out_dir = Path(args.input), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {'extracted': 0, 'skipped': 0, 'failed': 0}
    for path, rel in iter_files(in_path):
        status, note = extract_file(path, out_dir / rel.parent / f'{rel.name}.txt', out_dir)
        counts[status] += 1
        print(f'{status:9} {rel}  ({note})')
    print(f"\n{counts['extracted']} extracted, {counts['skipped']} skipped, {counts['failed']} failed")
    return 0


if __name__ == '__main__':
    sys.exit(main())
