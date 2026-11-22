#!/usr/bin/env python3
"""
Render every XLSX in a folder to PNG images so charts can be reviewed visually.

Tries, in order, whatever is installed on this computer:
  1. Microsoft Excel (macOS or Windows): best chart fidelity
  2. LibreOffice (any system)
  3. Quick Look (macOS only): first sheet only, lowest fidelity

If none works, it prints why and exits 0. The review continues without chart
images; formulas and values are still read by extract_submission_text.py.
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

from _tools import IS_MAC, IS_WINDOWS, find_tool, utf8_console


def excel_available():
    if IS_MAC:
        return Path('/Applications/Microsoft Excel.app').exists()
    if IS_WINDOWS:
        try:
            import winreg
            winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'Excel.Application'))
            return True
        except OSError:
            return False
    return False


def methods():
    """Renderers to try, best first. WMF_CHART_TOOLS (e.g. "libreoffice" or "none") limits them."""
    allowed = os.environ.get('WMF_CHART_TOOLS', 'excel,libreoffice,quicklook').lower().split(',')
    found = [m for m in _all_methods() if m[0].lower().replace(' ', '') in allowed]
    return found


def render_file(path, out_dir, available=None):
    """Render one workbook. Returns (method name or None, list of error notes)."""
    errors = []
    for name, render in (methods() if available is None else available):
        try:
            render(path, out_dir)
            return name, errors
        except Exception as exc:
            errors.append(f'{name}: {exc}')
    return None, errors


def _all_methods():
    found = []
    if excel_available() and find_tool('pdftoppm'):
        import render_xlsx_excel
        found.append(('Excel', render_xlsx_excel.render_xlsx))
    if find_tool('soffice') and find_tool('pdftoppm'):
        import render_xlsx
        found.append(('LibreOffice', render_xlsx.render_xlsx))
    if IS_MAC and shutil.which('qlmanage'):
        import render_xlsx_quicklook
        found.append(('Quick Look', render_xlsx_quicklook.render_xlsx))
    return found


def main():
    utf8_console()
    parser = argparse.ArgumentParser(description='Render XLSX charts to PNG with the best available tool.')
    parser.add_argument('--input', required=True, help='XLSX file or directory')
    parser.add_argument('--out', required=True, help='Output directory')
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    files = sorted(p for p in in_path.iterdir() if p.suffix.lower() == '.xlsx') if in_path.is_dir() else [in_path]
    if not files:
        print("No .xlsx files to render.")
        return 0

    available = methods()
    if not available:
        print("Chart images skipped: no renderer found. Install Microsoft Excel or "
              "LibreOffice, plus poppler (pdftoppm). Formulas and values are still extracted.")
        return 0

    failed = []
    for path in files:
        used, errors = render_file(path, out_dir, available)
        for e in errors:
            print(f"  {e}")
        if used:
            print(f"Rendered {path.name} with {used}")
        else:
            failed.append(path.name)

    if failed:
        print(f"No chart images for: {', '.join(failed)}. Review those charts from formulas only.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
