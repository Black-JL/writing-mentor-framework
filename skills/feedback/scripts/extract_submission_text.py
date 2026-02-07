#!/usr/bin/env python3
import argparse
import io
import re
import struct
import subprocess
import sys
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import olefile

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    's': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
}


def run(cmd, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def write_text(path, text):
    path.write_text(text, encoding='utf-8', errors='ignore')


def extract_docx(path):
    """Extract text, track changes, and comments from a DOCX file."""
    text_parts = []
    track_changes = {
        'insertions': [],
        'deletions': [],
    }
    comments = []
    comment_map = {}  # id -> comment text

    try:
        with zipfile.ZipFile(path) as z:
            # First, extract comments if they exist
            if 'word/comments.xml' in z.namelist():
                with z.open('word/comments.xml') as f:
                    tree = ET.parse(f)
                    for comment in tree.findall('.//w:comment', NS):
                        comment_id = comment.attrib.get(f"{{{NS['w']}}}id")
                        author = comment.attrib.get(f"{{{NS['w']}}}author", "Unknown")
                        date = comment.attrib.get(f"{{{NS['w']}}}date", "")
                        # Get comment text
                        comment_text = []
                        for t in comment.iter():
                            if t.tag == f"{{{NS['w']}}}t" and t.text:
                                comment_text.append(t.text)
                        if comment_id and comment_text:
                            full_text = ''.join(comment_text)
                            comment_map[comment_id] = {
                                'author': author,
                                'date': date,
                                'text': full_text
                            }
                            comments.append({
                                'id': comment_id,
                                'author': author,
                                'date': date,
                                'text': full_text
                            })

            # Extract main document with track changes
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)

                for node in tree.iter():
                    # Regular text
                    if node.tag == f"{{{NS['w']}}}t" and node.text:
                        text_parts.append(node.text)

                    # Track changes - insertions
                    elif node.tag == f"{{{NS['w']}}}ins":
                        author = node.attrib.get(f"{{{NS['w']}}}author", "Unknown")
                        date = node.attrib.get(f"{{{NS['w']}}}date", "")
                        ins_text = []
                        for t in node.iter():
                            if t.tag == f"{{{NS['w']}}}t" and t.text:
                                ins_text.append(t.text)
                        if ins_text:
                            track_changes['insertions'].append({
                                'author': author,
                                'date': date,
                                'text': ''.join(ins_text)
                            })

                    # Track changes - deletions
                    elif node.tag == f"{{{NS['w']}}}del":
                        author = node.attrib.get(f"{{{NS['w']}}}author", "Unknown")
                        date = node.attrib.get(f"{{{NS['w']}}}date", "")
                        del_text = []
                        for t in node.iter():
                            if t.tag == f"{{{NS['w']}}}delText" and t.text:
                                del_text.append(t.text)
                        if del_text:
                            track_changes['deletions'].append({
                                'author': author,
                                'date': date,
                                'text': ''.join(del_text)
                            })

                    # Comment references (marks where comments are in the text)
                    elif node.tag == f"{{{NS['w']}}}commentRangeStart":
                        comment_id = node.attrib.get(f"{{{NS['w']}}}id")
                        if comment_id and comment_id in comment_map:
                            text_parts.append(f" [COMMENT: {comment_map[comment_id]['text'][:50]}...] ")

    except Exception as exc:
        return f"[docx extract error: {exc}]"

    # Build output
    output = []
    output.append("=" * 60)
    output.append("DOCUMENT TEXT")
    output.append("=" * 60)
    output.append("\n".join(text_parts))

    # Add track changes section if any exist
    if track_changes['insertions'] or track_changes['deletions']:
        output.append("\n" + "=" * 60)
        output.append("TRACK CHANGES DETECTED")
        output.append("=" * 60)
        output.append("The writer submitted with track changes enabled.")
        output.append("Use these to understand what was modified from the previous version.")
        output.append("")

        if track_changes['insertions']:
            output.append("-" * 40)
            output.append(f"INSERTIONS ({len(track_changes['insertions'])} found):")
            output.append("-" * 40)
            for i, ins in enumerate(track_changes['insertions'][:50], 1):  # Limit to 50
                output.append(f"  [{i}] \"{ins['text'][:200]}{'...' if len(ins['text']) > 200 else ''}\"")
                if ins['author'] != "Unknown":
                    output.append(f"      - by {ins['author']}")
            if len(track_changes['insertions']) > 50:
                output.append(f"  ... and {len(track_changes['insertions']) - 50} more insertions")

        if track_changes['deletions']:
            output.append("-" * 40)
            output.append(f"DELETIONS ({len(track_changes['deletions'])} found):")
            output.append("-" * 40)
            for i, dele in enumerate(track_changes['deletions'][:50], 1):  # Limit to 50
                output.append(f"  [{i}] \"{dele['text'][:200]}{'...' if len(dele['text']) > 200 else ''}\"")
                if dele['author'] != "Unknown":
                    output.append(f"      - by {dele['author']}")
            if len(track_changes['deletions']) > 50:
                output.append(f"  ... and {len(track_changes['deletions']) - 50} more deletions")

    # Add comments section if any exist
    if comments:
        output.append("\n" + "=" * 60)
        output.append("COMMENTS IN DOCUMENT")
        output.append("=" * 60)
        output.append("The writer's document contains comments.")
        output.append("These may be instructor feedback or writer notes.")
        output.append("")
        for i, comment in enumerate(comments[:30], 1):  # Limit to 30
            output.append(f"  [{i}] {comment['author']}: \"{comment['text'][:300]}{'...' if len(comment['text']) > 300 else ''}\"")
        if len(comments) > 30:
            output.append(f"  ... and {len(comments) - 30} more comments")

    return "\n".join(output)


def _parse_ole10_native(data):
    try:
        pos = 0
        _total = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        pos += 2
        pos += 2
        end = data.index(b"\x00", pos)
        filename = data[pos:end].decode("latin1", errors="ignore")
        pos = end + 1
        end = data.index(b"\x00", pos)
        pos = end + 1
        pos += 4
        pos += 4
        size = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        filedata = data[pos:pos + size]
        return filename, filedata
    except Exception:
        return None, None


def extract_embedded_from_docx(path, out_dir):
    embedded_paths = []
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if not name.startswith("word/embeddings/"):
                    continue
                base = Path(name).name
                data = z.read(name)
                if base.lower().endswith((".xlsx", ".xlsm", ".xls")):
                    out_path = out_dir / f"{path.stem}__{base}"
                    out_path.write_bytes(data)
                    embedded_paths.append(out_path)
                elif base.lower().endswith(".bin"):
                    try:
                        ole = olefile.OleFileIO(io.BytesIO(data))
                        if ole.exists("\x01Ole10Native"):
                            stream = ole.openstream("\x01Ole10Native").read()
                            fname, fdata = _parse_ole10_native(stream)
                            if fdata:
                                safe = Path(fname).name if fname else f"{base}.bin"
                                out_path = out_dir / f"{path.stem}__{safe}"
                                out_path.write_bytes(fdata)
                                embedded_paths.append(out_path)
                        ole.close()
                    except Exception:
                        continue
    except Exception:
        return embedded_paths
    return embedded_paths


def extract_xlsx(path):
    strings = []
    sheets = {}
    formulas = []
    charts = []
    try:
        with zipfile.ZipFile(path) as z:
            if 'xl/sharedStrings.xml' in z.namelist():
                with z.open('xl/sharedStrings.xml') as f:
                    tree = ET.parse(f)
                    for t in tree.iter():
                        if t.tag.endswith('}t') and t.text:
                            strings.append(t.text)
            if 'xl/workbook.xml' in z.namelist():
                with z.open('xl/workbook.xml') as f:
                    tree = ET.parse(f)
                    for sh in tree.findall('.//s:sheets/s:sheet', NS):
                        name = sh.attrib.get('name')
                        if name:
                            sheets[name] = []
            for name in z.namelist():
                if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                    with z.open(name) as f:
                        tree = ET.parse(f)
                        rows = []
                        for row in tree.findall('.//s:row', NS):
                            row_vals = []
                            for c in row.findall('s:c', NS):
                                v = c.find('s:v', NS)
                                t = c.attrib.get('t')
                                if t == 's' and v is not None and v.text is not None:
                                    idx = int(v.text)
                                    if 0 <= idx < len(strings):
                                        row_vals.append(strings[idx])
                                elif t == 'inlineStr':
                                    isv = c.find('s:is/s:t', NS)
                                    if isv is not None and isv.text:
                                        row_vals.append(isv.text)
                                elif v is not None and v.text:
                                    row_vals.append(v.text)
                                fnode = c.find('s:f', NS)
                                if fnode is not None and fnode.text:
                                    formulas.append(fnode.text)
                            if row_vals:
                                rows.append(row_vals)
                            if len(rows) >= 40:
                                break
                        if sheets:
                            sheet_name = next(iter(sheets))
                            sheets[sheet_name] = rows
            charts = [n for n in z.namelist() if n.startswith('xl/charts/chart')]
    except Exception as exc:
        return {"error": str(exc)}

    out = []
    out.append(f"FILE: {path.name}")
    out.append("CHART_FILES:")
    out.extend(charts)
    out.append("FORMULAS:")
    out.extend(formulas[:200])
    out.append("SHEETS_PREVIEW:")
    for sheet, rows in sheets.items():
        out.append(f"[Sheet] {sheet}")
        for row in rows:
            out.append("\t" + " | ".join(row))
    uniq = []
    seen = set()
    for s in strings:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
        if len(uniq) >= 200:
            break
    out.append("UNIQUE_STRINGS:")
    out.extend(uniq)
    return "\n".join(out)


def extract_pdf(path, out_dir):
    txt_path = out_dir / f"{path.name}.txt"
    try:
        result = run(['pdftotext', str(path), '-'])
        text = result.stdout
    except Exception as exc:
        text = f"[pdftotext error: {exc}]"

    # If text is too small, fall back to OCR
    if len(re.sub(r'\s+', '', text)) < 200:
        ocr_text = []
        img_prefix = out_dir / path.stem
        try:
            run(['pdftoppm', '-r', '200', '-png', str(path), str(img_prefix)])
            for img in sorted(out_dir.glob(f"{path.stem}-*.png")):
                ocr = run(['tesseract', str(img), 'stdout'])
                ocr_text.append(ocr.stdout)
        except Exception as exc:
            ocr_text.append(f"[ocr error: {exc}]")
        text = text + "\n" + "\n".join(ocr_text)
    write_text(txt_path, text)


def extract(path, out_dir):
    suffix = path.suffix.lower()
    out_path = out_dir / f"{path.name}.txt"
    if suffix == '.docx':
        text = extract_docx(path)
        embedded_dir = out_dir / "embedded"
        embedded_dir.mkdir(parents=True, exist_ok=True)
        embedded_files = extract_embedded_from_docx(path, embedded_dir)
        if embedded_files:
            text += "\n\n[EMBEDDED_FILES]\n"
            for embedded in embedded_files:
                if embedded.suffix.lower() in {'.xlsx', '.xlsm', '.xls'}:
                    text += f"\n[Embedded] {embedded.name}\n"
                    text += extract_xlsx(embedded)
                else:
                    text += f"\n[Embedded] {embedded.name} (unparsed)\n"
        write_text(out_path, text)
    elif suffix == '.xlsx':
        data = extract_xlsx(path)
        if isinstance(data, dict) and 'error' in data:
            write_text(out_path, f"ERROR: {data['error']}")
        else:
            write_text(out_path, data)
    elif suffix == '.pdf':
        extract_pdf(path, out_dir)


def main():
    parser = argparse.ArgumentParser(description='Extract text from DOCX/PDF/XLSX submissions.')
    parser.add_argument('--input', required=True, help='File or directory to process')
    parser.add_argument('--out', required=True, help='Output directory for extracted text')
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if in_path.is_dir():
        for path in sorted(in_path.iterdir()):
            if path.suffix.lower() in {'.docx', '.xlsx', '.pdf'}:
                extract(path, out_dir)
    else:
        extract(in_path, out_dir)


if __name__ == '__main__':
    main()
